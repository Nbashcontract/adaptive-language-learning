import re
from models.entities import RawMetrics
from .base_parser import BaseParser

class JavaScriptParser(BaseParser):
    PATTERNS = ["Singleton", "Factory", "Repository", "Component", "Redux"]
    def get_language(self): return "javascript"
    def parse_file(self, file_path, content):
        c = 1.0 + len(re.findall(r'\bif\b', content)) + len(re.findall(r'\bfor\b', content)) + len(re.findall(r'\bwhile\b', content)) + len(re.findall(r'&&', content))
        fc = len(re.findall(r'function\s+\w+', content)) + len(re.findall(r'=>', content))
        cc = len(re.findall(r'class\s+\w+', content))
        types = '.ts' in file_path or bool(re.search(r':\s*(string|number|boolean)', content))
        return RawMetrics(file_path, "javascript", self._count_lines(content), c, types, 'try' in content and 'catch' in content, '.test.' in file_path, 0.3, self._detect_patterns(content, self.PATTERNS), fc, cc, re.findall(r"from\s+['\"]([^'\"]+)['\"]", content))
