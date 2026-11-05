# main_config/views.py
from django.http import JsonResponse

def healthcheck(request):
    """
    A simple health check endpoint that returns a JSON response indicating the server is running.
    """
    return JsonResponse({"status": "ok"})
