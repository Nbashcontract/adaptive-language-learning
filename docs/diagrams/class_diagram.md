# Диаграмма классов (обновлённая)

```mermaid
classDiagram
    class RawMetrics {
        +file_path: str
        +language: str
        +lines_of_code: int
        +cyclomatic_complexity: float
        +has_type_hints: bool
        +has_error_handling: bool
        +has_tests: bool
        +docstring_coverage: float
        +design_patterns_found: List[str]
        +function_count: int
        +class_count: int
        +imported_modules: List[str]
    }

    class LanguageScore {
        +language: str
        +score: float
        +category: TechCategory
        +pattern_verdicts: List[PatternVerdict]
    }

    class StackAssessment {
        +languages: List[LanguageScore]
        +overall_score: float
        +level_name: str
        +industry_equivalent: str
        +feedback: str
    }

    class TaskEnvelope {
        +task_id: str
        +repo_url: str
        +target_languages: List[str]
        +status: str
        +producer_agent_id: str
        +lease: TaskLease
    }

    class HandoffManager {
        +active_tasks: Dict[str, TaskEnvelope]
        +create_task(repo_url, langs, producer) TaskEnvelope
        +acquire_lease(task_id, agent_id) TaskLease
        +share_raw_metrics(task_id, agent_id, token, ref)
        +complete_task(task_id, agent_id, result) TaskEnvelope
    }

    class BaseParser {
        <<abstract>>
        +parse_file(file_path, content) RawMetrics
        +get_language() str
        +_count_lines(content) int
        +_detect_patterns(content, patterns) List[str]
    }

    class PythonParser
    class JavaScriptParser
    class SQLParser
    class MarkupParser

    class ParserFactory {
        -_parsers: Dict[str, BaseParser]
        +get_parser(lang) BaseParser
        +get_supported_languages() List[str]
    }

    class PatternAnalyzer {
        <<interface>>
        +evaluate(context) PatternVerdict
        +get_pattern_name() str
    }

    class SingletonAnalyzer
    class RepositoryAnalyzer

    class PatternAnalyzerFactory {
        -_analyzers: Dict[str, PatternAnalyzer]
        +get_analyzer(name) PatternAnalyzer
    }

    class AssessmentAggregator {
        +LEVELS: List[Tuple]
        +aggregate(scores) StackAssessment
        -_calculate_weighted_score(scores) float
        -_pattern_factor(verdicts) float
        -_get_level(score) Tuple[str, str]
    }

    class GitClient {
        +temp_path: Path
        +clone_repository(repo_url) str
        +get_repo_info(repo_path) RepoInfo
        +get_files_by_language(repo_path, lang) List[str]
        +cleanup_all()
    }

    class RepositoryScanner {
        +git_client: GitClient
        +parser_factory: ParserFactory
        +scan_repository(repo_url, langs) Dict[str, List[RawMetrics]]
    }

    class Database {
        +db_path: Path
        +conn: sqlite3.Connection
        +create_tables()
        +save_assessment(url, name, result, scores)
        +get_all_projects() List[Tuple]
        +get_unique_languages() List[str]
        +get_scores_by_language(lang) List[Tuple]
    }

    class Queue {
        <<threading>>
        +put(item)
        +get(timeout) item
        +task_done()
        +join()
    }

    BaseParser <|-- PythonParser
    BaseParser <|-- JavaScriptParser
    BaseParser <|-- SQLParser
    BaseParser <|-- MarkupParser
    ParserFactory --> BaseParser

    PatternAnalyzer <|.. SingletonAnalyzer
    PatternAnalyzer <|.. RepositoryAnalyzer
    PatternAnalyzerFactory --> PatternAnalyzer

    HandoffManager --> TaskEnvelope
    RepositoryScanner --> GitClient
    RepositoryScanner --> ParserFactory
    AssessmentAggregator --> LanguageScore
    AssessmentAggregator --> StackAssessment
    Database --> RawMetrics