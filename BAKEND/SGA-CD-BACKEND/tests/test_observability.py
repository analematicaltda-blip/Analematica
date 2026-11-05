import json
import logging
from app.core.logging_config import JSONStructuredFormatter

def test_correlation_id_middleware(client):
    # Custom Correlation ID
    custom_cid = "test-correlation-12345"
    response = client.get("/", headers={"X-Correlation-ID": custom_cid})

    assert response.status_code == 200
    assert response.headers.get("X-Correlation-ID") == custom_cid

    # Generated Correlation ID when not provided
    response2 = client.get("/")
    assert response2.status_code == 200
    assert "X-Correlation-ID" in response2.headers
    assert len(response2.headers["X-Correlation-ID"]) > 0

def test_json_formatter_privacy_redaction():
    formatter = JSONStructuredFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg='User password login payload: {"password": "SuperSecret123", "token": "eyJhbGci.secretToken"}',
        args=(),
        exc_info=None
    )

    formatted_log = formatter.format(record)
    log_json = json.loads(formatted_log)

    assert "timestamp" in log_json
    assert log_json["level"] == "INFO"
    assert "SuperSecret123" not in formatted_log
    assert "eyJhbGci" not in formatted_log
    assert "[REDACTADO]" in formatted_log
