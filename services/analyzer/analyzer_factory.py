from .singleton_analyzer import SingletonAnalyzer
from .repository_analyzer import RepositoryAnalyzer
class PatternAnalyzerFactory:
    def __init__(self): self._analyzers = {'Singleton': SingletonAnalyzer(), 'Repository': RepositoryAnalyzer()}
    def get_analyzer(self, name): return self._analyzers.get(name)
    def get_supported_patterns(self): return list(self._analyzers.keys())
