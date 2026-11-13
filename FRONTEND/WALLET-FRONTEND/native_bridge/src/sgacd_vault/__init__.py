"""Only metadata crosses Flet. Plaintext and encryption keys stay in the native client."""
import asyncio
from dataclasses import dataclass
import json
from uuid import UUID,uuid4
from flet.core.control import Control

SAFE_CODES=frozenset(['NATIVE_UNAVAILABLE', 'BUSY', 'BUSY_OR_UNSUPPORTED', 'INVALID_ARGUMENTS', 'INVALID_ARGUMENTS_OR_UNAVAILABLE', 'ACTIVITY_UNAVAILABLE', 'CANCELLED', 'UNSUPPORTED_METHOD', 'KEY_ALREADY_EXISTS', 'KEY_OR_HARDWARE_UNAVAILABLE', 'KEY_OR_ENCRYPTION_UNAVAILABLE', 'STRONG_BIOMETRICS_REQUIRED', 'ENROLLMENT_BUSY', 'ENROLLMENT_LOCK_UNAVAILABLE', 'HARDWARE_POLICY_MISMATCH', 'KEY_MISSING', 'AUTHENTICATION_OR_INTEGRITY_FAILED', 'INVALID_DOCUMENT_OR_KEY_UNAVAILABLE', 'BIOMETRIC_CANCELLED_OR_UNAVAILABLE', 'BIOMETRIC_CANCELLED', 'BIOMETRIC_UNAVAILABLE', 'PICKER_UNAVAILABLE', 'INVALID_DOCUMENT_SOURCE', 'DOCUMENT_IMPORT_FAILED', 'DOCUMENT_ALREADY_EXISTS_USE_NEW_UUID', 'ENCRYPTED_STORAGE_FAILED', 'INVALID_ENCRYPTED_FILE', 'ENCRYPTED_FILE_TOO_LARGE', 'PRIVATE_STORAGE_UNAVAILABLE', 'STORAGE_UNAVAILABLE', 'NATIVE_OPERATION_FAILED','CLIENT_INTEGRITY_BLOCKED'])

class VaultError(RuntimeError):
    pass

def canonical(value):
    if isinstance(value,UUID):return str(value)
    if not isinstance(value,str):raise ValueError('A canonical UUID is required')
    parsed=str(UUID(value))
    if value!=parsed:raise ValueError('A lowercase canonical UUID is required')
    return parsed

@dataclass(frozen=True)
class DocumentScope:
    tenant: str
    account: str
    version: int=1
    hardware: str='STRONGBOX_REQUIRED'
    def __post_init__(self):
        object.__setattr__(self,'tenant',canonical(self.tenant))
        object.__setattr__(self,'account',canonical(self.account))
        if type(self.version) is not int or not 1<=self.version<=2147483647:raise ValueError('Invalid key version')
        if self.hardware not in {'STRONGBOX_REQUIRED','TRUSTED_HARDWARE'}:raise ValueError('Unsupported hardware policy')

class DocumentVault(Control):
    """Nonvisual native control; mount in page.overlay in a packaged Flet 0.28 app.

    Unsupported clients fail closed. No file path, byte/base64 argument, upload,
    key export, key deletion or transaction-approval method is exposed.
    """
    def __init__(self,scope:DocumentScope):
        super().__init__()
        if not isinstance(scope,DocumentScope):raise TypeError('DocumentScope required')
        self.__scope=scope
        self.__busy=False
    def _get_control_name(self):return 'sgacdvault'

    async def _request(self,method,document_id=None):
        if method not in {'provision','import_document','verify_document','list_documents'}:raise VaultError('UNSUPPORTED_METHOD')
        if self.__busy:raise VaultError('BUSY')
        scope=self.__scope
        args={'tenant':scope.tenant,'account':scope.account,'version':str(scope.version),'hardware':scope.hardware,'request_id':str(uuid4())}
        if document_id is not None:args['document_id']=canonical(document_id)
        self.__busy=True
        try:
            try:
                raw=await self.invoke_method_async(method,args,wait_for_result=True,wait_timeout=180)
            except asyncio.CancelledError:raise
            except Exception:raise VaultError('NATIVE_UNAVAILABLE') from None
            if not isinstance(raw,str) or len(raw)>8192:raise VaultError('INVALID_NATIVE_RESPONSE')
            try:reply=json.loads(raw)
            except (ValueError,TypeError):raise VaultError('INVALID_NATIVE_RESPONSE') from None
            if not isinstance(reply,dict):raise VaultError('INVALID_NATIVE_RESPONSE')
            if reply.get('ok') is not True:
                code=reply.get('code','NATIVE_UNAVAILABLE')
                raise VaultError(code if isinstance(code,str) and code in SAFE_CODES else 'NATIVE_UNAVAILABLE')
            expected={'provision':'provisioned','import_document':'stored','verify_document':'verified','list_documents':'listed'}[method]
            allowed={'ok','protocol','status','document_id','documents','has_more'}
            if set(reply)-allowed or type(reply.get('protocol')) is not int or reply['protocol']!=1 or reply.get('status')!=expected:raise VaultError('INVALID_NATIVE_RESPONSE')
            if method in {'import_document','verify_document'}:
                try:canonical(reply.get('document_id'))
                except (ValueError,TypeError):raise VaultError('INVALID_NATIVE_RESPONSE') from None
                if document_id is not None and reply['document_id']!=canonical(document_id):raise VaultError('SCOPE_MISMATCH')
            if method=='list_documents':
                docs=reply.get('documents')
                if not isinstance(docs,list) or len(docs)>64 or type(reply.get('has_more')) is not bool:raise VaultError('INVALID_NATIVE_RESPONSE')
                try:
                    for document in docs:canonical(document)
                except (ValueError,TypeError):raise VaultError('INVALID_NATIVE_RESPONSE') from None
            return reply
        finally:self.__busy=False

    async def provision(self,*,confirm_new_key=False):
        if confirm_new_key is not True:raise VaultError('EXPLICIT_ENROLLMENT_REQUIRED')
        return await self._request('provision')
    async def import_document(self):return await self._request('import_document')
    async def verify_document(self,document_id):return await self._request('verify_document',document_id)
    async def list_documents(self):return await self._request('list_documents')


class SensitiveDisplay(Control):
    """Screen-only protection. No financial identity, key or authentication claim."""
    def _get_control_name(self):return 'sgacdsensitivedisplay'
    async def protect(self):
        try:raw=await self.invoke_method_async('protect_display',{},wait_for_result=True,wait_timeout=15)
        except Exception:raise VaultError('SENSITIVE_DISPLAY_UNAVAILABLE') from None
        if not isinstance(raw,str) or len(raw)>512:raise VaultError('SENSITIVE_DISPLAY_UNAVAILABLE')
        try:reply=json.loads(raw)
        except (TypeError,ValueError):raise VaultError('SENSITIVE_DISPLAY_UNAVAILABLE') from None
        if not isinstance(reply,dict) or set(reply)!={'ok','protocol','status'} or reply.get('ok')is not True or type(reply.get('protocol'))is not int or reply.get('protocol')!=1 or reply.get('status')!='protected':raise VaultError('SENSITIVE_DISPLAY_UNAVAILABLE')
        return True
