import pytest

from src import create_app
from src.data import SUBSTANCE_DATA
from src.utils import slugify


class TestAppClass:
    @pytest.fixture()
    def app(self):
        app = create_app()
        app.config.update(
            {
                "TESTING": True,
            }
        )

        yield app

    @pytest.fixture()
    def client(self, app):
        return app.test_client()

    def test_home_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200

    @pytest.mark.parametrize("substance_name", SUBSTANCE_DATA.keys())
    def test_substance_endpoint_sccuess(self, client, substance_name):
        slug = slugify(substance_name)
        response = client.get(f"/substance/{slug}")
        assert response.status_code == 200, f"Error rendering route[/substance/{slug}]"

    def test_substance_endpoint_failure(self, client):
        response = client.get("/substance/NON-EXISTENT-SUBSTANCE")
        assert response.status_code == 404
