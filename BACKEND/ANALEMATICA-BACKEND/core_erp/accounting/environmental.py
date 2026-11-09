"""Deterministic environmental estimate, not a carbon credit or accounting liability.

Factors and activities are supplied explicitly by the owner. No factor is fetched,
endorsed, defaulted or persisted. Decimal arithmetic retains exact products before
rounding the aggregate; passenger allocation never changes total emissions.
"""
from datetime import date
from decimal import Decimal, localcontext, ROUND_HALF_UP
import re
from .exceptions import AccountingError
from .integrity import fingerprint

UNITS={'vehicle_km','passenger_km','litre_fuel','kwh'}
BOUNDARIES={'direct_combustion','electricity_location_based','lifecycle'}
NUMBER=re.compile(r'(?:0|[1-9][0-9]{0,9})(?:\.[0-9]{1,6})?\Z')
CODE=re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z')

def _fields(value,fields):
    if not isinstance(value,dict) or set(value)!=set(fields):raise AccountingError('Explicit environmental contract required.')

def _code(value):
    if not isinstance(value,str) or not CODE.fullmatch(value):raise AccountingError('Canonical environmental identifier required.')
    return value

def _date(value):
    if not isinstance(value,str):raise AccountingError('Canonical economic date required.')
    try:parsed=date.fromisoformat(value)
    except ValueError:raise AccountingError('Canonical economic date required.') from None
    if parsed.isoformat()!=value:raise AccountingError('Canonical economic date required.')
    return parsed

def _amount(value):
    if not isinstance(value,str) or not NUMBER.fullmatch(value):raise AccountingError('Nonnegative decimal string with at most six places required.')
    parsed=Decimal(value)
    if parsed>Decimal('1000000000'):raise AccountingError('Environmental quantity exceeds supported bound.')
    return parsed

def estimate(*,company_id,activities,factors):
    if not isinstance(factors,list) or not 1<=len(factors)<=10 or not isinstance(activities,list) or not 1<=len(activities)<=30:raise AccountingError('Bounded factors and activities required.')
    catalog={};canonical_factors=[]
    for factor in factors:
        _fields(factor,{'id','version','unit','kg_co2e_per_unit','valid_from','valid_until','source_digest','geography','boundary'})
        key=_code(factor['id']);_code(factor['version']);_code(factor['geography'])
        if key in catalog:raise AccountingError('Duplicate factor identity; choose one explicit version per calculation.')
        if not isinstance(factor['unit'],str) or factor['unit'] not in UNITS or not isinstance(factor['boundary'],str) or factor['boundary'] not in BOUNDARIES:raise AccountingError('Explicit factor unit and boundary required.')
        start,end=_date(factor['valid_from']),_date(factor['valid_until'])
        if end<start:raise AccountingError('Invalid factor validity interval.')
        if not isinstance(factor['source_digest'],str) or not re.fullmatch('[0-9a-f]{64}',factor['source_digest']):raise AccountingError('Declared factor source digest required.')
        amount=_amount(factor['kg_co2e_per_unit'])
        catalog[key]=(factor,amount,start,end);canonical_factors.append(dict(factor))
    ids=set();used=set();rows=[];groups={}
    with localcontext() as ctx:
        ctx.prec=60
        total=Decimal(0)
        for activity in activities:
            _fields(activity,{'id','date','quantity','unit','factor_id','passengers'})
            key=_code(activity['id']);factor_key=_code(activity['factor_id'])
            if key in ids or factor_key not in catalog:raise AccountingError('Duplicate activity or missing explicit factor.')
            ids.add(key);used.add(factor_key);factor,rate,start,end=catalog[factor_key];day=_date(activity['date'])
            if activity['unit']!=factor['unit'] or not start<=day<=end:raise AccountingError('Activity unit/date incompatible with factor.')
            passengers=activity['passengers']
            if passengers is not None and (activity['unit']!='vehicle_km' or type(passengers) is not int or not 1<=passengers<=10000):raise AccountingError('Passenger allocation only for vehicle distance with explicit positive count.')
            quantity=_amount(activity['quantity']);emissions=quantity*rate;total+=emissions
            boundary=factor['boundary'];groups[boundary]=groups.get(boundary,Decimal(0))+emissions
            rows.append({**activity,'factor_version':factor['version'],'source_digest':factor['source_digest'],'boundary':boundary,'kg_co2e':format(emissions,'f'),'kg_co2e_per_passenger':None if passengers is None else format((emissions/passengers).quantize(Decimal('0.000001'),rounding=ROUND_HALF_UP),'f')})
        if used!=set(catalog):raise AccountingError('Unused factors are not accepted as calculation evidence.')
        snapshot={'company_id':str(company_id),'activities':sorted([dict(a) for a in activities],key=lambda a:a['id']),'factors':sorted(canonical_factors,key=lambda f:f['id'])}
        mixed=len(groups)>1
        return {'schema':'sgacd-environmental-estimate-v1','company_id':str(company_id),'assessment_digest':fingerprint(snapshot),'snapshot':snapshot,'items':rows,'totals_by_boundary':{b:format(v.quantize(Decimal('0.000001'),rounding=ROUND_HALF_UP),'f') for b,v in sorted(groups.items())},'kg_co2e':None if mixed else format(total.quantize(Decimal('0.000001'),rounding=ROUND_HALF_UP),'f'),'aggregate_available':not mixed,'unavailable_reason':'INCOMPATIBLE_SYSTEM_BOUNDARIES' if mixed else None,'unit':'kg_co2e','factor_sources_independently_verified':False,'read_only':True,'ledger_written':False,'money_transferred':False,'liability_recognized':False,'carbon_credit_issued':False,'esg_certified':False}
