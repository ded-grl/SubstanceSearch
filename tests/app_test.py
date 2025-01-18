import pytest
from src import create_app


class TestAppClass:
    @pytest.fixture()
    def app(self):
        app = create_app()
        app.config.update({
            'TESTING': True,
        })

        yield app

    @pytest.fixture()
    def client(self, app):
        return app.test_client()

    def test_home_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_substance_endpoint_sccuess(self, client):
        response = client.get("/substance/alcohol")
        assert response.status_code == 200

    def test_substance_endpoint_failure(self, client):
        response = client.get("/substance/NON-EXISTENT-SUBSTANCE")
        assert response.status_code == 404
