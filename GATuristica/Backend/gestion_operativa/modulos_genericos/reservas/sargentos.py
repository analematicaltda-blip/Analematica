from apps.domain_business.operativa.sargentos import DomainSargentoReservas

class SargentoReservas:
    @staticmethod
    def confirmar_reserva(reserva_id):
        DomainSargentoReservas.confirm_reservation(reserva_id)
