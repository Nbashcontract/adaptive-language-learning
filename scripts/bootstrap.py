from pathlib import Path

BASE = Path(__file__).parent

def wf(p, c):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(c, encoding='utf-8')
    print("OK " + p)

FILES = {}

FILES["models/__init__.py"] = "from .entities import *\nfrom .task_envelope import *\n"

FILES["models/entities.py"] = """from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any

class TechCategory(Enum):
    ALGORITHM = "algorithm"; DATA = "data"; UI_FRAMEWORK = "ui_framework"
    MARKUP = "markup"; INFRA = "infra"; CONFIG = "config"

WEIGHT_MATRIX = {TechCategory.ALGORITHM: 1.0, TechCategory.DATA: 0.7, TechCategory.UI_FRAMEWORK: 0.6, TechCategory.MARKUP: 0.3, TechCategory.INFRA: 0.5, TechCategory.CONFIG: 0.2}
LANGUAGE_CATEGORY = {"python": TechCategory.ALGORITHM, "java": TechCategory.ALGORITHM, "javascript": TechCategory.ALGORITHM, "typescript": TechCategory.ALGORITHM, "sql": TechCategory.DATA, "html": TechCategory.MARKUP, "css": TechCategory.MARKUP}

@dataclass
class RawMetrics:
    file_path: str; language: str; lines_of_code: int; cyclomatic_complexity: float
    has_type_hints: bool; has_error_handling: bool; has_tests: bool; docstring_coverage: float
    design_patterns_found: List[str]; function_count: int; class_count: int; imported_modules: List[str]

@dataclass
class LanguageScore:
    language: str; score: float; category: TechCategory; pattern_verdicts: List[Any] = field(default_factory=list)

@dataclass
class PatternContext:
    pattern_name: str; file_size_loc: int; module_size_loc: int; has_database: bool
    has_tests: bool; call_sites_count: int; is_in_script: bool; has_state_mutation: bool

@dataclass
class PatternVerdict:
    pattern: str; appropriateness: float; rationale: str; recommendation: str

@dataclass
class StackAssessment:
    languages: List[LanguageScore]; overall_score: float; level_name: str
    industry_equivalent: str; feedback: str; cross_language_analysis: Optional[Dict] = None
"""

FILES["models/task_envelope.py"] = """import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, List

@dataclass
class TaskLease:
    agent_id: str; token: str; expires_at: datetime

@dataclass
class TaskEnvelope:
    task_id: str; repo_url: str; target_languages: List[str]; status: str
    producer_agent_id: str; consumer_agent_id: Optional[str] = None
    lease: Optional[TaskLease] = None; temp_storage_path: Optional[str] = None
    checkpoint_data: Optional[Dict] = None; raw_metrics_ref: Optional[str] = None
    attempts: int = 0; created_at: datetime = field(default_factory=datetime.now)

class HandoffManager:
    def __init__(self, temp_path): self.temp_path = temp_path; self.active_tasks = {}
    def create_task(self, repo_url, langs, producer):
        t = TaskEnvelope(task_id=str(uuid.uuid4()), repo_url=repo_url, target_languages=langs, status="CREATED", producer_agent_id=producer)
        self.active_tasks[t.task_id] = t; return t
    def acquire_lease(self, task_id, agent_id):
        t = self.active_tasks[task_id]
        t.lease = TaskLease(agent_id=agent_id, token=str(uuid.uuid4()), expires_at=datetime.now() + timedelta(seconds=60))
        t.status = "LEASED"; t.consumer_agent_id = agent_id; t.attempts += 1; return t.lease
    def share_raw_metrics(self, task_id, agent_id, token, ref):
        t = self.active_tasks.get(task_id)
        if t and t.lease and t.lease.token == token: t.raw_metrics_ref = ref
    def complete_task(self, task_id, agent_id, result):
        t = self.active_tasks.get(task_id); t.status = "DONE"; t.checkpoint_data = {"result": result}; return t
"""

FILES["services/parser/__init__.py"] = "from .base_parser import BaseParser\nfrom .python_parser import PythonParser\nfrom .js_parser import JavaScriptParser\nfrom .sql_parser import SQLParser\nfrom .markup_parser import MarkupParser\nfrom .parser_factory import ParserFactory\n"

