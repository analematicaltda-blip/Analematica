"""Declared commercial return terms, without inferring legal or banking approval."""
from .exceptions import AccountingError
from .environmental import _date, _code
from .invoice_intent import _money, _format_money
from .bank_reconciliation import digest


def validate(policy):
    if not isinstance(policy,dict) or set(policy)!={'code','version','valid_from','valid_until','tiers','evidence_digest'}:
        raise AccountingError('Explicit versioned return policy required.')
    _code(policy['code']);_code(policy['version']);digest(policy['evidence_digest'])
    if _date(policy['valid_from'])>_date(policy['valid_until']):raise AccountingError('Invalid policy validity.')
    tiers=policy['tiers']
    if not isinstance(tiers,list) or not 1<=len(tiers)<=20:raise AccountingError('Bounded anticipation tiers required.')
    last=-1
    for tier in tiers:
        if not isinstance(tier,dict) or set(tier)!={'minimum_days','refund_bps'} or type(tier['minimum_days']) is not int or not last<tier['minimum_days']<=3650 or type(tier['refund_bps']) is not int or not 0<=tier['refund_bps']<=10000:
            raise AccountingError('Strictly increasing day thresholds and basis points required.')
        last=tier['minimum_days']
    if tiers[0]['minimum_days']!=0:raise AccountingError('Explicit zero-day tier required.')
    return policy


def quote(policy, *, paid, scheduled_date, requested_date):
    validate(policy);scheduled=_date(scheduled_date);requested=_date(requested_date)
    if not _date(policy['valid_from'])<=requested<=_date(policy['valid_until']):raise AccountingError('Policy not applicable on request date.')
    days=(scheduled-requested).days
    if days<0:raise AccountingError('This anticipation policy does not authorize past service refunds.')
    tier=next(t for t in reversed(policy['tiers']) if t['minimum_days']<=days)
    numerator=_money(paid)*tier['refund_bps']
    if numerator%10000:raise AccountingError('Policy produces fractional cents; explicit reviewed terms required.')
    return {'anticipation_days':days,'refund_bps':tier['refund_bps'],'maximum_refund':_format_money(numerator//10000),
        'policy_code':policy['code'],'policy_version':policy['version'],'regulatory_verified':False}
