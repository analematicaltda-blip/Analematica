from django.utils.module_loading import import_string

# Using dynamic import to maintain decoupling if app labels change
Reserva = import_string('apps.prestadores.models.Reserva')

class ReservationRepository:
    """
    Encapsula el acceso a datos para el dominio de reservas.
    """
    @staticmethod
    def get_by_id(reservation_id):
        return Reserva.objects.get(id=reservation_id)

    @staticmethod
    def list_active():
        return Reserva.objects.filter(estado='CONFIRMADA')

    @staticmethod
    def cancel(reservation_id):
        return ReservationRepository.update_status(reservation_id, 'CANCELADA')

    @staticmethod
    def update_status(reservation_id, status):
        res = Reserva.objects.get(id=reservation_id)
        res.estado = status
        res.save()
        return res
