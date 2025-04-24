from urllib.parse import urlparse

import pytest
from pytest_mock import MockerFixture

from linkedin_bot.bot import LNLoginManager
from linkedin_bot.services import SimpleClient
from linkedin_bot.utilities import CAPTCHAOccurredError


class TestLNLoginManager:

    @pytest.fixture(autouse=True)
    def _setup(self, fake_client: SimpleClient, page: MockerFixture, manager_factory):
        """
        Autouse fixture to initialize the login manager test class.

        Automatically applies the following dependencies before each test:
          - `fake_client`: A dummy `SimpleClient` with fake credentials.
          - `page`: A mocked Playwright `Page` object using `pytest-mock`.
          - `manager_factory`: A factory fixture that constructs any manager
            class and injects `fake_client`.

        Sets:
          - self.client (SimpleClient): The fake client instance.
          - self.page (MagicMock): The mocked page object.
          - self.manager (LNLoginManager): The manager under test.
        """
        self.client = fake_client
        self.page = page
        self.manager: LNLoginManager = manager_factory(LNLoginManager)

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Simulate successfully log in."""
        self.page.url = 'https://www.linkedin.com/feed/'
        result = await self.manager._log_in(self.page)

        self.page.goto.assert_awaited_once_with(self.manager.client.url)
        self.page.wait_for_selector.assert_awaited_once_with('form.login__form')
        self.page.locator.assert_any_call('input#username')
        self.page.locator.assert_any_call('input#password')
        assert result is self.page
        assert urlparse(self.page.url).path.startswith('/feed')

    @pytest.mark.asyncio
    async def test_login_failed_due_to_captcha(self):
        """
        Simulate failed login: page.url does NOT end with `/feed`.

        This should raise CAPTCHAOccurredError.
        """
        self.page.url = 'https://www.linkedin.com/checkpoint/challenge'

        with pytest.raises(CAPTCHAOccurredError):
            await self.manager._log_in(self.page)
