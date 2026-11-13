from .inbox import Inbox
from .inbox_store import Store
def service(crm):return Inbox(Store(crm.store),crm)
def native(crm,body):
 import base64,binascii
 from .crm import CRMError
 from .inbox_ingress import meta
 if not isinstance(body,dict) or set(body)!={'account_ref','raw_base64','signature'}:raise CRMError('INBOX_NATIVE_ENVELOPE_REQUIRED')
 try:raw=base64.b64decode(body['raw_base64'],validate=True)
 except (ValueError,TypeError,binascii.Error):raise CRMError('INBOX_NATIVE_ENVELOPE_REQUIRED') from None
 return meta(service(crm),body['account_ref'],raw,body['signature'])
def source_sync(crm,body):
 from .crm import CRMError
 from .inbox_ingress import sync
 if not isinstance(body,dict) or set(body)!={'account_ref','channel'} or not isinstance(body['channel'],str) or body['channel'] not in ('EMAIL','YOUTUBE_COMMENT') or not isinstance(body['account_ref'],str):raise CRMError('INBOX_SOURCE_ENVELOPE_REQUIRED')
 return sync(service(crm),body['account_ref'],body['channel'])
