# import csv
# from django.http import HttpResponse
# from rest_framework import viewsets, permissions, status, serializers
# from rest_framework.decorators import action
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from decimal import Decimal
#
# # Modelos locales
# from .models import Proveedor, FacturaCompra
# from .serializers import ProveedorSerializer, FacturaCompraSerializer
#
# # Modelos de otros módulos para integración
# from apps.prestadores.mi_negocio.gestion_financiera.models import CuentaBancaria, OrdenPago
# from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import JournalEntry, Transaction, ChartOfAccount
#
#
# class IsPrestadorOwner(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         # Para Proveedor y FacturaCompra, el perfil está directamente en el objeto.
#         return obj.perfil == request.user.perfil_prestador
#
# class ProveedorViewSet(viewsets.ModelViewSet):
#     serializer_class = ProveedorSerializer
#     permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]
#
#     def get_queryset(self):
#         return Proveedor.objects.filter(perfil=self.request.user.perfil_prestador)
#
# class FacturaCompraViewSet(viewsets.ModelViewSet):
#     serializer_class = FacturaCompraSerializer
#     permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]
#
#     def get_queryset(self):
#         return FacturaCompra.objects.filter(perfil=self.request.user.perfil_prestador)
#
#     def perform_create(self, serializer):
#         perfil = self.request.user.perfil_prestador
#         factura = serializer.save(perfil=perfil, creado_por=self.request.user)
#
#         # --- Creación del Asiento Contable de la Compra ---
#         try:
#             cuenta_gasto = ChartOfAccount.objects.get(code__startswith='5105', perfil=perfil) # Asumimos una cuenta de gasto
#             cuenta_cxp = ChartOfAccount.objects.get(code__startswith='2105', perfil=perfil) # Cuentas por Pagar
#         except ChartOfAccount.DoesNotExist:
#             raise serializers.ValidationError(
#                 "No se encontraron las cuentas contables requeridas para registrar la compra (Gastos '5105' o Cuentas por Pagar '2105')."
#             )
#
#         journal_entry = JournalEntry.objects.create(
#             perfil=perfil,
#             entry_date=factura.issue_date,
#             description=f"Compra según Factura No. {factura.number} de {factura.proveedor.nombre}",
#             entry_type="COMPRA",
#             user=self.request.user,
#             origin_document=factura
#         )
#
#         # Débito a Gasto/Inventario
#         Transaction.objects.create(journal_entry=journal_entry, account=cuenta_gasto, debit=factura.total)
#         # Crédito a Cuentas por Pagar
#         Transaction.objects.create(journal_entry=journal_entry, account=cuenta_cxp, credit=factura.total)
#
#     @action(detail=True, methods=['post'], url_path='pagar')
#     def pagar_factura(self, request, pk=None):
#         factura = self.get_object()
#         cuenta_bancaria_id = request.data.get('cuenta_bancaria_id')
#
#         if not cuenta_bancaria_id:
#             return Response({"error": "Debe proporcionar el ID de la cuenta bancaria para el pago."}, status=status.HTTP_400_BAD_REQUEST)
#
#         if factura.estado != FacturaCompra.Estado.POR_PAGAR:
#             return Response({"error": "La factura no está en estado 'Por Pagar'."}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             cuenta_bancaria = CuentaBancaria.objects.get(id=cuenta_bancaria_id, perfil=request.user.perfil_prestador)
#         except CuentaBancaria.DoesNotExist:
#             return Response({"error": "La cuenta bancaria no existe o no pertenece a su perfil."}, status=status.HTTP_404_NOT_FOUND)
#
#         # 1. Crear la orden de pago en el módulo financiero
#         OrdenPago.objects.create(
#             perfil=request.user.perfil_prestador,
#             cuenta_bancaria_origen=cuenta_bancaria,
#             monto=factura.total,
#             concepto=f"Pago de Factura #{factura.number} a {factura.proveedor.nombre}",
#             estado=OrdenPago.EstadoPago.PAGADA
#         )
#
#         # 2. Crear el asiento contable del pago
#         try:
#             cuenta_por_pagar = ChartOfAccount.objects.get(code='210501') # Pasivo
#             cuenta_banco = ChartOfAccount.objects.get(code='111005')    # Activo - Bancos
#         except ChartOfAccount.DoesNotExist:
#             return Response({"error": "Cuentas contables para el pago no configuradas."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         journal_entry = JournalEntry.objects.create(
#             perfil=factura.perfil,
#             entry_date=factura.issue_date, # O fecha actual
#             description=f"Pago de Factura #{factura.number}",
#             entry_type="PAGO_COMPRA",
#             user=request.user,
#             origin_document=factura
#         )
#         # Débito a Cuentas por Pagar (disminuye el pasivo)
#         Transaction.objects.create(journal_entry=journal_entry, account=cuenta_por_pagar, debit=factura.total)
#         # Crédito a Bancos (disminuye el activo)
#         Transaction.objects.create(journal_entry=journal_entry, account=cuenta_banco, credit=factura.total)
#
#         # 3. Actualizar el estado de la factura
#         factura.estado = FacturaCompra.Estado.PAGADA
#         factura.save()
#
#         return Response({"status": "Factura pagada exitosamente."}, status=status.HTTP_200_OK)
#
# class GenerarPagoMasivoProveedoresView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         factura_ids = request.data.get('factura_ids', [])
#         if not factura_ids:
#             return Response({"error": "No se proporcionaron IDs de facturas."}, status=status.HTTP_400_BAD_REQUEST)
#
#         perfil = request.user.perfil_prestador
#         facturas = FacturaCompra.objects.filter(id__in=factura_ids, perfil=perfil, estado=FacturaCompra.Estado.POR_PAGAR)
#
#         if not facturas.exists():
#             return Response({"error": "Ninguna de las facturas seleccionadas es válida para pago."}, status=status.HTTP_404_NOT_FOUND)
#
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="pagos_masivos.csv"'
#
#         writer = csv.writer(response)
#         writer.writerow(['ID Factura', 'Proveedor', 'Identificacion Proveedor', 'Monto a Pagar', 'Numero Cuenta', 'Banco'])
#
#         for factura in facturas:
#             # Asumimos que el proveedor tiene un número de cuenta guardado en el campo 'notas' para este ejemplo
#             # En una implementación real, esto debería estar en un modelo de 'InformacionBancariaProveedor'
#             writer.writerow([
#                 factura.id,
#                 factura.proveedor.nombre,
#                 factura.proveedor.identificacion,
#                 factura.total,
#                 "CTA-EJEMPLO-123", # Placeholder
#                 "BANCO-EJEMPLO" # Placeholder
#             ])
#
#         return response
