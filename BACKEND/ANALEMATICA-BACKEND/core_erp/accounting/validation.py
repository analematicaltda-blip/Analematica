"""Deterministic validation for the existing two-decimal ledger.
No tax assumptions, AI classifications, FX fallback or external calls.
"""
from decimal import Decimal, InvalidOperation
from .exceptions import AccountingError, UnbalancedEntryError

CENT = Decimal('0.01')
MAX_AMOUNT = Decimal('9999999999999999.99')


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


def validate_lines(lines):
    if not isinstance(lines, (list, tuple)) or not 2 <= len(lines) <= 1000:
        raise UnbalancedEntryError('An entry requires 2 to 1000 explicit lines.')
    normalized = []
    debit = credit = Decimal('0.00')
    for line in lines:
        if not isinstance(line, dict):
            raise AccountingError('Each line must be a mapping.')
        left = money(line.get('debit', line.get('debit_amount', 0)))
        right = money(line.get('credit', line.get('credit_amount', 0)))
        if (left > 0) == (right > 0):
            raise UnbalancedEntryError('Each line requires exactly one positive debit or credit.')
        debit += left; credit += right
        normalized.append({**line, 'debit': left, 'credit': right})
    if debit != credit:
        raise UnbalancedEntryError('Debit and credit totals must match exactly.')
    return normalized
