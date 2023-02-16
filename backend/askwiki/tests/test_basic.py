# basics
import pytest
from fastapi.testclient import TestClient

from askwiki import __version__
from askwiki.main import app

client = TestClient(app)


def test_version():
    assert __version__ == "0.1.0"


def test_hello_bad_parameter():
    response = client.get("/hello?bob=name")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "name"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


@pytest.mark.parametrize(
    "test_input, expected",
    [("james", "james"), ("bob", "bob"), ("BoB", "BoB"), (100, 100)],
)
def test_hello(test_input, expected):
    response = client.get(f"/hello?name={test_input}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Hello {expected}"}


def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200
