from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.middleware import RateLimitMiddleware
import time

def test_rate_limit_middleware():
    app = FastAPI()
    # Set a very low limit for testing: 5 requests per 1 second
    app.add_middleware(RateLimitMiddleware, limit=5, window=1.0)

    @app.get("/")
    def read_root():
        return {"message": "ok"}

    client = TestClient(app)

    # 5 requests should pass
    for _ in range(5):
        response = client.get("/")
        assert response.status_code == 200

    # 6th request should fail
    response = client.get("/")
    assert response.status_code == 429
    assert response.text == "Too Many Requests"

    # Wait for window to pass
    time.sleep(1.1)

    # Should pass again
    response = client.get("/")
    assert response.status_code == 200
