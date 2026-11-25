import time
import random
from playwright.sync_api import sync_playwright
from .base_source import BaseRepoSource


class GitHubSource(BaseRepoSource):
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    def get_source_name(self):
        return "GitHub"

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
            url = f"https://github.com/search?q={encoded_query}&type=repositories&page={page_num}"

            print(f"    [GitHub] Страница {page_num}")

            try:
                self.page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(2)

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
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"    [GitHub] Ошибка: {e}")
                break

        print(f"    [GitHub] Найдено: {len(all_repos)}")
        return all_repos

    def _extract_repos(self):
        repos = []
        repo_blocks = self.page.query_selector_all(
            '[data-testid="results-list"] > div, .search-result'
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

                desc_elem = block.query_selector('p')
                description = desc_elem.inner_text().strip() if desc_elem else ''

                # Усиленные селекторы для языка
                lang_elem = block.query_selector('[itemprop="programmingLanguage"]') or \
                            block.query_selector('[data-testid="language-color"] + span') or \
                            block.query_selector('.repo-language-color + span') or \
                            block.query_selector('span[itemprop="programmingLanguage"]')
                
                language = lang_elem.inner_text().strip() if lang_elem else 'Unknown'

                stars_elem = block.query_selector('a[href$="/stargazers"] span')
                stars_text = stars_elem.inner_text().strip() if stars_elem else '0'
                stars = self._parse_number(stars_text)

                repos.append({
                    'name': repo_name,
                    'url': f"https://github.com/{owner}/{repo_name}.git",
                    'full_name': f"{owner}/{repo_name}",
                    'language': language,
                    'stars': stars,
                    'description': description[:100],
                    'source': 'GitHub',
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
