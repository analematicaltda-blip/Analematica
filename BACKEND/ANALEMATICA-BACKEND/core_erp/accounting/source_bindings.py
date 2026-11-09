"""Internal source reservations prevent generic endpoints bypassing native reviews."""
from contextvars import ContextVar
from contextlib import contextmanager
from uuid import UUID,uuid5
import re
from .exceptions import AccountingError
from .integrity import fingerprint
from apps.core_erp.outbox_models import OutboxEvent
NS=UUID('130c15b1-3bd3-4914-84ca-e001a19f6509')
RESERVED='accounting.native-source.reserved.v1'
_SCOPE=ContextVar('accounting_native_source_scope',default=None)

def identity(value):
    if not isinstance(value,dict) or set(value)!={'kind','provider_id','invoice_id'} or value['kind']!='ERP_PURCHASE' or type(value['invoice_id']) is not int or value['invoice_id']<1 or not isinstance(value['provider_id'],str) or str(UUID(value['provider_id']))!=value['provider_id']:raise AccountingError('Explicit supported native source identity required.')
    return value

def binding(value):
    if not isinstance(value,dict) or set(value)!={'identity','snapshot_digest'} or not isinstance(value['snapshot_digest'],str) or not re.fullmatch('[0-9a-f]{64}',value['snapshot_digest']):raise AccountingError('Native source snapshot required.')
    identity(value['identity']);return value

def reserved_id(company,document):return uuid5(NS,str(company)+':'+document)

def digest_id(company,document_digest):return uuid5(NS,'digest:'+str(company)+':'+document_digest)

def reserve(company,document,source,document_digest):
    identity(source)
    if not isinstance(document_digest,str) or not re.fullmatch('[0-9a-f]{64}',document_digest):raise AccountingError('Native document digest required.')
    body={'company_id':str(company),'document_id':document,'document_digest':document_digest,'identity':source};payload={'body':body,'digest':fingerprint(body)}
    for key in (reserved_id(company,document),digest_id(company,document_digest)):
        old=OutboxEvent.objects.filter(pk=key).first()
        if old:
            if old.event_type!=RESERVED or old.domain!='accounting' or old.version!=1 or old.aggregate_root!=str(company)+':'+document or old.payload!=payload:raise AccountingError('Native source reservation changed or document already reserved.')
        else:OutboxEvent.objects.create(id=key,event_type=RESERVED,domain='accounting',aggregate_root=str(company)+':'+document,payload=payload,version=1)

@contextmanager
def _permit(company,document,source,actor,operation):
    binding(source);token=_SCOPE.set((str(company),document,fingerprint(source),str(actor),operation))
    try:yield
    finally:_SCOPE.reset(token)

def require(company,document,source,actor,operation,document_digest):
    row=OutboxEvent.objects.filter(pk=reserved_id(company,document)).first()
    digest_row=OutboxEvent.objects.filter(pk=digest_id(company,document_digest)).first()
    if row is None:
        if source is not None or digest_row is not None:raise AccountingError('Native source reservation missing; no downgrade to a manual fact.')
        return
    if source is None:raise AccountingError('Reserved native document requires its native adapter.')
    binding(source);body={'company_id':str(company),'document_id':document,'document_digest':document_digest,'identity':source['identity']}
    if row.event_type!=RESERVED or row.domain!='accounting' or row.version!=1 or row.aggregate_root!=str(company)+':'+document or row.payload!={'body':body,'digest':fingerprint(body)}:raise AccountingError('Native source reservation changed.')
    if digest_row is None or digest_row.event_type!=row.event_type or digest_row.domain!=row.domain or digest_row.version!=row.version or digest_row.aggregate_root!=row.aggregate_root or digest_row.payload!=row.payload:raise AccountingError('Native document digest reservation missing or changed.')
    if _SCOPE.get()!=(str(company),document,fingerprint(source),str(actor),operation):raise AccountingError('Use the authenticated native source flow; generic posting cannot bypass source checks.')