FILES["services/parser/base_parser.py"] = """from abc import ABC, abstractmethod
from models.entities import RawMetrics

class BaseParser(ABC):
    @abstractmethod
    def parse_file(self, file_path, content): pass
    @abstractmethod
    def get_language(self): pass
    def _count_lines(self, content):
        return sum(1 for l in content.split(chr(10)) if l.strip() and not l.strip().startswith(('#', '//')))
    def _detect_patterns(self, content, patterns):
        low = content.lower(); return [p for p in patterns if p.lower() in low]
"""

FILES["services/parser/python_parser.py"] = """import ast, re
from models.entities import RawMetrics
from .base_parser import BaseParser

class PythonParser(BaseParser):
    PATTERNS = ["Singleton", "Factory", "Repository", "Strategy", "Observer", "Decorator"]
    def get_language(self): return "python"
    def parse_file(self, file_path, content):
        try: tree = ast.parse(content)
        except SyntaxError: return RawMetrics(file_path, "python", 0, 0.0, False, False, False, 0.0, [], 0, 0, [])
        v = V(); v.visit(tree)
        return RawMetrics(file_path, "python", self._count_lines(content), v.c, bool(re.search(r':\\s*(str|int|bool|float|List|Dict)', content)), 'try' in content and 'except' in content, 'test' in file_path.lower(), 0.5, self._detect_patterns(content, self.PATTERNS), v.fc, v.cc, v.imp)

class V(ast.NodeVisitor):
    def __init__(self): self.c=1.0; self.fc=0; self.cc=0; self.imp=[]
    def visit_FunctionDef(self, n): self.fc+=1; self.c+=1; self.generic_visit(n)
    def visit_ClassDef(self, n): self.cc+=1; self.c+=1; self.generic_visit(n)
    def visit_If(self, n): self.c+=1; self.generic_visit(n)
    def visit_For(self, n): self.c+=1; self.generic_visit(n)
    def visit_While(self, n): self.c+=1; self.generic_visit(n)
    def visit_ExceptHandler(self, n): self.c+=1; self.generic_visit(n)
    def visit_Import(self, n):
        for a in n.names: self.imp.append(a.name)
        self.generic_visit(n)
    def visit_ImportFrom(self, n):
        if n.module: self.imp.append(n.module)
        self.generic_visit(n)
"""

FILES["services/parser/js_parser.py"] = """import re
from models.entities import RawMetrics
from .base_parser import BaseParser

class JavaScriptParser(BaseParser):
    PATTERNS = ["Singleton", "Factory", "Repository", "Component", "Redux"]
    def get_language(self): return "javascript"
    def parse_file(self, file_path, content):
        c = 1.0 + len(re.findall(r'\\bif\\b', content)) + len(re.findall(r'\\bfor\\b', content)) + len(re.findall(r'\\bwhile\\b', content)) + len(re.findall(r'&&', content))
        fc = len(re.findall(r'function\\s+\\w+', content)) + len(re.findall(r'=>', content))
        cc = len(re.findall(r'class\\s+\\w+', content))
        types = '.ts' in file_path or bool(re.search(r':\\s*(string|number|boolean)', content))
        return RawMetrics(file_path, "javascript", self._count_lines(content), c, types, 'try' in content and 'catch' in content, '.test.' in file_path, 0.3, self._detect_patterns(content, self.PATTERNS), fc, cc, re.findall(r"from\\s+['\\"]([^'\\"]+)['\\"]", content))
"""

FILES["services/parser/sql_parser.py"] = """import re
from models.entities import RawMetrics
from .base_parser import BaseParser

class SQLParser(BaseParser):
    def get_language(self): return "sql"
    def parse_file(self, file_path, content):
        up = content.upper(); pats = []
        if 'JOIN' in up: pats.append('JOIN')
        if 'BEGIN' in up and 'COMMIT' in up: pats.append('TRANSACTION')
        c = 1.0 + len(re.findall(r'\\bJOIN\\b', up)) + len(re.findall(r'\\bGROUP\\s+BY\\b', up))
        return RawMetrics(file_path, "sql", self._count_lines(content), c, False, 'BEGIN' in up and 'COMMIT' in up, False, 0.2, pats, 0, len(re.findall(r'CREATE\\s+TABLE', up)), [])
"""

