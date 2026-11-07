# backend/apps/prestadores/mi_negocio/gestion_contable/services/reportes.py
import logging
from django.db.models import Sum
from decimal import Decimal
from ..contabilidad.models import Transaccion, PeriodoContable, Cuenta

logger = logging.getLogger(__name__)

class FinancialReportService:
    @staticmethod
    def generar_balance_general(periodo_id, perfil_id):
        try:
            periodo = PeriodoContable.objects.get(id=periodo_id, provider_id=perfil_id)

            saldos = Transaccion.objects.filter(
                asiento__provider_id=perfil_id,
                asiento__fecha__lte=periodo.fecha_fin
            ).values('cuenta__codigo', 'cuenta__nombre', 'cuenta__tipo').annotate(
                total_debito=Sum('debito'),
                total_credito=Sum('credito')
            ).order_by('cuenta__codigo')

            data = {
                "periodo": periodo.nombre,
                "activos": {"items": [], "total": Decimal('0.00')},
                "pasivos": {"items": [], "total": Decimal('0.00')},
                "patrimonio": {"items": [], "total": Decimal('0.00')},
                "total_pasivo_patrimonio": Decimal('0.00')
            }

            for s in saldos:
                balance = s['total_debito'] - s['total_credito']
                item = {"codigo": s['cuenta__codigo'], "nombre": s['cuenta__nombre'], "saldo": balance}

                if s['cuenta__tipo'] == 'ACTIVO':
                    data['activos']['items'].append(item)
                    data['activos']['total'] += balance
                elif s['cuenta__tipo'] == 'PASIVO':
                    data['pasivos']['items'].append(item)
                    data['pasivos']['total'] += -balance
                elif s['cuenta__tipo'] == 'PATRIMONIO':
                    data['patrimonio']['items'].append(item)
                    data['patrimonio']['total'] += -balance

            data['total_pasivo_patrimonio'] = data['pasivos']['total'] + data['patrimonio']['total']
            return data
        except Exception as e:
            logger.error(f"Error al generar balance general: {e}")
            return None
