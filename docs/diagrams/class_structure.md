# Классовая структура системы

```mermaid
classDiagram
    class BaseRepoSource {
        <<interface>>
        +search_repositories(query, max_results)
        +get_source_name()
        +start()
        +stop()
    }
    class GitHubSource
    class GitLabSource
    class GitVerseSource
    class RepoSourceFactory {
        +create(source_name) BaseRepoSource
        +get_available_sources() List
    }
    class BaseParser {
        <<interface>>
        +parse_file(file_path, content) RawMetrics
        +get_language()
    }
    class ParserFactory {
        +get_parser(lang) BaseParser
    }
    class RawMetrics {
        +file_path: str
        +lines_of_code: int
        +cyclomatic_complexity: float
        +has_type_hints: bool
        +has_error_handling: bool
    }
    class LanguageScore {
        +language: str
        +score: float
        +category: TechCategory
    }
    class StackAssessment {
        +overall_score: float
        +level_name: str
        +feedback: str
    }
    class AssessmentAggregator {
        +aggregate(scores) StackAssessment
    }
    class Database {
        +save_assessment(url, name, result, scores)
        +get_all_projects()
    }

    BaseRepoSource <|-- GitHubSource
    BaseRepoSource <|-- GitLabSource
    BaseRepoSource <|-- GitVerseSource
    RepoSourceFactory ..> BaseRepoSource
    BaseParser <|-- PythonParser
    BaseParser <|-- JavaScriptParser
    ParserFactory ..> BaseParser
    AssessmentAggregator --> LanguageScore
    AssessmentAggregator --> StackAssessment
    Database --> StackAssessment