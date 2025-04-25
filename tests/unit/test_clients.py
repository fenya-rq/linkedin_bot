import pytest


class TestClient:
    @pytest.fixture(autouse=True)
    def _setup(self, fake_client):
        self.client = fake_client

    def test_client_post_init(self):
        """Check the user agent aws chosen and assigned."""
        assert self.client.user_agent in self.client.USER_AGENTS
