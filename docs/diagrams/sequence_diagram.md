\# Диаграмма последовательности: процесс оценки репозитория



```mermaid

sequenceDiagram

&#x20;   participant User as Пользователь

&#x20;   participant Coordinator as Координатор

&#x20;   participant Handoff as HandoffManager

&#x20;   participant Agent1 as Агент-1 (Python+SQL)

&#x20;   participant Agent2 as Агент-2 (JS+HTML)

&#x20;   participant TempStorage as Временное хранилище

&#x20;   participant Aggregator as Агрегатор



&#x20;   User->>Coordinator: Оценить репозиторий X

&#x20;   Coordinator->>Handoff: create\_task(repo\_url, \[Python, SQL, JS, HTML])

&#x20;   Handoff->>Handoff: Создать TaskEnvelope #1

&#x20;   Handoff->>Handoff: Создать TaskEnvelope #2



&#x20;   Coordinator->>Agent1: Передать задачу #1 (Python+SQL)

&#x20;   Agent1->>Handoff: acquire\_lease(task\_id, agent1\_id)

&#x20;   Handoff->>Agent1: Выдать lease с fencing token



&#x20;   Agent1->>TempStorage: Клонировать Python-репозиторий

&#x20;   Agent1->>Agent1: Парсинг Python-файлов (AST)

&#x20;   Agent1->>Agent1: Извлечение RawMetrics для Python

&#x20;   Agent1->>TempStorage: Сохранить RawMetrics Python



&#x20;   Agent1->>TempStorage: Клонировать SQL-схемы

&#x20;   Agent1->>Agent1: Парсинг SQL-файлов

&#x20;   Agent1->>Agent1: Извлечение RawMetrics для SQL

&#x20;   Agent1->>TempStorage: Сохранить RawMetrics SQL



&#x20;   Agent1->>Handoff: save\_checkpoint(task\_id, agent1\_id, token, metrics)

&#x20;   Handoff->>TempStorage: Записать checkpoint



&#x20;   Agent1->>Handoff: share\_raw\_metrics(task\_id, agent1\_id, token, ref)

&#x20;   Handoff->>TempStorage: Сохранить ссылку на метрики



&#x20;   Coordinator->>Agent2: Передать задачу #2 (JS+HTML)

&#x20;   Agent2->>Handoff: acquire\_lease(task\_id, agent2\_id)

&#x20;   Handoff->>Agent2: Выдать lease



&#x20;   Agent2->>TempStorage: Клонировать JS-фронтенд

&#x20;   Agent2->>Agent2: Парсинг JS-файлов

&#x20;   Agent2->>Agent2: Извлечение RawMetrics для JS



&#x20;   Agent2->>Handoff: get\_raw\_metrics\_ref(task\_id\_1)

&#x20;   Handoff->>TempStorage: Получить ссылку на Python-метрики

&#x20;   TempStorage-->>Agent2: Ссылка на Python RawMetrics



&#x20;   Agent2->>TempStorage: Прочитать Python API-контракты

&#x20;   Agent2->>Agent2: Сравнить JS-вызовы с Python API

&#x20;   Agent2->>Agent2: Вычислить cross\_language\_consistency



&#x20;   Agent2->>Handoff: complete\_task(task\_id, agent2\_id, token, result)

&#x20;   Handoff->>TempStorage: Записать финальный результат



&#x20;   Coordinator->>Aggregator: Собрать результаты от всех агентов

&#x20;   Aggregator->>TempStorage: Прочитать RawMetrics от Agent1

&#x20;   Aggregator->>TempStorage: Прочитать RawMetrics от Agent2



&#x20;   Aggregator->>Aggregator: Оценить уместность паттернов

&#x20;   Aggregator->>Aggregator: Применить матрицу весов

&#x20;   Aggregator->>Aggregator: Рассчитать общий балл

&#x20;   Aggregator->>Aggregator: Сгенерировать отзыв



&#x20;   Aggregator-->>Coordinator: StackAssessment (JSON)

&#x20;   Coordinator-->>User: Результат оценки

