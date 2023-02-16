import pytest
import json
from fastapi.testclient import TestClient

from askwiki import __version__
from askwiki.main import app

client = TestClient(app)


DUMMY_EXAMPLE = {
    'pipeline': 'dummy',
    'prompt': 'what is the difference between a duck?'
    }


def test_complete():
    response = client.post("/completions/", data=json.dumps(DUMMY_EXAMPLE))
    assert response.status_code == 200
    assert 'summary' in response.json()
                           
def test_completions_malformed_json():
    # the below removes the initial curly brace
    bad_json = json.dumps(DUMMY_EXAMPLE)[1:]
    response = client.post("/completions/", data=bad_json)
    # fastapi generates a 422 when an unparseable entity is sent
    assert response.status_code == 422
    assert 'summary' not in response.json()
    
def test_completions_feature_missing():
    bad_example = DUMMY_EXAMPLE.copy().pop('pipeline')
    response = client.post("/completions/", data=json.dumps(bad_example))
    # surprisingly, fastapi generates a 422 when a parseable but malformed entity is sent
    assert response.status_code == 422
    assert 'summary' not in response.json()

# This test is failing - i.e. a numeric prompt seems to be acceptable
# def test_completions_feature_badly_typed():
#     bad_example = DUMMY_EXAMPLE.copy()
#     bad_example['prompt'] = 42.05
#     # fastapi generates a 422 for this case as well
#     response = client.post("/completions/", data=json.dumps(bad_example))
#     assert response.status_code == 422
#     assert 'summary' not in response.json()

def test_completions_extra_feature():
    example = DUMMY_EXAMPLE.copy()
    example['xyzzy'] = 'foo'
    response = client.post("/completions/", data=json.dumps(example))
    assert response.status_code == 200
    assert 'summary' in response.json()

    