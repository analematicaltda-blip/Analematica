"""Estado mayor propio: Neko interpreta, Jarvi manda y SOUP evalúa."""
from apps.core_erp.accounting import agent_army_staff as base
from .hierarchy import POLICY
class JarviGeneralOrchestrator(base.JarviOperationalGeneral):
    def __init__(self):super().__init__(POLICY)
class NekoConversationalGeneral(base.NekoConversationalGeneral):pass
class SoupProcessOptimizerGeneral(base.SoupProcessOptimizerGeneral):pass
