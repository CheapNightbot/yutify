import pytest
from app import create_app, db


# Fixture to provide a Flask test client
@pytest.fixture
def client():
    app = create_app("config.TestingConfig")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_index(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Home" in response.data


def test_docs(client):
    """Test the docs route."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"Docs" in response.data
