# Взаимодействие агентов и фабрик

```mermaid
graph TB
    PF[Фабрика парсеров]
    AF[Фабрика анализаторов]
    P_PY[Python парсер]
    P_JS[JavaScript парсер]
    P_SQL[SQL парсер]
    P_HTML[HTML/CSS парсер]
    A_SING[Анализатор Singleton]
    A_REPO[Анализатор Repository]
    WORKER[Рабочий агент]
    AGG[Агрегатор оценок]
    Q[(Очередь результатов)]

    WORKER --> PF
    PF --> P_PY
    PF --> P_JS
    PF --> P_SQL
    PF --> P_HTML
    WORKER --> AF
    AF --> A_SING
    AF --> A_REPO
    P_PY --> WORKER
    P_JS --> WORKER
    A_SING --> WORKER
    A_REPO --> WORKER
    WORKER --> AGG
    AGG --> Q