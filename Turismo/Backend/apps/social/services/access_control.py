from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def adult_only_required(view_func):
    """
    Decorator for views that checks if the user is 18+ before allowing access.
    """
    @wraps(view_func)
    def _wrapped_view(instance, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        if not hasattr(user, 'is_adult') or not user.is_adult():
            return Response(
                {"error": "This feature is restricted to users 18 years of age or older."},
                status=status.HTTP_403_FORBIDDEN
            )

        return view_func(instance, request, *args, **kwargs)
    return _wrapped_view