FILES["services/parser/markup_parser.py"] = """import re
from models.entities import RawMetrics
from .base_parser import BaseParser

class MarkupParser(BaseParser):
    def get_language(self): return "html"
    def parse_file(self, file_path, content):
        is_css = file_path.endswith('.css') or file_path.endswith('.scss')
        lang = "css" if is_css else "html"; pats = []
        if is_css:
            if 'display: flex' in content: pats.append('Flexbox')
            if '@media' in content: pats.append('Responsive')
        else:
            if '<header' in content.lower(): pats.append('Semantic')
        c = 1.0 + len(re.findall(r'@media', content)) * 2 if is_css else 1.0 + content.count('<div') * 0.5
        cls = len(re.findall(r'\\.[a-zA-Z]+\\s*\\{', content)) if is_css else len(re.findall(r'class="[^"]*"', content))
        return RawMetrics(file_path, lang, self._count_lines(content), c, False, False, False, 0.1, pats, 0, cls, [])
"""

FILES["services/parser/parser_factory.py"] = """from .python_parser import PythonParser
from .js_parser import JavaScriptParser
from .sql_parser import SQLParser
from .markup_parser import MarkupParser

class ParserFactory:
    def __init__(self): self._parsers = {'python': PythonParser(), 'javascript': JavaScriptParser(), 'sql': SQLParser(), 'html': MarkupParser(), 'css': MarkupParser()}
    def get_parser(self, lang): return self._parsers.get(lang.lower())
    def get_supported_languages(self): return list(self._parsers.keys())
"""

FILES["services/analyzer/__init__.py"] = "from .base_analyzer import PatternAnalyzer\nfrom .singleton_analyzer import SingletonAnalyzer\nfrom .repository_analyzer import RepositoryAnalyzer\nfrom .analyzer_factory import PatternAnalyzerFactory\n"

FILES["services/analyzer/base_analyzer.py"] = """from abc import ABC, abstractmethod
class PatternAnalyzer(ABC):
    @abstractmethod
    def evaluate(self, context): pass
    @abstractmethod
    def get_pattern_name(self): pass
"""

FILES["services/analyzer/singleton_analyzer.py"] = """from models.entities import PatternVerdict
from .base_analyzer import PatternAnalyzer
class SingletonAnalyzer(PatternAnalyzer):
    def get_pattern_name(self): return "Singleton"
    def evaluate(self, ctx):
        if ctx.is_in_script or ctx.file_size_loc < 100: return PatternVerdict("Singleton", 0.0, "Over-engineering", "Замените на функцию")
        if ctx.has_database and ctx.has_tests: return PatternVerdict("Singleton", 1.0, "Уместно для pool", "Добавьте тест")
        return PatternVerdict("Singleton", 0.5, "Нейтрально", "Рассмотрите DI")
"""

FILES["services/analyzer/repository_analyzer.py"] = """from models.entities import PatternVerdict
from .base_analyzer import PatternAnalyzer
class RepositoryAnalyzer(PatternAnalyzer):
    def get_pattern_name(self): return "Repository"
    def evaluate(self, ctx):
        if not ctx.has_database: return PatternVerdict("Repository", 0.0, "Repository без БД", "Простые функции")
        if ctx.has_database and ctx.has_tests: return PatternVerdict("Repository", 1.0, "Профессионально", "Добавьте кэш")
        return PatternVerdict("Repository", 0.5, "Есть БД, нет тестов", "Добавьте unit-тесты")
"""

FILES["services/analyzer/analyzer_factory.py"] = """from .singleton_analyzer import SingletonAnalyzer
from .repository_analyzer import RepositoryAnalyzer
class PatternAnalyzerFactory:
    def __init__(self): self._analyzers = {'Singleton': SingletonAnalyzer(), 'Repository': RepositoryAnalyzer()}
    def get_analyzer(self, name): return self._analyzers.get(name)
    def get_supported_patterns(self): return list(self._analyzers.keys())
"""

FILES["services/aggregator/__init__.py"] = "from .assessment_aggregator import AssessmentAggregator\n"

