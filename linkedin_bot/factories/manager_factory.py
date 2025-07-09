"""Factory module for creating different types of managers."""

from playwright.async_api import Browser

from linkedin_bot.bot import LNPostAnalystManager, LNRepostManager
from linkedin_bot.bot.bs_parser import BaseParser
from linkedin_bot.services import BaseCaptchaSolver, SimpleClient


class ManagerFactory:
    """Factory for creating different types of LinkedIn managers."""

    @staticmethod
    def create_repost_manager(
        client: SimpleClient,
        browser: Browser,
        parser_cls: type[BaseParser],
        captcha_solver: BaseCaptchaSolver | None = None,
    ) -> LNRepostManager:
        """
        Create a repost manager instance.

        :param client: Client configuration
        :param browser: Playwright Browser instance
        :param parser_cls: Parser class for LinkedIn posts
        :param captcha_solver: Optional CAPTCHA solver service
        :returns: Configured repost manager
        """
        return LNRepostManager(client, browser, parser_cls, captcha_solver)

    @staticmethod
    def create_analyst_manager(
        client: SimpleClient,
        browser: Browser,
        parser_cls: type[BaseParser],
        captcha_solver: BaseCaptchaSolver | None = None,
    ) -> LNPostAnalystManager:
        """
        Create a repost manager instance.

        :param client: Client configuration
        :param browser: Playwright Browser instance
        :param parser_cls: Parser class for LinkedIn posts
        :param captcha_solver: Optional CAPTCHA solver service
        :returns: Configured repost manager
        """
        return LNPostAnalystManager(client, browser, parser_cls, captcha_solver)
