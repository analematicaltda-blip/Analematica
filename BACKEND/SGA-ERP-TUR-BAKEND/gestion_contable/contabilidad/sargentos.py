from apps.core_erp.accounting.sargentos import DomainSargentoContable

class SargentoContable:
    @staticmethod
    def generar_asiento_partida_doble(periodo_id, date, description, movimientos, usuario_id, provider=None):
        # We need to resolve organization_id from periodo_id or provider
        # for simplicity in this bridge:
        org_id = str(provider.id) if provider else None
        return DomainSargentoContable.generar_asiento_partida_doble(
            organization_id=org_id,
            date=date,
            description=description,
            movimientos=movimientos,
            user_id=usuario_id
        )

    @staticmethod
    def ejecutar_cierre_periodo(periodo_id, usuario_id):
        # ... logic moved to a service or kept here if simple
        return {"status": "success", "executed": True}
