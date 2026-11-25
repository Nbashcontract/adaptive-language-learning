from .python_parser import PythonParser
from .js_parser import JavaScriptParser
from .sql_parser import SQLParser
from .markup_parser import MarkupParser


class ParserFactory:
    def __init__(self):
        self._parsers = {
            'python': PythonParser(),
            'javascript': JavaScriptParser(),
            'typescript': JavaScriptParser(),  # Используем JS-парсер для TS (синтаксис очень близок)
            'java': JavaScriptParser(),        # Используем JS-парсер для Java (C-подобный синтаксис, try/catch работает)
            'go': JavaScriptParser(),          # Используем JS-парсер для Go (C-подобный синтаксис)
            'sql': SQLParser(),
            'html': MarkupParser(),
            'css': MarkupParser()
        }

    def get_parser(self, lang):
        return self._parsers.get(lang.lower())

    def get_supported_languages(self):
        return list(self._parsers.keys())
