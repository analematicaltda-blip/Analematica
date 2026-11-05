import time
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

class RateLimiterMiddleware:
    """
    PHASE F: Institutional Grade Rate Limiting
    Targets: Brute Force, API Flooding, and Bot Protection.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip = self._get_client_ip(request)
        user = getattr(request, 'user', None)

        # Determine Rate Limit Tier
        path = request.path
        is_sensitive = any(p in path for p in ['/login/', '/register/', '/payment/', '/invoice/'])

        if is_sensitive:
            limit = 10
            key = f"rl_sens_{client_ip}"
        elif user and user.is_authenticated:
            limit = 120
            key = f"rl_auth_{user.id}"
        else:
            limit = 30
            key = f"rl_anon_{client_ip}"

        if self._is_rate_limited(key, limit):
            return JsonResponse({
                "error": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please slow down."
            }, status=429)

        return self.get_response(request)

    def _is_rate_limited(self, key, limit):
        count = cache.get(key, 0)
        if count >= limit:
            return True
        cache.set(key, count + 1, timeout=60)
        return False

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
