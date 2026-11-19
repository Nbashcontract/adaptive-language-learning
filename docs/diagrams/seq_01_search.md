\# Этап 1: Поиск репозиториев через GitHub API



```mermaid

sequenceDiagram

&#x20;   participant User as Пользователь

&#x20;   participant Main as run\_batch\_parallel.py

&#x20;   participant API as GitHub API



&#x20;   User->>Main: Запустить анализ

&#x20;   Main->>Main: Загрузить SEARCH\_QUERIES



&#x20;   loop Для каждого критерия

&#x20;       Main->>API: GET /search/repositories

&#x20;       API-->>Main: JSON со списком репозиториев

&#x20;       Main->>Main: Добавить уникальные URL

&#x20;       Main->>Main: Пауза 2 сек (лимит API)

&#x20;   end



&#x20;   Main->>Main: Дедупликация по URL

&#x20;   Main-->>User: Список уникальных репозиториев

