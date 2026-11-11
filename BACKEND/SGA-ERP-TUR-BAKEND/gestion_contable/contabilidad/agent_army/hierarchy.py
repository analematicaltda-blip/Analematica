"""Política y jerarquía propias de ERP Empresas Turísticas."""
from uuid import UUID
from apps.core_erp.accounting.agent_army_runtime import ArmyPolicy,hierarchy
POLICY=ArmyPolicy(system='erp-tur',prefix='ERP_TUR_ACCOUNTING_ARMY',namespace=UUID('09062972-852f-487d-aab5-3ad13483006e'),label='ERP Empresas Turísticas',
 groups=(('registro','Registro e integridad · ERP Empresas Turísticas'),('comercial_fiscal','Comercial y fiscal · ERP Empresas Turísticas'),('analitica','Analítica financiera · ERP Empresas Turísticas')))
def structure():return hierarchy(POLICY)
