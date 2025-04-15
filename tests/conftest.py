import pytest

from linkedin_bot.services import SimpleClient


@pytest.fixture(scope='class')
def get_fake_client():
    client = SimpleClient('fake_name', 'fake_pass', 'fake_url')
    yield client
