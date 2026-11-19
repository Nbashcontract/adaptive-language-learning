import ast, re
from models.entities import RawMetrics
from .base_parser import BaseParser

class PythonParser(BaseParser):
    PATTERNS = ["Singleton", "Factory", "Repository", "Strategy", "Observer", "Decorator"]
    def get_language(self): return "python"
    def parse_file(self, file_path, content):
        try: tree = ast.parse(content)
        except SyntaxError: return RawMetrics(file_path, "python", 0, 0.0, False, False, False, 0.0, [], 0, 0, [])
        v = V(); v.visit(tree)
        return RawMetrics(file_path, "python", self._count_lines(content), v.c, bool(re.search(r':\s*(str|int|bool|float|List|Dict)', content)), 'try' in content and 'except' in content, 'test' in file_path.lower(), 0.5, self._detect_patterns(content, self.PATTERNS), v.fc, v.cc, v.imp)

class V(ast.NodeVisitor):
    def __init__(self): self.c=1.0; self.fc=0; self.cc=0; self.imp=[]
    def visit_FunctionDef(self, n): self.fc+=1; self.c+=1; self.generic_visit(n)
    def visit_ClassDef(self, n): self.cc+=1; self.c+=1; self.generic_visit(n)
    def visit_If(self, n): self.c+=1; self.generic_visit(n)
    def visit_For(self, n): self.c+=1; self.generic_visit(n)
    def visit_While(self, n): self.c+=1; self.generic_visit(n)
    def visit_ExceptHandler(self, n): self.c+=1; self.generic_visit(n)
    def visit_Import(self, n):
        for a in n.names: self.imp.append(a.name)
        self.generic_visit(n)
    def visit_ImportFrom(self, n):
        if n.module: self.imp.append(n.module)
        self.generic_visit(n)
