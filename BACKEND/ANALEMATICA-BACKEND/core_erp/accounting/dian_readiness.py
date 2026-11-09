"""Fail-closed DIAN boundary and public, company-scoped readiness diagnosis.
A hash is never a signature; local configuration is never fiscal acceptance.
"""
from datetime import date
import re
from uuid import UUID
from .exceptions import AccountingError

class DianIntegrationUnavailable(AccountingError):
    code='DIAN_VERIFIED_TRANSPORT_UNAVAILABLE'

def block_unverified_submission(*args,**kwargs):
    raise DianIntegrationUnavailable('DIAN no integrada: faltan firma XAdES verificada, custodia del cliente, transporte habilitado y validación auténtica del acuse. No se envió ni aceptó el documento.')

def inspect_readiness(company_id,profile=None,*,today=None):
    company=str(UUID(str(company_id)));today=today or date.today();issues=[]
    expected={'company_id','supplier_nit','resolution_number','prefix','range_start','range_end','next_number','valid_from','valid_until','environment','software_id','test_set_id'}
    profile_ok=isinstance(profile,dict) and set(profile)==expected and profile.get('company_id')==company
    if not profile_ok:issues.append('PUBLIC_PROFILE_MISSING_OR_INCOMPATIBLE')
    else:
        if not isinstance(profile['supplier_nit'],str) or not re.fullmatch('[0-9]{6,15}',profile['supplier_nit']):issues.append('SUPPLIER_NIT_INVALID')
        if not isinstance(profile['resolution_number'],str) or not re.fullmatch('[0-9]{1,30}',profile['resolution_number']):issues.append('RESOLUTION_NUMBER_INVALID')
        if not isinstance(profile['prefix'],str) or not re.fullmatch('[A-Z0-9]{0,10}',profile['prefix']):issues.append('INVOICE_PREFIX_INVALID')
        values=[profile[k] for k in ('range_start','range_end','next_number')]
        if not all(type(v) is int and 0<v<=999999999999 for v in values) or not values[0]<=values[2]<=values[1]:issues.append('RESOLUTION_RANGE_EXHAUSTED_OR_INVALID')
        try:
            begin=date.fromisoformat(profile['valid_from']);end=date.fromisoformat(profile['valid_until'])
            if not begin<=today<=end:issues.append('RESOLUTION_NOT_CURRENT')
        except (TypeError,ValueError):issues.append('RESOLUTION_DATES_INVALID')
        try:UUID(profile['software_id'])
        except (TypeError,ValueError,AttributeError):issues.append('SOFTWARE_ID_INVALID')
        if profile['environment']!='HABILITACION':issues.append('HABILITATION_REQUIRED_BEFORE_PRODUCTION')
        if not isinstance(profile['test_set_id'],str) or not re.fullmatch('[A-Za-z0-9-]{1,100}',profile['test_set_id']):issues.append('TEST_SET_ID_MISSING_OR_INVALID')
    return {'schema':'sgacd-dian-readiness-v1','company_id':company,'read_only':True,'public_configuration_valid':not issues,'blocking_codes':issues+['CLIENT_KEY_CUSTODY_NOT_QUALIFIED','UBL_XADES_NOT_QUALIFIED','DIAN_TRANSPORT_NOT_INTEGRATED','AUTHENTIC_RECEIPT_VALIDATION_NOT_INTEGRATED'],'ready_to_submit':False,'signature_verified':False,'network_called':False,'fiscal_accepted':False,'ledger_written':False,'secrets_returned':False,'configuration_is_official_verification':False}
