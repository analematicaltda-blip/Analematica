from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum
from decimal import Decimal

from ..cierres.models import PeriodoContable
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import Transaction

class EstadoResultadosView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        periodo_id = request.query_params.get('periodo_id')
        if not periodo_id:
            return Response({"error": "Se requiere 'periodo_id'."}, status=400)

        try:
            periodo = PeriodoContable.objects.get(id=periodo_id, perfil=request.user.perfil_prestador)
        except PeriodoContable.DoesNotExist:
            return Response({"error": "Período no encontrado."}, status=404)

        if periodo.estado != PeriodoContable.Estado.CERRADO:
            return Response({"error": "El período debe estar cerrado."}, status=400)

        # Cuentas de Ingresos (4), Gastos (5) y Costos (6)
        saldos = Transaction.objects.filter(
            journal_entry__perfil=request.user.perfil_prestador,
            journal_entry__entry_date__range=(periodo.fecha_inicio, periodo.fecha_fin),
            account__code__in=['4', '5', '6']
        ).values('account__code', 'account__name').annotate(
            saldo=Sum('credit') - Sum('debit')
        ).order_by('account__code')

        ingresos = []
        gastos = []
        total_ingresos = Decimal('0.00')
        total_gastos = Decimal('0.00')

        for saldo in saldos:
            cuenta = {"code": saldo['account__code'], "name": saldo['account__name'], "balance": saldo['saldo']}
            if saldo['account__code'].startswith('4'):
                ingresos.append(cuenta)
                total_ingresos += saldo['saldo']
            else:
                gastos.append(cuenta)
                total_gastos += saldo['saldo']

        utilidad_neta = total_ingresos - total_gastos

        return Response({
            "periodo": periodo.nombre,
            "ingresos": {"items": ingresos, "total": total_ingresos},
            "gastos": {"items": gastos, "total": total_gastos},
            "utilidad_neta": utilidad_neta
        })
