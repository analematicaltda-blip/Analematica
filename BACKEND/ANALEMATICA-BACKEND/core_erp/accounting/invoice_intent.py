"""Versioned invoice request contract, not fiscal issuance or a posting command.
Caller must obtain the snapshot from an authorized, transactionally locked source.
"""
import hashlib
import json
import re
from uuid import UUID

SCHEMA = 'sgacd-invoice-intent-v1'


def _uuid(value):
    if not isinstance(value, str) or str(UUID(value)) != value:
        raise ValueError('Canonical UUID required.')
    return value


def _money(value):
    if not isinstance(value, str) or not re.fullmatch(r'(0|[1-9][0-9]{0,11})\.[0-9]{2}', value):
        raise ValueError('Explicit nonnegative money string with two decimals required.')
    return int(value.replace('.', ''))


def _format_money(cents):
    return f'{cents // 100}.{cents % 100:02d}'


def prepare_invoice_intent(snapshot, expected_company):
    """Pure bounded normalization. Does not authenticate the source or resolve tax law."""
    fields = {'schema', 'company_id', 'source_type', 'source_id', 'revision', 'state', 'currency', 'items'}
    if not isinstance(snapshot, dict) or set(snapshot) != fields or snapshot['schema'] != SCHEMA:
        raise ValueError('Unsupported invoice request shape.')
    company = _uuid(snapshot['company_id'])
    if company != _uuid(expected_company):
        raise ValueError('Company mismatch.')
    source = _uuid(snapshot['source_id'])
    states = {'crm_opportunity': 'WON', 'reservation': 'CONFIRMED'}
    if not isinstance(snapshot['source_type'], str) or snapshot['source_type'] not in states or snapshot['state'] != states[snapshot['source_type']]:
        raise ValueError('Source is not eligible for an invoice request.')
    revision = snapshot['revision']
    if type(revision) is not int or not 1 <= revision <= 2147483647:
        raise ValueError('Positive source revision required.')
    currency = snapshot['currency']
    if not isinstance(currency, str) or currency not in {'COP', 'USD', 'EUR'}:
        raise ValueError('Currency requires an explicit supported policy.')
    items = snapshot['items']
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise ValueError('Between one and 100 items required.')
    normalized = []; seen = set(); net_total = 0; tax_total = 0
    for item in items:
        if not isinstance(item, dict) or set(item) != {'item_id', 'net', 'tax', 'tax_category', 'policy_reference'}:
            raise ValueError('Unsupported invoice item shape.')
        item_id = _uuid(item['item_id'])
        if item_id in seen:
            raise ValueError('Duplicate item identifier.')
        seen.add(item_id)
        net = _money(item['net']); tax = _money(item['tax'])
        category = item['tax_category']; reference = item['policy_reference']
        if not isinstance(category, str) or category not in {'TAXABLE', 'EXEMPT', 'EXCLUDED'} or (category != 'TAXABLE' and tax != 0):
            raise ValueError('Inconsistent explicit tax category.')
        if not isinstance(reference, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}', reference):
            raise ValueError('Tax policy reference required, not document content.')
        if net <= 0:
            raise ValueError('Positive net amount required.')
        normalized.append({'item_id': item_id, 'net': _format_money(net), 'tax': _format_money(tax), 'tax_category': category, 'policy_reference': reference})
        net_total += net; tax_total += tax
    payload = {key: snapshot[key] for key in fields if key != 'items'}
    payload['items'] = sorted(normalized, key=lambda row: row['item_id'])
    payload['totals'] = {'net': _format_money(net_total), 'tax': _format_money(tax_total), 'gross': _format_money(net_total + tax_total)}
    encoded = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    identity = [SCHEMA, company, snapshot['source_type'], source, revision]
    return {'payload': payload, 'payload_digest': hashlib.sha256(encoded).hexdigest(),
            'idempotency_key': hashlib.sha256(json.dumps(identity, separators=(',', ':')).encode()).hexdigest(),
            'status': 'REQUEST_ONLY', 'fiscal_accepted': False, 'ledger_written': False, 'published': False,
            'source_authority_verified': False, 'tax_policy_verified': False}
