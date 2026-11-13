"""Permission vocabulary only. Local roles remain owned by each system."""
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from uuid import UUID

NON_DELEGABLE = {'ledger.sale.post', 'vault.document.persist', 'agents.process.optimize'}
CHANNELS = {'EMAIL','SMS','MMS','WHATSAPP','META_DM','PUBLIC_COMMENT','YOUTUBE_COMMENT','TIKTOK_DM'}
PURPOSES = {'SERVICE_FULFILMENT','MARKETING','CROSS_SYSTEM_ATTRIBUTION'}
SYSTEMS = {'sga-cd','erp-tur','analematica'}
class AccessFault(ValueError):
    def __init__(self, code, status=422):
        self.code=code;self.status=status;super().__init__(code)

def canonical(value):
    def encode(item):
        if isinstance(item,datetime):
            return utc(item).isoformat()
        raise TypeError('Unsupported policy value')
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False,default=encode)

def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def utc(value):return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
def now():return datetime.now(timezone.utc)
def identifier(value):
    if not isinstance(value,str):raise AccessFault('INVALID_REFERENCE')
    try:valid=str(UUID(value))
    except (ValueError,TypeError):raise AccessFault('INVALID_REFERENCE') from None
    if valid!=value:raise AccessFault('INVALID_REFERENCE')
    return value

def reference(value,max_length=96):
    if not isinstance(value,str) or not 1<=len(value)<=max_length or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]*',value):raise AccessFault('INVALID_REFERENCE')
    return value

def person(value):
    reference(value,80)
    if not value.isdecimal() or str(int(value))!=value or not 0<int(value)<2**63:raise AccessFault('INVALID_MEMBER')
    return value

def revision(value):
    if type(value) is not int or not 0<=value<2**31:raise AccessFault('INVALID_REVISION')
    return value

def expiry(value):
    if not isinstance(value,str) or len(value)>40:raise AccessFault('INVALID_EXPIRY')
    try:result=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError:raise AccessFault('INVALID_EXPIRY') from None
    current=now()
    if result.tzinfo is None or not current<result<=current+timedelta(days=30):raise AccessFault('INVALID_EXPIRY')
    return result

def evidence(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise AccessFault('INVALID_EVIDENCE_DIGEST')
    return value

def fields(body,expected):
    if not isinstance(body,dict) or set(body)!=set(expected):raise AccessFault('INVALID_FIELDS')
    return body

def verify(row):
    if row and digest({key:value for key,value in row.items() if key!='digest'})!=row['digest']:
        raise AccessFault('POLICY_INTEGRITY_REVIEW_REQUIRED',503)
    return row

def seal(row):
    row['digest']=digest({key:value for key,value in row.items() if key!='digest'});return row