FILES["services/aggregator/assessment_aggregator.py"] = """from models.entities import StackAssessment, WEIGHT_MATRIX

class AssessmentAggregator:
    LEVELS = [(0, 19, "Новичок", "Trainee"), (20, 39, "Начинающий", "Junior-"), (40, 59, "Базовый", "Junior"), (60, 79, "Уверенный", "Middle"), (80, 100, "Эксперт", "Senior")]
    def aggregate(self, scores):
        if not scores: return StackAssessment([], 0.0, "Новичок", "Trainee", "Нет данных")
        total_w, total_s = 0.0, 0.0
        for s in scores:
            w = WEIGHT_MATRIX.get(s.category, 0.5); pf = 1.0
            if s.pattern_verdicts:
                avg = sum(v.appropriateness for v in s.pattern_verdicts) / len(s.pattern_verdicts)
                pf = 0.8 + avg * 0.2
            total_s += s.score * w * pf; total_w += w
        overall = total_s / total_w if total_w > 0 else 0.0
        level, ind = "Неизвестно", "-"
        for mn, mx, n, i in self.LEVELS:
            if mn <= overall <= mx: level, ind = n, i; break
        fb = f"Общий уровень: {round(overall, 1)}% ({level} / {ind}).\\n"
        if scores: fb += f"Сильная сторона: {max(scores, key=lambda x: x.score).language}.\\n"
        fb += "Вы можете самостоятельно разрабатывать приложения." if overall >= 60 else "Рекомендуется углубить знания."
        return StackAssessment(scores, round(overall, 1), level, ind, fb)
"""

FILES["services/git_client.py"] = """import shutil, subprocess
from pathlib import Path
from dataclasses import dataclass

@dataclass
class RepoInfo:
    repo_url: str; local_path: str; languages: dict; total_files: int; total_lines: int

class GitClient:
    def __init__(self, temp_path):
        self.temp_path = Path(temp_path); self.temp_path.mkdir(parents=True, exist_ok=True)
    def clone_repository(self, repo_url):
        name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        path = self.temp_path / name
        if path.exists():
            try: shutil.rmtree(path)
            except Exception: subprocess.run(['cmd', '/c', 'rmdir', '/s', '/q', str(path)], capture_output=True)
        subprocess.run(['git', 'clone', '--depth', '1', repo_url, str(path)], check=True, capture_output=True, text=True)
        print("OK clone: " + str(path)); return str(path)
    def get_repo_info(self, repo_path):
        p = Path(repo_path); langs, files, lines = {}, 0, 0
        ext_map = {'.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript', '.sql': 'SQL', '.html': 'HTML', '.css': 'CSS', '.scss': 'CSS'}
        for f in p.rglob('*'):
            if f.is_file() and not f.name.startswith('.'):
                ext = f.suffix.lower()
                if ext in ext_map:
                    langs[ext_map[ext]] = langs.get(ext_map[ext], 0) + 1; files += 1
                    try:
                        with open(f, 'r', encoding='utf-8', errors='ignore') as file: lines += sum(1 for _ in file)
                    except Exception: pass
        return RepoInfo(str(p), str(p), langs, files, lines)
    def get_files_by_language(self, repo_path, lang):
        p = Path(repo_path)
        exts = {'Python': ['.py'], 'JavaScript': ['.js', '.jsx'], 'TypeScript': ['.ts', '.tsx'], 'SQL': ['.sql'], 'HTML': ['.html'], 'CSS': ['.css', '.scss']}
        return [str(f) for ext in exts.get(lang, []) for f in p.rglob('*' + ext) if f.is_file()]
    def cleanup_all(self):
        if self.temp_path.exists():
            try: shutil.rmtree(self.temp_path)
            except Exception: subprocess.run(['cmd', '/c', 'rmdir', '/s', '/q', str(self.temp_path)], capture_output=True)
            self.temp_path.mkdir(parents=True, exist_ok=True); print("OK cleanup")
"""

FILES["services/repository_scanner.py"] = """from services.parser import ParserFactory

class RepositoryScanner:
    def __init__(self, git_client): self.git_client = git_client; self.parser_factory = ParserFactory()
    def scan_repository(self, repo_url, target_languages):
        print("Scan: " + repo_url)
        repo_path = self.git_client.clone_repository(repo_url)
        info = self.git_client.get_repo_info(repo_path)
        print("Files: " + str(info.total_files) + ", Lines: " + str(info.total_lines))
        all_metrics = {}
        for lang in target_languages:
            files = self.git_client.get_files_by_language(repo_path, lang)
            parser = self.parser_factory.get_parser(lang.lower())
            if not parser: continue
            metrics_list = []
            for f in files:
                try:
                    with open(f, 'r', encoding='utf-8', errors='ignore') as file: metrics_list.append(parser.parse_file(f, file.read()))
                except Exception: pass
            all_metrics[lang] = metrics_list; print("  " + lang + ": " + str(len(metrics_list)) + " files")
        return all_metrics
"""

