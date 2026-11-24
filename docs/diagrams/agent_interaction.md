\# Взаимодействие агентов и фабрик



```mermaid

graph TB

&#x20;   subgraph FACTORIES\["Фабрики компонентов"]

&#x20;       PF\[Фабрика парсеров]

&#x20;       AF\[Фабрика анализаторов]

&#x20;   end



&#x20;   subgraph PARSERS\["Специализированные парсеры"]

&#x20;       P\_PY\[Python парсер]

&#x20;       P\_JS\[JavaScript парсер]

&#x20;       P\_SQL\[SQL парсер]

&#x20;       P\_HTML\[HTML/CSS парсер]

&#x20;   end



&#x20;   subgraph ANALYZERS\["Анализаторы паттернов"]

&#x20;       A\_SING\[Анализатор Singleton]

&#x20;       A\_REPO\[Анализатор Repository]

&#x20;   end



&#x20;   subgraph CORE\["Ядро обработки"]

&#x20;       WORKER\[Рабочий агент]

&#x20;       AGG\[Агрегатор оценок]

&#x20;   end



&#x20;   WORKER --> PF

&#x20;   PF --> P\_PY

&#x20;   PF --> P\_JS

&#x20;   PF --> P\_SQL

&#x20;   PF --> P\_HTML

&#x20;   

&#x20;   WORKER --> AF

&#x20;   AF --> A\_SING

&#x20;   AF --> A\_REPO

&#x20;   

&#x20;   P\_PY --> WORKER

&#x20;   P\_JS --> WORKER

&#x20;   A\_SING --> WORKER

&#x20;   A\_REPO --> WORKER

&#x20;   

&#x20;   WORKER --> AGG

&#x20;   AGG --> Q\[(Очередь результатов)]



&#x20;   style FACTORIES fill:#e6f3ff,stroke:#0066cc,stroke-width:2px,color:#000000

&#x20;   style PARSERS fill:#e6ffe6,stroke:#008000,stroke-width:2px,color:#000000

&#x20;   style ANALYZERS fill:#ffe6e6,stroke:#cc0000,stroke-width:2px,color:#000000

&#x20;   style CORE fill:#f9f0ff,stroke:#800080,stroke-width:2px,color:#000000

