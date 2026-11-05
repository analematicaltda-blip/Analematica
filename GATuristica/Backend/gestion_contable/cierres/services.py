from django.db.models import Sum, Q
from decimal import Decimal
from .models import PeriodoContable
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import JournalEntry

class CierreContableService:
    def __init__(self, periodo: PeriodoContable):
        self.periodo = periodo

    def validar_periodo_para_cierre(self):
        """
        Ejecuta todas las validaciones requeridas antes de permitir un cierre.
        Lanza una excepción si alguna validación falla.
        """
        self._validar_asientos_balanceados()
        # Aquí se añadirían otras validaciones, como:
        # - No existen facturas de venta en estado 'Borrador'.
        # - Todas las planillas de nómina están 'Contabilizadas' o 'Pagadas'.
        # - No hay pagos pendientes de conciliación.

    def _validar_asientos_balanceados(self):
        """Verifica que todos los asientos del período cumplan la partida doble."""
        asientos = JournalEntry.objects.filter(
            perfil=self.periodo.perfil,
            entry_date__range=(self.periodo.fecha_inicio, self.periodo.fecha_fin)
        )
        for asiento in asientos:
            asiento.clean() # Lanza ValidationError si está desbalanceado

    def cerrar_periodo(self):
        if self.periodo.estado == PeriodoContable.Estado.CERRADO:
            raise Exception("El período ya está cerrado.")

        self.validar_periodo_para_cierre()

        self.periodo.estado = PeriodoContable.Estado.CERRADO
        self.periodo.save()

    def reabrir_periodo(self):
        if self.periodo.estado == PeriodoContable.Estado.ABIERTO:
            raise Exception("El período ya está abierto.")

        self.periodo.estado = PeriodoContable.Estado.ABIERTO
        self.periodo.save()
