import urllib.request
import urllib.parse
import urllib.error
import json
import time
import signal
import sys
from queue import Queue, Empty
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from services.git_client import GitClient
from services.repository_scanner import RepositoryScanner
from services.aggregator import AssessmentAggregator
from services.database import Database
from models.entities import LanguageScore, TechCategory, LANGUAGE_CATEGORY


# ============================================================
# НАСТРОЙКИ
# ============================================================
MAX_REPOS_PER_QUERY = 5
PAGE_SIZE = 30
PAUSE_BETWEEN_REQUESTS = 2
NUM_WORKERS = 4  # Количество параллельных агентов

SEARCH_QUERIES = [
    "language:python stars:>10000",
    "language:javascript stars:>10000",
    "language:java stars:>5000",
    "language:typescript stars:>5000",
    "language:go stars:>3000",
]

stop_requested = False

def signal_handler(sig, frame):
    global stop_requested
    print("\n[WARNING] Остановка запрошена...")
    stop_requested = True

signal.signal(signal.SIGINT, signal_handler)


# ============================================================
# ПОИСК ЧЕРЕЗ API
# ============================================================
def search_github_repos(query, max_results=5):
    all_repos = []
    seen_urls = set()
    page = 1
    encoded_query = urllib.parse.quote(query)
    
    while len(all_repos) < max_results:
        url = (f"https://api.github.com/search/repositories?"
               f"q={encoded_query}&per_page={PAGE_SIZE}&page={page}"
               f"&sort=stars&order=desc")
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'PolySkill-App',
            'Accept': 'application/vnd.github.v3+json'
        })
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("    [WARNING] Лимит API. Ждём 60 секунд...")
                time.sleep(60)
                continue
            else:
                print(f"    [ERROR] Ошибка API: {e.code}")
                break
        except Exception as e:
            print(f"    [ERROR] Ошибка: {e}")
            break
        
        items = data.get('items', [])
        if not items:
            break
        
        for item in items:
            if len(all_repos) >= max_results:
                break
            clone_url = item.get('clone_url', '')
            if clone_url and clone_url not in seen_urls:
                seen_urls.add(clone_url)
                all_repos.append({
                    'name': item['name'],
                    'url': clone_url,
                    'language': item.get('language', 'Unknown'),
                    'stars': item.get('stargazers_count', 0),
                    'description': (item.get('description') or '')[:100],
                    'full_name': item['full_name'],
                })
        
        if len(items) < PAGE_SIZE:
            break
        page += 1
        time.sleep(PAUSE_BETWEEN_REQUESTS)
    
    return all_repos


# ============================================================
# АГЕНТ-РАБОТНИК (Producer)
# ============================================================
def worker_agent(repo, worker_id, result_queue, temp_base):
    """
    Параллельный агент: клонирует, парсит, кладёт результат в очередь.
    """
    global stop_requested
    
    if stop_requested:
        return
    
    name = repo['name']
    url = repo['url']
    langs = [repo['language']] if repo['language'] else ['Python']
    
    # Каждый агент работает в своей папке, чтобы не было конфликтов
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
            # Кладём результат в очередь (не в БД!)
            result_queue.put({
                'url': url,
                'name': name,
                'result': result,
                'scores': scores,
                'status': 'success'
            })
            print(f"  [Worker-{worker_id}] ✅ {name}: {result.overall_score}%")
        else:
            result_queue.put({
                'url': url,
                'name': name,
                'status': 'no_data'
            })
            print(f"  [Worker-{worker_id}] ⚠ {name}: нет данных")
        
        git_client.cleanup_all()
        
    except Exception as e:
        result_queue.put({
            'url': url,
            'name': name,
            'status': 'error',
            'error': str(e)
        })
        print(f"  [Worker-{worker_id}] ❌ {name}: {str(e)[:50]}")


