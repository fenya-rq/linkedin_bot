from urllib.parse import urlparse

import pytest
from pytest_mock import MockerFixture

from linkedin_bot.bot import LNLoginManager
from linkedin_bot.services import SimpleClient, TwoCaptchaSolver
from linkedin_bot.utilities import CaptchaSolverError


class TestLNLoginManager:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        fake_client: SimpleClient,
        fake_page: MockerFixture,
        fake_2captcha_solver: TwoCaptchaSolver,
    ):
        """Autouse fixture to initialize the login manager test class.

        Automatically applies test dependencies before each test method execution.

        :param fake_client: A dummy SimpleClient with fake credentials
        :type fake_client: SimpleClient
        :param fake_page: A mocked Playwright Page object using pytest-mock
        :type fake_page: MockerFixture
        :param fake_2captcha_solver: A mocked CAPTCHA solver service
        :type fake_2captcha_solver: TwoCaptchaSolver

        :ivar client: The fake client instance
        :ivar page: The mocked page object
        :ivar captcha_solver: The mocked CAPTCHA solver
        """
        self.client = fake_client
        self.page = fake_page
        self.captcha_solver = fake_2captcha_solver

    @pytest.mark.asyncio
    async def test_login_success(self, manager_factory):
        """
        Simulate successfully log in.

        Instantiating manager without captha colver instance.
        """
        manager = manager_factory(LNLoginManager)

        self.page.url = 'https://www.linkedin.com/feed/'
        result = await manager._log_in(self.page)

        # Check that goto was called with correct expected URL
        assert self.page.goto.call_args[0][0] == manager.client.url
        assert self.page.goto.await_count == 1

        # Check that wait_for_selector was called with form selector
        assert self.page.wait_for_selector.call_args[0][0] == 'form.login__form'
        assert self.page.wait_for_selector.await_count == 1

        # Check username and password fields were located
        self.page.locator.assert_any_call('input#username')
        self.page.locator.assert_any_call('input#password')

        assert result is self.page
        assert urlparse(self.page.url).path.startswith('/feed')

    @pytest.mark.asyncio
    async def test_login_failed_with_capcha_occured_without_solver(self, manager_factory):
        """
        Simulate failed login: page.url does NOT end with `/feed`.

        Creates a manager without a fake captcha solver instance and set behavior
        to raise `CaptchaSolverError` with `'No CAPTCHA solver provided'` message.
        :raises CaptchaSolverError: If the login fails due to a captcha.
        """
        manager = manager_factory(
            LNLoginManager, captcha_behavior=CaptchaSolverError('No CAPTCHA solver provided')
        )

        self.page.url = 'https://www.linkedin.com/checkpoint/challenge'

        with pytest.raises(CaptchaSolverError) as e:
            await manager._log_in(self.page)

        assert manager._handle_captcha.call_count == 1
        assert str(e.value) == 'No CAPTCHA solver provided'

    @pytest.mark.asyncio
    async def test_login_with_captcha_solving_failed(self, manager_factory):
        """
        Simulate failed login: page.url does NOT end with `/feed`.

        Creates a manager with a fake captcha solver instance.
        :raises CaptchaSolverError: If the login fails due to a captcha.
        """
        manager = manager_factory(
            LNLoginManager, captcha_solver=self.captcha_solver, captcha_behavior=CaptchaSolverError
        )

        self.page.url = 'https://www.linkedin.com/checkpoint/challenge'

        with pytest.raises(CaptchaSolverError):
            await manager._log_in(self.page)

        assert manager._handle_captcha.call_count == 1

    @pytest.mark.asyncio
    async def test_login_success_with_captcha_solving_success(self, manager_factory):
        """
        Simulate successfully log in.

        Creates a manager with a fake captcha solver instance
        and simulate successful CAPTCHA solving through redirecting to /feed.
        """

        async def redirect_to_feed(page):
            self.page.url = 'https://www.linkedin.com/feed/'

        self.page.url = 'https://www.linkedin.com/checkpoint/challenge'

        manager = manager_factory(
            LNLoginManager, captcha_solver=self.captcha_solver, captcha_behavior=redirect_to_feed
        )

        result = await manager._log_in(self.page)

        assert result.url == 'https://www.linkedin.com/feed/'
        assert manager._handle_captcha.call_count == 1
