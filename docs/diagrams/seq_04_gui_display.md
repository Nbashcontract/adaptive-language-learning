\# Этап 4: Отображение результатов в GUI



```mermaid

sequenceDiagram

&#x20;   participant User as Пользователь

&#x20;   participant GUI as gui\_app.py (CustomTkinter)

&#x20;   participant DB as SQLite Database



&#x20;   User->>GUI: Открыть приложение

&#x20;   GUI->>DB: SELECT id, name, level\_name FROM projects

&#x20;   DB-->>GUI: Список проектов

&#x20;   GUI->>DB: SELECT DISTINCT language FROM language\_scores

&#x20;   DB-->>GUI: Список языков



&#x20;   GUI->>User: Отобразить сайдбар (проекты + языки)



&#x20;   alt Пользователь кликает на проект

&#x20;       User->>GUI: Клик на проект X

&#x20;       GUI->>DB: SELECT ... FROM projects WHERE id=X

&#x20;       GUI->>DB: SELECT language, score FROM language\_scores WHERE project\_id=X

&#x20;       DB-->>GUI: Данные проекта + оценки языков

&#x20;       GUI->>User: Показать балл, уровень, отзыв, прогресс-бары

&#x20;   else Пользователь кликает на язык

&#x20;       User->>GUI: Клик на язык Y

&#x20;       GUI->>DB: SELECT p.name, ls.score FROM language\_scores JOIN projects WHERE language=Y

&#x20;       DB-->>GUI: Список проектов с оценкой по языку Y

&#x20;       GUI->>User: Показать список проектов с прогресс-барами

&#x20;   end

