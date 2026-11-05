import logging
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from .models import SaaSSubscription, SaaSInvoice, SaaSInvoiceLine
from .plan_model import SaaSPlan
from apps.core_erp.billing_engine import BillingEngine
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class SubscriptionEngine:
    """
    Gestiona el ciclo de vida de las suscripciones SaaS y su facturación automática.
    """

    @classmethod
    @transaction.atomic
    def activate_subscription(cls, company_id, plan_id, billing_cycle='MONTHLY', lead_id=None):
        """
        Activa una nueva suscripción para una empresa.
        Hardening 100%: Automated lead-to-tenant conversion.
        """
        plan = SaaSPlan.objects.get(id=plan_id)
        if lead_id:
            from .lead_model import SaaSLead
            lead = SaaSLead.objects.get(id=lead_id)
            lead.status = SaaSLead.Status.CONVERTED
            lead.save()

        # 1. Determinar Fechas y MRR
        start_date = timezone.now().date()
        if billing_cycle == 'MONTHLY':
            renewal_date = start_date + timedelta(days=30)
            mrr = plan.monthly_price
        else:
            renewal_date = start_date + timedelta(days=365)
            mrr = plan.monthly_price # El MRR sigue siendo mensual aunque pague anual

        # 2. Crear Suscripción
        subscription = SaaSSubscription.objects.create(
            company_id=company_id,
            plan=plan,
            status=SaaSSubscription.Status.ACTIVE,
            renewal_date=renewal_date,
            billing_cycle=billing_cycle,
            mrr=mrr
        )

        # 3. Generar Factura Inicial
        invoice = cls.generate_invoice(subscription)

        # 4. Emitir Evento
        EventBus.emit('SUBSCRIPTION_ACTIVATED', {
            'subscription_id': str(subscription.id),
            'company_id': str(company_id),
            'plan_name': plan.name,
            'plan_code': plan.code,
            'mrr': float(mrr)
        })

        # 5. Trigger Automated Onboarding
        EventBus.emit('TENANT_PROVISIONING_REQUESTED', {
            'tenant_id': str(company_id),
            'name': plan.name, # Using plan name as default for provisioned profile
            'plan_code': plan.code
        })

        return subscription

    @classmethod
    def generate_invoice(cls, subscription: SaaSSubscription):
        """
        Crea la factura para el periodo actual de la suscripción.
        """
        amount = subscription.plan.monthly_price if subscription.billing_cycle == 'MONTHLY' else subscription.plan.annual_price

        invoice = SaaSInvoice.objects.create(
            subscription=subscription,
            company_id=subscription.company_id,
            number=f"INV-SAAS-{timezone.now().strftime('%Y%m%d')}-{subscription.id.hex[:6].upper()}",
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=5),
            total_amount=0 # Se calcula abajo
        )

        SaaSInvoiceLine.objects.create(
            invoice=invoice,
            description=f"Suscripción SaaS - Plan {subscription.plan.name} ({subscription.billing_cycle})",
            quantity=1,
            unit_price=amount,
            subtotal=amount
        )

        # Usar BillingEngine del Core para cálculos
        BillingEngine.issue_invoice(invoice)

        # Generar Impacto Contable en el ERP del Admin
        cls.create_accounting_impact(invoice)

        return invoice

    @classmethod
    def create_accounting_impact(cls, invoice: SaaSInvoice):
        """
        Crea el asiento contable en el ERP del Super Admin para la factura emitida.
        Impacto: 130505 (CXC Clientes) DB vs 413501 (Ingresos SaaS) CR
        """
        from apps.admin_plataforma.gestion_contable.contabilidad.models import (
            AdminJournalEntry, AdminAccountingTransaction, AdminAccount, AdminFiscalPeriod
        )
        from apps.core_erp.accounting_engine import AccountingEngine

        # 1. Obtener Periodo Fiscal Abierto
        period = AdminFiscalPeriod.objects.filter(status='open').first()
        if not period:
             # Fallback: crear uno para propósitos de la demo si no existe (solo en desarrollo)
             # Intentar obtener el perfil de la holding primero
             from apps.domain_business.operativa.models import ProviderProfile
             from api.models import CustomUser
             admin_user = CustomUser.objects.filter(is_superuser=True).first()
             holding_profile, _ = ProviderProfile.objects.get_or_create(
                 nombre_negocio="Sarita Holding",
                 defaults={'usuario': admin_user}
             )

             period = AdminFiscalPeriod.objects.create(
                 period_start=timezone.now().date().replace(day=1),
                 period_end=timezone.now().date().replace(day=28), # simplificado
                 status='open',
                 organization=holding_profile
             )

        # 1.5 Obtener/Crear Perfil de la Holding (Sarita) y Plan de Cuentas
        from apps.domain_business.operativa.models import ProviderProfile
        from apps.admin_plataforma.gestion_contable.contabilidad.models import AdminChartOfAccounts
        from api.models import CustomUser

        # Intentar obtener el superusuario para asociarlo al perfil de la holding
        admin_user = CustomUser.objects.filter(is_superuser=True).first()

        holding_profile, _ = ProviderProfile.objects.get_or_create(
            nombre_negocio="Sarita Holding",
            defaults={'usuario': admin_user}
        )

        chart, _ = AdminChartOfAccounts.objects.get_or_create(
            name="Plan Contable Holding Sarita",
            organization=holding_profile
        )

        # 2. Obtener/Crear Cuentas Mandatarias en Admin
        cxc_account, _ = AdminAccount.objects.get_or_create(
            code='130505',
            chart_of_accounts=chart,
            defaults={'name': 'Cuentas por Cobrar Clientes SaaS', 'type': 'asset', 'organization': holding_profile}
        )
        income_account, _ = AdminAccount.objects.get_or_create(
            code='413501',
            chart_of_accounts=chart,
            defaults={'name': 'Ingresos Suscripciones SaaS', 'type': 'income', 'organization': holding_profile}
        )

        # 3. Crear Asiento
        entry = AdminJournalEntry.objects.create(
            date=invoice.issue_date,
            period=period,
            reference=invoice.number,
            description=f"Reconocimiento de ingreso SaaS - {invoice.subscription.company_id}",
            organization=holding_profile
        )

        # Línea de CXC (Débito)
        AdminAccountingTransaction.objects.create(
            journal_entry=entry,
            account=cxc_account,
            account_code=cxc_account.code,
            debit=invoice.total_amount,
            credit=0
        )

        # Línea de Ingreso (Crédito)
        AdminAccountingTransaction.objects.create(
            journal_entry=entry,
            account=income_account,
            account_code=income_account.code,
            debit=0,
            credit=invoice.total_amount
        )

        # 4. Postear Asiento vía Core Engine
        AccountingEngine.post_journal_entry(entry)

        logger.info(f"Impacto contable generado para factura {invoice.number}")
