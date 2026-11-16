from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Any


class TechCategory(Enum):
    ALGORITHM = "algorithm"        # Python, Java, C++, Go, JS
    DATA = "data"                  # SQL, GraphQL
    UI_FRAMEWORK = "ui_framework"  # React, Vue, Angular
    MARKUP = "markup"              # HTML, CSS
    INFRA = "infra"                # Docker, K8s
    CONFIG = "config"              # YAML, JSON, Bash


class IndustryLevel(Enum):
    TRAINEE = "Trainee"
    JUNIOR_MINUS = "Junior-"
    JUNIOR = "Junior"
    MIDDLE = "Middle"
    SENIOR = "Senior"


# Фиксированная матрица весов 
WEIGHT_MATRIX = {
    TechCategory.ALGORITHM: 1.0,
    TechCategory.DATA: 0.7,
    TechCategory.UI_FRAMEWORK: 0.6,
    TechCategory.MARKUP: 0.3,
    TechCategory.INFRA: 0.5,
    TechCategory.CONFIG: 0.2,
}

# Маппинг языков в категории
LANGUAGE_CATEGORY = {
    "python": TechCategory.ALGORITHM,
    "java": TechCategory.ALGORITHM,
    "csharp": TechCategory.ALGORITHM,
    "cpp": TechCategory.ALGORITHM,
    "go": TechCategory.ALGORITHM,
    "rust": TechCategory.ALGORITHM,
    "javascript": TechCategory.ALGORITHM,
    "typescript": TechCategory.ALGORITHM,
    "sql": TechCategory.DATA,
    "graphql": TechCategory.DATA,
    "react": TechCategory.UI_FRAMEWORK,
    "vue": TechCategory.UI_FRAMEWORK,
    "angular": TechCategory.UI_FRAMEWORK,
    "svelte": TechCategory.UI_FRAMEWORK,
    "html": TechCategory.MARKUP,
    "css": TechCategory.MARKUP,
    "scss": TechCategory.MARKUP,
    "docker": TechCategory.INFRA,
    "kubernetes": TechCategory.INFRA,
    "yaml": TechCategory.CONFIG,
    "json": TechCategory.CONFIG,
    "bash": TechCategory.CONFIG,
}


@dataclass
class RawMetrics:
    file_path: str
    language: str
    lines_of_code: int
    cyclomatic_complexity: float
    has_type_hints: bool
    has_error_handling: bool
    has_tests: bool
    docstring_coverage: float  # 0.0 - 1.0
    design_patterns_found: List[str]
    function_count: int
    class_count: int
    imported_modules: List[str]
    raw_ast_dump: Optional[str] = None


@dataclass
class LanguageScore:
    language: str
    score: float  # 0-100
    category: TechCategory
    pattern_verdicts: List["PatternVerdict"] = field(default_factory=list)


@dataclass
class PatternContext:
    pattern_name: str
    file_size_loc: int
    module_size_loc: int
    has_database: bool
    has_tests: bool
    call_sites_count: int
    is_in_script: bool
    has_state_mutation: bool


@dataclass
class PatternVerdict:
    pattern: str
    appropriateness: float  # 0.0 - 1.0
    rationale: str
    recommendation: str


@dataclass
class StackAssessment:
    """Итоговая оценка стека языков"""
    languages: List[LanguageScore]
    overall_score: float  # 0-100
    level_name: str
    industry_equivalent: str
    feedback: str
    cross_language_analysis: Optional[Dict[str, Any]] = None
    assessed_at: datetime = field(default_factory=datetime.now)