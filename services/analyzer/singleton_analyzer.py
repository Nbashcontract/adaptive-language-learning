from models.entities import PatternVerdict
from .base_analyzer import PatternAnalyzer
class SingletonAnalyzer(PatternAnalyzer):
    def get_pattern_name(self): return "Singleton"
    def evaluate(self, ctx):
        if ctx.is_in_script or ctx.file_size_loc < 100: return PatternVerdict("Singleton", 0.0, "Over-engineering", "Замените на функцию")
        if ctx.has_database and ctx.has_tests: return PatternVerdict("Singleton", 1.0, "Уместно для pool", "Добавьте тест")
        return PatternVerdict("Singleton", 0.5, "Нейтрально", "Рассмотрите DI")
