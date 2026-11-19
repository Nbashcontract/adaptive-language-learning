from models.entities import PatternVerdict
from .base_analyzer import PatternAnalyzer
class RepositoryAnalyzer(PatternAnalyzer):
    def get_pattern_name(self): return "Repository"
    def evaluate(self, ctx):
        if not ctx.has_database: return PatternVerdict("Repository", 0.0, "Repository без БД", "Простые функции")
        if ctx.has_database and ctx.has_tests: return PatternVerdict("Repository", 1.0, "Профессионально", "Добавьте кэш")
        return PatternVerdict("Repository", 0.5, "Есть БД, нет тестов", "Добавьте unit-тесты")
