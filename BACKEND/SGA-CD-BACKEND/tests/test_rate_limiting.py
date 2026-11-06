import pytest
from fastapi import Request
from app.core.rate_limiter import SlidingWindowRateLimiter, limiter
from app.core.config import settings

def test_rate_limiter_proxy_ip_extraction():
    limiter_obj = SlidingWindowRateLimiter()

    # X-Forwarded-For test
    scope = {
        "type": "http",
        "headers": [(b"x-forwarded-for", b"203.0.113.195, 70.41.3.18, 150.172.238.178")],
        "client": ("10.0.0.1", 1234)
    }
    req = Request(scope)
    assert limiter_obj.get_client_ip(req) == "203.0.113.195"

    # X-Real-IP fallback
    scope2 = {
        "type": "http",
        "headers": [(b"x-real-ip", b"198.51.100.10")],
        "client": ("10.0.0.1", 1234)
    }
    req2 = Request(scope2)
    assert limiter_obj.get_client_ip(req2) == "198.51.100.10"

    # Direct client IP
    scope3 = {
        "type": "http",
        "headers": [],
        "client": ("192.168.1.50", 1234)
    }
    req3 = Request(scope3)
    assert limiter_obj.get_client_ip(req3) == "192.168.1.50"

def test_sliding_window_rate_limiting_enforcement():
    limiter_obj = SlidingWindowRateLimiter()

    # Temporarily force TESTING=False to test rate limiting logic directly
    orig_testing = getattr(settings, "TESTING", False)
    setattr(settings, "TESTING", False)

    try:
        key = "test_key_limit"
        max_reqs = 3
        window = 10

        # First 3 requests -> allowed
        is_limited, _ = limiter_obj.is_rate_limited(key, max_reqs, window)
        assert not is_limited

        is_limited, _ = limiter_obj.is_rate_limited(key, max_reqs, window)
        assert not is_limited

        is_limited, _ = limiter_obj.is_rate_limited(key, max_reqs, window)
        assert not is_limited

        # 4th request -> blocked (HTTP 429 logic)
        is_limited, retry_after = limiter_obj.is_rate_limited(key, max_reqs, window)
        assert is_limited
        assert retry_after > 0
    finally:
        setattr(settings, "TESTING", orig_testing)
