"""Deterministic validation for the existing two-decimal ledger.
No tax assumptions, AI classifications, FX fallback or external calls.
"""
from decimal import Decimal, InvalidOperation, Context, localcontext
from functools import wraps
from .exceptions import AccountingError, UnbalancedEntryError

CENT = Decimal('0.01')
MAX_AMOUNT = Decimal('9999999999999999.99')


def exact_arithmetic(function):
    """Ledger arithmetic never inherits a caller's precision, rounding or traps."""
    @wraps(function)
    def wrapped(*args, **kwargs):
        with localcontext(Context(prec=50)):
            return function(*args, **kwargs)
    return wrapped


@exact_arithmetic
def money(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise AccountingError('Use decimal strings, integers or Decimal; binary floats are not monetary input.')
    try:
        amount = Decimal(value)
        if not amount.is_finite() or amount < 0 or amount > MAX_AMOUNT:
            raise AccountingError('Amount must be finite, nonnegative and fit the ledger precision.')
        rounded = amount.quantize(CENT)
        if amount != rounded:
            raise AccountingError('This ledger requires exact two-decimal amounts; no silent rounding.')
    except (InvalidOperation, ValueError, OverflowError):
        raise AccountingError('Invalid monetary amount.') from None
    return rounded


@exact_arithmetic
def validate_lines(lines):
    if not isinstance(lines, (list, tuple)) or not 2 <= len(lines) <= 1000:
        raise UnbalancedEntryError('An entry requires 2 to 1000 explicit lines.')
    normalized = []
    debit = credit = Decimal('0.00')
    for line in lines:
        if not isinstance(line, dict):
            raise AccountingError('Each line must be a mapping.')
        for primary, alias in [('debit','debit_amount'),('credit','credit_amount')]:
            if primary in line and alias in line and money(line[primary])!=money(line[alias]):
                raise AccountingError('Conflicting monetary aliases are not accepted.')
        left = money(line.get('debit', line.get('debit_amount', 0)))
        right = money(line.get('credit', line.get('credit_amount', 0)))
        if (left > 0) == (right > 0):
            raise UnbalancedEntryError('Each line requires exactly one positive debit or credit.')
        debit += left; credit += right
        result={**line, 'debit': left, 'credit': right}
        if 'amount_transaction' in line:result['amount_transaction']=money(line['amount_transaction'])
        normalized.append(result)
    if debit != credit:
        raise UnbalancedEntryError('Debit and credit totals must match exactly.')
    return normalized


def lock_company(tenant_id):
    from apps.core_erp.tenancy.models import Tenant
    from .exceptions import TenantMismatchError
    if not tenant_id:
        raise TenantMismatchError('An explicit accounting company is required.')
    company = Tenant.objects.select_for_update().filter(pk=tenant_id).first()
    if company is None or not company.is_active or company.state != 'ACTIVE':
        raise TenantMismatchError('Accounting company is inactive or unavailable.')
    return company


def current_actor(actor):
    from django.contrib.auth import get_user_model
    if actor is None or not getattr(actor, 'pk', None):
        raise AccountingError('An explicit audit actor is required.')
    user = get_user_model().objects.filter(pk=actor.pk, is_active=True).first()
    if user is None:
        raise AccountingError('Audit actor is inactive or unavailable.')
    return user
