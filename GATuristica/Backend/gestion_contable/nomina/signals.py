# # backend/apps/prestadores/mi_negocio/gestion_contable/nomina/signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from decimal import Decimal
#
# from .models import Planilla
# from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import JournalEntry, Transaction, ChartOfAccount
#
# @receiver(post_save, sender=Planilla)
# def crear_asiento_contable_planilla(sender, instance, created, **kwargs):
#     if created:
#         try:
#             # Se asume que las cuentas existen para el perfil. Es crucial que el plan de cuentas se cree al crear un perfil.
#             cuenta_gasto_salarios = ChartOfAccount.objects.get(perfil=instance.perfil, code='510506') # Gasto - Sueldos
#             cuenta_por_pagar_salarios = ChartOfAccount.objects.get(perfil=instance.perfil, code='250501') # Pasivo - Salarios por pagar
#             cuenta_deducciones_por_pagar = ChartOfAccount.objects.get(perfil=instance.perfil, code='237005') # Pasivo - Aportes y retenciones de nómina
#         except ChartOfAccount.DoesNotExist:
#             # Si alguna cuenta esencial no existe, no se puede crear el asiento.
#             # Se podría loggear un error aquí para notificar al administrador.
#             return
#
#         # Determinar el usuario que crea el asiento.
#         user = None
#         if instance.novedades.exists():
#             first_novedad = instance.novedades.first()
#             if hasattr(first_novedad, 'empleado') and hasattr(first_novedad.empleado, 'creado_por'):
#                  user = first_novedad.empleado.creado_por
#
#         if not user:
#             # Si no se puede determinar un usuario, se aborta la creación del asiento.
#             return
#
#         journal_entry = JournalEntry.objects.create(
#             perfil=instance.perfil,
#             entry_date=instance.periodo_fin,
#             description=f"Asiento de nómina para el periodo {instance.periodo_inicio} a {instance.periodo_fin}",
#             entry_type="NOMINA",
#             user=user,
#             origin_document=instance
#         )
#
#         # Débito a la cuenta de gasto por el total devengado
#         Transaction.objects.create(
#             journal_entry=journal_entry,
#             account=cuenta_gasto_salarios,
#             debit=instance.total_devengado,
#             credit=Decimal('0.00')
#         )
#
#         # Crédito a la cuenta por pagar por el total neto
#         Transaction.objects.create(
#             journal_entry=journal_entry,
#             account=cuenta_por_pagar_salarios,
#             debit=Decimal('0.00'),
#             credit=instance.total_neto
#         )
#
#         # Crédito a la cuenta de deducciones para balancear el asiento
#         if instance.total_deducciones > 0:
#             Transaction.objects.create(
#                 journal_entry=journal_entry,
#                 account=cuenta_deducciones_por_pagar,
#                 debit=Decimal('0.00'),
#                 credit=instance.total_deducciones
#             )
