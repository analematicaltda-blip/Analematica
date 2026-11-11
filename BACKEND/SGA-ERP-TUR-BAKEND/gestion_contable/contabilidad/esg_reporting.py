"""Bounded, reproducible emissions evidence report. No certification or scope inference."""
from datetime import datetime,timezone as dtz
from decimal import Decimal,localcontext,Context,ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone
from apps.core_erp.accounting.environmental import _date,_code,BOUNDARIES
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import canonical
import hashlib
from apps.core_erp.outbox_models import OutboxEvent
from . import environmental_records as records,environmental_corrections as corrections

def mapping(value):
    if not isinstance(value,dict) or set(value)-BOUNDARIES:raise AccountingError('Explicit boundary mapping required.')
    for row in value.values():
        if not isinstance(row,dict) or set(row)!={'framework','version','reference','evidence_digest'} or not isinstance(row['framework'],str) or row['framework'] not in {'GRI','SASB','CUSTOM'}:raise AccountingError('Declared framework/version/reference required.')
        _code(row['version']);_code(row['reference'])
        import re
        if not isinstance(row['evidence_digest'],str) or not re.fullmatch('[a-f0-9]{64}',row['evidence_digest']):raise AccountingError('Mapping evidence digest required.')
    return value

@transaction.atomic
def report(*,actor,provider_id,since,until,as_of,mappings):
    _,provider,company=records._context(actor,provider_id);start,end=_date(since),_date(until);mapping(mappings)
    if end<start or (end-start).days>366 or end>timezone.localdate():raise AccountingError('Past/current economic window of at most367 days required.')
    if not isinstance(as_of,str) or len(as_of)>40:raise AccountingError('Explicit knowledge cutoff required.')
    cutoff=datetime.fromisoformat(as_of)
    if cutoff.tzinfo is None or cutoff.utcoffset().total_seconds()!=0 or cutoff>timezone.now():raise AccountingError('UTC nonfuture knowledge cutoff required.')
    roots=list(OutboxEvent.objects.filter(event_type=records.RECORDED,payload__company_id=str(company.pk),payload__provider_id=str(provider.pk)).order_by('pk')[:201])
    if len(roots)>200:raise AccountingError('Company history exceeds200 observations; reviewed snapshots required.')
    items=[];seen=set();totals={}
    with localcontext(Context(prec=60)) as ctx:
        ctx.prec=60
        for root in roots:
            if root.domain!='accounting' or root.version!=1 or root.aggregate_root!=str(provider.pk):raise AccountingError('Observation envelope changed.')
            head=corrections._chain(company,provider,root.pk)
            if root.created_at>cutoff:continue
            original_review,original_body=records._review(company,provider,root.payload['review_id']);support=original_body['evidence_digest']
            assessment=head['original_assessment'];revision=0;proof_digest=root.payload['record_digest'];known=root.created_at
            for change in head['history']:
                if datetime.fromisoformat(change['known_at'])<=cutoff:
                    review=OutboxEvent.objects.get(pk=change['review_id']);assessment=review.payload['review']['assessment'];support=review.payload['review']['evidence_digest'];revision=change['revision'];proof_digest=change['correction_digest'];known=datetime.fromisoformat(change['known_at'])
            factors={r['id']:r for r in assessment['snapshot']['factors']}
            for row in assessment['items']:
                if not since<=row['date']<=until:continue
                if row['id'] in seen:raise AccountingError('Duplicate effective activity; no double counting permitted.')
                if len(items)>=200:raise AccountingError('Report exceeds200 activities; narrow the economic period.')
                seen.add(row['id']);factor=factors[row['factor_id']];amount=Decimal(row['quantity'])*Decimal(factor['kg_co2e_per_unit']);boundary=row['boundary'];totals[boundary]=totals.get(boundary,Decimal(0))+amount
                items.append({'observation_id':str(root.pk),'activity_id':row['id'],'date':row['date'],'quantity':row['quantity'],'activity_unit':row['unit'],'factor_id':factor['id'],'factor_version':factor['version'],'factor_rate':factor['kg_co2e_per_unit'],'factor_source_digest':factor['source_digest'],'boundary':boundary,'kg_co2e':format(amount,'f'),'revision':revision,'known_at':known.isoformat(),'proof_digest':proof_digest,'framework_mapping':mappings.get(boundary),'activity_support_digest':support,**({k:row[k] for k in ['source_reference','source_segment']} if 'source_reference' in row else {})})
        totals={k:format(v.quantize(Decimal('0.000001'),rounding=ROUND_HALF_UP),'f') for k,v in sorted(totals.items())}
    items.sort(key=lambda r:(r['date'],r['activity_id']))
    body={'schema':'sgacd-esg-evidence-report-v1','company_id':str(company.pk),'provider_id':str(provider.pk),'since':since,'until':until,'as_of':as_of,'mappings':mappings,'items':items,'totals_by_boundary':totals,'activity_count':len(items),'unmapped_count':sum(r['framework_mapping'] is None for r in items),'unit':'kg_co2e','read_only':True,'ledger_written':False,'money_transferred':False,'liability_recognized':False,'carbon_credit_issued':False,'esg_certified':False,'framework_applicability_verified':False,'sources_independently_verified':False,'confirmations_restored':False}
    encoded=canonical(body).encode()
    if len(encoded)>524288:raise AccountingError('Report exceeds512KiB; narrow scope.')
    return {**body,'report_digest':hashlib.sha256(encoded).hexdigest()}
