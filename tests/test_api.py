import pytest
from api import app


# Fixture to provide a Flask test client
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


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
