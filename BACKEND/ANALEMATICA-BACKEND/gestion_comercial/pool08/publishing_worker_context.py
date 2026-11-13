from contextlib import contextmanager
from types import SimpleNamespace
from django.http import QueryDict
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from .publishing_models import PublishingRecord
from .crm_api import CRMView
from .crm import CRMError

def candidates():
    from datetime import datetime,timezone
    from .crm import moment
    states=('SCHEDULED','READY_TO_PUBLISH','WAIT_CONTAINER','VERIFY','REMOTE_REVIEW')
    rows=[(r.id,r.document) for r in PublishingRecord.objects.filter(status__in=states).order_by('pk')[:501]]
    if len(rows)>500:raise CRMError('PUBLISH_GLOBAL_QUEUE_REVIEW_REQUIRED',503)
    now=datetime.now(timezone.utc)
    return sorted([(ref,d) for ref,d in rows if moment(d['scheduled_at'])<=now and (not d.get('next_poll_at') or moment(d['next_poll_at'])<=now)],key=lambda row:(row[1]['scheduled_at'],row[0]))
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
