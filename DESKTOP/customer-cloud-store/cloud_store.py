"""Customer-operated Drive/OneDrive adapters for opaque immutable file plans.

No ERP token, DEK, KEK, plaintext, sharing or permission-management endpoints.
Live OAuth applications, conditional-create semantics and customer ownership need
qualification with the real selected accounts; this module never certifies them.
"""
import sys,json,hashlib,re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote,urlsplit
import httpx
from oauth_client import bounded_request,OAuthError
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'BACKEND/ANALEMATICA-BACKEND'))
from core_erp.accounting.customer_package_store import inspect_package

class CloudError(ValueError):pass
class CloudConflict(CloudError):pass
class UploadOutcomeUnknown(CloudError):
    def __init__(self,plan):super().__init__('Upload outcome unknown; read this exact plan and retry identical encrypted bytes only.');self.plan=dict(plan)

@dataclass(frozen=True)
class Destination:
    provider:str
    company_id:str
    account_id:str
    root_id:str
    approved_download_hosts:tuple=()
    def checked(self):
        from uuid import UUID
        if self.provider not in {'google_drive','onedrive'} or str(UUID(self.company_id))!=self.company_id or not all(isinstance(v,str) and re.fullmatch('[A-Za-z0-9!_-]{3,200}',v) for v in [self.account_id,self.root_id]):raise CloudError('Explicit customer account/root binding required.')
        if not isinstance(self.approved_download_hosts,tuple) or any(not isinstance(host,str) or not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?",host) or "." not in host for host in self.approved_download_hosts):raise CloudError("Explicit reviewed download hosts required.")
        return self

class CloudStore:
    def __init__(self,destination,session,*,client=None):
        self.destination=destination.checked();self.session=session
        if session.provider!=destination.provider:raise CloudError('OAuth provider and destination differ.')
        self.client=client or httpx.Client(timeout=httpx.Timeout(20,connect=5),trust_env=False,follow_redirects=False);self._owns=client is None
    def close(self):
        if self._owns:self.client.close()
    def request(self,method,path,*,content=None,params=None,headers=None,maximum=1500000):
        base='https://www.googleapis.com' if self.destination.provider=='google_drive' else 'https://graph.microsoft.com'
        if not path.startswith('/') or path.startswith('//') or '?' in path or '#' in path:raise CloudError('Fixed provider path required.')
        status,raw=bounded_request(self.client,method,base+path,headers={'Authorization':self.session.bearer(),**(headers or {})},content=content,params=params,maximum=maximum)
        if status==401:self.session.forget();raise CloudError('Customer authorization revoked; no receipt acknowledged.')
        if status==403:raise CloudError('Customer permissions do not allow this operation.')
        return status,raw
    def metadata(self,path,params=None):
        status,raw=self.request('GET',path,params=params,maximum=65536)
        if status==404:return None
        if status!=200:raise CloudError('Provider metadata unavailable; no storage receipt acknowledged.')
        try:value=json.loads(raw)
        except (ValueError,UnicodeError):raise CloudError('Provider metadata incompatible.') from None
        if not isinstance(value,dict):raise CloudError('Provider metadata incompatible.')
        return value
    def verify_destination(self):
        d=self.destination
        if d.provider=='google_drive':
            account=self.metadata('/drive/v3/about',{'fields':'user(permissionId)'})
            root=self.metadata('/drive/v3/files/'+quote(d.root_id,safe=''),{'fields':'id,mimeType,ownedByMe,trashed'})
            if not account or account.get('user',{}).get('permissionId')!=d.account_id or not root or root.get('id')!=d.root_id or root.get('mimeType')!='application/vnd.google-apps.folder' or root.get('ownedByMe') is not True or root.get('trashed') is not False:raise CloudError('Customer-owned Drive folder/account not matched.')
        else:
            root=self.metadata('/v1.0/me/drive/special/approot',{'$select':'id,parentReference,folder'})
            if not root or root.get('id')!=d.root_id or root.get('parentReference',{}).get('driveId')!=d.account_id or not isinstance(root.get('folder'),dict):raise CloudError('Customer OneDrive app folder/account not matched.')
    def checked_package(self,value):
        report,raw=inspect_package(value,self.destination.company_id)
        sha=hashlib.sha256(raw).hexdigest();name='sgacd-'+report['company_id']+'-'+report['document_id']+'-r'+str(report['revision'])+'-'+sha+'.json.enc'
        return report,raw,sha,name
    def prepare(self,value):
        report,raw,sha,name=self.checked_package(value);self.verify_destination();file_id=None
        if self.destination.provider=='google_drive':
            ids=self.metadata('/drive/v3/files/generateIds',{'count':'1','space':'drive','type':'files'})
            if not ids or not isinstance(ids.get('ids'),list) or len(ids['ids'])!=1 or not isinstance(ids['ids'][0],str) or not re.fullmatch('[A-Za-z0-9_-]{10,200}',ids['ids'][0]):raise CloudError('Provider did not allocate one file identity.')
            file_id=ids['ids'][0]
        return {'schema':'sgacd-cloud-upload-plan-v1','provider':self.destination.provider,'company_id':report['company_id'],'document_id':report['document_id'],'revision':report['revision'],'package_digest':report['package_digest'],'blob_sha256':sha,'account_id':self.destination.account_id,'root_id':self.destination.root_id,'name':name,'file_id':file_id}
    def check_plan(self,value,plan):
        report,raw,sha,name=self.checked_package(value);d=self.destination
        expected={'schema':'sgacd-cloud-upload-plan-v1','provider':d.provider,'company_id':report['company_id'],'document_id':report['document_id'],'revision':report['revision'],'package_digest':report['package_digest'],'blob_sha256':sha,'account_id':d.account_id,'root_id':d.root_id,'name':name,'file_id':None}
        if d.provider=='google_drive':
            if not isinstance(plan,dict) or not isinstance(plan.get('file_id'),str) or not re.fullmatch('[A-Za-z0-9_-]{10,200}',plan['file_id']):raise CloudError('Persisted provider file identity required.')
            expected['file_id']=plan['file_id']
        if plan!=expected:raise CloudConflict('Upload plan differs from account, scope or encrypted bytes.')
        return report,raw
    def receipt(self,plan,replayed):
        return {k:plan[k] for k in ['provider','company_id','document_id','revision','package_digest','blob_sha256','file_id']}|{'schema':'sgacd-cloud-package-receipt-v1','stored':True,'replayed':replayed,'verified_by':'EXACT_ENCRYPTED_BYTES_READBACK','latest_version_verified':False,'authenticated_ciphertext_verified':False,'ownership_independently_verified':False,'fiscal_accepted':False,'ledger_written':False,'provider_live_qualified':False}
    def recover(self,value,plan):
        report,raw=self.check_plan(value,plan);self.verify_destination();d=self.destination
        if d.provider=='google_drive':
            path='/drive/v3/files/'+quote(plan['file_id'],safe='');metadata=self.metadata(path,{'fields':'id,name,mimeType,parents,appProperties,trashed,ownedByMe'})
            if metadata is None:return None
            if metadata.get('id')!=plan['file_id'] or metadata.get('name')!=plan['name'] or metadata.get('parents')!=[d.root_id] or metadata.get('ownedByMe') is not True or metadata.get('trashed') is not False or metadata.get('appProperties')!={'sgacd_blob_sha256':plan['blob_sha256'],'sgacd_company_id':d.company_id}:raise CloudConflict('Stored Drive identity or metadata conflict.')
            status,stored=self.request('GET',path,params={'alt':'media'})
        else:
            path='/v1.0/me/drive/special/approot:/'+quote(plan['name'],safe='');metadata=self.metadata(path)
            if metadata is None:return None
            if metadata.get('name')!=plan['name'] or metadata.get('parentReference',{}).get('id')!=d.root_id or metadata.get('parentReference',{}).get('driveId')!=d.account_id or not isinstance(metadata.get('file'),dict) or metadata.get('size')!=len(raw):raise CloudConflict('Stored OneDrive identity or size conflict.')
            # Preauthenticated URL stays transient; never forward the OAuth bearer.
            location=metadata.get('@microsoft.graph.downloadUrl')
            if not isinstance(location,str) or len(location)>16384:raise CloudError('Reviewed OneDrive download destination unavailable.')
            target=urlsplit(location)
            if target.scheme!='https' or target.hostname not in d.approved_download_hosts or target.username or target.password or target.port not in {None,443} or target.fragment:raise CloudError('OneDrive download host is not explicitly approved.')
            status,stored=bounded_request(self.client,'GET',location,maximum=1500000,anonymous=True)
        if status!=200:raise CloudError('Encrypted readback unavailable or redirected; no storage receipt acknowledged.')
        if stored!=raw or hashlib.sha256(stored).hexdigest()!=plan['blob_sha256']:raise CloudConflict('Encrypted stored bytes differ; never overwrite.')
        return self.receipt(plan,True)
    def put(self,value,plan,*,confirmed=False):
        if confirmed is not True:raise CloudError('Explicit client upload confirmation required.')
        report,raw=self.check_plan(value,plan);found=self.recover(value,plan)
        if found:return found
        d=self.destination
        try:
            if d.provider=='google_drive':
                boundary='sgacd'+__import__('secrets').token_hex(16)
                metadata={'id':plan['file_id'],'name':plan['name'],'parents':[d.root_id],'mimeType':'application/octet-stream','appProperties':{'sgacd_blob_sha256':plan['blob_sha256'],'sgacd_company_id':d.company_id}}
                body=('--'+boundary+'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n').encode()+json.dumps(metadata,separators=(',',':')).encode()+('\r\n--'+boundary+'\r\nContent-Type: application/octet-stream\r\n\r\n').encode()+raw+('\r\n--'+boundary+'--\r\n').encode()
                status,_=self.request('POST','/upload/drive/v3/files',params={'uploadType':'multipart','fields':'id'},content=body,headers={'Content-Type':'multipart/related; boundary='+boundary})
            else:
                status,_=self.request('PUT','/v1.0/me/drive/special/approot:/'+quote(plan['name'],safe='')+':/content',params={'@microsoft.graph.conflictBehavior':'fail'},content=raw,headers={'Content-Type':'application/octet-stream','If-None-Match':'*'})
        except httpx.HTTPError:raise UploadOutcomeUnknown(plan) from None
        if status>=500:raise UploadOutcomeUnknown(plan)
        if status not in {200,201,409,412}:raise CloudError('Provider did not confirm creation; retain the exact plan/package.')
        try:found=self.recover(value,plan)
        except (httpx.HTTPError,CloudError,OAuthError):raise UploadOutcomeUnknown(plan) from None
        if found is None:raise UploadOutcomeUnknown(plan)
        found['replayed']=status in {409,412};return found
