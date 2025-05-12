import random
from abc import ABC, abstractmethod
from typing import Type
from urllib.parse import urlparse

import asyncio
from playwright.async_api import Browser, BrowserContext, Page

from linkedin_bot.services import SimpleClient
from linkedin_bot.utilities import CAPTCHAOccurredError, log_writer
from .bs_parser import LinkedInPostsParser
from . import main_logger


class BaseManager(ABC):
    """
    Abstract base class for browser session management.

    Provides the interface for creating a browser context and page.
    """

    __slots__ = ('client',)

    def __init__(self, client: SimpleClient):
        """
        Initialize with a SimpleClient instance.

        Args:
            client (SimpleClient): The client configuration object.
        """
        self.client = client

    @abstractmethod
    async def _create_context(self, browser: Browser, **kwargs: dict[str, str]) -> BrowserContext:
        """Create a browser context.

        Args:
            browser (Browser): The Playwright browser instance.
            **kwargs (dict[str, str]): Additional context options.

        Returns:
            BrowserContext: The created browser context.
        """
        pass

    @staticmethod
    @abstractmethod
    async def _create_page(context: BrowserContext) -> Page:
        """Create a new page within a context.

        Args:
            context (BrowserContext): The browser context.

        Returns:
            Page: The new page instance.
        """
        pass


class LNLoginManager(BaseManager):
    """Manages login logic and context setup for LinkedIn."""

    __slots__ = ('client',)

    async def _create_context(self, browser: Browser, **kwargs: dict[str, str]) -> BrowserContext:
        user_agent = random.choice(self.client.USER_AGENTS)
        return await browser.new_context(java_script_enabled=True, user_agent=user_agent)

    @staticmethod
    async def _create_page(context: BrowserContext):
        return await context.new_page()

    async def _log_in(self, page: Page) -> Page:
        """
        Perform login with stored credentials.

        Navigates to the login page, fills in credentials, and submits
        the form.

        Args:
            page (Page): The browser page instance.

        Returns:
            Page: The resulting page after login.
        """
        await page.goto(self.client.url)
        await page.wait_for_selector('form.login__form')

        # Refuse in checkbox with "Remember Me"
        if await page.locator('label[for="rememberMeOptIn-checkbox"]').count() > 0:
            await page.locator('label[for="rememberMeOptIn-checkbox"]').click()

        # Fill the account creds
        await page.locator('input#username').fill(self.client.name)
        await page.locator('input#password').fill(self.client.password)

        login_button = page.locator('button[type="submit"]')
        await login_button.click()
        await page.wait_for_timeout(5000)

        if not (url := page.url) or not urlparse(url).path.startswith('/feed'):
            raise CAPTCHAOccurredError()

        return page

    async def log_in(self, browser: Browser) -> Page:
        """
        Set up the context and perform login.

        Args:
            browser (Browser): The Playwright browser instance.

        Returns:
            Page: The feed page if successful, otherwise raise the error.
        """
        context = await self._create_context(browser)
        page = await self._create_page(context)
        try:
            feed_page = await self._log_in(page)
            log_writer(main_logger, 55, 'Logged successfully!')
            return feed_page
        except Exception as e:
            log_writer(main_logger, 40, f'{e}')
            raise


class LNPostManager(LNLoginManager):
    """Handles LinkedIn post interactions such as reposting."""

    def __init__(self, client: SimpleClient, parser_cls: Type[LinkedInPostsParser]) -> None:
        super().__init__(client)
        self.parser_cls = parser_cls

    @staticmethod
    async def _scroll_page(
        page: Page,
        total_posts: int = 50,
        posts_per_scroll: int = 1,
        min_scroll_height: int = 400,
        max_scroll_height: int = 600,
    ) -> None:
        """
        Scroll the page to load a given number of posts.

        Simulates human-like scrolling behavior.

        Args:
            page (Page): The LinkedIn feed page.
            total_posts (int): Total posts to load.
            posts_per_scroll (int): Expected posts loaded per scroll.
            min_scroll_height (int): Minimum pixels per scroll.
            max_scroll_height (int): Maximum pixels per scroll.
        """
        scroll_count = total_posts // posts_per_scroll

        for i in range(scroll_count):
            scroll_amount = random.randint(min_scroll_height, max_scroll_height)
            await page.evaluate(f'window.scrollBy(0, {scroll_amount});')

            # Simulate human delay: reading or scanning posts
            delay = random.uniform(1.2, 2.5)
            await asyncio.sleep(delay)

    async def _get_post_ids(self, page: Page) -> set[str]:
        """
        Extract unique post IDs from the feed page.

        Args:
            page (Page): The LinkedIn feed page.

        Returns:
            set[str]: A set of extracted post IDs.
        """
        # Ensure the page content was loaded for correct getting
        await page.wait_for_load_state('load')
        await self._scroll_page(page)
        content = await page.content()
        parser_obj = self.parser_cls(content)
        return parser_obj.parse()

    async def _make_reposts(self, page: Page, post_ids: set[str], restrict: int):
        """
        Perform reposts for given post IDs.

        Clicks the repost button for each post and chooses the
        instant repost option when available.

        Args:
            page (Page): The LinkedIn feed page.
            post_ids (set[str]): Set of post IDs to repost.
            restrict (int): Max number of posts to repost.
        """
        for pos, id_ in enumerate(post_ids):
            container = page.locator(f'div[data-id="{id_}"]')
            share_btn = container.locator('button:has-text("Поделиться")')

            if await share_btn.count() < 1:
                continue

            await share_btn.click()

            instant_repost = container.locator(
                'div.artdeco-dropdown__item:has-text("Вы можете мгновенно отправить")'
            )

            # Make pauses to imitate human behavior
            await page.wait_for_timeout(random.uniform(35000.0, 70000.0))
            try:
                await instant_repost.wait_for(state='visible', timeout=1000)
                await instant_repost.click()
            except Exception as e:
                log_writer(main_logger, 30, f'Instant repost option not found for post {id_}: {e}')
                continue

            # Limit with passed reposts amount restrict
            if pos == restrict - 1:
                break

    async def make_reposts(self, browser: Browser, restrict: int):
        """
        Main entry point to perform reposts.

        Logs in, extracts post IDs, and performs reposts up to
        the restrict limit.

        Args:
            browser (Browser): The Playwright browser instance.
            restrict (int): Max number of reposts to make.
        """
        feed_page = await self.log_in(browser)
        post_ids = await self._get_post_ids(feed_page)
        log_writer(main_logger, 55, 'Start reposting...')
        await self._make_reposts(feed_page, post_ids, restrict)
