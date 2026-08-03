from abc import ABC, abstractmethod


class BaseScraper(ABC):

    @abstractmethod
    def search(self, keyword: str):
        """Return a list of job dictionaries."""
        pass