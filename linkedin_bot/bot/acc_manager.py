import random
import re
from abc import ABC, abstractmethod

from config import logger_prd
from playwright.async_api import Browser, BrowserContext, Page
from services import SimpleClient


class BaseManager(ABC):
    __slots__ = ('client',)

    def __init__(self, client: SimpleClient):
        self.client = client

    @abstractmethod
    async def create_context(self, browser: Browser) -> BrowserContext:
        pass

    @staticmethod
    @abstractmethod
    async def create_page(context: BrowserContext) -> Page:
        pass


class LoginManager(BaseManager):
    __slots__ = ('client',)

    def __init__(self, client: SimpleClient):
        super().__init__(client)

    async def create_context(self, browser: Browser) -> BrowserContext:
        user_agent = random.choice(self.client.USER_AGENTS)
        return await browser.new_context(java_script_enabled=True, user_agent=user_agent)

    @staticmethod
    async def create_page(context: BrowserContext):
        return await context.new_page()

    async def log_in(self, page: Page) -> bool:
        await page.goto(self.client.url)
        # await page.wait_for_load_state('load')
        await page.wait_for_selector('form.login__form')
        await page.locator('input#username').fill(self.client.name)
        await page.locator('input#password').fill(self.client.password)
        await page.locator('button[type="submit"]').click()

        await page.wait_for_timeout(200000)

        title = await page.title()
        if not re.search('| LinkedIn', title):
            return False
        return True

    async def start_manage(self, browser: Browser):
        context = await self.create_context(browser)
        page = await self.create_page(context)
        log_in_success = await self.log_in(page)
        logger_prd.log(55, f'{log_in_success}')
