"""Private financial responses must not be retained by HTTP caches.
This does not erase downloaded data or protect a compromised client.
"""
from django.utils.cache import patch_vary_headers

class PrivateAccountingResponseMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'private, no-store, no-cache, max-age=0, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        patch_vary_headers(response, ['Cookie', 'Authorization'])
        return response
