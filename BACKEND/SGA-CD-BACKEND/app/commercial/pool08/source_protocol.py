"""Fixed server-to-server source proof; it never carries a credential or a private key."""
import os,hmac,hashlib,re
from datetime import datetime,timezone,timedelta
from .crm import CRMError,digest,moment

def secret():
    value=os.environ.get('COMMERCIAL_SALES_SOURCE_KEY','')
    if len(value)<32:raise CRMError('SALE_SOURCE_KEY_REQUIRED',503)
    return value.encode()
def mac(value):return hmac.new(secret(),digest(value).encode(),hashlib.sha256).hexdigest()
def wrap(context,body):
    value={'schema':'commercial-sale-source-v1','context':context,'body':body};return {**value,'signature':mac(value)}
def verify(value):
    if not isinstance(value,dict) or set(value)!={'schema','context','body','signature'} or value['schema']!='commercial-sale-source-v1':raise CRMError('INVALID_SALE_SOURCE')
    signature=value['signature'];unsigned={k:v for k,v in value.items() if k!='signature'}
    if not isinstance(signature,str) or not re.fullmatch('[a-f0-9]{64}',signature) or not hmac.compare_digest(signature,mac(unsigned)):raise CRMError('SALE_SOURCE_DENIED',403)
    ctx=value['context']
    if not isinstance(ctx,dict) or set(ctx)!={'system','scope','actor','role_fingerprint','issued_at'} or ctx['system']!='sga-cd' or not isinstance(ctx['scope'],str) or not re.fullmatch(r'(?:platform|tenant:[1-9][0-9]{0,18})',ctx['scope']) or not isinstance(ctx['actor'],str) or not re.fullmatch('[1-9][0-9]{0,18}',ctx['actor']) or not isinstance(ctx['role_fingerprint'],str) or not re.fullmatch('[a-f0-9]{64}',ctx['role_fingerprint']):raise CRMError('INVALID_SALE_SOURCE')
    if abs((datetime.now(timezone.utc)-moment(ctx['issued_at'])).total_seconds())>120:raise CRMError('SALE_SOURCE_EXPIRED',409)
    return ctx,value['body']
def acknowledge(context,body):return wrap(context,body)
