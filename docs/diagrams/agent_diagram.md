# Диаграмма агентов системы PolySkill

```mermaid
graph TB
    subgraph "Уровень управления"
        Coord[Координатор<br/>run_batch_parallel.py]
        Handoff[HandoffManager<br/>Менеджер передачи задач]
    end

    subgraph "Уровень поиска"
        API[GitHub REST API]
    end

    subgraph "Параллельные рабочие агенты (4 потока)"
        W1[Worker-1]
        W2[Worker-2]
        W3[Worker-3]
        W4[Worker-4]
    end

    subgraph "Агенты-парсеры (Фабрика парсеров)"
        PF[ParserFactory]
        P1[Python Parser]
        P2[JS/TS Parser]
        P3[SQL Parser]
        P4[HTML/CSS Parser]
    end

    subgraph "Агенты-анализаторы паттернов (Фабрика анализаторов)"
        AF[AnalyzerFactory]
        A1[Singleton Analyzer]
        A2[Repository Analyzer]
    end

    subgraph "Уровень агрегации"
        Agg[Assessment Aggregator<br/>Агент-агрегатор]
    end

    subgraph "Уровень хранения"
        Q[(Queue<br/>Очередь результатов)]
        DBW[DB Writer<br/>Агент-потребитель]
        DB[(SQLite Database)]
    end

    subgraph "Уровень представления"
        GUI[GUI Agent<br/>gui_app.py]
    end

    Coord --> API
    Coord --> Handoff
    Handoff --> W1
    Handoff --> W2
    Handoff --> W3
    Handoff --> W4

    W1 --> PF
    W2 --> PF
    W3 --> PF
    W4 --> PF

    PF --> P1
    PF --> P2
    PF --> P3
    PF --> P4

    W1 --> AF
    W2 --> AF
    W3 --> AF
    W4 --> AF

    AF --> A1
    AF --> A2

    W1 --> Agg
    W2 --> Agg
    W3 --> Agg
    W4 --> Agg

    W1 --> Q
    W2 --> Q
    W3 --> Q
    W4 --> Q

    Q --> DBW
    DBW --> DB

    GUI --> DB

    style Coord fill:#f96,stroke:#333,stroke-width:3px
    style Handoff fill:#9cf,stroke:#333,stroke-width:2px
    style W1 fill:#9f9,stroke:#333,stroke-width:2px
    style W2 fill:#9f9,stroke:#333,stroke-width:2px
    style W3 fill:#9f9,stroke:#333,stroke-width:2px
    style W4 fill:#9f9,stroke:#333,stroke-width:2px
    style Q fill:#ff9,stroke:#333,stroke-width:3px
    style DBW fill:#9cf,stroke:#333,stroke-width:2px
    style GUI fill:#f9f,stroke:#333,stroke-width:2px