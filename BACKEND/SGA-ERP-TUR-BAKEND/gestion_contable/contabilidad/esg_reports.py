"""Scoped draft ESG mapping over verified event chains, never certification.

Framework applicability and support authenticity remain a professional decision.
Only explicit mappings are emitted; incompatible boundaries are never summed.
"""
from decimal import Decimal, localcontext, Context
from django.db import transaction
from django.utils import timezone
from apps.core_erp.accounting.environmental import _date, _code
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.outbox_models import OutboxEvent
from .tourism_metrics import _context
from . import environmental_records as records, environmental_corrections as corrections


@transaction.atomic
def report(*, actor, provider_id, since, until, mappings):
    _, provider, company = _context(actor, provider_id)
    start, end = _date(since), _date(until)
    if start > end or end>timezone.localdate() or (end-start).days > 366 or not isinstance(mappings, list) or not 1 <= len(mappings) <= 20:
        raise AccountingError('Bounded period and explicit framework mappings required.')
    catalog = {}; mapped_boundaries = set()
    for mapping in mappings:
        if not isinstance(mapping, dict) or set(mapping) != {'framework','version','disclosure','boundary','applicability_reason','evidence_digest'}:
            raise AccountingError('Exact applicability mapping required.')
        if not isinstance(mapping['framework'],str) or mapping['framework'] not in {'GRI','SASB'}:
            raise AccountingError('Explicit GRI or SASB mapping required.')
        _code(mapping['version']); _code(mapping['disclosure'])
        from apps.core_erp.accounting.environmental import BOUNDARIES
        from apps.core_erp.accounting.bank_reconciliation import digest
        digest(mapping['evidence_digest'])
        if not isinstance(mapping['boundary'],str) or mapping['boundary'] not in BOUNDARIES or not isinstance(mapping['applicability_reason'], str) or not 1 <= len(mapping['applicability_reason'].strip()) <= 500:
            raise AccountingError('Applicable boundary and reviewed rationale required.')
        key = (mapping['framework'], mapping['version'], mapping['disclosure'])
        if key in catalog or (mapping['framework'], mapping['boundary']) in mapped_boundaries:
            raise AccountingError('Duplicate disclosure or repeated framework boundary.')
        catalog[key] = mapping; mapped_boundaries.add((mapping['framework'], mapping['boundary']))
    roots = list(OutboxEvent.objects.filter(event_type=records.RECORDED,
        payload__company_id=str(company.pk), payload__provider_id=str(provider.pk)).order_by('pk')[:201])
    if len(roots) > 200:
        raise AccountingError('Report exceeds bounded source history; reviewed export required.')
    sources = []; seen = set(); totals = {}
    with localcontext(Context(prec=60)) as ctx:
        ctx.prec = 60
        for root in roots:
            head = corrections._chain(company, provider, root.pk)
            review, body = records._review(company, provider, root.payload['review_id'])
            for item in head['effective_assessment']['items']:
                if not since <= item['date'] <= until: continue
                if item['id'] in seen: raise AccountingError('Repeated observed activity in report.')
                seen.add(item['id'])
                value = Decimal(item['kg_co2e']); boundary = item['boundary']
                totals[boundary] = totals.get(boundary, Decimal(0)) + value
                evidence = body['evidence_digest']
                if head['history']:
                    last = OutboxEvent.objects.get(pk=head['history'][-1]['review_id'])
                    evidence = last.payload['review']['evidence_digest']
                sources.append({'observation_id':str(root.pk), 'activity_id':item['id'],
                    'date':item['date'], 'revision':head['revision'], 'head_digest':head['head_digest'],
                    'boundary':boundary, 'kg_co2e':format(value,'f'), 'factor_source_digest':item['source_digest'],
                    'activity_support_digest':evidence})
        disclosures = [{**m, 'unit':'kg_co2e', 'value':format(totals.get(m['boundary'], Decimal(0)),'.6f'),
            'source_activity_ids':[s['activity_id'] for s in sources if s['boundary']==m['boundary']],
            'data_available':m['boundary'] in totals} for m in catalog.values()]
    result = {'schema':'sgacd-esg-draft-v1','company_id':str(company.pk),'since':since,'until':until,
        'disclosures':disclosures,'sources':sources,'unmapped_boundaries':sorted(set(totals)-{m['boundary'] for m in catalog.values()}),
        'evidence_chain_verified':True,'supports_independently_verified':False,'applicability_independently_verified':False,
        'esg_certified':False,'status':'DRAFT_REQUIRES_PROFESSIONAL_REVIEW','read_only':True,
        'ledger_written':False,'money_transferred':False}
    return {**result,'report_digest':fingerprint(result)}
