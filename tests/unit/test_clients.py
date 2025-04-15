import pytest


class TestClient:

    @pytest.fixture(autouse=True)
    def setup(self, get_fake_client):
        self.client = get_fake_client

    @pytest.mark.usefixtures('get_fake_client')
    def test_client_post_init(self):
        assert self.client.user_agent in self.client.USER_AGENTS
