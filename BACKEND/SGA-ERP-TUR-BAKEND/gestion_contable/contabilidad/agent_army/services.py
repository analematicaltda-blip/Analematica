"""Instancias propias, independientes del estado mayor de SGA-CD."""
from .command_staff import JarviGeneralOrchestrator,NekoConversationalGeneral,SoupProcessOptimizerGeneral
JARVI=JarviGeneralOrchestrator()
NEKO=NekoConversationalGeneral(JARVI)
SOUP=SoupProcessOptimizerGeneral(JARVI)
ARMY=JARVI
