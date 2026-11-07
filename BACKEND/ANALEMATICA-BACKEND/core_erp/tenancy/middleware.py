from .utils import set_current_tenant_id, clear_current_tenant_id
import uuid
from django.http import JsonResponse
from django.conf import settings

class TenantContextMiddleware:
    """
    Middleware that identifies the tenant from the 'X-Tenant-ID' header
    and sets it in the request context.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Exclusion list for public or administrative paths
        path = request.path
        if any(path.startswith(prefix) for prefix in ['/admin/', '/api/public/', '/health/']):
            return self.get_response(request)

        # 2. Extract and Validate Tenant ID
        tenant_id = request.headers.get('X-Tenant-ID')

        if not tenant_id:
            return JsonResponse(
                {"error": "Multi-tenancy violation: X-Tenant-ID header is missing."},
                status=403
            )

        try:
            # Validate UUID format
            uuid.UUID(tenant_id)
        except ValueError:
            return JsonResponse(
                {"error": "Invalid X-Tenant-ID format. UUID v4 expected."},
                status=400
            )

        # 3. Set Context
        token = set_current_tenant_id(tenant_id)
        request.tenant_id = tenant_id

        try:
            response = self.get_response(request)
        finally:
            # 4. Clear Context
            clear_current_tenant_id(token)

        return response
