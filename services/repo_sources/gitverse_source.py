import time
from playwright.sync_api import sync_playwright
from .base_source import BaseRepoSource


class GitVerseSource(BaseRepoSource):
    def __init__(self, headless=True, base_url="https://gitverse.ru"):
        self.headless = headless
        self.base_url = base_url
        self.playwright = None
        self.browser = None
        self.page = None

    def get_source_name(self):
        return "GitVerse"

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def search_repositories(self, query, max_results=50):
        if not self.page:
            self.start()

        all_repos = []
        seen_urls = set()
        page_num = 1

        while len(all_repos) < max_results:
            encoded_query = query.replace(' ', '+')
            url = f"{self.base_url}/search?q={encoded_query}&page={page_num}"

            print(f"    [GitVerse] Страница {page_num}")

            try:
                self.page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(2)

                # ПРОВЕРКА НА ЗАЩИТУ / ЛИМИТЫ
                page_text = self.page.inner_text('body').lower()
                if 'лимит' in page_text or 'входа' in page_text or 'доступно после' in page_text:
                    print(f"    [GitVerse] Обнаружена защита: превышен лимит запросов или требуется авторизация. Пропуск источника.")
                    break

                repos = self._extract_repos()
                if not repos:
                    break

                for repo in repos:
                    if len(all_repos) >= max_results:
                        break
                    if repo['url'] not in seen_urls:
                        seen_urls.add(repo['url'])
                        all_repos.append(repo)

                page_num += 1
                time.sleep(2)

            except Exception as e:
                print(f"    [GitVerse] Ошибка: {e}")
                break

        print(f"    [GitVerse] Итог: найдено {len(all_repos)} проектов")
        return all_repos

    def _extract_repos(self):
        repos = []
        repo_blocks = self.page.query_selector_all(
            '.repo-item, .repository, .search-result, [class*="repo"], [class*="project"]'
        )

        for block in repo_blocks:
            try:
                title_elem = block.query_selector('a[href*="/"][href*="/"]')
                if not title_elem:
                    continue

                href = title_elem.get_attribute('href')
                if not href or href.count('/') < 2:
                    continue

                parts = href.strip('/').split('/')
                if len(parts) < 2:
                    continue

                owner, repo_name = parts[0], parts[1]

                desc_elem = block.query_selector('.description, p')
                description = desc_elem.inner_text().strip() if desc_elem else ''

                lang_elem = block.query_selector('.language')
                language = lang_elem.inner_text().strip() if lang_elem else 'Unknown'

                stars_elem = block.query_selector('.stars, .star-count')
                stars_text = stars_elem.inner_text().strip() if stars_elem else '0'
                stars = self._parse_number(stars_text)

                repos.append({
                    'name': repo_name,
                    'url': f"{self.base_url}/{owner}/{repo_name}.git",
                    'full_name': f"{owner}/{repo_name}",
                    'language': language,
                    'stars': stars,
                    'description': description[:100],
                    'source': 'GitVerse',
                })

            except Exception:
                continue

        return repos

    def _parse_number(self, text):
        text = text.strip().replace(',', '')
        if 'k' in text.lower():
            return int(float(text.lower().replace('k', '')) * 1000)
        if 'm' in text.lower():
            return int(float(text.lower().replace('m', '')) * 1000000)
        try:
            return int(text)
        except Exception:
            return 0
