from typing import Protocol

from bs4 import BeautifulSoup


class PageParser(Protocol):

    def parse_signin_page(self, html: str, parser_type: str = 'html.parser') -> str:
        ...


class LinkedInLoginFormParser:
    __slots__ = ()

    @staticmethod
    def parse_signin_page(html: str, parser_type: str = 'html.parser') -> str:
        # TODO: add parsing logic, change return

        soup = BeautifulSoup(html, parser_type)
        ...
        return 'test result'
