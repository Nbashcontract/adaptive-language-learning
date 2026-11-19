import urllib.request
import urllib.parse
import urllib.error
import json
import time
import signal
import sys
from services.git_client import GitClient
from services.repository_scanner import RepositoryScanner
from services.aggregator import AssessmentAggregator
from services.database import Database
from models.entities import LanguageScore, TechCategory, LANGUAGE_CATEGORY


# ============================================================
# НАСТРОЙКИ ПОИСКА
# ============================================================
MAX_REPOS_PER_QUERY = 50  # Сколько проектов брать по каждому критерию
PAGE_SIZE = 30            # Максимум на одной странице GitHub API
PAUSE_BETWEEN_REQUESTS = 3  # Пауза между запросами к API (сек)
PAUSE_BETWEEN_REPOS = 1     # Пауза между анализом проектов (сек)

# Критерии поиска — каждый запрос даст УНИКАЛЬНУЮ выборку
SEARCH_QUERIES = [
    # Python — разные категории
    "language:python stars:>10000",
    "language:python topic:web-framework stars:>1000",
    "language:python topic:machine-learning stars:>500",
    "language:python topic:data-science stars:>500",
    "language:python topic:automation stars:>200",
    
    # JavaScript / TypeScript
    "language:javascript stars:>10000",
    "language:typescript stars:>5000",
    "language:javascript topic:react stars:>1000",
    "language:typescript topic:vue stars:>500",
    
    # Другие языки
    "language:java stars:>5000",
    "language:java topic:spring stars:>1000",
    "language:go stars:>3000",
    "language:go topic:api stars:>500",
    "language:rust stars:>2000",
    "language:rust topic:web stars:>200",
    "language:c stars:>3000",
    "language:c++ stars:>3000",
    "language:swift stars:>2000",
    "language:kotlin stars:>2000",
    "language:php stars:>3000",
    "language:ruby stars:>3000",
    "language:scala stars:>1000",
]

# Глобальный флаг для graceful shutdown
stop_requested = False

def signal_handler(sig, frame):
    global stop_requested
    print("\n\n[WARNING] Остановка запрошена. Завершаю текущий проект и сохраняю прогресс...")
    stop_requested = True

signal.signal(signal.SIGINT, signal_handler)


# ============================================================
# ФУНКЦИИ
# ============================================================
def search_github_repos(query, max_results=50):
    """
    Ищет репозитории на GitHub через REST API с пагинацией.
    Возвращает список уникальных репозиториев (до max_results штук).
    """
    all_repos = []
    seen_urls = set()
    page = 1
    
    encoded_query = urllib.parse.quote(query)
    
    while len(all_repos) < max_results:
        url = (f"https://api.github.com/search/repositories?"
               f"q={encoded_query}&per_page={PAGE_SIZE}&page={page}"
               f"&sort=stars&order=desc")
        
        print(f"    Страница {page}: {url[:80]}...")
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'PolySkill-App',
            'Accept': 'application/vnd.github.v3+json'
        })
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("    [WARNING] Лимит API исчерпан. Ждём 60 секунд...")
                time.sleep(60)
                continue
            else:
                print(f"    [ERROR] Ошибка API: {e.code} {e.reason}")
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
        
        # Если получили меньше чем PAGE_SIZE — дальше страниц нет
        if len(items) < PAGE_SIZE:
            break
        
        page += 1
        time.sleep(PAUSE_BETWEEN_REQUESTS)
    
    print(f"    Найдено уникальных репозиториев: {len(all_repos)}")
    return all_repos


def is_already_in_db(url, db):
    """Проверяет, есть ли проект уже в БД"""
    projects = db.get_all_projects()
    for proj in projects:
        if proj[2] == url:  # proj[2] = url
            return True
    return False


def analyze_repo(name, url, langs, git_client, scanner, aggregator, db):
    """Анализирует один репозиторий и сохраняет в БД"""
    try:
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
            db.save_assessment(url, name, result, scores)
            return True, f"{result.overall_score}% ({result.level_name})"
        return False, "Нет данных по языкам"
    except Exception as e:
        return False, f"Ошибка: {str(e)[:50]}"
    finally:
        git_client.cleanup_all()


