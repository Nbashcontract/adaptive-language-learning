\# Этап 3: Запись результатов в БД через DB Writer



```mermaid

sequenceDiagram

&#x20;   participant Queue as Queue (очередь)

&#x20;   participant DBW as DB Writer (потребитель)

&#x20;   participant DB as SQLite Database

&#x20;   participant Main as Главный поток



&#x20;   Note over Queue,DBW: DB Writer работает в отдельном потоке



&#x20;   loop Пока не обработаны все задачи

&#x20;       DBW->>Queue: get(timeout=5)

&#x20;       Queue-->>DBW: {url, name, result, scores}



&#x20;       alt Статус = success

&#x20;           DBW->>DB: get\_all\_projects()

&#x20;           DB-->>DBW: Список проектов



&#x20;           alt Проект уже в БД

&#x20;               DBW->>DBW: Пропустить (skipped++)

&#x20;           else Проект новый

&#x20;               DBW->>DB: save\_assessment(url, name, result, scores)

&#x20;               DB-->>DBW: OK

&#x20;               DBW->>DBW: written++

&#x20;           end

&#x20;       else Статус = no\_data

&#x20;           DBW->>DBW: skipped++

&#x20;       else Статус = error

&#x20;           DBW->>DBW: errors++

&#x20;       end



&#x20;       DBW->>Queue: task\_done()

&#x20;   end



&#x20;   Main->>Queue: queue.join() завершён

&#x20;   Main->>DBW: thread.join(timeout=10)

&#x20;   DBW-->>Main: Статистика (written, skipped, errors)

