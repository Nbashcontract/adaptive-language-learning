# Диаграмма классов системы оценки кода

```mermaid
classDiagram
    %% === МОДЕЛИ ДАННЫХ ===
    class TechCategory {
        <<enumeration>>
        ALGORITHM
        DATA
        UI_FRAMEWORK
        MARKUP
        INFRA
        CONFIG
    }

    class IndustryLevel {
        <<enumeration>>
        TRAINEE
        JUNIOR_MINUS
        JUNIOR
        MIDDLE
        SENIOR
    }

    class RawMetrics {
        +String file_path
        +String language
        +int lines_of_code
        +float cyclomatic_complexity
        +boolean has_type_hints
        +boolean has_error_handling
        +boolean has_tests
        +float docstring_coverage
        +List~String~ design_patterns_found
        +int function_count
        +int class_count
        +List~String~ imported_modules
        +String raw_ast_dump
    }

    class LanguageScore {
        +String language
        +float score
        +TechCategory category
        +List~PatternVerdict~ pattern_verdicts
    }

    class PatternContext {
        +String pattern_name
        +int file_size_loc
        +int module_size_loc
        +boolean has_database
        +boolean has_tests
        +int call_sites_count
        +boolean is_in_script
        +boolean has_state_mutation
    }

    class PatternVerdict {
        +String pattern
        +float appropriateness
        +String rationale
        +String recommendation
    }

    class StackAssessment {
        +List~LanguageScore~ languages
        +float overall_score
        +String level_name
        +String industry_equivalent
        +String feedback
        +Dict cross_language_analysis
        +datetime assessed_at
    }

    %% === ПРОТОКОЛ ПЕРЕДАЧИ ЗАДАЧ ===
    class TaskLease {
        +String agent_id
        +String token
        +datetime expires_at
    }

    class TaskEnvelope {
        +String task_id
        +String repo_url
        +List~String~ target_languages
        +String status
        +String producer_agent_id
        +String consumer_agent_id
        +TaskLease lease
        +String temp_storage_path
        +Dict checkpoint_data
        +String raw_metrics_ref
        +int attempts
        +datetime created_at
        +datetime completed_at
        +create(repo_url, languages, producer_id) TaskEnvelope
    }

    class HandoffManager {
        -String temp_storage_path
        -Dict~String, TaskEnvelope~ active_tasks
        +create_task(repo_url, languages, producer_id) TaskEnvelope
        +acquire_lease(task_id, agent_id, ttl) TaskLease
        +save_checkpoint(task_id, agent_id, token, data) String
        +share_raw_metrics(task_id, agent_id, token, metrics_ref) void
        +complete_task(task_id, agent_id, token, result) TaskEnvelope
        +get_task(task_id) TaskEnvelope
        +get_raw_metrics_ref(task_id) String
    }

    %% === ПАРСЕРЫ ===
    class BaseParser {
        <<abstract>>
        +parse_file(file_path, content) RawMetrics
        +get_language() String
        #_count_lines(content) int
        #_detect_patterns(content, patterns) List~String~
    }

    class PythonParser {
        -List~String~ PYTHON_PATTERNS
        +parse_file(file_path, content) RawMetrics
        -_has_type_hints(content) boolean
        -_is_test_file(file_path) boolean
        -_docstring_coverage(tree) float
        -_create_basic_metrics(file_path, content) RawMetrics
    }

    class JavaScriptParser {
        -List~String~ JS_PATTERNS
        +parse_file(file_path, content) RawMetrics
        -_is_typescript(content) boolean
        -_calculate_complexity(content) float
        -_count_functions(content) int
        -_extract_imports(content) List~String~
    }

    class SQLParser {
        -List~String~ SQL_PATTERNS
        +parse_file(file_path, content) RawMetrics
        -_detect_sql_patterns(content) List~String~
        -_calculate_complexity(content) float
        -_count_procedures(content) int
    }

    class MarkupParser {
        -List~String~ MARKUP_PATTERNS
        +parse_file(file_path, content) RawMetrics
        -_detect_markup_patterns(content, is_css) List~String~
        -_calculate_complexity(content, is_css) float
    }

    class ParserFactory {
        -Dict~String, BaseParser~ _parsers
        -Dict~String, String~ EXTENSION_MAP
        +get_parser(language) BaseParser
        +get_parser_by_extension(file_path) BaseParser
        +get_supported_languages() List~String~
        +can_parse(file_path) boolean
    }

    %% === АНАЛИЗАТОР (будет создан) ===
    class PatternAnalyzer {
        <<interface>>
        +evaluate(pattern, context) PatternVerdict
    }

    class SingletonAnalyzer {
        +evaluate(pattern, context) PatternVerdict
    }

    class RepositoryAnalyzer {
        +evaluate(pattern, context) PatternVerdict
    }

    class PatternAnalyzerFactory {
        +get_analyzer(pattern_name) PatternAnalyzer
    }

    %% === АГРЕГАТОР (будет создан) ===
    class AssessmentAggregator {
        -Dict~TechCategory, float~ weight_matrix
        +aggregate(scores, role) StackAssessment
        -_calculate_weighted_score(scores) float
        -_get_level(score) Tuple~String, String~
        -_generate_feedback(scores, overall, role) String
        -_check_cross_language_consistency(scores) Dict
    }

    %% === СВЯЗИ ===
    RawMetrics --> TechCategory : language maps to
    LanguageScore --> TechCategory : category
    LanguageScore --> PatternVerdict : contains
    PatternVerdict --> PatternContext : evaluated from
    StackAssessment --> LanguageScore : contains
    TaskEnvelope --> TaskLease : has
    HandoffManager --> TaskEnvelope : manages
    BaseParser <|-- PythonParser
    BaseParser <|-- JavaScriptParser
    BaseParser <|-- SQLParser
    BaseParser <|-- MarkupParser
    BaseParser --> RawMetrics : produces
    ParserFactory --> BaseParser : creates
    PatternAnalyzerFactory --> PatternAnalyzer : creates
    SingletonAnalyzer ..|> PatternAnalyzer
    RepositoryAnalyzer ..|> PatternAnalyzer
    AssessmentAggregator --> LanguageScore : aggregates
    AssessmentAggregator --> StackAssessment : produces
    AssessmentAggregator --> TechCategory : uses weights