from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum
from decimal import Decimal

from ..cierres.models import PeriodoContable
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import Transaction

class ReporteIVAView(APIView):
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

        # IVA Generado (Ventas) - Cuenta 2408
        iva_generado = Transaction.objects.filter(
            journal_entry__perfil=request.user.perfil_prestador,
            journal_entry__entry_date__range=(periodo.fecha_inicio, periodo.fecha_fin),
            account__code__startswith='2408'
        ).aggregate(total=Sum('credit'))['total'] or Decimal('0.00')

        # IVA Descontable (Compras) - Cuenta 240810 (Estándar PUC Colombia para descontables)
        iva_descontable = Transaction.objects.filter(
            journal_entry__perfil=request.user.perfil_prestador,
            journal_entry__entry_date__range=(periodo.fecha_inicio, periodo.fecha_fin),
            account__code__startswith='240810'
        ).aggregate(total=Sum('debit'))['total'] or Decimal('0.00')

        saldo_a_pagar = iva_generado - iva_descontable

        return Response({
            "periodo": periodo.nombre,
            "iva_generado": iva_generado,
            "iva_descontable": iva_descontable,
            "saldo_a_pagar": saldo_a_pagar
        })
