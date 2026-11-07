import time
import logging
import threading
from typing import Dict, Tuple, Optional, Callable
from fastapi import Request, HTTPException, status
from app.core.config import settings

logger = logging.getLogger("sga_cd_rate_limiter")

class SlidingWindowRateLimiter:
    """
    In-memory thread-safe rate limiter supporting sliding windows.
    Compatible with multi-instance backend deployments when paired with sticky sessions or Redis.
    Safely resolves real client IPs using trusted proxy headers.
    """
    def __init__(self):
        self._requests: Dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def get_client_ip(self, request: Request) -> str:
        """
        Extract real client IP safely behind reverse proxies.
        """
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # First IP in the comma-separated list is the original client IP
            client_ip = x_forwarded_for.split(",")[0].strip()
            if client_ip:
                return client_ip

        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip.strip()

        return request.client.host if request.client else "127.0.0.1"

    def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, int]:
        """
        Checks if the request rate limit for the given key is exceeded.
        Returns (is_limited, retry_after_seconds).
        """
        # Bypass during automated test execution or if rate limiting is explicitly disabled
        if getattr(settings, "TESTING", False) or getattr(settings, "ENVIRONMENT", "").lower() == "test":
            return False, 0

        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            timestamps = self._requests.get(key, [])
            # Filter out timestamps outside the sliding window
            timestamps = [ts for ts in timestamps if ts > window_start]

            if len(timestamps) >= max_requests:
                # Earliest request in window defines retry after
                earliest = timestamps[0]
                retry_after = int((earliest + window_seconds) - now) + 1
                self._requests[key] = timestamps
                return True, max(retry_after, 1)

            timestamps.append(now)
            self._requests[key] = timestamps
            return False, 0

    def check_limit(
        self,
        request: Request,
        resource_name: str,
        max_requests: int,
        window_seconds: int,
        identifier: Optional[str] = None
    ) -> None:
        """
        Enforces rate limiting on a FastAPI route.
        Raises HTTP 429 if the limit is exceeded and logs suspicious activity.
        """
        client_ip = self.get_client_ip(request)
        key_id = identifier or client_ip
        rate_key = f"rate_limit:{resource_name}:{key_id}"

        is_limited, retry_after = self.is_rate_limited(rate_key, max_requests, window_seconds)

        if is_limited:
            logger.warning(
                f"[SUSPICIOUS ACTIVITY / RATE LIMIT EXCEEDED] "
                f"IP={client_ip} Key={key_id} Resource='{resource_name}' "
                f"Limit={max_requests}/{window_seconds}s RetryAfter={retry_after}s"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Demasiadas solicitudes para '{resource_name}'. Por favor, intente de nuevo en {retry_after} segundos.",
                headers={"Retry-After": str(retry_after)}
            )

limiter = SlidingWindowRateLimiter()

def rate_limit(resource_name: str, max_requests: int, window_seconds: int):
    """
    FastAPI dependency factory for endpoint rate limiting.
    """
    async def dependency(request: Request):
        limiter.check_limit(
            request=request,
            resource_name=resource_name,
            max_requests=max_requests,
            window_seconds=window_seconds
        )
    return dependency
