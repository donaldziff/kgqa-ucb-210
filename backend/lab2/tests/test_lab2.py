import pytest
import json
from fastapi.testclient import TestClient

from lab2 import __version__
from lab2.main import app

client = TestClient(app)


# Following is from the output of trainer/train.py

# features: ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude']
# Example 0:
#  [   8.3252       41.            6.98412698    1.02380952  322.
#     2.55555556   37.88       -122.23      ], 4.526
# Example 1:
#  [ 8.30140000e+00  2.10000000e+01  6.23813708e+00  9.71880492e-01
#   2.40100000e+03  2.10984183e+00  3.78600000e+01 -1.22220000e+02], 3.585
# Example 2:
#  [   7.2574       52.            8.28813559    1.07344633  496.
#     2.80225989   37.85       -122.24      ], 3.521
# Example 3:
#  [   5.6431       52.            5.8173516     1.07305936  558.
#     2.54794521   37.85       -122.25      ], 3.413
# Example 4:
#  [   3.8462       52.            6.28185328    1.08108108  565.
#     2.18146718   37.85       -122.25      ], 3.422

GOOD_EXAMPLE = {
    'MedInc': 8.3252,
    'HouseAge': 41,
    'AveRooms': 6.98412698,
    'AveBedrms': 1.02380952,
    'Population': 322.,
    'AveOccup': 2.55555556,
    'Latitude': 37.88,
    'Longitude': -122.23
    }


def test_predict():
    response = client.post("/predict/", data=json.dumps(GOOD_EXAMPLE))
    assert response.status_code == 200
    assert 'prediction' in response.json()
                           
def test_predict_malformed_json():
    # the below removes the initial curly brace
    bad_json = json.dumps(GOOD_EXAMPLE)[1:]
    response = client.post("/predict/", data=bad_json)
    # fastapi generates a 422 when an unparseable entity is sent
    assert response.status_code == 422
    assert 'prediction' not in response.json()
    
def test_predict_feature_missing():
    bad_example = GOOD_EXAMPLE.copy().pop('MedInc')
    response = client.post("/predict/", data=json.dumps(bad_example))
    # surprisingly, fastapi generates a 422 when a parseable but malformed entity is sent
    assert response.status_code == 422
    assert 'prediction' not in response.json()

def test_predict_feature_badly_typed():
    bad_example = GOOD_EXAMPLE.copy()
    bad_example['AveOccup'] = 'bazfaz'
    # fastapi generates a 422 for this case as well
    response = client.post("/predict/", data=json.dumps(bad_example))
    assert response.status_code == 422
    assert 'prediction' not in response.json()

def test_predict_extra_feature():
    example = GOOD_EXAMPLE.copy()
    example['xyzzy'] = 'foo'
    response = client.post("/predict/", data=json.dumps(example))
    assert response.status_code == 200
    assert 'prediction' in response.json()

    
