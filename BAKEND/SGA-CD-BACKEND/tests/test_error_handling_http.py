from fastapi import HTTPException

def test_http_404_not_found(client):
    response = client.get("/api/v1/non-existent-endpoint-12345")
    assert response.status_code == 404
    assert "X-Correlation-ID" in response.headers

def test_http_401_unauthorized(client):
    response = client.get("/api/v1/eventos/")
    assert response.status_code == 401
    assert "X-Correlation-ID" in response.headers

def test_http_405_method_not_allowed(client):
    # GET on a POST-only route like login
    response = client.get("/api/v1/auth/login")
    assert response.status_code == 405
    assert "X-Correlation-ID" in response.headers

def test_http_500_global_exception_handler():
    from app.main import app
    from fastapi.testclient import TestClient

    # Temporarily add a route that raises an unhandled error
    @app.get("/api/v1/test-500-error")
    def trigger_error():
        raise RuntimeError("Simulated internal database crash")

    custom_client = TestClient(app, raise_server_exceptions=False)
    response = custom_client.get("/api/v1/test-500-error")
    assert response.status_code == 500
    assert "X-Correlation-ID" in response.headers
    data = response.json()
    assert "detail" in data
    assert "correlation_id" in data
    assert "Simulated internal database crash" not in data["detail"]
