from abc import ABC, abstractmethod
class PatternAnalyzer(ABC):
    @abstractmethod
    def evaluate(self, context): pass
    @abstractmethod
    def get_pattern_name(self): pass