FILES["services/database.py"] = """import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_name="poly_skill.db"):
        self.db_path = Path(__file__).parent.parent / db_name
        self.conn = sqlite3.connect(str(self.db_path)); self.create_tables()
    def create_tables(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, name TEXT, overall_score REAL, level_name TEXT, industry_level TEXT, feedback TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS language_scores (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, language TEXT, score REAL, category TEXT, FOREIGN KEY(project_id) REFERENCES projects(id))")
        self.conn.commit()
    def save_assessment(self, url, name, result, scores):
        c = self.conn.cursor()
        c.execute('INSERT OR REPLACE INTO projects (url, name, overall_score, level_name, industry_level, feedback) VALUES (?, ?, ?, ?, ?, ?)', (url, name, result.overall_score, result.level_name, result.industry_equivalent, result.feedback))
        self.conn.commit()
        c.execute('SELECT id FROM projects WHERE url = ?', (url,)); row = c.fetchone()
        if not row: return
        pid = row[0]; c.execute('DELETE FROM language_scores WHERE project_id = ?', (pid,))
        for s in scores:
            cat_val = s.category.value if hasattr(s.category, 'value') else str(s.category)
            c.execute('INSERT INTO language_scores (project_id, language, score, category) VALUES (?, ?, ?, ?)', (pid, s.language, s.score, cat_val))
        self.conn.commit()
    def get_all_projects(self):
        c = self.conn.cursor(); c.execute('SELECT id, name, url, overall_score, level_name FROM projects'); return c.fetchall()
    def get_unique_languages(self):
        c = self.conn.cursor(); c.execute('SELECT DISTINCT language FROM language_scores'); return [r[0] for r in c.fetchall()]
    def get_scores_by_language(self, lang):
        c = self.conn.cursor(); c.execute('SELECT p.name, ls.score FROM language_scores ls JOIN projects p ON ls.project_id = p.id WHERE ls.language = ?', (lang,)); return c.fetchall()
"""

FILES["docs/diagrams/seq_01_task_creation.md"] = "sequenceDiagram\\n    participant User as Пользователь\\n    participant Coord as Координатор\\n    participant Handoff as HandoffManager\\n    User->>Coord: Оценить репозиторий\\n    Coord->>Handoff: create_task\\n    Handoff->>Handoff: TaskEnvelope 1\\n    Coord-->>User: Принято"

FILES["docs/diagrams/seq_02_agent1_work.md"] = "sequenceDiagram\\n    participant Coord as Координатор\\n    participant Agent1 as Агент-1\\n    participant Handoff as HandoffManager\\n    participant Temp as TempStorage\\n    Coord->>Agent1: Задача 1\\n    Agent1->>Handoff: acquire_lease\\n    Handoff-->>Agent1: lease + token\\n    Agent1->>Temp: Клонировать Python\\n    Agent1->>Temp: RawMetrics Python\\n    Agent1->>Handoff: save_checkpoint\\n    Agent1->>Handoff: share_raw_metrics"

FILES["docs/diagrams/seq_03_agent2_work.md"] = "sequenceDiagram\\n    participant Coord as Координатор\\n    participant Agent2 as Агент-2\\n    participant Handoff as HandoffManager\\n    participant Temp as TempStorage\\n    Coord->>Agent2: Задача 2\\n    Agent2->>Handoff: acquire_lease\\n    Agent2->>Temp: Клонировать JS\\n    Agent2->>Handoff: get_raw_metrics_ref\\n    Temp-->>Agent2: Python API\\n    Agent2->>Agent2: cross_language_consistency\\n    Agent2->>Handoff: complete_task"

FILES["docs/diagrams/seq_04_aggregation.md"] = "sequenceDiagram\\n    participant Coord as Координатор\\n    participant Agg as Агрегатор\\n    participant Temp as TempStorage\\n    participant User as Пользователь\\n    Coord->>Agg: Собрать результаты\\n    Agg->>Temp: RawMetrics Agent1\\n    Agg->>Temp: RawMetrics Agent2\\n    Agg->>Agg: Уместность паттернов\\n    Agg->>Agg: Матрица весов\\n    Agg-->>Coord: StackAssessment\\n    Coord-->>User: Результат"

