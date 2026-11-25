from services.parser import ParserFactory


class RepositoryScanner:
    def __init__(self, git_client):
        self.git_client = git_client
        self.parser_factory = ParserFactory()

    def scan_repository(self, repo_path, target_languages):
        """
        Сканирует уже клонированный репозиторий по локальному пути.
        """
        print(f"Scan: {repo_path}")
        
        info = self.git_client.get_repo_info(repo_path)
        print(f"Files: {info.total_files}, Lines: {info.total_lines}")
        
        all_metrics = {}
        for lang in target_languages:
            files = self.git_client.get_files_by_language(repo_path, lang)
            parser = self.parser_factory.get_parser(lang.lower())
            if not parser:
                continue
            metrics_list = []
            for f in files:
                try:
                    with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                        metrics_list.append(parser.parse_file(f, file.read()))
                except Exception:
                    pass
            all_metrics[lang] = metrics_list
            print(f"  {lang}: {len(metrics_list)} files")
        
        return all_metrics
