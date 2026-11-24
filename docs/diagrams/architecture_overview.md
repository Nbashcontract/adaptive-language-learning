# Общая архитектура системы

```mermaid
graph TB
    GUI[Графический интерфейс<br/>gui_app.py]
    COORD[Координатор<br/>run_batch_parallel.py]
    GH[GitHub]
    GL[GitLab]
    GV[GitVerse]
    W1[Рабочий агент 1]
    W2[Рабочий агент 2]
    W3[Рабочий агент 3]
    W4[Рабочий агент 4]
    Q[Очередь результатов]
    DBW[Агент записи в БД]
    DB[(База данных SQLite)]

    GUI --> DB
    COORD --> GH
    COORD --> GL
    COORD --> GV
    COORD --> W1
    COORD --> W2
    COORD --> W3
    COORD --> W4
    W1 --> Q
    W2 --> Q
    W3 --> Q
    W4 --> Q
    Q --> DBW
    DBW --> DB