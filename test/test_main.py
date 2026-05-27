import pytest
from src.main import app


@pytest.fixture
def client():
    """Create and configure a Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_hello(client):
    """Test that home route renders index.html successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Flask" in response.data


def test_feature1(client):
    """Test that /feature1 returns 200 OK and correct message."""
    response = client.get("/feature1")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "早上要看股票"


def test_feature2(client):
    """Test that /feature2 returns 200 OK and correct message."""
    response = client.get("/feature2")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "要找下午上班的公司"
