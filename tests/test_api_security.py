from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_security_headers_root():
    """
    Test that GET / returns security headers.
    """
    response = client.get("/")
    # status_code might be 200 if public/index.html exists, or 200 with message if not.
    # In this environment public/index.html exists.
    assert response.status_code == 200

    headers = response.headers
    assert "X-Content-Type-Options" in headers
    assert headers["X-Content-Type-Options"] == "nosniff"

    assert "X-Frame-Options" in headers
    assert headers["X-Frame-Options"] == "DENY"

    assert "Strict-Transport-Security" in headers
    assert headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"

    assert "Content-Security-Policy" in headers
    csp = headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    # Ensure unsafe-inline is NOT in script-src
    script_src = [p for p in csp.split(';') if 'script-src' in p][0]
    assert "'unsafe-inline'" not in script_src

    assert "Referrer-Policy" in headers
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    assert "Permissions-Policy" in headers
    assert headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"

def test_security_headers_calculate():
    """
    Test that POST /api/calculate returns security headers.
    """
    payload = {
        "material": {
            "E1": 140e9,
            "E2": 10e9,
            "G12": 5e9,
            "v12": 0.3,
            "name": "Carbon/Epoxy"
        },
        "stack": [0, 45, -45, 90],
        "symmetry": True,
        "thickness": 0.125e-3
    }
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200

    headers = response.headers
    assert "X-Content-Type-Options" in headers
    assert headers["X-Content-Type-Options"] == "nosniff"

    assert "X-Frame-Options" in headers
    assert headers["X-Frame-Options"] == "DENY"

    assert "Strict-Transport-Security" in headers
    assert headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"

    assert "Content-Security-Policy" in headers
    csp = headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    # Ensure unsafe-inline is NOT in script-src
    script_src = [p for p in csp.split(';') if 'script-src' in p][0]
    assert "'unsafe-inline'" not in script_src
