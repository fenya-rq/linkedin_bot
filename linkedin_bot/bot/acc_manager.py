import random
from abc import ABC, abstractmethod
from typing import Type
from urllib.parse import urlparse

from config import logger_prd
from playwright.async_api import Browser, BrowserContext, Page
from services import SimpleClient

from .bs_parser import LinkedInPostsParser


class BaseManager(ABC):
    __slots__ = ('client',)

    def __init__(self, client: SimpleClient):
        self.client = client

    @abstractmethod
    async def _create_context(self, browser: Browser, **kwargs: dict[str, str]) -> BrowserContext:
        pass

    @staticmethod
    @abstractmethod
    async def _create_page(context: BrowserContext) -> Page:
        pass


class LoginManager(BaseManager):
    __slots__ = ('client',)

    async def _create_context(self, browser: Browser, **kwargs: dict[str, str]) -> BrowserContext:
        user_agent = random.choice(self.client.USER_AGENTS)
        return await browser.new_context(java_script_enabled=True, user_agent=user_agent)

    @staticmethod
    async def _create_page(context: BrowserContext):
        return await context.new_page()

    async def _log_in(self, page: Page) -> Page:
        await page.goto(self.client.url)
        await page.wait_for_selector('form.login__form')
        await page.locator('input#username').fill(self.client.name)
        await page.locator('input#password').fill(self.client.password)

        login_button = page.locator('button[type="submit"]')
        await login_button.click()

        if not (url := page.url) or not urlparse(url).path.startswith('/feed'):
            raise Exception('Log in failed!')
        return page

    async def log_in(self, browser: Browser) -> Page:
        context = await self._create_context(browser)
        page = await self._create_page(context)
        try:
            feed_page = await self._log_in(page)
            logger_prd.log(55, 'Logged successfully!')
            return feed_page
        except Exception as e:
            logger_prd.error(e)


class PostManager(LoginManager):
    def __init__(self, client: SimpleClient, parser_cls: Type[LinkedInPostsParser]) -> None:
        super().__init__(client)
        self.parser_cls = parser_cls

    async def get_posts_id(self, browser: Browser) -> set[str]:
        feed_page = await self.log_in(browser)
        # Ensure the page content was loaded for correct getting
        await feed_page.wait_for_load_state('load')
        content = await feed_page.content()
        parser_obj = self.parser_cls(content)
        return parser_obj.parse()
