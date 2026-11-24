from abc import ABC, abstractmethod


class BaseRepoSource(ABC):
    @abstractmethod
    def search_repositories(self, query, max_results=50):
        pass

    @abstractmethod
    def get_source_name(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass