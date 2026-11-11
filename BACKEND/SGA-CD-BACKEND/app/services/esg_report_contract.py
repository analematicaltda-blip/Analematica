"""Never allow the bridge to turn an evidence report into a certificate."""
import json,hashlib,re
from datetime import date,datetime
from decimal import Decimal,localcontext,Context,ROUND_HALF_UP
from uuid import UUID
BOUNDARIES={'direct_combustion','electricity_location_based','lifecycle'}
FLAGS={'ledger_written','money_transferred','liability_recognized','carbon_credit_issued','esg_certified','framework_applicability_verified','sources_independently_verified','confirmations_restored'}
def identifier(v):
    if not isinstance(v,str) or str(UUID(v))!=v:raise ValueError('Canonical identifier required.')
def digest(v):
    if not isinstance(v,str) or not re.fullmatch('[a-f0-9]{64}',v):raise ValueError('Digest required.')
def validate(data,payload,context):
    fields={'schema','company_id','provider_id','since','until','as_of','mappings','items','totals_by_boundary','activity_count','unmapped_count','unit','read_only','report_digest'}|FLAGS
    if not isinstance(data,dict) or set(data)!=fields or data['schema']!='sgacd-esg-evidence-report-v1' or data['company_id']!=context['tenant_id'] or data['provider_id']!=context['provider_id'] or data['unit']!='kg_co2e' or data['read_only'] is not True or any(data[k] is not False for k in FLAGS):raise ValueError('ESG context/flags invalid.')
    if any(data[k]!=payload[k] for k in ['since','until','as_of','mappings']):raise ValueError('ESG request changed.')
    mappings=data['mappings']
    if not isinstance(mappings,dict) or set(mappings)-BOUNDARIES:raise ValueError('Declared boundary mappings required.')
    for row in mappings.values():
        if not isinstance(row,dict) or set(row)!={'framework','version','reference','evidence_digest'} or not isinstance(row['framework'],str) or row['framework'] not in {'GRI','SASB','CUSTOM'}:raise ValueError('Declared framework required.')
        for key in ['version','reference']:
            if not isinstance(row[key],str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}',row[key]):raise ValueError('Canonical framework reference required.')
        digest(row['evidence_digest'])
    start,end=date.fromisoformat(data['since']),date.fromisoformat(data['until']);cutoff=datetime.fromisoformat(data['as_of'])
    if end<start or (end-start).days>366 or cutoff.tzinfo is None:raise ValueError('Bounded date window required.')
    digest(data['report_digest']);encoded=json.dumps({k:v for k,v in data.items() if k!='report_digest'},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    if len(encoded)>524288 or hashlib.sha256(encoded).hexdigest()!=data['report_digest']:raise ValueError('ESG digest changed.')
    if not isinstance(data['items'],list) or len(data['items'])>200 or type(data['activity_count']) is not int or data['activity_count']!=len(data['items']):raise ValueError('ESG bounded count required.')
    seen=set();totals={};unmapped=0
    with localcontext(Context(prec=60)) as ctx:
        ctx.prec=60
        for row in data['items']:
            if not isinstance(row,dict):raise ValueError('ESG activity object required.')
            extra=set(row)&{'activity_support_digest','source_reference','source_segment'}
            if ('source_reference' in extra)!=('source_segment' in extra):raise ValueError('Paired operational source required.')
            if 'activity_support_digest' in extra:digest(row['activity_support_digest'])
            if 'source_reference' in extra:
                identifier(row['source_reference'])
                if not isinstance(row['source_segment'],str) or not re.fullmatch(r'[A-Z0-9][A-Z0-9_.-]{0,63}',row['source_segment']):raise ValueError('Canonical source segment required.')
            if set(row)-extra!={'observation_id','activity_id','date','quantity','activity_unit','factor_id','factor_version','factor_rate','factor_source_digest','boundary','kg_co2e','revision','known_at','proof_digest','framework_mapping'}:raise ValueError('ESG unexpected activity fields.')
            identifier(row['observation_id']);digest(row['factor_source_digest']);digest(row['proof_digest'])
            if not isinstance(row['activity_id'],str) or row['activity_id'] in seen or not data['since']<=row['date']<=data['until'] or type(row['revision']) is not int or row['revision']<0:raise ValueError('ESG source reuse or dates invalid.')
            if date.fromisoformat(row['date']).isoformat()!=row['date']:raise ValueError('Canonical activity date required.')
            for key in ['activity_id','factor_id','factor_version']:
                if not isinstance(row[key],str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}',row[key]):raise ValueError('Canonical source codes required.')
            seen.add(row['activity_id']);known=datetime.fromisoformat(row['known_at'])
            if known.tzinfo is None or known>cutoff or row['boundary'] not in BOUNDARIES or row['activity_unit'] not in {'vehicle_km','passenger_km','litre_fuel','kwh'}:raise ValueError('ESG known date/unit/boundary invalid.')
            for key in ['quantity','factor_rate','kg_co2e']:
                if not isinstance(row[key],str) or not re.fullmatch(r'(0|[1-9][0-9]{0,24})(\.[0-9]{1,12})?',row[key]):raise ValueError('ESG exact nonnegative decimals required.')
            amount=Decimal(row['quantity'])*Decimal(row['factor_rate'])
            if amount!=Decimal(row['kg_co2e']):raise ValueError('ESG factor product changed.')
            boundary=row['boundary'];totals[boundary]=totals.get(boundary,Decimal(0))+amount
            if row['framework_mapping']!=data['mappings'].get(boundary):raise ValueError('ESG declared mapping changed.')
            unmapped+=row['framework_mapping'] is None
        expected={k:format(v.quantize(Decimal('0.000001'),rounding=ROUND_HALF_UP),'f') for k,v in sorted(totals.items())}
    if data['totals_by_boundary']!=expected or type(data['unmapped_count']) is not int or data['unmapped_count']!=unmapped:raise ValueError('ESG totals or mapping coverage changed.')
