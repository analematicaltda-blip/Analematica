# from decimal import Decimal
# from django.utils import timezone
# from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import JournalEntry, Transaction
# from apps.prestadores.mi_negocio.gestion_contable.contabilidad.services import ChartOfAccountService
# from ..nomina.models import Planilla, DetalleLiquidacion
#
# class ContabilidadNominaService:
#     def __init__(self, planilla: Planilla):
#         self.planilla = planilla
#         self.perfil = planilla.perfil
#         self.chart_of_accounts = ChartOfAccountService(self.perfil)
#
#     def contabilizar_liquidacion(self):
#         description = f"Contabilización nómina {self.planilla.periodo_inicio} a {self.planilla.periodo_fin}"
#         journal_entry = JournalEntry.objects.create(
#             profile=self.perfil,
#             date=timezone.now().date(),
#             description=description,
#             is_automatic=True
#         )
#
#         for detalle in self.planilla.detalles_liquidacion.all():
#             # Gastos (Débito)
#             Transaction.objects.create(journal_entry=journal_entry, account=self.chart_of_accounts.get_expense_account(), debit=detalle.valor_prima, description=f"Gasto Prima {detalle.empleado}")
#             Transaction.objects.create(journal_entry=journal_entry, account=self.chart_of_accounts.get_expense_account(), debit=detalle.valor_cesantias, description=f"Gasto Cesantías {detalle.empleado}")
#             # ... (más gastos)
#
#             # Pasivos (Crédito)
#             Transaction.objects.create(journal_entry=journal_entry, account=self.chart_of_accounts.get_liability_account(), credit=detalle.valor_prima, description=f"Provisión Prima {detalle.empleado}")
#             Transaction.objects.create(journal_entry=journal_entry, account=self.chart_of_accounts.get_liability_account(), credit=detalle.valor_cesantias, description=f"Provisión Cesantías {detalle.empleado}")
#             # ... (más pasivos)
#
#         journal_entry.validate_debits_and_credits()
#         return journal_entry
