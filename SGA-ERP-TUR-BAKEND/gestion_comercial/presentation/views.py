from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
from ..sales.models import Venta, DetalleVenta
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.inventario.models import InventoryItem, MovimientoInventario

class BusinessReportsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def sales_summary(self, request):
        """
        Reporte de Ventas: Diarias y Mensuales.
        """
        provider_id = request.user.perfil_prestador.id

        # Ventas diarias (últimos 30 días)
        last_30_days = timezone.now() - timedelta(days=30)
        daily_sales = Venta.objects.filter(
            provider_id=provider_id,
            estado='CONFIRMADA',
            fecha__gte=last_30_days
        ).annotate(day=TruncDay('fecha')).values('day').annotate(
            total=Sum('total'),
            count=Count('id')
        ).order_by('day')

        # Ventas por producto
        top_products = DetalleVenta.objects.filter(
            venta__provider_id=provider_id,
            venta__estado='CONFIRMADA'
        ).values('producto_ref_id').annotate(
            total_sold=Sum('cantidad'),
            revenue=Sum('subtotal')
        ).order_by('-total_sold')[:10]

        return Response({
            "daily_sales": daily_sales,
            "top_products": top_products
        })

    @action(detail=False, methods=['get'])
    def inventory_status(self, request):
        """
        Reporte de Inventario y Alertas.
        """
        provider_id = request.user.perfil_prestador.id

        items = InventoryItem.objects.filter(provider_id=provider_id)

        stock_alerts = items.filter(stock_actual__lt=models.F('stock_minimo')).values(
            'id', 'nombre_item', 'stock_actual', 'stock_minimo'
        )

        return Response({
            "total_items": items.count(),
            "stock_alerts": stock_alerts,
            "inventory_value": items.aggregate(total=Sum('stock_actual'))['total'] or 0
        })

    @action(detail=False, methods=['get'])
    def cash_flow(self, request):
        """
        Reporte de Flujo de Caja (Ingresos vs Egresos via Ledger/Wallet).
        """
        provider_id = request.user.perfil_prestador.id

        # Simplificado para Fase 2 basándose en ventas confirmadas
        income = Venta.objects.filter(
            provider_id=provider_id,
            estado='CONFIRMADA'
        ).aggregate(total=Sum('total'))['total'] or 0

        return Response({
            "total_income": income,
            "net_cash": income # En Fase 2 asumimos solo ingresos por ahora
        })
