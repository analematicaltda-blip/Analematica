"""Bounded Bold link transport. A checkout link is never evidence of payment.
No automatic retry after a request can have reached the provider. Webhook
qualification remains explicit: a checkout integrity hash is not its signature.
"""
import hashlib,json,os,re,urllib.request,urllib.error
from decimal import Decimal,InvalidOperation
from urllib.parse import urlsplit

class GatewayError(ValueError):
    def __init__(self,code,uncertain=False):super().__init__(code);self.uncertain=uncertain

def amount(value):
    if type(value) not in (int,str,Decimal):raise GatewayError('INVALID_PAYMENT_AMOUNT')
    raw=str(value)
    if not re.fullmatch(r'(?:0|[1-9][0-9]{0,14})(?:\.[0-9]{1,2})?',raw):raise GatewayError('INVALID_PAYMENT_AMOUNT')
    n=Decimal(raw)
    if not 0<n<=Decimal('999999999999.99'):raise GatewayError('INVALID_PAYMENT_AMOUNT')
    return format(n,'.2f')

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise GatewayError('BOLD_REDIRECT_REJECTED',True)

class BoldGateway:
    endpoint='https://integrations.api.bold.co/online/link/v1'
    def __init__(self,identity_key='',secret_key='',sender=None):
        self.identity_key,self.secret_key,self.sender=identity_key,secret_key,sender
    def integrity(self,reference,total,currency):
        if not self.secret_key:raise GatewayError('BOLD_CREDENTIALS_REQUIRED')
        total=amount(total)
        if currency!='COP' or not isinstance(reference,str) or not re.fullmatch('[A-Za-z0-9_-]{1,100}',reference):raise GatewayError('INVALID_PAYMENT_REFERENCE_OR_CURRENCY')
        canonical=total[:-3] if total.endswith('.00') else total.rstrip('0')
        return hashlib.sha256((reference+canonical+currency+self.secret_key).encode()).hexdigest()
    def send(self,payload):
        req=urllib.request.Request(self.endpoint,data=json.dumps(payload,separators=(',',':')).encode(),headers={'Authorization':'x-api-key '+self.identity_key,'Content-Type':'application/json','Accept':'application/json'},method='POST')
        try:
            with urllib.request.build_opener(NoRedirect()).open(req,timeout=10) as response:
                raw=response.read(65537)
                if len(raw)>65536:raise GatewayError('BOLD_RESPONSE_LIMIT',True)
                return json.loads(raw)
        except urllib.error.HTTPError as e:raise GatewayError('BOLD_HTTP_ERROR',True) from None
        except (OSError,ValueError):raise GatewayError('BOLD_RESULT_UNCERTAIN',True) from None
    def create(self,reference,total,currency,description):
        total=amount(total)
        if not self.identity_key or not self.secret_key:raise GatewayError('BOLD_CREDENTIALS_REQUIRED')
        self.integrity(reference,total,currency)
        # Existing link contract uses integer pesos. Reject fractions instead of
        # silently truncating; no unqualified JSON decimal encoding is invented.
        if not total.endswith('.00'):raise GatewayError('BOLD_FRACTIONAL_AMOUNT_REQUIRES_CONTRACT')
        if not isinstance(description,str) or not 1<=len(description)<=500:raise GatewayError('INVALID_PAYMENT_DESCRIPTION')
        body={'amount_type':'CLOSE','amount':{'total':int(Decimal(total)),'currency':currency},'description':description[:90],'reference':reference}
        try:result=(self.sender or self.send)(body)
        except GatewayError:raise
        except Exception:raise GatewayError('BOLD_RESULT_UNCERTAIN',True) from None
        p=result.get('payload') if isinstance(result,dict) else None
        if not isinstance(p,dict) or not isinstance(p.get('id'),str) or not re.fullmatch('[A-Za-z0-9_-]{1,128}',p['id']) or not isinstance(p.get('url'),str):raise GatewayError('BOLD_INVALID_LINK_RESPONSE',True)
        try:url=urlsplit(p['url']);port=url.port
        except ValueError:raise GatewayError('BOLD_INVALID_CHECKOUT_ORIGIN',True) from None
        if url.scheme!='https' or url.hostname!='checkout.bold.co' or url.username or url.password or port not in (None,443) or not url.path or len(p['url'])>2048:raise GatewayError('BOLD_INVALID_CHECKOUT_ORIGIN',True)
        if 'reference' in p and p['reference']!=reference:raise GatewayError('BOLD_REFERENCE_MISMATCH',True)
        return {'checkout_url':p['url'],'provider_link_id':p['id'],'reference':reference,'amount':total,'currency':currency,'payment_verified':False,'money_transferred':False}
    def verify_webhook(self,raw,signature):
        # No authenticated Bold contract/receipt has been recovered in this
        # environment. Never substitute the SDK checkout hash or parsed JSON.
        raise GatewayError('BOLD_WEBHOOK_QUALIFICATION_REQUIRED')