FILES["docs/diagrams/class_diagram.md"] = "classDiagram\\n    class RawMetrics { +file_path +language }\\n    class LanguageScore { +language +score }\\n    class StackAssessment { +overall_score +feedback }\\n    class TaskEnvelope { +task_id +status }\\n    class HandoffManager { +create_task() +acquire_lease() }\\n    class BaseParser { <<abstract>> +parse_file() }\\n    class PythonParser\\n    class JavaScriptParser\\n    class ParserFactory { +get_parser() }\\n    class AssessmentAggregator { +aggregate() }\\n    BaseParser <|-- PythonParser\\n    BaseParser <|-- JavaScriptParser\\n    ParserFactory --> BaseParser\\n    HandoffManager --> TaskEnvelope\\n    AssessmentAggregator --> LanguageScore"

FILES["docs/diagrams/component_diagram.md"] = "graph LR\\n    UI[Пользователь] --> Coord[Координатор]\\n    Coord --> Handoff[HandoffManager]\\n    Handoff --> Agent1[Агент-1]\\n    Handoff --> Agent2[Агент-2]\\n    Agent1 --> PF[ParserFactory]\\n    Agent2 --> PF\\n    Agent1 --> Temp[(Temp Storage)]\\n    Agent2 --> Temp\\n    Temp --> Analyzer[Анализатор]\\n    Analyzer --> Agg[Агрегатор]\\n    Agg --> Coord\\n    Coord --> UI"

FILES["requirements.txt"] = "customtkinter\n"

FILES["run_demo.py"] = """from services.git_client import GitClient
from services.repository_scanner import RepositoryScanner
from services.aggregator import AssessmentAggregator
from services.database import Database
from models.entities import LanguageScore, TechCategory, LANGUAGE_CATEGORY

def demo():
    print("=" * 60 + "\\nDEMO: Оценка FastAPI\\n" + "=" * 60)
    git_client = GitClient('./temp_repos')
    scanner = RepositoryScanner(git_client)
    aggregator = AssessmentAggregator()
    db = Database()
    try:
        metrics = scanner.scan_repository('https://github.com/tiangolo/fastapi', ['Python', 'HTML'])
        scores = []
        for lang, m_list in metrics.items():
            if not m_list: continue
            cat = LANGUAGE_CATEGORY.get(lang.lower(), TechCategory.ALGORITHM)
            avg_loc = sum(m.lines_of_code for m in m_list) / len(m_list)
            type_ratio = sum(1 for m in m_list if m.has_type_hints) / len(m_list)
            err_ratio = sum(1 for m in m_list if m.has_error_handling) / len(m_list)
            score = min(100, max(0, min(100, avg_loc / 5) * 0.3 + type_ratio * 100 * 0.4 + err_ratio * 100 * 0.3))
            print("  " + lang + ": " + str(round(score, 1)) + "%")
            scores.append(LanguageScore(language=lang, score=score, category=cat))
        result = aggregator.aggregate(scores)
        db.save_assessment('https://github.com/tiangolo/fastapi', 'FastAPI', result, scores)
        print("=" * 60 + "\\nОБЩИЙ: " + str(result.overall_score) + "% (" + result.level_name + ")\\n" + result.feedback + "\\n" + "=" * 60)
    finally:
        git_client.cleanup_all()

if __name__ == '__main__': demo()
"""

