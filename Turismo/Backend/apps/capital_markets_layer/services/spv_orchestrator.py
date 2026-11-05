from ..models import SPV

class SPVOrchestrator:
    """
    Orquestador de vehículos de propósito especial (Fase 8).
    """

    @staticmethod
    def create_regional_spv(name, jurisdiction, committed_capital):
        spv = SPV.objects.create(
            name=name,
            jurisdiction=jurisdiction,
            capital_committed=committed_capital,
            purpose="Regional Expansion Investment Vehicle"
        )
        return spv

    @staticmethod
    def get_spv_consolidation_status():
        active_spvs = SPV.objects.filter(is_active=True)
        return {
            "count": active_spvs.count(),
            "total_committed": sum(s.capital_committed for s in active_spvs),
            "consolidation_layer": "Global Orchestration (F6)"
        }
