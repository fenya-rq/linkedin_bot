from abc import ABC, abstractmethod

from bs4 import BeautifulSoup


class PageParser(ABC):
    __slots__ = ()

    @staticmethod
    @abstractmethod
    def parse(html: str, parser_type: str = "html.parser") -> str:
        pass


class LinkedInLoginFormParser(PageParser):
    __slots__ = ()

    @staticmethod
    def parse(html: str, parser_type: str = "html.parser") -> str:
        # TODO: add parsing logic, change return

        soup = BeautifulSoup(html, parser_type)
        ...
        return "test result"
