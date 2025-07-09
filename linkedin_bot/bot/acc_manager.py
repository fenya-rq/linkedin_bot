"""Module for managing LinkedIn browser sessions and interactions."""

import asyncio
import random
import pyperclip
from abc import ABC, abstractmethod
from urllib.parse import urlparse

from playwright.async_api import Browser, BrowserContext, Page

from linkedin_bot.services import BaseCaptchaSolver, SimpleClient
from linkedin_bot.utilities import CaptchaSolverError, log_writer, retry_on_failure

from . import main_logger
from .bs_parser import BaseParser


class BaseManager(ABC):
    """
    Abstract base class for browser session management.

    Provides the interface for creating a browser context and page.
    """

    __slots__ = 'client', 'browser'

    def __init__(self, client: SimpleClient, browser: Browser) -> None:
        """
        Initialize with a SimpleClient instance.

        :param client: The client configuration object
        """
        self.client = client
        self.browser = browser

    @abstractmethod
    async def _create_context(self, **kwargs: dict[str, str]) -> BrowserContext:
        """
        Create a browser context.

        :param kwargs: Additional context options
        :returns: The created browser context
        """
        pass

    @staticmethod
    @abstractmethod
    async def _create_page(context: BrowserContext) -> Page:
        """
        Create a new page within a context.

        :param context: The browser context
        :returns: The new page instance
        """
        pass


class LNLoginManager(BaseManager):
    """
    Manages login logic and context setup for LinkedIn.

    Handles browser context creation, page setup, and authentication.
    """

    __slots__ = 'captcha_solver'

    def __init__(
        self, client: SimpleClient, browser: Browser, captcha_solver: BaseCaptchaSolver | None = None
    ) -> None:
        """
        Initialize with client and optional CAPTCHA solver.

        :param client: The client configuration object
        :param captcha_solver: Optional CAPTCHA solving service
        """
        super().__init__(client, browser)
        self.captcha_solver = captcha_solver

    async def _create_context(self, **kwargs: dict[str, str]) -> BrowserContext:
        """
        Create a browser context with random user agent.

        :param kwargs: Additional context options
        :returns: Configured browser context
        """
        user_agent = random.choice(self.client.USER_AGENTS)
        return await self.browser.new_context(java_script_enabled=True, user_agent=user_agent)

    @staticmethod
    async def _create_page(context: BrowserContext) -> Page:
        """
        Create a new page in the given context.

        :param context: The browser context
        :returns: New page instance
        """
        return await context.new_page()

    async def _handle_captcha(self, page: Page) -> None:
        """
        Handle CAPTCHA challenge if encountered.

        :param page: The browser page instance
        :raises CaptchaSolverError: If CAPTCHA handling fails
        """
        if not self.captcha_solver:
            raise CaptchaSolverError('No CAPTCHA solver provided')

        iframe_selector = 'iframe[title*="recaptcha"]'
        try:
            await page.wait_for_selector(iframe_selector, timeout=5000)
        except:
            return

        iframe = page.frame_locator(iframe_selector)
        site_key = await iframe.locator('[data-sitekey]').get_attribute('data-sitekey')
        if not site_key:
            raise CaptchaSolverError(details={'url': page.url})

        solution = await self.captcha_solver.solve_captcha(page_url=page.url, site_key=site_key)

        await page.evaluate(f"""
            document.querySelector('#g-recaptcha-response').innerHTML = '{solution}';
            ___grecaptcha_cfg.clients[0].K.K.callback('{solution}');
        """)

        await page.wait_for_load_state('load')

    async def _log_in(self, page: Page) -> Page:
        """
        Perform login with stored credentials.

        Navigates to login page, fills credentials, and handles CAPTCHA if
        needed.

        :param page: The browser page instance
        :returns: The resulting page after login
        :raises CaptchaSolverError: If login or CAPTCHA handling fails
        """
        await page.goto(self.client.url)
        await page.wait_for_selector('form.login__form')

        if await page.locator('label[for="rememberMeOptIn-checkbox"]').count() > 0:
            await page.locator('label[for="rememberMeOptIn-checkbox"]').click()

        await page.locator('input#username').fill(self.client.name)
        await page.locator('input#password').fill(self.client.password)

        login_button = page.locator('button[type="submit"]')
        await login_button.click()
        await page.wait_for_timeout(5000)

        if (url := page.url) and not urlparse(url).path.startswith('/feed'):
            try:
                await self._handle_captcha(page)
            except CaptchaSolverError:
                raise
            except Exception:
                raise

        return page

    @retry_on_failure(max_attempts=5, delay=10, exceptions=(CaptchaSolverError,))
    async def log_in(self) -> Page:
        """
        Set up context and perform login.

        :returns: The feed page if successful
        :raises CaptchaSolverError: If login process fails
        """
        context = await self._create_context()
        page = await self._create_page(context)
        feed_page = await self._log_in(page)
        log_writer(main_logger, 55, 'Logged successfully!')
        return feed_page


