# Диаграмма агентов системы PolySkill

```mermaid
graph TB
    subgraph Management["Уровень управления"]
        Coord[Координатор<br/>run_batch_parallel.py]
        Handoff[HandoffManager<br/>Менеджер передачи задач]
    end

    subgraph Search["Уровень поиска"]
        API[GitHub REST API]
    end

    subgraph Workers["Параллельные рабочие агенты (4 потока)"]
        W1[Worker-1]
        W2[Worker-2]
        W3[Worker-3]
        W4[Worker-4]
    end

    subgraph Parsers["Агенты-парсеры (Фабрика парсеров)"]
        PF[ParserFactory]
        P1[Python Parser]
        P2[JS/TS Parser]
        P3[SQL Parser]
        P4[HTML/CSS Parser]
    end

    subgraph Analyzers["Агенты-анализаторы паттернов"]
        AF[AnalyzerFactory]
        A1[Singleton Analyzer]
        A2[Repository Analyzer]
    end

    subgraph Aggregation["Уровень агрегации"]
        Agg[Assessment Aggregator]
    end

    subgraph Storage["Уровень хранения"]
        Q[(Queue<br/>Очередь результатов)]
        DBW[DB Writer<br/>Агент-потребитель]
        DB[(SQLite Database)]
    end

    subgraph Presentation["Уровень представления"]
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

    style Management fill:#FFE0B2,stroke:#E65100,stroke-width:2px
    style Search fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style Workers fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style Parsers fill:#FFF3E0,stroke:#EF6C00,stroke-width:2px
    style Analyzers fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px
    style Aggregation fill:#FFF9C4,stroke:#F57F17,stroke-width:2px
    style Storage fill:#E0F7FA,stroke:#00695C,stroke-width:2px
    style Presentation fill:#FCE4EC,stroke:#AD1457,stroke-width:2px