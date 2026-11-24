\# Классовая структура системы



```mermaid

classDiagram

&#x20;   %% Источники данных

&#x20;   class BaseRepoSource {

&#x20;       <<interface>>

&#x20;       +search\_repositories(query, max\_results)

&#x20;       +get\_source\_name()

&#x20;       +start()

&#x20;       +stop()

&#x20;   }

&#x20;   class GitHubSource

&#x20;   class GitLabSource

&#x20;   class GitVerseSource

&#x20;   class RepoSourceFactory {

&#x20;       +create(source\_name) BaseRepoSource

&#x20;       +get\_available\_sources() List

&#x20;   }



&#x20;   %% Парсеры

&#x20;   class BaseParser {

&#x20;       <<interface>>

&#x20;       +parse\_file(file\_path, content) RawMetrics

&#x20;       +get\_language()

&#x20;   }

&#x20;   class ParserFactory {

&#x20;       +get\_parser(lang) BaseParser

&#x20;   }



&#x20;   %% Модели данных

&#x20;   class RawMetrics {

&#x20;       +file\_path: str

&#x20;       +lines\_of\_code: int

&#x20;       +cyclomatic\_complexity: float

&#x20;       +has\_type\_hints: bool

&#x20;       +has\_error\_handling: bool

&#x20;   }

&#x20;   class LanguageScore {

&#x20;       +language: str

&#x20;       +score: float

&#x20;       +category: TechCategory

&#x20;   }

&#x20;   class StackAssessment {

&#x20;       +overall\_score: float

&#x20;       +level\_name: str

&#x20;       +feedback: str

&#x20;   }



&#x20;   %% Агрегация и БД

&#x20;   class AssessmentAggregator {

&#x20;       +aggregate(scores) StackAssessment

&#x20;   }

&#x20;   class Database {

&#x20;       +save\_assessment(url, name, result, scores)

&#x20;       +get\_all\_projects()

&#x20;   }



&#x20;   BaseRepoSource <|-- GitHubSource

&#x20;   BaseRepoSource <|-- GitLabSource

&#x20;   BaseRepoSource <|-- GitVerseSource

&#x20;   RepoSourceFactory ..> BaseRepoSource

&#x20;   

&#x20;   BaseParser <|-- PythonParser

&#x20;   BaseParser <|-- JavaScriptParser

&#x20;   ParserFactory ..> BaseParser

&#x20;   

&#x20;   AssessmentAggregator --> LanguageScore

&#x20;   AssessmentAggregator --> StackAssessment

&#x20;   Database --> StackAssessment



&#x20;   classDiagram

&#x20;   style BaseRepoSource fill:#f0f8ff,stroke:#0066cc,color:#000000

&#x20;   style GitHubSource fill:#ffffff,stroke:#0066cc,color:#000000

&#x20;   style GitLabSource fill:#ffffff,stroke:#0066cc,color:#000000

&#x20;   style GitVerseSource fill:#ffffff,stroke:#0066cc,color:#000000

&#x20;   style BaseParser fill:#f0fff0,stroke:#008000,color:#000000

&#x20;   style RawMetrics fill:#fff8dc,stroke:#b8860b,color:#000000

&#x20;   style StackAssessment fill:#fff8dc,stroke:#b8860b,color:#000000

