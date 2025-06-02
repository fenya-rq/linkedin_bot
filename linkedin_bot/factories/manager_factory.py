"""Factory module for creating different types of managers."""

from linkedin_bot.bot import LNRepostManager
from linkedin_bot.bot.bs_parser import BaseParser
from linkedin_bot.services import BaseCaptchaSolver, SimpleClient


class ManagerFactory:
    """Factory for creating different types of LinkedIn managers."""

    @staticmethod
    def create_repost_manager(
        client: SimpleClient,
        parser_cls: type[BaseParser],
        captcha_solver: BaseCaptchaSolver | None = None,
    ) -> LNRepostManager:
        """
        Create a repost manager instance.

        :param client: Client configuration
        :param parser_cls: Parser class for LinkedIn posts
        :param captcha_solver: Optional CAPTCHA solver service
        :returns: Configured repost manager
        """
        return LNRepostManager(client, parser_cls, captcha_solver)
