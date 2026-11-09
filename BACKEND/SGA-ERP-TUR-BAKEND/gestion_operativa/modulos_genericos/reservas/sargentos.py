from apps.domain_business.operativa.sargentos import DomainSargentoReservas

class SargentoReservas:
    @staticmethod
    def confirmar_reserva(reserva_id, *, actor=None, provider_id=None):
        return DomainSargentoReservas.confirm_reservation(reserva_id, actor=actor, provider_id=provider_id)
