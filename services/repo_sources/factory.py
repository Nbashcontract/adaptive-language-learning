from .base_source import BaseRepoSource
from .github_source import GitHubSource
from .gitlab_source import GitLabSource
from .gitverse_source import GitVerseSource


class RepoSourceFactory:
    _sources = {
        'github': GitHubSource,
        'gitlab': GitLabSource,
        'gitverse': GitVerseSource,
    }

    @staticmethod
    def create(source_name, **kwargs):
        source_class = RepoSourceFactory._sources.get(source_name.lower())
        if not source_class:
            raise ValueError(f"Неизвестный источник: {source_name}")
        return source_class(**kwargs)

    @staticmethod
    def get_available_sources():
        return list(RepoSourceFactory._sources.keys())