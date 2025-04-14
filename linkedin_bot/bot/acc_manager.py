import random
from abc import ABC, abstractmethod

from playwright.async_api import Browser, BrowserContext, Page

from services import SimpleClient
from .bs_parser import PageParser


class BaseManager(ABC):
    __slots__ = ("client", "parser")

    def __init__(self, client: SimpleClient, parser: PageParser):
        self.client = client
        self.parser = parser

    @abstractmethod
    async def create_context(self, browser: Browser) -> BrowserContext:
        pass

    @abstractmethod
    async def create_page(self, context: BrowserContext) -> Page:
        pass

    @abstractmethod
    async def get_page_content(self, page: Page) -> str:
        pass

    @abstractmethod
    async def process_page(self, page_content: str):
        pass


class LoginManager(BaseManager):
    __slots__ = ("client", "parser")

    def __init__(self, client: SimpleClient, parser: PageParser):
        super().__init__(client, parser)

    async def create_context(self, browser: Browser) -> BrowserContext:
        user_agent = random.choice(self.client.USER_AGENTS)
        return await browser.new_context(
            java_script_enabled=True, user_agent=user_agent
        )

    async def create_page(self, context: BrowserContext):
        return await context.new_page()

    async def get_page_content(self, page: Page) -> str:
        await page.goto(self.client.url)
        await page.wait_for_load_state("load")
        return await page.content()

    async def process_page(self, page_content: str):
        return self.parser.parse(page_content)

    async def start_manage(self, browser: Browser):
        context = await self.create_context(browser)
        page = await self.create_page(context)
        content = await self.get_page_content(page)
        result = await self.process_page(content)
