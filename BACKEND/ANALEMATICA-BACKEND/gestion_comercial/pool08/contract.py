"""Versioned, bounded commercial contract. This boundary only validates drafts."""
import hashlib
import json
import logging
import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

SYSTEM = 'analematica'
CURRENT_VERSION = '1.1'
SUPPORTED_VERSIONS = ('1.0', CURRENT_VERSION)
MAX_BYTES = 16384
MAX_DEPTH = 10
_ROOT = Path(__file__).resolve().parent
_SCHEMAS = {version: json.loads((_ROOT / filename).read_text()) for version, filename in
            [('1.0', 'commercial-intent.v1.0.schema.json'), ('1.1', 'commercial-intent.schema.json')]}
_VALIDATORS = {}
for _version, _schema in _SCHEMAS.items():
    Draft202012Validator.check_schema(_schema)
    _VALIDATORS[_version] = Draft202012Validator(_schema, format_checker=FormatChecker())
_CAPABILITIES = json.loads((_ROOT / 'capabilities.json').read_text())
_AUDIT = logging.getLogger('pool08.audit')
ERROR_STATUS = {'BODY_LIMIT': 413, 'INVALID_JSON': 400, 'DUPLICATE_FIELD': 400,
                'NONSTANDARD_NUMBER': 400, 'TOO_DEEP': 400,
                'UNSUPPORTED_VERSION': 409, 'CONTRACT_VERSION_MISMATCH': 409,
                'CONTEXT_MISMATCH': 403, 'EXPIRY_INVALID': 409}

class ContractRejected(ValueError):
    """Only fixed codes; never echo rejected bodies, customer data or credentials."""

def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()

def _select_version(version=None):
    version = CURRENT_VERSION if version is None else version
    if not isinstance(version, str) or version not in SUPPORTED_VERSIONS:
        raise ContractRejected('UNSUPPORTED_VERSION')
    return version

def _audit(code, tenant_ref, actor_ref, fingerprint=None):
    # Metadata only; no request body, tokens, customer reference or supplied nonce.
    context = hashlib.sha256(_canonical([SYSTEM, tenant_ref, actor_ref])).hexdigest()
    _AUDIT.info(json.dumps({'event': 'POOL08_CONTRACT_VALIDATION', 'system': SYSTEM,
                           'context_digest': context, 'code': code,
                           'fingerprint': fingerprint}, sort_keys=True))

def http_status(error):
    return ERROR_STATUS.get(str(error), 422)

def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractRejected('DUPLICATE_FIELD')
        result[key] = value
    return result

def _constant(value):
    raise ContractRejected('NONSTANDARD_NUMBER')

def _bounded(value, depth=0):
    if depth > MAX_DEPTH:
        raise ContractRejected('TOO_DEEP')
    if isinstance(value, dict):
        if len(value) > 32 or any(not isinstance(k, str) for k in value):
            raise ContractRejected('INVALID_FIELDS')
        for item in value.values():
            _bounded(item, depth + 1)
    elif isinstance(value, list):
        if len(value) > 100:
            raise ContractRejected('TOO_MANY_ITEMS')
        for item in value:
            _bounded(item, depth + 1)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ContractRejected('NONSTANDARD_NUMBER')

def decode(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ContractRejected('BODY_LIMIT')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique, parse_constant=_constant)
        _bounded(value)
        return value
    except (ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, ContractRejected):
            raise
        raise ContractRejected('INVALID_JSON') from None

def routes():
    prefix = '/api/v1/mi-negocio/comercial/unified/' if SYSTEM == 'erp-tur' else '/api/v1/commercial-unified/'
    suffix = '' if SYSTEM == 'sga-cd' else '/'
    return {name: {'method': method, 'path': prefix + path + suffix} for name, method, path in
            [('contract', 'GET', 'contract'), ('capabilities', 'GET', 'capabilities'),
             ('validate_intent', 'POST', 'intents/validate')]}

def contract_document(version=None):
    version = _select_version(version)
    schema = _SCHEMAS[version]
    return {'pool': 'POOL-08-UNIFIED', 'system': SYSTEM, 'schema_version': version,
            'supported_versions': list(SUPPORTED_VERSIONS),
            'schema_digest': hashlib.sha256(_canonical(schema)).hexdigest(),
            'schema': json.loads(json.dumps(schema)),
            'limits': {'max_bytes': MAX_BYTES, 'max_depth': MAX_DEPTH,
                       'max_tasks': schema['properties']['task_graph']['maxItems'],
                       'max_validity_seconds': 900},
            'states': ['VALIDATED_DRAFT', 'REJECTED'], 'routes': routes(),
            'execution_enabled': False, 'error_status': dict(ERROR_STATUS),
            'default_contract_error_status': 422}

