"""Own transactional guard for exact duplicate internal after-sales followups.
No beneficiary identity, marketing consent, reward or refund is inferred here.
"""
from contextlib import contextmanager
from copy import copy
from .crm import CRMError, text, moment
from .opportunities import uuid_ref


def record_followup(crm, data):
    if not isinstance(data, dict) or set(data) != {'request_id','contact_id','expected_revision','reservation_id','title','due_at','responsible_ref'}:
        raise CRMError('INVALID_AFTER_SALES_FIELDS')
    request_id=uuid_ref(data['request_id']);reservation=uuid_ref(data['reservation_id'])
    contact=data['contact_id'];revision=data['expected_revision']
    if not isinstance(contact,str) or not 1<=len(contact)<=96:raise CRMError('INVALID_CONTACT_ID')
    if type(revision)!=int or not 0<=revision<2**31:raise CRMError('INVALID_COMMAND')
    title='Posventa '+reservation+': '+text(data['title'],100)
    due=moment(data['due_at']).isoformat();responsible=text(data['responsible_ref'],96)
    body={'request_id':request_id,'operation':'task','contact_id':contact,'expected_revision':revision,
          'data':{'title':title,'due_at':data['due_at'],'responsible_ref':responsible}}
    with crm.store.transaction():
        crm.authorize();crm.store.lock()
        @contextmanager
        def join():yield
        child=copy(crm);child.store=copy(crm.store);child.store.transaction=join
        # Existing IDs retain the canonical CRM fingerprint/replay checks.
        if crm.store.event(request_id):return child.command(body)
        current=crm.get(contact)
        for task in current['tasks']:
            if task['title']==title and task['due_at']==due and task['responsible_ref']==responsible:
                raise CRMError('FOLLOWUP_ALREADY_RECORDED',409)
        return child.command(body)
