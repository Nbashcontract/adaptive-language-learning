import re
from models.entities import RawMetrics
from .base_parser import BaseParser

class SQLParser(BaseParser):
    def get_language(self): return "sql"
    def parse_file(self, file_path, content):
        up = content.upper(); pats = []
        if 'JOIN' in up: pats.append('JOIN')
        if 'BEGIN' in up and 'COMMIT' in up: pats.append('TRANSACTION')
        c = 1.0 + len(re.findall(r'\bJOIN\b', up)) + len(re.findall(r'\bGROUP\s+BY\b', up))
        return RawMetrics(file_path, "sql", self._count_lines(content), c, False, 'BEGIN' in up and 'COMMIT' in up, False, 0.2, pats, 0, len(re.findall(r'CREATE\s+TABLE', up)), [])
