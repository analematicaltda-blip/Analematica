"""Deterministic Spanish query baseline. No LLM, generated SQL or side effects.
Authorization belongs to the caller; all tools receive the resolved company.
"""
from datetime import date
import unicodedata

QUESTIONS = {
    'rentabilidad': 'profitability',
    'muestra la rentabilidad': 'profitability',
    'cual es el resultado neto de mi empresa': 'profitability',
    'liquidez': 'quick_ratio',
    'liquidez acida': 'quick_ratio',
    'cual es mi liquidez acida': 'quick_ratio',
    'consulta mi liquidez acida': 'quick_ratio',
    'cual es la rentabilidad de mi empresa': 'profitability',
    'cual es mi rentabilidad': 'profitability',
    'estado de la cola de facturacion': 'commercial_queue',
    'estado de la cola comercial': 'commercial_queue',
    'como esta la cola de facturacion': 'commercial_queue',
}


def resolve_question(question):
    if not isinstance(question, str) or not 1 <= len(question) <= 240:
        raise ValueError('Pregunta de una a 240 letras requerida.')
    normalized = ''.join(char for char in unicodedata.normalize('NFKD', question.casefold())
                         if not unicodedata.combining(char))
    normalized = ' '.join(normalized.strip(' ¿?¡!.,\t\r\n').split())
    intent = QUESTIONS.get(normalized)
    if intent is None:
        raise ValueError('Pregunta no soportada; consulta rentabilidad, liquidez ácida o estado de la cola de facturación.')
    return intent


def _day(value):
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError('Fecha ISO requerida.')
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError('Fecha ISO canónica requerida.')
    return parsed


def answer_query(company_id, payload):
    """Tool dispatch only; never trust a company identifier from the payload."""
    if not isinstance(payload, dict) or not set(payload) <= {'question', 'since', 'until'} or 'question' not in payload:
        raise ValueError('Contrato de consulta no soportado.')
    intent = resolve_question(payload['question'])
    if intent == 'profitability':
        if set(payload) != {'question', 'since', 'until'}:
            raise ValueError('La rentabilidad requiere fechas since y until explícitas.')
        since = _day(payload['since']); until = _day(payload['until'])
        if since > until or (until - since).days > 366:
            raise ValueError('El intervalo debe ser ordenado y no superar 366 días.')
        from .reports_engine import ReportsEngine
        data = ReportsEngine.get_profitability(company_id, since, until)
        source = 'ReportsEngine.get_profitability'
    elif intent == 'quick_ratio':
        if set(payload) != {'question','until'}:
            raise ValueError('La liquidez requiere solo el corte until explícito.')
        cutoff = _day(payload['until'])
        from .ratios import quick_ratio
        data = quick_ratio(company_id, cutoff)
        source = 'ratios.quick_ratio'
    else:
        if set(payload) != {'question'}:
            raise ValueError('La cola no admite un filtro de fechas no implementado.')
        from .commercial_outbox_status import inspect_commercial_outbox
        data = inspect_commercial_outbox(company_id)
        source = 'inspect_commercial_outbox'
    return {'schema': 'sgacd-accounting-query-v1', 'intent': intent, 'company_id': str(company_id),
            'read_only': True, 'execution': 'DETERMINISTIC_ALLOWLIST', 'source': source, 'data': data,
            'generated_sql': False, 'external_model_used': False, 'ledger_written': False,
            'financial_action_authorized': False}
