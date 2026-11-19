\# Этап 2: Параллельный анализ агентами-работниками



```mermaid

sequenceDiagram

&#x20;   participant Main as Главный поток

&#x20;   participant Pool as ThreadPoolExecutor

&#x20;   participant W1 as Worker-1

&#x20;   participant W2 as Worker-2

&#x20;   participant W3 as Worker-3

&#x20;   participant W4 as Worker-4

&#x20;   participant Git as GitClient

&#x20;   participant Parser as RepositoryScanner

&#x20;   participant Queue as Queue (очередь)



&#x20;   Main->>Pool: Запустить NUM\_WORKERS потоков



&#x20;   loop Для каждого репозитория

&#x20;       Pool->>W1: worker\_agent(repo\_1)

&#x20;       Pool->>W2: worker\_agent(repo\_2)

&#x20;       Pool->>W3: worker\_agent(repo\_3)

&#x20;       Pool->>W4: worker\_agent(repo\_4)



&#x20;       W1->>Git: clone(temp\_repos\_parallel/worker\_1)

&#x20;       W2->>Git: clone(temp\_repos\_parallel/worker\_2)

&#x20;       W3->>Git: clone(temp\_repos\_parallel/worker\_3)

&#x20;       W4->>Git: clone(temp\_repos\_parallel/worker\_4)



&#x20;       W1->>Parser: scan\_repository(repo\_1)

&#x20;       W2->>Parser: scan\_repository(repo\_2)

&#x20;       W3->>Parser: scan\_repository(repo\_3)

&#x20;       W4->>Parser: scan\_repository(repo\_4)



&#x20;       W1->>Parser: Извлечь RawMetrics (Python)

&#x20;       W2->>Parser: Извлечь RawMetrics (JS)

&#x20;       W3->>Parser: Извлечь RawMetrics (Java)

&#x20;       W4->>Parser: Извлечь RawMetrics (TS)



&#x20;       W1->>W1: Рассчитать LanguageScore

&#x20;       W2->>W2: Рассчитать LanguageScore

&#x20;       W3->>W3: Рассчитать LanguageScore

&#x20;       W4->>W4: Рассчитать LanguageScore



&#x20;       W1->>Queue: put({url, name, result, scores})

&#x20;       W2->>Queue: put({url, name, result, scores})

&#x20;       W3->>Queue: put({url, name, result, scores})

&#x20;       W4->>Queue: put({url, name, result, scores})



&#x20;       W1->>Git: cleanup\_all(worker\_1)

&#x20;       W2->>Git: cleanup\_all(worker\_2)

&#x20;       W3->>Git: cleanup\_all(worker\_3)

&#x20;       W4->>Git: cleanup\_all(worker\_4)

&#x20;   end



&#x20;   Main->>Main: as\_completed(futures)

&#x20;   Main->>Queue: queue.join() (ждать обработки)

