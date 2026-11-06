# # Este servicio contendrá la lógica contable para los pagos.
# from django.utils import timezone
# from apps.prestadores.mi_negocio.gestion_contable.contabilidad.services import ChartOfAccountService
# from ...gestion_financiera.models import OrdenPago
# from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import JournalEntry, Transaction
#
# class ContabilidadPagoService:
#     @staticmethod
#     def contabilizar_pago(orden_pago: OrdenPago):
#         perfil = orden_pago.perfil
#         chart_of_accounts = ChartOfAccountService(perfil)
#
#         cuenta_pasivo = chart_of_accounts.get_liability_account()
#         cuenta_banco = orden_pago.cuenta_bancaria_origen.cuenta_contable
#
#         description = f"Pago según orden #{orden_pago.id}: {orden_pago.concepto}"
#
#         journal_entry = JournalEntry.objects.create(
#             profile=perfil,
#             date=orden_pago.fecha_pago,
#             description=description,
#             is_automatic=True
#         )
#
#         Transaction.objects.create(journal_entry=journal_entry, account=cuenta_pasivo, debit=orden_pago.monto)
#         Transaction.objects.create(journal_entry=journal_entry, account=cuenta_banco, credit=orden_pago.monto)
#         journal_entry.validate_debits_and_credits()
#         return journal_entry
