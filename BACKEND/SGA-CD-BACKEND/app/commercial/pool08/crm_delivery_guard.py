"""CRM can only restrict existing delivery authority; it never grants permission to send."""
import re
from datetime import datetime,timezone
from sqlalchemy import inspect
from fastapi import HTTPException
from .crm_models import CRMContact
from .crm import moment

def require_not_suppressed(db,scope,provider,address):
    channel={'gmail':'EMAIL','whatsapp':'WHATSAPP'}.get(provider)
    if channel is None:return
    if not inspect(db.get_bind()).has_table(CRMContact.__tablename__):return
    normalized=address.strip().casefold() if channel=='EMAIL' else re.sub(r'[ ()-]','',address)
    for row in db.query(CRMContact).filter_by(scope=scope).yield_per(100):
        item=row.document
        candidate=item['email'] if channel=='EMAIL' else item['phone']
        if not candidate or normalized!=candidate:continue
        consent=item['consents'].get(channel+':MARKETING')
        if item['status']=='WITHDRAWN' or (consent and (not consent['granted'] or moment(consent['expires_at'])<=datetime.now(timezone.utc))):
            raise HTTPException(409,'El CRM registra baja, revocación o vencimiento para este destinatario y canal.')
