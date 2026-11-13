"""Versioned commercial price profiles; no invoicing, payments or legal certification."""
import uuid,re,copy
from datetime import datetime,timezone,timedelta
from decimal import Decimal,ROUND_HALF_UP,localcontext,Context,InvalidOperation,DivisionByZero,Overflow
from .crm import CRMError,text,moment,digest
from .opportunities import uuid_ref,money,CURRENCIES as OPPORTUNITY_CURRENCIES,FALSE_FINANCIAL
# Offer pricing currently supports currencies with two decimal minor units.
CURRENCIES=tuple(code for code in OPPORTUNITY_CURRENCIES if code!='CLP')
TREATMENTS=('TAXABLE','EXEMPT','EXCLUDED','NOT_SUBJECT')
def integer(value,low,high,code):
    if type(value)!=int or not low<=value<=high:raise CRMError(code)
    return value
def amount(value):return format(value.quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'.2f')
class Pricing:
    def __init__(self,store,crm):self.store,self.crm,self.actor=store,crm,crm.actor
    def authority(self,manage=False):
        access=self.crm.authorize()
        if not access.session()['capability_permissions'].get('quote.prepare'):raise CRMError('OFFER_PERMISSION_REQUIRED',403)
        if manage and not access.principal.get('is_manager'):raise CRMError('LOCAL_ADMINISTRATOR_REQUIRED',403)
        return access
    def get(self,ref):
        self.authority();uuid_ref(ref);item=self.store.get(ref)
        if item is None:raise CRMError('PRICE_NOT_FOUND',404)
        self.verify(item);return item
    def verify(self,item):
        event=self.store.last_event(item['id'])
        if not event or event['event_digest']!=item['last_event_digest'] or digest({k:v for k,v in event.items() if k!='event_digest'})!=event['event_digest'] or event['result_digest']!=digest({k:v for k,v in item.items() if k!='last_event_digest'}):raise CRMError('PRICE_INTEGRITY_REVIEW_REQUIRED',503)
    def list(self,q='',offset=0,limit=30):
        access=self.authority()
        if not isinstance(q,str) or len(q)>200 or type(offset)!=int or not 0<=offset<=100000 or type(limit)!=int or not 1<=limit<=100:raise CRMError('INVALID_PAGE')
        rows,more=self.store.list(q,'',offset,limit)
        for row in rows:self.verify(row)
        return {'items':rows,'next_offset':offset+limit if more else None,'context':{'tenant_ref':self.store.scope,'actor_ref':self.actor},'can_manage':bool(access.principal.get('is_manager')),'can_discount':bool(access.principal.get('is_manager')),'currencies':list(CURRENCIES),'tax_acceptance_verified':False}
    def history(self,ref,offset=0):
        initial=self.get(ref);integer(offset,0,100000,'INVALID_PAGE');events=[];previous='0'*64
        for event in self.store.events(ref):
            if event['previous_event_digest']!=previous or digest({k:v for k,v in event.items() if k!='event_digest'})!=event['event_digest']:raise CRMError('PRICE_HISTORY_REVIEW_REQUIRED',503)
            previous=event['event_digest'];events.append(event)
        final=self.store.get(ref)
        if final['revision']!=initial['revision']:raise CRMError('HISTORY_CHANGED_RETRY',409)
        if previous!=final['last_event_digest']:raise CRMError('PRICE_HISTORY_REVIEW_REQUIRED',503)
        return {'events':events[offset:offset+5],'next_offset':offset+5 if len(events)>offset+5 else None,'history_verified':True,'external_authenticity_verified':False}
    def values(self,data,prior=None):
        allowed={'code','title','kind','sector','unit_price','currency','valid_from','valid_until','max_discount_bps','terms','tax'}
        if not data or set(data)-allowed:raise CRMError('UNKNOWN_PRICE_FIELDS')
        if prior and any(k in data and data[k]!=prior[k] for k in ('kind','sector','currency')) and 'tax' not in data:raise CRMError('TAX_REVIEW_REQUIRED_FOR_CONTEXT_CHANGE')
        value=copy.deepcopy(prior or {});value.update(data)
        required=allowed
        if not required<=set(value):raise CRMError('PRICE_FIELDS_REQUIRED')
        code=text(value['code'],40)
        if not re.fullmatch(r'[A-Z0-9][A-Z0-9_.-]{0,39}',code):raise CRMError('INVALID_PRODUCT_CODE')
        if prior and code!=prior['code']:raise CRMError('IMMUTABLE_PRODUCT_CODE')
        value.update(code=code,title=text(value['title'],200),sector=text(value['sector'],100),terms=text(value['terms'],2000),unit_price=money(value['unit_price']))
        if value['kind'] not in ('PRODUCT','SERVICE') or value['currency'] not in CURRENCIES:raise CRMError('INVALID_PRICE_TYPE_OR_CURRENCY')
        start=moment(value['valid_from']);end=moment(value['valid_until'])
        if end<=start:raise CRMError('INVALID_VALIDITY')
        value.update(valid_from=start.isoformat(),valid_until=end.isoformat(),max_discount_bps=integer(value['max_discount_bps'],0,10000,'INVALID_DISCOUNT_LIMIT'))
        tax=value['tax']
        if not isinstance(tax,dict) or set(tax)!={'name','treatment','rate_bps','policy_ref','support_digest','review_reason'}:raise CRMError('INVALID_TAX_POLICY')
        if tax['treatment'] not in TREATMENTS:raise CRMError('INVALID_TAX_TREATMENT')
        rate=integer(tax['rate_bps'],0,10000,'INVALID_TAX_RATE')
        if (tax['treatment']=='TAXABLE')!=(rate>0):raise CRMError('TAX_TREATMENT_RATE_MISMATCH')
        if not isinstance(tax['support_digest'],str) or not re.fullmatch('[a-f0-9]{64}',tax['support_digest']):raise CRMError('TAX_SUPPORT_REQUIRED')
        value['tax']={**tax,'name':text(tax['name'],40),'policy_ref':text(tax['policy_ref'],200),'review_reason':text(tax['review_reason'],500)}
        value['tax_review']=copy.deepcopy(prior['tax_review']) if prior and 'tax' not in data else {'actor_ref':self.actor,'reviewed_at':datetime.now(timezone.utc).isoformat(),'status':'DECLARED_REVIEW','professional_authorization_verified':False,'external_authenticity_verified':False}
        value['price_basis']='EXCLUSIVE_OF_DECLARED_TAX';return value
    def estimate(self,data):
        access=self.authority()
        if set(data)!={'currency','lines'} or data['currency'] not in CURRENCIES or not isinstance(data['lines'],list) or not 1<=len(data['lines'])<=30:raise CRMError('INVALID_OFFER')
        now=datetime.now(timezone.utc);expiry=now+timedelta(hours=24);seen=set();lines=[];subtotal=discounts=taxes=Decimal(0)
        # Monetary calculations must not inherit process/request Decimal settings.
        with localcontext(Context(prec=50, rounding=ROUND_HALF_UP, Emin=-999999,
                                  Emax=999999, capitals=1, clamp=0, flags=[],
                                  traps=[InvalidOperation, DivisionByZero, Overflow])):
            for line in data['lines']:
                if not isinstance(line,dict) or set(line)!={'item_id','revision','quantity','discount_bps'}:raise CRMError('CLIENT_PRICE_NOT_ALLOWED')
                ref=uuid_ref(line['item_id'])
                if ref in seen:raise CRMError('DUPLICATE_OFFER_ITEM')
                seen.add(ref);item=self.get(ref);self.history(ref)
                if type(line['revision'])!=int or line['revision']!=item['revision']:raise CRMError('PRICE_REVISION_CHANGED',409)
                if item['status']!='ACTIVE' or not moment(item['valid_from'])<=now<moment(item['valid_until']):raise CRMError('PRICE_NOT_CURRENT',409)
                if item['currency']!=data['currency']:raise CRMError('MIXED_CURRENCY')
                q=line['quantity']
                if not isinstance(q,str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,5})(?:\.[0-9]{1,3})?',q) or not Decimal(0)<Decimal(q)<=100000:raise CRMError('INVALID_QUANTITY')
                bps=integer(line['discount_bps'],0,item['max_discount_bps'],'DISCOUNT_OUTSIDE_POLICY')
                if bps and not access.principal.get('is_manager'):raise CRMError('DISCOUNT_PERMISSION_REQUIRED',403)
                gross=Decimal(amount(Decimal(item['unit_price'])*Decimal(q)));discount=Decimal(amount(gross*Decimal(bps)/10000));base=gross-discount;tax=Decimal(amount(base*Decimal(item['tax']['rate_bps'])/10000))
                subtotal+=gross;discounts+=discount;taxes+=tax;expiry=min(expiry,moment(item['valid_until']))
                lines.append({'item_id':ref,'revision':item['revision'],'code':item['code'],'title':item['title'],'kind':item['kind'],'sector':item['sector'],'unit_price':item['unit_price'],'quantity':q,'discount_bps':bps,'gross':amount(gross),'discount':amount(discount),'base':amount(base),'tax':amount(tax),'total':amount(base+tax),'tax_policy':item['tax'],'tax_review':item['tax_review'],'terms':item['terms'],'catalog_event_digest':item['last_event_digest']})
            total=subtotal-discounts+taxes
            if total>Decimal('999999999999999999.99'):raise CRMError('OFFER_VALUE_LIMIT')
            return {'currency':data['currency'],'lines':lines,'subtotal':amount(subtotal),'discount':amount(discounts),'tax':amount(taxes),'total':amount(total),'rounding':'HALF_UP_PER_LINE_2_DECIMALS','calculated_at':now.isoformat(),'expires_at':expiry.isoformat(),'price_source':'OWNED_SERVER_CATALOG','tax_acceptance_verified':False,'status':'COMMERCIAL_ESTIMATE_NOT_FISCAL_DOCUMENT',**FALSE_FINANCIAL}
    def receipt(self,rid):
        self.authority();uuid_ref(rid);event=self.store.event(rid)
        if not event or event['scope']!=self.store.scope or event['actor']!=self.actor:raise CRMError('PRICE_RECEIPT_NOT_FOUND',404)
        if digest({k:v for k,v in event.items() if k!='event_digest'})!=event['event_digest']:raise CRMError('PRICE_INTEGRITY_REVIEW_REQUIRED',503)
        return {**event['receipt'],'previous_receipt_only':True}
    def command(self,body):
        self.authority()
        if not isinstance(body,dict) or set(body)!={'request_id','operation','item_id','expected_revision','data'} or not isinstance(body['data'],dict):raise CRMError('INVALID_COMMAND')
        rid=uuid_ref(body['request_id']);operation=body['operation'];ref=body['item_id'];revision=integer(body['expected_revision'],0,2**31-1,'INVALID_REVISION');data=body['data'];signature=digest({'domain':'PRICE','scope':self.store.scope,'actor':self.actor,'body':body})
        with self.store.transaction():
            self.authority();self.store.lock();prior=self.store.event(rid)
            if prior:
                if prior['fingerprint']!=signature:raise CRMError('REQUEST_CONFLICT',409)
                return self.receipt(rid)|{'replayed':True}
            previous='0'*64
            if operation=='estimate':
                if ref is not None or revision:raise CRMError('INVALID_COMMAND')
                receipt={'request_id':rid,'estimate':self.estimate(data),'replayed':False};result=digest(receipt);ref=None
            else:
                self.authority(manage=True)
                if operation=='create':
                    if ref is not None or revision:raise CRMError('INVALID_COMMAND')
                    item=self.values(data)
                    if self.store.find_code(item['code']):raise CRMError('PRODUCT_CODE_EXISTS',409)
                    ref=str(uuid.uuid4());item.update(id=ref,revision=1,status='ACTIVE')
                else:
                    item=self.get(ref)
                    if item['revision']!=revision:raise CRMError('REVISION_CONFLICT',409)
                    self.history(ref);previous=item['last_event_digest'];item=copy.deepcopy(item)
                    if operation=='update':item=self.values(data,item)
                    elif operation in ('deactivate','activate'):
                        if set(data)!={'reason'}:raise CRMError('REASON_REQUIRED')
                        text(data['reason'],500);item['status']='ACTIVE' if operation=='activate' else 'INACTIVE'
                    else:raise CRMError('UNKNOWN_OPERATION')
                    item['revision']=revision+1
                item['updated_at']=datetime.now(timezone.utc).isoformat();result=digest({k:v for k,v in item.items() if k!='last_event_digest'});receipt={'request_id':rid,'item_id':ref,'revision':item['revision'],'replayed':False,**FALSE_FINANCIAL}
            event={'id':rid,'scope':self.store.scope,'actor':self.actor,'item_id':ref,'operation':operation,'fingerprint':signature,'previous_event_digest':previous,'result_digest':result,'created_at':datetime.now(timezone.utc).isoformat(),'receipt':receipt,'data':data}
            event['event_digest']=digest(event)
            if operation!='estimate':item['last_event_digest']=event['event_digest'];self.store.save(item,revision)
            self.store.append(event)
        return receipt
