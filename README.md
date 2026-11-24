##### \# PolySkill - Многоагентная система оценки качества кода



\## Описание



PolySkill - многоагентная система, которая автоматически анализирует репозитории с GitHub, GitLab и GitVerse, оценивая качество кода по множеству метрик. Система использует HTML-парсинг через браузер Playwright, параллельную обработку с пулом рабочих агентов и персистентное хранение результатов в SQLite.



\## Архитектура



Система состоит из следующих уровней:



1\. \*\*Уровень представления\*\* - графический интерфейс на CustomTkinter

2\. \*\*Уровень управления\*\* - координатор, управляющий процессом анализа

3\. \*\*Уровень источников\*\* - HTML-парсеры для GitHub, GitLab, GitVerse

4\. \*\*Уровень обработки\*\* - 4 параллельных рабочих агента

5\. \*\*Уровень хранения\*\* - очередь результатов и SQLite база данных



\## Ключевые компоненты



\### Источники данных (services/repo\_sources/)

\- `base\_source.py` - абстрактный базовый класс

\- `factory.py` - фабрика источников

\- `github\_source.py` - парсер GitHub через Playwright

\- `gitlab\_source.py` - парсер GitLab через Playwright

\- `gitverse\_source.py` - парсер GitVerse через Playwright



\### Парсеры кода (services/parser/)

\- Python, JavaScript, SQL, HTML/CSS парсеры

\- ParserFactory для создания нужного парсера по языку



\### Анализаторы паттернов (services/analyzer/)

\- SingletonAnalyzer, RepositoryAnalyzer

\- PatternAnalyzerFactory



\### Агрегация (services/aggregator/)

\- AssessmentAggregator с матрицей весов



\### Хранение (services/database.py)

\- SQLite база данных с защитой от дубликатов



\## Запуск



\### Установка зависимостей

```bash

pip install customtkinter playwright

playwright install chromium

