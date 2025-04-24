import pytest
from pytest_mock import MockerFixture

from playwright.async_api import Page

from linkedin_bot.services import SimpleClient


@pytest.fixture(scope='class')
def fake_client():
    yield SimpleClient('fake_name', 'fake_pass', 'fake_url')


@pytest.fixture
def manager_factory(fake_client):
    """
    Return a callable that instantiates an arbitrary Manager subclass
    and injects the shared `fake_client`.
    Usage inside tests:
        mgr = manager_factory(LNLoginManager)
    """
    def _build(manager_cls, *args, **kwargs):
        mgr = manager_cls(fake_client, *args, **kwargs)
        return mgr

    return _build


@pytest.fixture
def page(mocker: MockerFixture):
    """A fully‑mocked Playwright Page object."""
    page = mocker.MagicMock(spec=Page)
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
