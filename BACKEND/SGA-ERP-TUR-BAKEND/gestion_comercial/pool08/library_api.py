"""Owned library transport: no file paths, external imports or fiscal-vault references."""
import base64
from .crm import CRMError
from .contract import decode,ContractRejected
from .library_store import Store
from .media_library import Library
from .library_sanitize import MAX_UPLOAD
HEADERS={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'",'Referrer-Policy':'no-referrer'}
def upload_metadata(value):
    try:
        if not isinstance(value,str) or len(value)>6000:raise ValueError()
        return decode(base64.b64decode(value,validate=True))
    except (ValueError,ContractRejected):raise CRMError('INVALID_LIBRARY_UPLOAD_METADATA',400) from None
def service(crm):return Library(Store(crm.store),crm)

def public_service(db,ref):
    from types import SimpleNamespace
    from django.http import QueryDict
    from django.contrib.auth import get_user_model
    from .crm_api import CRMView
    from .access_protocol import AccessFault
    from rest_framework.exceptions import APIException
    scope=Store.public_scope(None,ref)
    if not scope or scope['document'].get('published_version') is None:raise CRMError('LIBRARY_PUBLIC_MEDIA_NOT_FOUND',404)
    publisher=scope['document'].get('publisher_ref')
    if not str(publisher).isdigit():raise CRMError('LIBRARY_PUBLIC_MEDIA_NOT_FOUND',404)
    user=get_user_model().objects.filter(pk=publisher,is_active=True).first()
    if not user:raise CRMError('LIBRARY_PUBLIC_MEDIA_NOT_FOUND',404)
    query=QueryDict(mutable=True);query['provider_id']=scope['provider']
    try:crm=CRMView().service(SimpleNamespace(method='POST',query_params=query,user=user))
    except (AccessFault,APIException):raise CRMError('LIBRARY_PUBLIC_MEDIA_NOT_FOUND',404) from None
    if crm.store.scope!=scope['scope'] or crm.store.provider!=scope['provider']:raise CRMError('LIBRARY_PUBLIC_MEDIA_NOT_FOUND',404)
    return service(crm)
