from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any

class TechCategory(Enum):
    ALGORITHM = "algorithm"; DATA = "data"; UI_FRAMEWORK = "ui_framework"
    MARKUP = "markup"; INFRA = "infra"; CONFIG = "config"

WEIGHT_MATRIX = {TechCategory.ALGORITHM: 1.0, TechCategory.DATA: 0.7, TechCategory.UI_FRAMEWORK: 0.6, TechCategory.MARKUP: 0.3, TechCategory.INFRA: 0.5, TechCategory.CONFIG: 0.2}
LANGUAGE_CATEGORY = {"python": TechCategory.ALGORITHM, "java": TechCategory.ALGORITHM, "javascript": TechCategory.ALGORITHM, "typescript": TechCategory.ALGORITHM, "sql": TechCategory.DATA, "html": TechCategory.MARKUP, "css": TechCategory.MARKUP}

@dataclass
class RawMetrics:
    file_path: str; language: str; lines_of_code: int; cyclomatic_complexity: float
    has_type_hints: bool; has_error_handling: bool; has_tests: bool; docstring_coverage: float
    design_patterns_found: List[str]; function_count: int; class_count: int; imported_modules: List[str]

@dataclass
class LanguageScore:
    language: str; score: float; category: TechCategory; pattern_verdicts: List[Any] = field(default_factory=list)

@dataclass
class PatternContext:
    pattern_name: str; file_size_loc: int; module_size_loc: int; has_database: bool
    has_tests: bool; call_sites_count: int; is_in_script: bool; has_state_mutation: bool

@dataclass
class PatternVerdict:
    pattern: str; appropriateness: float; rationale: str; recommendation: str

@dataclass
class StackAssessment:
    languages: List[LanguageScore]; overall_score: float; level_name: str
    industry_equivalent: str; feedback: str; cross_language_analysis: Optional[Dict] = None
