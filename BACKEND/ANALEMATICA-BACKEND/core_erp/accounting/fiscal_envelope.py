"""Opaque envelope shape validation only. Never receives a KEK, decrypts or stores."""
import base64,binascii,hashlib,json,re
from uuid import UUID
SCHEMA='sgacd-fiscal-envelope-v1'
ALGORITHM='AES-256-GCM+A256KW'
MAX_WIRE_BYTES=1500000
MAX_DOCUMENT_BYTES=1024*1024  # Intake preview is intentionally stricter than the browser primitive.


def reject():raise ValueError('Invalid fiscal envelope or company scope.')


def identifier(value):
    if not isinstance(value,str):reject()
    try:parsed=str(UUID(value))
    except (ValueError,TypeError,AttributeError):reject()
    if value!=parsed:reject()
    return parsed


def decode(value,minimum,maximum):
    if not isinstance(value,str) or not value or len(value)>(maximum*4+2)//3 or not re.fullmatch('[A-Za-z0-9_-]+',value):reject()
    try:data=base64.b64decode(value+'='*((4-len(value)%4)%4),altchars=b'-_',validate=True)
    except (ValueError,binascii.Error):reject()
    if not minimum<=len(data)<=maximum or base64.urlsafe_b64encode(data).rstrip(b'=').decode()!=value:reject()
    return data


def inspect_envelope(value,company_id):
    fields={'schema','algorithm','context','iv','wrapped_key','ciphertext'}
    if not isinstance(value,dict) or set(value)!=fields or value['schema']!=SCHEMA or value['algorithm']!=ALGORITHM:reject()
    context=value['context']
    if not isinstance(context,dict) or set(context)!={'company_id','document_id'}:reject()
    company=identifier(context['company_id']);document=identifier(context['document_id'])
    if company!=str(UUID(str(company_id))):reject()
    decode(value['iv'],12,12);decode(value['wrapped_key'],40,40)
    cipher=decode(value['ciphertext'],17,MAX_DOCUMENT_BYTES+16)
    digest=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
    return {'mode':'STRUCTURAL_VALIDATION_ONLY','company_id':company,'document_id':document,
            'schema':SCHEMA,'envelope_digest':digest,'ciphertext_bytes':len(cipher),
            'max_document_bytes_accepted':MAX_DOCUMENT_BYTES,'max_request_body_bytes':MAX_WIRE_BYTES,
            'authenticated_ciphertext_verified':False,'fiscal_document_validated':False,
            'stored':False,'storage_ready':False,'ledger_written':False}
