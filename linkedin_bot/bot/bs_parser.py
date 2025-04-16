from abc import ABC, abstractmethod
from typing import Any

from bs4 import BeautifulSoup


class BaseParser(ABC):
    __slots__ = ()

    @abstractmethod
    def parse(self) -> Any:
        pass


class LinkedInPostsParser(BaseParser):
    __slots__ = ('html', 'parser_type', 'soup')

    KEY_WORDS = {'python', 'backend', 'api', 'roadmap'}

    def __init__(self, html: str, parser_type: str = 'html.parser') -> None:
        self.html = html
        self.parser_type = parser_type
        self.soup: BeautifulSoup = BeautifulSoup(self.html, self.parser_type)

    def parse(self) -> set[str]:
        data_ids = set()

        # Get feeds container and then all posts from it
        feeds = self.soup.find('div', attrs={'data-finite-scroll-hotkey-context': 'FEED'})
        posts = feeds.find_all('div', recursive=False)
        # Iterate through all founded posts, check if key in its text and add data_id
        for post in posts:
            post_container = post.find_next('div')
            spans = post_container.find_all('span', dir='ltr')
            text = spans[1].get_text().lower() if len(spans) > 1 else ''
            if any(key in text for key in self.KEY_WORDS):
                data_id = post_container.attrs.get('data-id')
                data_ids.add(data_id)

        return data_ids
