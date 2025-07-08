from abc import ABC, abstractmethod
from typing import Any

from bs4 import BeautifulSoup


class BaseParser(ABC):
    """Abstract base parser class."""

    __slots__ = ()

    @abstractmethod
    def parse(self) -> Any:
        """
        Parse content and return results.

        :returns: Parsed output after processing content
        """
        pass


class LinkedInPostsParser(BaseParser):
    """Parser for extracting LinkedIn post IDs based on keywords."""

    __slots__ = ('html', 'parser_type', 'soup')

    KEY_WORDS = {'python', 'backend', 'api', 'roadmap'}

    def __init__(self, html: str, parser_type: str = 'html.parser') -> None:
        """
        Initialize parser with HTML content.

        :param html: Raw HTML to be parsed
        :param parser_type: BeautifulSoup parser to use
        """
        self.html = html
        self.parser_type = parser_type
        self.soup: BeautifulSoup = BeautifulSoup(self.html, self.parser_type)

    def get_feeds(self):
        return self.soup.find('div', attrs={'data-finite-scroll-hotkey-context': 'FEED'})

    def get_posts(self):
        return self.get_feeds().find_all('div', recursive=False)  # type: ignore

    def extract_posts_text(self):
        for post in self.get_posts():
            post_container = post.find_next('div')
            spans = post_container.find_all('span', dir='ltr')
            text = spans[1].get_text().lower() if len(spans) > 1 else ''
            yield post_container, text

    def parse(self) -> set[str]:
        """
        Extract post data IDs containing specified keywords.

        Scans the feed container for posts, inspects text spans,
        filters by KEY_WORDS, and collects data IDs.

        :returns: Unique data IDs of matching posts
        """
        data_ids = set()

        for post_container, text in self.extract_posts_text():
            if any(key in text for key in self.KEY_WORDS):
                data_id = post_container.attrs.get('data-id')
                data_ids.add(data_id)

        return data_ids


class LinkedInVacancyAnalyzeParser(LinkedInPostsParser):

    KEY_WORDS = {
        'hiring', 'ищу', 'ищем', 'vacancy', 'vacancies', 'вакансия', 'вакансии', 'python',
        'backend', 'питон', 'бэкенд', 'найдись', 'в поиске', 'в поисках'
    }

    def parse(self) -> set[str]:
        data_content = set()

        for _, text in self.extract_posts_text():
            if any(key in text for key in self.KEY_WORDS):
                data_content.add(text)

        return data_content
