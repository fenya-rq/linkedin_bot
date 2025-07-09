import pytest
from playwright.async_api import Browser, Page
from pytest_mock import MockerFixture

from linkedin_bot.services import SimpleClient, TwoCaptchaSolver


@pytest.fixture(scope='class')
def fake_client():
    yield SimpleClient('fake_name', 'fake_pass', 'fake_url')


@pytest.fixture
def manager_factory(mocker: MockerFixture, fake_client, fake_browser):
    """
    Return a callable that instantiates an arbitrary Manager subclass
    and injects the shared `fake_client`.
    Usage inside tests:
        ```
        # Simple usage
        mgr = manager_factory(LNLoginManager)

        # With custom captcha behavior
        mgr = manager_factory(LNLoginManager, captcha_behavior=CaptchaSolverError('Test error'))
        ```
    """

    def _build(manager_cls, *args, captcha_behavior=None, **kwargs):
        mock_config = {'new_callable': mocker.AsyncMock}
        if captcha_behavior:
            mock_config['side_effect'] = captcha_behavior

        mocker.patch.object(manager_cls, '_handle_captcha', **mock_config)
        mgr = manager_cls(fake_client, fake_browser, *args, **kwargs)
        return mgr

    return _build


@pytest.fixture
def fake_browser(mocker: MockerFixture):
    """A fully‑mocked Playwright Browser object."""
    return mocker.Mock(spec=Browser)


@pytest.fixture
def fake_page(mocker: MockerFixture):
    """A fully‑mocked Playwright Page object."""
    page = mocker.Mock(spec=Page)
    page.url = ''

    def make_locator(count=0):
        loc = mocker.MagicMock()
        loc.count = mocker.AsyncMock(return_value=count)
        loc.click = mocker.AsyncMock()
        loc.fill = mocker.AsyncMock()
        return loc

    page.goto = mocker.AsyncMock()
    page.wait_for_selector = mocker.AsyncMock()
    page.wait_for_timeout = mocker.AsyncMock()
    page.locator.side_effect = lambda sel: make_locator(1 if sel.startswith('label') else 0)
    return page


@pytest.fixture
def fake_2captcha_solver(mocker: MockerFixture):
    """Mock TwoCaptchaSolver fixture for testing."""
    captcha_solver = mocker.Mock(spec=TwoCaptchaSolver)

    captcha_solver.api_key = 'fake_api_key'
    captcha_solver.solve_captcha = mocker.AsyncMock(return_value='fake_captcha_solution')
    yield captcha_solver
