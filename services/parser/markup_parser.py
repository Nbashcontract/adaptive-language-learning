import re
from models.entities import RawMetrics
from .base_parser import BaseParser

class MarkupParser(BaseParser):
    def get_language(self): return "html"
    def parse_file(self, file_path, content):
        is_css = file_path.endswith('.css') or file_path.endswith('.scss')
        lang = "css" if is_css else "html"; pats = []
        if is_css:
            if 'display: flex' in content: pats.append('Flexbox')
            if '@media' in content: pats.append('Responsive')
        else:
            if '<header' in content.lower(): pats.append('Semantic')
        c = 1.0 + len(re.findall(r'@media', content)) * 2 if is_css else 1.0 + content.count('<div') * 0.5
        cls = len(re.findall(r'\.[a-zA-Z]+\s*\{', content)) if is_css else len(re.findall(r'class="[^"]*"', content))
        return RawMetrics(file_path, lang, self._count_lines(content), c, False, False, False, 0.1, pats, 0, cls, [])
