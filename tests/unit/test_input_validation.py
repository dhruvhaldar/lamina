import pytest
from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_failure_limits_validation():
    """
    Test that invalid limits (<= 0) are rejected with 422.
    """
    payload = {
        "laminate": {
            "material": {
                "E1": 140e9,
                "E2": 10e9,
                "G12": 5e9,
                "v12": 0.3,
                "name": "Test"
            },
            "stack": [0, 90],
            "thickness": 0.125e-3
        },
        "limits": {
            "xt": 0,       # Invalid
            "xc": 1200e6,
            "yt": 50e6,
            "yc": 250e6,
            "s": 70e6
        }
    }
    response = client.post("/api/failure", json=payload)
    assert response.status_code == 422
    assert "xt" in response.text
    assert "Must be positive" in response.text

    # Test negative
    payload["limits"]["xt"] = -100
    response = client.post("/api/failure", json=payload)
    assert response.status_code == 422

def test_failure_limits_valid():
    """
    Test that valid limits work.
    """
    payload = {
        "laminate": {
            "material": {
                "E1": 140e9,
                "E2": 10e9,
                "G12": 5e9,
                "v12": 0.3,
                "name": "Test"
            },
            "stack": [0, 90],
            "thickness": 0.125e-3
        },
        "limits": {
            "xt": 1500e6,
            "xc": 1200e6,
            "yt": 50e6,
            "yc": 250e6,
            "s": 70e6
        }
    }
    response = client.post("/api/failure", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