def main():
    global stop_requested
    
    print("=" * 70)
    print("[START] ПАКЕТНЫЙ АНАЛИЗ ЧЕРЕЗ GITHUB API")
    print("=" * 70)
    print(f"Критериев поиска: {len(SEARCH_QUERIES)}")
    print(f"Макс. проектов на критерий: {MAX_REPOS_PER_QUERY}")
    print(f"Примерное кол-во проектов: до {len(SEARCH_QUERIES) * MAX_REPOS_PER_QUERY}")
    print(f"Для остановки нажмите Ctrl+C — прогресс сохранится")
    print("=" * 70)
    
    git_client = GitClient('./temp_repos')
    scanner = RepositoryScanner(git_client)
    aggregator = AssessmentAggregator()
    db = Database()
    
    # Собираем все репозитории со всех запросов
    all_repos = []
    seen_urls = set()
    
    # ШАГ 1: Поиск через API
    print("\n[SEARCH] ШАГ 1: Поиск репозиториев через GitHub API")
    print("-" * 70)
    
    for i, query in enumerate(SEARCH_QUERIES, 1):
        if stop_requested:
            print(f"\n[WARNING] Остановка после {i-1} запросов")
            break
        
        print(f"\n[{i}/{len(SEARCH_QUERIES)}] Критерий: {query}")
        repos = search_github_repos(query, max_results=MAX_REPOS_PER_QUERY)
        
        # Добавляем только уникальные
        for repo in repos:
            if repo['url'] not in seen_urls:
                seen_urls.add(repo['url'])
                all_repos.append(repo)
        
        print(f"    Всего уникальных: {len(all_repos)}")
        
        if i < len(SEARCH_QUERIES) and not stop_requested:
            time.sleep(PAUSE_BETWEEN_REQUESTS)
    
    print(f"\n[OK] Найдено уникальных репозиториев для анализа: {len(all_repos)}")
    
    # ШАГ 2: Анализ
    print("\n[ANALYSIS] ШАГ 2: Анализ репозиториев")
    print("-" * 70)
    
    success = 0
    skipped_db = 0
    failed = 0
    
    for i, repo in enumerate(all_repos, 1):
        if stop_requested:
            print(f"\n[WARNING] Остановлено на {i}/{len(all_repos)}")
            break
        
        print(f"\n[{i}/{len(all_repos)}] {repo['full_name']}")
        print(f"  [STARS] {repo['stars']} | Язык: {repo['language']}")
        print(f"  [DESC] {repo['description']}")
        
        # Проверяем БД
        if is_already_in_db(repo['url'], db):
            print(f"  [SKIP] Уже в БД, пропускаем")
            skipped_db += 1
            continue
        
        # Определяем языки для анализа
        langs = [repo['language']] if repo['language'] else ['Python']
        # Добавляем связанные языки для более полного анализа
        if repo['language'] == 'TypeScript':
            langs.append('JavaScript')
        elif repo['language'] == 'C++':
            langs.append('C')
        
        ok, info = analyze_repo(repo['name'], repo['url'], langs, 
                                git_client, scanner, aggregator, db)
        
        if ok:
            success += 1
            print(f"  [OK] Сохранено: {info}")
        else:
            failed += 1
            print(f"  [ERROR] {info}")
        
        if i < len(all_repos) and not stop_requested:
            time.sleep(PAUSE_BETWEEN_REPOS)
    
    # ШАГ 3: Статистика
    print("\n" + "=" * 70)
    print("[STATS] ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)
    
    projects = db.get_all_projects()
    langs = db.get_unique_languages()
    
    print(f"[OK] Успешно проанализировано в этом запуске: {success}")
    print(f"[SKIP] Пропущено (уже в БД): {skipped_db}")
    print(f"[ERROR] Ошибки: {failed}")
    print(f"[DB] ВСЕГО проектов в БД: {len(projects)}")
    print(f"[LANG] Уникальных языков: {len(langs)}")
    print(f"[LANG] Языки: {', '.join(sorted(langs))}")
    
    # Топ-5 проектов по оценке
    print("\n[TOP] ТОП-5 проектов по общей оценке:")
    sorted_projects = sorted(projects, key=lambda x: x[3] or 0, reverse=True)[:5]
    for idx, p in enumerate(sorted_projects, 1):
        print(f"  {idx}. {p[1]} — {p[3]}% ({p[4]})")
    
    print("\n[DONE] Готово! Откройте gui_app.py для просмотра результатов.")
    print("=" * 70)


if __name__ == '__main__':
    main()