class LNPostAnalystManager(LNLoginManager):
    """
    Handles LinkedIn post interactions such as reposting.

    Extends login manager with post-specific functionality.
    """

    __slots__ = 'parser_cls'

    def __init__(
        self,
        client: SimpleClient,
        browser: Browser,
        parser_cls: type[BaseParser],
        captcha_solver: BaseCaptchaSolver | None = None,
    ) -> None:
        """
        Initialize with client and parser class.

        :param client: The client configuration object
        :param parser_cls: Parser class for LinkedIn posts
        :param captcha_solver: Optional CAPTCHA solver service
        """
        super().__init__(client, browser, captcha_solver)
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
        Scroll page to load posts with human-like behavior.

        :param page: The LinkedIn feed page
        :param total_posts: Total posts to load
        :param posts_per_scroll: Expected posts loaded per scroll
        :param min_scroll_height: Minimum pixels per scroll
        :param max_scroll_height: Maximum pixels per scroll
        """
        scroll_count = total_posts // posts_per_scroll

        for _ in range(scroll_count):
            scroll_amount = random.randint(min_scroll_height, max_scroll_height)
            await page.evaluate(f'window.scrollBy(0, {scroll_amount});')

            delay = random.uniform(1.2, 2.5)
            await asyncio.sleep(delay)

    def _parse_data(self, content: str) -> set[str] | dict[str, dict[str, str]]:
        """
        Parse data from content.

        Instantiate parser object and apply parse method.
        :param content: The content to parse
        :returns: Set of parsed data
        """
        # TODO: fix type error [call-arg] for MyPy
        parser_obj = self.parser_cls(html=content)  # type: ignore
        return parser_obj.parse()

    async def get_post_data(self, page: Page) -> set[str] | dict[str, dict[str, str]]:
        """
        Extract unique post IDs from feed page.

        :returns: Set of extracted post IDs
        """
        await page.wait_for_load_state('load')
        await self._scroll_page(page, 5)
        content = await page.content()
        return self._parse_data(content)

    async def add_post_links(self) -> dict[str, dict[str, str]]:
        page = await self.log_in()

        posts_data: dict[str, dict[str, str]] = await self.get_post_data(page)

        for post_id in posts_data.keys():
            container = page.locator(f'div[data-id="{post_id}"]')
            menu_btn = container.locator('button[aria-label^="Открыть меню управления"]')

            if await menu_btn.count() < 1:
                continue

            await menu_btn.click()

            save_link = container.locator(
                'div[role="button"]:has-text("Скопировать ссылку на публикацию")'
            )

            await page.wait_for_timeout(random.uniform(35000.0, 70000.0))
            try:
                await save_link.wait_for(state='visible', timeout=500)
                await save_link.click()
                await page.wait_for_timeout(150)

                posts_data[post_id]['url'] = pyperclip.paste()

            except Exception as e:
                log_writer(main_logger, 30, f'Instant repost option not found for post {post_id}: {e}')
                continue
        return posts_data


class LNRepostManager(LNPostAnalystManager):

    async def _make_reposts(self, page: Page, post_ids: set[str], restrict: int) -> None:
        """
        Perform reposts for given post IDs.

        :param post_ids: Set of post IDs to repost
        :param restrict: Max number of posts to repost
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

            await page.wait_for_timeout(random.uniform(35000.0, 70000.0))
            try:
                await instant_repost.wait_for(state='visible', timeout=1500)
                await instant_repost.click()
            except Exception as e:
                log_writer(main_logger, 30, f'Instant repost option not found for post {id_}: {e}')
                continue

            if pos == restrict - 1:
                break

    async def make_reposts(self, restrict: int) -> None:
        """
        Main entry point for performing reposts.

        :param restrict: Max number of reposts to make
        """
        page = await self.log_in()
        post_ids = await self.get_post_data(page)
        log_writer(main_logger, 55, 'Start reposting...')
        await self._make_reposts(page, post_ids, restrict)
