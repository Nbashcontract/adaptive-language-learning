import time
import signal
from queue import Queue, Empty
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from services.git_client import GitClient
from services.repository_scanner import RepositoryScanner
from services.aggregator import AssessmentAggregator
from services.database import Database
from services.repo_sources import RepoSourceFactory
from models.entities import LanguageScore, TechCategory, LANGUAGE_CATEGORY

MAX_REPOS_PER_QUERY = 5
NUM_WORKERS = 4

QUERIES_BY_SOURCE = {
    'github': [
        "language:python stars:>10000",
        "language:javascript stars:>10000",
    ],
    'gitlab': [
        "python",
        "javascript",
    ],
    'gitverse': [
        "python",
        "javascript",
    ],
}

stop_requested = False

def signal_handler(sig, frame):
    global stop_requested
    print("\n[WARNING] Остановка запрошена...")
    stop_requested = True

signal.signal(signal.SIGINT, signal_handler)


def search_repos_from_sources(queries_by_source, max_per_query=5):
    all_repos = []
    seen_urls = set()

    for source_name, queries in queries_by_source.items():
        print(f"\n[SEARCH] Источник: {source_name.upper()} (HTML-парсинг)")
        print("-" * 70)

        source = RepoSourceFactory.create(source_name, headless=True)
        try:
            source.start()

            for i, query in enumerate(queries, 1):
                if stop_requested:
                    break
                print(f"\n[{i}/{len(queries)}] Запрос: {query}")
                repos = source.search_repositories(query, max_results=max_per_query)

                for repo in repos:
                    if repo['url'] not in seen_urls:
                        seen_urls.add(repo['url'])
                        all_repos.append(repo)

                print(f"    Всего уникальных: {len(all_repos)}")

                if i < len(queries):
                    time.sleep(1)

        finally:
            source.stop()

    print(f"\n[OK] Всего найдено: {len(all_repos)}")
    return all_repos


def worker_agent(repo, worker_id, result_queue, temp_base):
    global stop_requested

    if stop_requested:
        return

    name = repo['name']
    url = repo['url']
    langs = [repo['language']] if repo['language'] else ['Python']
    temp_path = f"{temp_base}/worker_{worker_id}"

    try:
        print(f"  [Worker-{worker_id}] Анализ {repo['full_name']}...")

        git_client = GitClient(temp_path)
        scanner = RepositoryScanner(git_client)
        aggregator = AssessmentAggregator()

        metrics = scanner.scan_repository(url, langs)

        scores = []
        for lang, m_list in metrics.items():
            if not m_list:
                continue
            cat = LANGUAGE_CATEGORY.get(lang.lower(), TechCategory.ALGORITHM)
            avg_loc = sum(m.lines_of_code for m in m_list) / len(m_list)
            type_ratio = sum(1 for m in m_list if m.has_type_hints) / len(m_list)
            err_ratio = sum(1 for m in m_list if m.has_error_handling) / len(m_list)
            score = min(100, max(0,
                min(100, avg_loc / 5) * 0.3 +
                type_ratio * 100 * 0.4 +
                err_ratio * 100 * 0.3
            ))
            scores.append(LanguageScore(language=lang, score=score, category=cat))

        if scores:
            result = aggregator.aggregate(scores)
            result_queue.put({
                'url': url,
                'name': name,
                'result': result,
                'scores': scores,
                'status': 'success'
            })
            print(f"  [Worker-{worker_id}] OK: {result.overall_score}%")
        else:
            result_queue.put({
                'url': url,
                'name': name,
                'status': 'no_data'
            })
            print(f"  [Worker-{worker_id}] Пропуск: нет данных")

        git_client.cleanup_all()

    except Exception as e:
        result_queue.put({
            'url': url,
            'name': name,
            'status': 'error',
            'error': str(e)
        })
        print(f"  [Worker-{worker_id}] Ошибка: {str(e)[:50]}")


