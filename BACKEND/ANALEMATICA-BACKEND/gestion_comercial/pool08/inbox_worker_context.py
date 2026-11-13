from contextlib import contextmanager
from types import SimpleNamespace
from django.http import QueryDict
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from .inbox_models import InboxRecord
from .crm_api import CRMView
from .crm import CRMError

def candidates():
    rows=[(r.id,r.document) for r in InboxRecord.objects.filter(status='QUEUED').order_by('pk')[:501]]
    if len(rows)>500:raise CRMError('INBOX_GLOBAL_QUEUE_REVIEW_REQUIRED',503)
    return rows
@contextmanager
def context(document):
    close_old_connections()
    try:
        actor=document.get('creator_ref') if isinstance(document,dict) else None
        if not str(actor).isdigit():raise CRMError('GENERATION_ACTOR_REQUIRED',403)
        user=get_user_model().objects.filter(pk=int(actor),is_active=True,is_agent=False).first()
        if not user:raise CRMError('GENERATION_ACTOR_REQUIRED',403)
        # Provider is scoped by the signed job record, not inferred from equal IDs in another system.
        provider=document.get('provider_ref')
        query=QueryDict(mutable=True);query['provider_id']=provider or ''
        yield CRMView().service(SimpleNamespace(method='POST',query_params=query,user=user))
    finally:close_old_connections()
