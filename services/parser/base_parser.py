from abc import ABC, abstractmethod
from models.entities import RawMetrics

class BaseParser(ABC):
    @abstractmethod
    def parse_file(self, file_path, content): pass
    @abstractmethod
    def get_language(self): pass
    def _count_lines(self, content):
        return sum(1 for l in content.split(chr(10)) if l.strip() and not l.strip().startswith(('#', '//')))
    def _detect_patterns(self, content, patterns):
        low = content.lower(); return [p for p in patterns if p.lower() in low]
