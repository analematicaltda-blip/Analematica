from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
import logging

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        from api.models import CustomUser
        access_token = AccessToken(token_key)
        user_id = access_token["user_id"]
        return CustomUser.objects.get(id=user_id)
    except Exception as e:
        logger.error(f"JWT WS Auth Error: {e}")
        return AnonymousUser()

class JwtAuthMiddleware(BaseMiddleware):
    """
    Middleware de autenticación JWT para WebSockets.
    Valida el token RS256 en la query string.
    """
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = dict(x.split("=") for x in query_string.split("&") if "=" in x)
        token = params.get("token")

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
