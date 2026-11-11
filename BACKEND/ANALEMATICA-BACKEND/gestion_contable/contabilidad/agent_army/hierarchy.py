"""Política y jerarquía propias de Analemática."""
from uuid import UUID
from apps.core_erp.accounting.agent_army_runtime import ArmyPolicy,hierarchy
POLICY=ArmyPolicy(system='analematica',prefix='ANA_ACCOUNTING_ARMY',namespace=UUID('998c0fb7-3416-4bd3-867a-19c2074fef50'),label='Analemática',
 groups=(('registro','Registro e integridad · Analemática'),('comercial_fiscal','Comercial y fiscal · Analemática'),('analitica','Analítica financiera · Analemática')))
def structure():return hierarchy(POLICY)
