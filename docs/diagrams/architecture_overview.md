\# Общая архитектура системы



```mermaid

graph TB

&#x20;   subgraph UI\["Уровень представления"]

&#x20;       GUI\[Графический интерфейс<br/>gui\_app.py]

&#x20;   end



&#x20;   subgraph CONTROL\["Уровень управления"]

&#x20;       COORD\[Координатор<br/>run\_batch\_parallel.py]

&#x20;   end



&#x20;   subgraph SOURCES\["Источники данных HTML-парсинг"]

&#x20;       GH\[GitHub]

&#x20;       GL\[GitLab]

&#x20;       GV\[GitVerse]

&#x20;   end



&#x20;   subgraph WORKERS\["Уровень параллельной обработки"]

&#x20;       W1\[Рабочий агент 1]

&#x20;       W2\[Рабочий агент 2]

&#x20;       W3\[Рабочий агент 3]

&#x20;       W4\[Рабочий агент 4]

&#x20;   end



&#x20;   subgraph STORAGE\["Уровень хранения"]

&#x20;       Q\[Очередь результатов]

&#x20;       DBW\[Агент записи в БД]

&#x20;       DB\[(База данных SQLite)]

&#x20;   end



&#x20;   GUI --> DB

&#x20;   COORD --> GH

&#x20;   COORD --> GL

&#x20;   COORD --> GV

&#x20;   COORD --> W1

&#x20;   COORD --> W2

&#x20;   COORD --> W3

&#x20;   COORD --> W4

&#x20;   W1 --> Q

&#x20;   W2 --> Q

&#x20;   W3 --> Q

&#x20;   W4 --> Q

&#x20;   Q --> DBW

&#x20;   DBW --> DB



&#x20;   style UI fill:#f0f8ff,stroke:#0066cc,stroke-width:2px,color:#000000

&#x20;   style CONTROL fill:#fff0f5,stroke:#cc0066,stroke-width:2px,color:#000000

&#x20;   style SOURCES fill:#f5f5dc,stroke:#8b8b00,stroke-width:2px,color:#000000

&#x20;   style WORKERS fill:#f0fff0,stroke:#008000,stroke-width:2px,color:#000000

&#x20;   style STORAGE fill:#fff8dc,stroke:#b8860b,stroke-width:2px,color:#000000

