import shutil
import subprocess
from pathlib import Path
from dataclasses import dataclass


@dataclass
class RepoInfo:
    repo_url: str
    local_path: str
    languages: dict
    total_files: int
    total_lines: int


class GitClient:
    def __init__(self, temp_path):
        self.temp_path = Path(temp_path)
        self.temp_path.mkdir(parents=True, exist_ok=True)

    def clone_repository(self, repo_url):
        name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        path = self.temp_path / name
        if path.exists():
            try:
                shutil.rmtree(path)
            except Exception:
                subprocess.run(
                    ['cmd', '/c', 'rmdir', '/s', '/q', str(path)],
                    capture_output=True
                )
        try:
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, str(path)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode == 0:
                print(f"OK clone: {path}")
                return str(path)
            else:
                print(f"Clone error: {result.stderr[:100]}")
                return None
        except Exception as e:
            print(f"Clone exception: {e}")
            return None

    def get_repo_info(self, repo_path):
        p = Path(repo_path)
        langs, files, lines = {}, 0, 0
        ext_map = {
            '.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript',
            '.ts': 'TypeScript', '.tsx': 'TypeScript', '.sql': 'SQL',
            '.html': 'HTML', '.css': 'CSS', '.scss': 'CSS', '.go': 'Go',
            '.java': 'Java'
        }
        for f in p.rglob('*'):
            if f.is_file() and not f.name.startswith('.'):
                ext = f.suffix.lower()
                if ext in ext_map:
                    langs[ext_map[ext]] = langs.get(ext_map[ext], 0) + 1
                    files += 1
                    try:
                        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                            lines += sum(1 for _ in file)
                    except Exception:
                        pass
        return RepoInfo(str(p), str(p), langs, files, lines)

    def get_files_by_language(self, repo_path, lang):
        p = Path(repo_path)
        exts = {
            'Python': ['.py'], 'JavaScript': ['.js', '.jsx'],
            'TypeScript': ['.ts', '.tsx'], 'SQL': ['.sql'],
            'HTML': ['.html'], 'CSS': ['.css', '.scss'],
            'Go': ['.go'], 'Java': ['.java']
        }
        return [str(f) for ext in exts.get(lang, []) for f in p.rglob('*' + ext) if f.is_file()]

    def cleanup_all(self):
        if self.temp_path.exists():
            try:
                shutil.rmtree(self.temp_path)
            except Exception:
                subprocess.run(
                    ['cmd', '/c', 'rmdir', '/s', '/q', str(self.temp_path)],
                    capture_output=True
                )
            self.temp_path.mkdir(parents=True, exist_ok=True)
            print("OK cleanup")
