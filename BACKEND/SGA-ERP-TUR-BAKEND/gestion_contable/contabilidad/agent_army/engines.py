"""Adaptadores locales propios, con configuración y titular por backend."""
from apps.core_erp.accounting.agent_army_engines import execute
from .hierarchy import POLICY
def dispatch(actor,company,engine,plan):
    return execute(POLICY,actor,company,engine,plan)
