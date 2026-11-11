"""Internal posting-save invariant, not a user authorization or SQL security boundary.

Only a scoped engine operation opens this temporary capability. A cached object
attribute cannot reuse it; PostgreSQL/SQLite guards remain necessary for bulk SQL.
"""
from contextlib import contextmanager
from contextvars import ContextVar

_allowed = ContextVar('accounting_posting_save', default=None)

def permits(entry):
    return _allowed.get() == (str(entry.tenant_id), str(entry.pk))

@contextmanager
def posting_save(entry):
    token = _allowed.set((str(entry.tenant_id), str(entry.pk)))
    try:
        yield
    finally:
        _allowed.reset(token)