def db_writer(result_queue, db, total_tasks):
    written = 0
    skipped = 0
    errors = 0

    print(f"\n[DB Writer] Ожидание результатов ({total_tasks} задач)...")

    while written + skipped + errors < total_tasks:
        try:
            item = result_queue.get(timeout=5)

            if item['status'] == 'success':
                existing = db.get_all_projects()
                already_exists = any(p[2] == item['url'] for p in existing)

                if not already_exists:
                    db.save_assessment(
                        item['url'],
                        item['name'],
                        item['result'],
                        item['scores']
                    )
                    written += 1
                    print(f"  [DB Writer] Записано: {item['name']}")
                else:
                    skipped += 1
                    print(f"  [DB Writer] Пропущено (дубликат): {item['name']}")

            elif item['status'] == 'no_data':
                skipped += 1
                print(f"  [DB Writer] Пропущено (нет данных): {item['name']}")

            elif item['status'] == 'error':
                errors += 1
                print(f"  [DB Writer] Ошибка: {item['name']}")

            result_queue.task_done()

        except Empty:
            continue
        except Exception as e:
            print(f"  [DB Writer] Критическая ошибка: {e}")
            errors += 1

    print(f"\n[DB Writer] Завершено: {written} записано, {skipped} пропущено, {errors} ошибок")
    return written, skipped, errors


def main():
    global stop_requested

    print("=" * 70)
    print("[START] ПАРАЛЛЕЛЬНЫЙ АНАЛИЗ ЧЕРЕЗ HTML-ПАРСИНГ")
    print("=" * 70)
    print(f"Источники: {', '.join(QUERIES_BY_SOURCE.keys())}")
    print(f"Рабочих агентов: {NUM_WORKERS}")
    print("=" * 70)

    db = Database()

    print("\n[SEARCH] ШАГ 1: Поиск репозиториев через браузер")
    print("-" * 70)

    all_repos = search_repos_from_sources(QUERIES_BY_SOURCE, max_per_query=MAX_REPOS_PER_QUERY)

    if not all_repos:
        print("[DONE] Нет проектов для анализа")
        return

    print("\n[ANALYSIS] ШАГ 2: Параллельный анализ")
    print("-" * 70)

    result_queue = Queue()
    temp_base = "./temp_repos_parallel"

    db_writer_thread = Thread(
        target=db_writer,
        args=(result_queue, db, len(all_repos)),
        daemon=True
    )
    db_writer_thread.start()

    print(f"\n[WORKERS] Запуск {NUM_WORKERS} агентов...")

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = []
        for i, repo in enumerate(all_repos):
            if stop_requested:
                break
            worker_id = (i % NUM_WORKERS) + 1
            future = executor.submit(
                worker_agent,
                repo,
                worker_id,
                result_queue,
                temp_base
            )
            futures.append(future)

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"  [ERROR] Ошибка в потоке: {e}")

    result_queue.join()
    db_writer_thread.join(timeout=10)

    print("\n" + "=" * 70)
    print("[STATS] ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)

    projects = db.get_all_projects()
    langs = db.get_unique_languages()

    print(f"[DB] Всего проектов: {len(projects)}")
    print(f"[LANG] Языков: {len(langs)}")
    print(f"[LANG] {', '.join(sorted(langs))}")

    print("\n[TOP] ТОП-5 проектов:")
    sorted_projects = sorted(projects, key=lambda x: x[3] or 0, reverse=True)[:5]
    for idx, p in enumerate(sorted_projects, 1):
        print(f"  {idx}. {p[1]} - {p[3]}% ({p[4]})")

    import shutil
    temp_path = Path(temp_base)
    if temp_path.exists():
        try:
            shutil.rmtree(temp_path)
            print("\n[CLEANUP] Временные папки удалены")
        except Exception as e:
            print(f"\n[WARNING] Не удалось удалить: {e}")

    print("\n[DONE] Откройте gui_app.py")
    print("=" * 70)


if __name__ == '__main__':
    main()