FILES["gui_app.py"] = """import customtkinter as ctk
import sqlite3
from pathlib import Path

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
DB_PATH = Path(__file__).parent / "poly_skill.db"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PolySkill - Оценка кода")
        self.geometry("1000x600")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="PolySkill", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        ctk.CTkButton(self.sidebar, text="Обновить", command=self.load_data).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkLabel(self.sidebar, text="Проекты:", anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=20, pady=(10, 0))
        self.proj_frame = ctk.CTkScrollableFrame(self.sidebar, width=210)
        self.proj_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="Языки:", anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=20, pady=(10, 0))
        self.lang_frame = ctk.CTkScrollableFrame(self.sidebar, width=210)
        self.lang_frame.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
        self.main = ctk.CTkFrame(self, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.header = ctk.CTkLabel(self.main, text="Выберите проект или язык", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=20)
        self.details = ctk.CTkFrame(self.main)
        self.details.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.load_data()

    def load_data(self):
        for w in self.proj_frame.winfo_children(): w.destroy()
        for w in self.lang_frame.winfo_children(): w.destroy()
        if not DB_PATH.exists():
            ctk.CTkLabel(self.proj_frame, text="Нет БД. Запустите run_demo.py", text_color="red").pack(pady=20)
            return
        conn = sqlite3.connect(str(DB_PATH)); c = conn.cursor()
        c.execute('SELECT id, name, level_name FROM projects')
        for p in c.fetchall():
            ctk.CTkButton(self.proj_frame, text=p[1] + " (" + p[2] + ")", height=50, command=lambda pid=p[0]: self.show_proj(pid)).pack(fill="x", pady=5)
        c.execute('SELECT DISTINCT language FROM language_scores')
        for r in c.fetchall():
            ctk.CTkButton(self.lang_frame, text=r[0], fg_color="gray", command=lambda l=r[0]: self.show_lang(l)).pack(fill="x", pady=5)
        conn.close()

    def show_proj(self, pid):
        for w in self.details.winfo_children(): w.destroy()
        conn = sqlite3.connect(str(DB_PATH)); c = conn.cursor()
        c.execute('SELECT name, overall_score, level_name, industry_level, feedback FROM projects WHERE id=?', (pid,))
        p = c.fetchone()
        c.execute('SELECT language, score FROM language_scores WHERE project_id=?', (pid,))
        scores = c.fetchall(); conn.close()
        if not p: return
        self.header.configure(text="Проект: " + p[0])
        ctk.CTkLabel(self.details, text=str(p[1]) + "%", font=ctk.CTkFont(size=40, weight="bold"), text_color="#2ecc71").pack(pady=10)
        ctk.CTkLabel(self.details, text=p[2] + " (" + p[3] + ")", font=ctk.CTkFont(size=18)).pack(pady=5)
        ctk.CTkLabel(self.details, text="Отзыв:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=20, pady=(20, 5))
        tb = ctk.CTkTextbox(self.details, height=80); tb.insert("0.0", p[4]); tb.configure(state="disabled"); tb.pack(fill="x", pady=5, padx=20)
        ctk.CTkLabel(self.details, text="Языки:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=20, pady=(20, 5))
        for lang, score in scores:
            row = ctk.CTkFrame(self.details); row.pack(fill="x", pady=5, padx=20)
            ctk.CTkLabel(row, text=lang, width=120, anchor="w").pack(side="left", padx=10)
            pb = ctk.CTkProgressBar(row, width=300); pb.pack(side="left", padx=10, pady=10); pb.set(score / 100.0)
            ctk.CTkLabel(row, text=str(round(score, 1)) + "%", width=60).pack(side="left", padx=10)

    def show_lang(self, lang):
        for w in self.details.winfo_children(): w.destroy()
        conn = sqlite3.connect(str(DB_PATH)); c = conn.cursor()
        c.execute('SELECT p.name, ls.score FROM language_scores ls JOIN projects p ON ls.project_id = p.id WHERE ls.language = ?', (lang,))
        items = c.fetchall(); conn.close()
        self.header.configure(text="Язык: " + lang)
        ctk.CTkLabel(self.details, text="Проекты с " + lang + ":", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=20, pady=10)
        for name, score in items:
            row = ctk.CTkFrame(self.details); row.pack(fill="x", pady=5, padx=20)
            ctk.CTkLabel(row, text=name, width=200, anchor="w").pack(side="left", padx=10)
            pb = ctk.CTkProgressBar(row, width=300); pb.pack(side="left", padx=10, pady=10); pb.set(score / 100.0)
            ctk.CTkLabel(row, text=str(round(score, 1)) + "%", width=60).pack(side="left", padx=10)

if __name__ == "__main__": App().mainloop()
"""

print("=" * 60)
print("Генерация всех файлов проекта...")
print("=" * 60)
for path, content in FILES.items():
    wf(path, content)
print("=" * 60)
print("ВСЕ ФАЙЛЫ СОЗДАНЫ!")
print("=" * 60)