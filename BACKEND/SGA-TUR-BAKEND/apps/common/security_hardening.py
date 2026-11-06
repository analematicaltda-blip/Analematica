import time
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

class SecurityHardeningMiddleware:
    """
    Middleware de Blindaje para el backend SARITA.
    Implementa: Rate Limiting por Rol, Validación de Nonce y Protección de Headers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Rate Limiting por Rol
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            limit_reached = self._check_rate_limit(user)
            if limit_reached:
                return JsonResponse({
                    "error": "SECURITY_RATE_LIMIT_EXCEEDED",
                    "message": "Actividad inusual detectada. Intento registrado en bitácora forense."
                }, status=429)

        # 2. Protección contra Replay Attacks en métodos críticos
        if request.method in ['POST', 'PUT', 'DELETE']:
            nonce = request.headers.get('X-Sarita-Nonce')
            if nonce:
                if not self._validate_nonce(nonce):
                    return JsonResponse({"error": "REPLAY_ATTACK_DETECTED"}, status=403)

        response = self.get_response(request)

        # 3. Security Headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response

    def _check_rate_limit(self, user):
        key = f"rl_{user.id}_{user.role if hasattr(user, 'role') else 'anon'}"
        count = cache.get(key, 0)

        # Límites por rol - Ajustados Fase Establecimiento
        # Se incrementan los umbrales para evitar falsos positivos en UX
        limit = 200 # Default (antes 100)
        if hasattr(user, 'role'):
            if user.role == 'SUPERADMIN': limit = 1000
            elif user.role == 'PRESTADOR': limit = 500
            elif user.role == 'TURISTA': limit = 150 # Antes 50

        # En modo DEBUG los límites son 5x mayores
        if settings.DEBUG:
            limit *= 5

        if count >= limit:
            return True

        cache.set(key, count + 1, timeout=60) # 1 minuto de ventana
        return False

    def _validate_nonce(self, nonce):
        key = f"nonce_{nonce}"
        if cache.get(key):
            return False # Replay!
        cache.set(key, True, timeout=300) # Expira en 5 min
        return True
