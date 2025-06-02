"""Service module for handling CAPTCHA solving operations."""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import cast

from aiohttp import ClientSession

from linkedin_bot.config import main_logger
from linkedin_bot.utilities import log_writer
from linkedin_bot.utilities.custom_exceptions import CaptchaSolverError


class BaseCaptchaSolver(ABC):
    """
    Abstract base class for CAPTCHA solving services.

    Provides interface for different CAPTCHA solving implementations.
    """

    __slots__ = ()

    @abstractmethod
    async def solve_captcha(
        self, page_url: str, site_key: str, **kwargs: dict[str, str | int]
    ) -> str:
        """
        Solve a CAPTCHA challenge.

        :param page_url: URL of the page containing the CAPTCHA
        :param site_key: The site key for the CAPTCHA service
        :param kwargs: Additional parameters for specific implementations
        :returns: The solution token for the CAPTCHA
        :raises CaptchaSolverError: If solving fails
        """
        pass


class TwoCaptchaSolver(BaseCaptchaSolver):
    """
    2captcha service implementation for solving CAPTCHAs.

    Handles communication with the 2captcha API for CAPTCHA solving.
    """

    __slots__ = ('api_key', '_base_url', '_result_url')

    def __init__(self, api_key: str):
        """
        Initialize the 2captcha solver.

        :param api_key: The 2captcha API key
        """
        self.api_key = api_key
        self._base_url = 'https://2captcha.com/in.php'
        self._result_url = 'https://2captcha.com/res.php'

    async def _submit_captcha(self, session: ClientSession, page_url: str, site_key: str) -> str:
        """
        Submit CAPTCHA for solving.

        :param session: The aiohttp client session
        :param page_url: URL of the page with CAPTCHA
        :param site_key: The CAPTCHA site key
        :returns: The request ID for the submitted CAPTCHA
        :raises CaptchaSolverError: If submission fails
        """
        params: dict[str, str | int] = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': site_key,
            'pageurl': page_url,
            'json': 1,
        }

        async with session.get(self._base_url, params=params) as response:
            result = await response.json()

            if result.get('status') != 1:
                raise CaptchaSolverError(
                    'Failed to submit CAPTCHA', {'error': result.get('error_text')}
                )

            request_id = result['request']
            log_writer(main_logger, 20, f'CAPTCHA submitted. ID: {request_id}')
            return request_id

    async def _get_solution(
        self, session: ClientSession, request_id: str, timeout: int = 180, polling_interval: int = 5
    ) -> str:
        """
        Poll for CAPTCHA solution.

        :param session: The aiohttp client session
        :param request_id: The CAPTCHA request ID
        :param timeout: Maximum wait time in seconds
        :param polling_interval: Time between polling attempts
        :returns: The CAPTCHA solution token
        :raises CaptchaSolverError: If solution retrieval fails or times out
        """
        start_time = time.time()
        params: dict[str, str | int] = {
            'key': self.api_key,
            'action': 'get',
            'id': request_id,
            'json': 1,
        }

        while time.time() - start_time < timeout:
            async with session.get(self._result_url, params=params) as response:
                result = await response.json()

                if result['status'] == 1:
                    log_writer(main_logger, 20, 'CAPTCHA solved successfully')
                    return result['request']

                if result.get('request') != 'CAPCHA_NOT_READY':
                    raise CaptchaSolverError(details={'error': result.get('error_text')})

                await asyncio.sleep(polling_interval)

        raise CaptchaSolverError('CAPTCHA solving timed out')

    async def solve_captcha(
        self, page_url: str, site_key: str, **kwargs: dict[str, str | int]
    ) -> str:
        """
        Implement the CAPTCHA solving process.

        :param page_url: URL of the page with CAPTCHA
        :param site_key: The CAPTCHA site key
        :param kwargs: Additional parameters (timeout, polling_interval)
        :returns: The CAPTCHA solution token
        :raises CaptchaSolverError: If solving process fails
        """
        timeout = cast(int, kwargs.get('timeout', 180))
        polling_interval = cast(int, kwargs.get('polling_interval', 5))

        async with ClientSession() as session:
            request_id = await self._submit_captcha(session, page_url, site_key)
            return await self._get_solution(session, request_id, timeout, polling_interval)
