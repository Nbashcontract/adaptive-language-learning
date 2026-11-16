# Диаграмма компонентов системы

```mermaid
graph TB
    subgraph "Пользовательский интерфейс"
        UI[Web UI / CLI]
    end

    subgraph "Координатор"
        Coordinator[Learning Agent<br/>Единственный владелец сессии]
    end

    subgraph "Протокол передачи задач"
        Handoff[HandoffManager<br/>Lease + Checkpoint + Exchange]
        TaskBus[Task Bus<br/>Очередь задач]
    end

    subgraph "Агенты-аналитики"
        Agent1[Агент-1<br/>Python + SQL]
        Agent2[Агент-2<br/>JS + HTML]
    end

    subgraph "Парсеры"
        ParserFactory[ParserFactory]
        PythonParser[PythonParser<br/>AST]
        JSParser[JavaScriptParser<br/>Regex]
        SQLParser[SQLParser]
        MarkupParser[MarkupParser]
    end

    subgraph "Анализатор"
        PatternAnalyzer[PatternAnalyzer<br/>Уместность паттернов]
        SingletonAnalyzer[SingletonAnalyzer]
        RepositoryAnalyzer[RepositoryAnalyzer]
    end

    subgraph "Агрегатор"
        Aggregator[AssessmentAggregator<br/>Взвешивание + Отзыв]
    end

    subgraph "Временное хранилище"
        TempStorage[(Temp Storage<br/>RawMetrics + Checkpoints)]
    end

    subgraph "Модели данных"
        Entities[RawMetrics<br/>LanguageScore<br/>StackAssessment]
        TaskEnvelope[TaskEnvelope<br/>TaskLease]
    end

    UI --> Coordinator
    Coordinator --> Handoff
    Handoff --> TaskBus
    TaskBus --> Agent1
    TaskBus --> Agent2
    Agent1 --> ParserFactory
    Agent2 --> ParserFactory
    ParserFactory --> PythonParser
    ParserFactory --> JSParser
    ParserFactory --> SQLParser
    ParserFactory --> MarkupParser
    PythonParser --> Entities
    JSParser --> Entities
    SQLParser --> Entities
    MarkupParser --> Entities
    Agent1 --> TempStorage
    Agent2 --> TempStorage
    Agent1 --> Handoff
    Agent2 --> Handoff
    Handoff --> Entities
    TempStorage --> PatternAnalyzer
    PatternAnalyzer --> SingletonAnalyzer
    PatternAnalyzer --> RepositoryAnalyzer
    PatternAnalyzer --> Aggregator
    Aggregator --> Entities
    Aggregator --> Coordinator
    Coordinator --> UI