def capabilities(version=None):
    document = contract_document(version)
    allowed = set(document['schema']['properties']['task_graph']['items']['properties']['capability']['enum'])
    rows = [dict(row) for row in _CAPABILITIES if row['id'] in allowed]
    return {'pool': 'POOL-08-UNIFIED', 'schema_version': document['schema_version'], 'system': SYSTEM,
            'supported_versions': list(SUPPORTED_VERSIONS), 'schema_digest': document['schema_digest'], 'routes': routes(),
            'catalog_digest': hashlib.sha256(_canonical(rows)).hexdigest(), 'execution_enabled': False,
            'general_roles': {'JARVI': 'OPERATIONS', 'NEKO': 'CONVERSATION', 'SOUP': 'AGENT_PROCESS_OPTIMIZATION'},
            'creative_role': 'CREATIVE_DIVISION_UNDER_JARVI',
            'voice_agent': {'name': None, 'configured': False, 'voice_is_approval': False},
            'capabilities': rows}

def validate_intent(value, *, tenant_ref, actor_ref, now=None, requested_version=None):
    if not isinstance(tenant_ref, str) or not tenant_ref or not isinstance(actor_ref, str) or not actor_ref:
        raise ContractRejected('SERVER_CONTEXT_REQUIRED')
    try:
        _bounded(value)
        encoded = _canonical(value)
        if len(encoded) > MAX_BYTES:
            raise ContractRejected('BODY_LIMIT')
        if not isinstance(value, dict):
            raise ContractRejected('SCHEMA_INVALID')
        version = _select_version(value.get('schema_version', ''))
        if requested_version is not None and _select_version(requested_version) != version:
            raise ContractRejected('CONTRACT_VERSION_MISMATCH')
        if next(_VALIDATORS[version].iter_errors(value), None) is not None:
            raise ContractRejected('SCHEMA_INVALID')
        if value['system'] != SYSTEM or value['tenant_ref'] != tenant_ref or value['actor_ref'] != actor_ref:
            raise ContractRejected('CONTEXT_MISMATCH')
        current = now if now is not None else datetime.now(timezone.utc)
        expiry = datetime.fromisoformat(value['expires_at'].replace('Z', '+00:00'))
        if current.tzinfo is None or expiry.tzinfo is None or not current < expiry <= current + timedelta(minutes=15):
            raise ContractRejected('EXPIRY_INVALID')
        kind = value.get('intent_kind', 'SALE_PREPARATION')
        if kind == 'SALE_PREPARATION' and Decimal(value['transaction_payload']['gross_fiat_amount']) <= 0:
            raise ContractRejected('AMOUNT_INVALID')
        nodes = value['task_graph']
        indexed = {node['id']: node for node in nodes}
        if len(indexed) != len(nodes):
            raise ContractRejected('DAG_DUPLICATE_NODE')
        pending = {key: set(node['depends_on']) for key, node in indexed.items()}
        if any(not deps <= indexed.keys() or key in deps for key, deps in pending.items()):
            raise ContractRejected('DAG_INVALID_DEPENDENCY')
        order = []
        while pending:
            ready = sorted(key for key, deps in pending.items() if not deps)
            if not ready:
                raise ContractRejected('DAG_CYCLE')
            order.extend(ready)
            for key in ready:
                del pending[key]
            for deps in pending.values():
                deps.difference_update(ready)
    except ContractRejected as exc:
        _audit(str(exc), tenant_ref, actor_ref)
        raise
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
        _audit('SCHEMA_INVALID', tenant_ref, actor_ref)
        raise ContractRejected('SCHEMA_INVALID') from None
    fingerprint = hashlib.sha256(encoded).hexdigest()
    _audit('VALIDATED_DRAFT', tenant_ref, actor_ref, fingerprint)
    by_capability = {row['id']: row for row in _CAPABILITIES}
    return {'system': SYSTEM, 'schema_version': version, 'orchestration_id': value['orchestration_id'],
            'schema_digest': contract_document(version)['schema_digest'], 'fingerprint': fingerprint,
            'state': 'VALIDATED_DRAFT', 'intent_kind': kind, 'validation_scope': 'STRUCTURE_CURRENT_ACTOR_AND_COMPANY_ONLY',
            'execution_authorized': False, 'payment_verified': False, 'fiscal_accepted': False,
            'inventory_locked': False, 'storage_written': False, 'network_called': False,
            'topological_order': order,
            'planned_tasks': [{'id': key, 'capability': indexed[key]['capability'],
                               'state': 'REQUIRES_DOMAIN_BINDING', 'execution_enabled': False,
                               'implementation_evidence': by_capability[indexed[key]['capability']]['implementation_evidence']}
                              for key in order],
            'required_domain_checks': ['CURRENT_PERMISSION', 'CONSENT', 'CURRENT_SERVER_PRICE', 'CAPACITY',
                                       'HUMAN_APPROVAL_WHEN_REQUIRED', 'AUTHENTIC_PROVIDER_RECEIPT',
                                       'LEDGER_AND_VAULT_CONTRACTS']}
