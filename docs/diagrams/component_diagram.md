# Диаграмма компонентов (обновлённая)

```mermaid
graph TB
    User[Пользователь] --> GUI[gui_app.py CustomTkinter]
    GUI --> DB[(SQLite Database)]

    Main[run_batch_parallel.py] --> API[GitHub REST API]
    API --> Main

    Main --> Pool[ThreadPoolExecutor]
    
    subgraph Параллельные агенты-работники
        Pool --> W1[Worker-1 Python]
        Pool --> W2[Worker-2 JavaScript]
        Pool --> W3[Worker-3 Java]
        Pool --> W4[Worker-4 TypeScript]
    end

    W1 --> Git1[temp_repos_parallel/worker_1]
    W2 --> Git2[temp_repos_parallel/worker_2]
    W3 --> Git3[temp_repos_parallel/worker_3]
    W4 --> Git4[temp_repos_parallel/worker_4]

    W1 --> PF1[ParserFactory]
    W2 --> PF2[ParserFactory]
    W3 --> PF3[ParserFactory]
    W4 --> PF4[ParserFactory]

    PF1 --> Parsers[Парсеры Python/JS/SQL/HTML]
    PF2 --> Parsers
    PF3 --> Parsers
    PF4 --> Parsers

    W1 --> Q[Queue очередь результатов]
    W2 --> Q
    W3 --> Q
    W4 --> Q

    Q --> DBW[DB Writer поток-потребитель]
    DBW --> DB

    DB --> GUI

    style Q fill:#f9f,stroke:#333,stroke-width:2px
    style DBW fill:#bbf,stroke:#333,stroke-width:2px