# ============================================================
# АГЕНТ-ПОТРЕБИТЕЛЬ (Consumer)
# ============================================================
def db_writer(result_queue, db, total_tasks):
    """
    Последовательно читает из очереди и записывает в БД.
    """
    written = 0
    skipped = 0
    errors = 0
    
    print(f"\n[DB Writer] Ожидание результатов ({total_tasks} задач)...")
    
    while written + skipped + errors < total_tasks:
        try:
            item = result_queue.get(timeout=5)
            
            if item['status'] == 'success':
                # Проверяем, нет ли уже в БД
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
                    print(f"  [DB Writer] ✅ Записано: {item['name']}")
                else:
                    skipped += 1
                    print(f"  [DB Writer] ⏭ Пропущено (уже в БД): {item['name']}")
            
            elif item['status'] == 'no_data':
                skipped += 1
                print(f"  [DB Writer] ⚠ Нет данных: {item['name']}")
            
            elif item['status'] == 'error':
                errors += 1
                print(f"  [DB Writer] ❌ Ошибка: {item['name']} - {item.get('error', '')}")
            
            result_queue.task_done()
            
        except Empty:
            # Очередь пуста, но задачи ещё не завершены
            continue
        except Exception as e:
            print(f"  [DB Writer] [ERROR] {e}")
            errors += 1
    
    print(f"\n[DB Writer] Завершено: {written} записано, {skipped} пропущено, {errors} ошибок")
    return written, skipped, errors


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================
def main():
    global stop_requested
    
    print("=" * 70)
    print("[START] ПАРАЛЛЕЛЬНЫЙ АНАЛИЗ ЧЕРЕЗ GITHUB API")
    print("=" * 70)
    print(f"Критериев поиска: {len(SEARCH_QUERIES)}")
    print(f"Макс. проектов на критерий: {MAX_REPOS_PER_QUERY}")
    print(f"Количество параллельных агентов: {NUM_WORKERS}")
    print("=" * 70)
    
    db = Database()
    
    # ШАГ 1: Поиск через API
    print("\n[SEARCH] ШАГ 1: Поиск репозиториев")
    print("-" * 70)
    
    all_repos = []
    seen_urls = set()
    
    for i, query in enumerate(SEARCH_QUERIES, 1):
        if stop_requested:
            break
        print(f"\n[{i}/{len(SEARCH_QUERIES)}] {query}")
        repos = search_github_repos(query, max_results=MAX_REPOS_PER_QUERY)
        for repo in repos:
            if repo['url'] not in seen_urls:
                seen_urls.add(repo['url'])
                all_repos.append(repo)
        print(f"    Найдено: {len(repos)}, Всего уникальных: {len(all_repos)}")
        if i < len(SEARCH_QUERIES):
            time.sleep(PAUSE_BETWEEN_REQUESTS)
    
    print(f"\n[OK] Найдено уникальных репозиториев: {len(all_repos)}")
    
    if not all_repos:
        print("[DONE] Нет проектов для анализа")
        return
    
    # ШАГ 2: Параллельный анализ
    print("\n[ANALYSIS] ШАГ 2: Параллельный анализ")
    print("-" * 70)
    
    result_queue = Queue()
    temp_base = "./temp_repos_parallel"
    
    # Запускаем агента-потребителя (DB Writer) в отдельном потоке
    db_writer_thread = Thread(
        target=db_writer,
        args=(result_queue, db, len(all_repos)),
        daemon=True
    )
    db_writer_thread.start()
    
    # Запускаем агентов-работников параллельно
    print(f"\n[WORKERS] Запуск {NUM_WORKERS} параллельных агентов...")
    
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
        
        # Ждём завершения всех задач
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"  [ERROR] Ошибка в потоке: {e}")
    
    # Ждём, пока DB Writer обработает все результаты
    result_queue.join()
    db_writer_thread.join(timeout=10)
    
    # ШАГ 3: Очистка очереди и статистика
    print("\n" + "=" * 70)
    print("[STATS] ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)
    
    projects = db.get_all_projects()
    langs = db.get_unique_languages()
    
    print(f"[DB] Всего проектов в БД: {len(projects)}")
    print(f"[LANG] Уникальных языков: {len(langs)}")
    print(f"[LANG] Языки: {', '.join(sorted(langs))}")
    
    print("\n[TOP] ТОП-5 проектов:")
    sorted_projects = sorted(projects, key=lambda x: x[3] or 0, reverse=True)[:5]
    for idx, p in enumerate(sorted_projects, 1):
        print(f"  {idx}. {p[1]} — {p[3]}% ({p[4]})")
    
    # Очистка временных папок
    print("\n[CLEANUP] Очистка временных папок...")
    import shutil
    temp_path = Path(temp_base)
    if temp_path.exists():
        try:
            shutil.rmtree(temp_path)
            print("[OK] Временные папки удалены")
        except Exception as e:
            print(f"[WARNING] Не удалось удалить: {e}")
    
    print("\n[DONE] Готово! Откройте gui_app.py")
    print("=" * 70)


if __name__ == '__main__':
    main()