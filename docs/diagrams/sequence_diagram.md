# Диаграмма последовательности: процесс оценки репозитория

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant Coordinator as Координатор
    participant Handoff as HandoffManager
    participant Agent1 as Агент-1 (Python+SQL)
    participant Agent2 as Агент-2 (JS+HTML)
    participant TempStorage as Временное хранилище
    participant Aggregator as Агрегатор

    User->>Coordinator: Оценить репозиторий X
    Coordinator->>Handoff: create_task(repo_url, [Python, SQL, JS, HTML])
    Handoff->>Handoff: Создать TaskEnvelope #1
    Handoff->>Handoff: Создать TaskEnvelope #2

    Coordinator->>Agent1: Передать задачу #1 (Python+SQL)
    Agent1->>Handoff: acquire_lease(task_id, agent1_id)
    Handoff->>Agent1: Выдать lease с fencing token

    Agent1->>TempStorage: Клонировать Python-репозиторий
    Agent1->>Agent1: Парсинг Python-файлов (AST)
    Agent1->>Agent1: Извлечение RawMetrics для Python
    Agent1->>TempStorage: Сохранить RawMetrics Python

    Agent1->>TempStorage: Клонировать SQL-схемы
    Agent1->>Agent1: Парсинг SQL-файлов
    Agent1->>Agent1: Извлечение RawMetrics для SQL
    Agent1->>TempStorage: Сохранить RawMetrics SQL

    Agent1->>Handoff: save_checkpoint(task_id, agent1_id, token, metrics)
    Handoff->>TempStorage: Записать checkpoint

    Agent1->>Handoff: share_raw_metrics(task_id, agent1_id, token, ref)
    Handoff->>TempStorage: Сохранить ссылку на метрики

    Coordinator->>Agent2: Передать задачу #2 (JS+HTML)
    Agent2->>Handoff: acquire_lease(task_id, agent2_id)
    Handoff->>Agent2: Выдать lease

    Agent2->>TempStorage: Клонировать JS-фронтенд
    Agent2->>Agent2: Парсинг JS-файлов
    Agent2->>Agent2: Извлечение RawMetrics для JS

    Agent2->>Handoff: get_raw_metrics_ref(task_id_1)
    Handoff->>TempStorage: Получить ссылку на Python-метрики
    TempStorage-->>Agent2: Ссылка на Python RawMetrics

    Agent2->>TempStorage: Прочитать Python API-контракты
    Agent2->>Agent2: Сравнить JS-вызовы с Python API
    Agent2->>Agent2: Вычислить cross_language_consistency

    Agent2->>Handoff: complete_task(task_id, agent2_id, token, result)
    Handoff->>TempStorage: Записать финальный результат

    Coordinator->>Aggregator: Собрать результаты от всех агентов
    Aggregator->>TempStorage: Прочитать RawMetrics от Agent1
    Aggregator->>TempStorage: Прочитать RawMetrics от Agent2

    Aggregator->>Aggregator: Оценить уместность паттернов
    Aggregator->>Aggregator: Применить матрицу весов
    Aggregator->>Aggregator: Рассчитать общий балл
    Aggregator->>Aggregator: Сгенерировать отзыв

    Aggregator-->>Coordinator: StackAssessment (JSON)
    Coordinator-->>User: Результат оценки
  ````