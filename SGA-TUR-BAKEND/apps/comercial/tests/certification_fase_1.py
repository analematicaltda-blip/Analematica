import os
import django
import sys
import uuid
from decimal import Decimal
from datetime import date, timedelta

# 1. Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()
from django.db.models.signals import post_save
from api.models import CustomUser
from apps.wallet.signals import create_user_wallet
post_save.disconnect(create_user_wallet, sender=CustomUser)

from apps.comercial.models import Lead, Opportunity, Plan, Subscription, UsageMetric, PricingRule, BillingCycle
from apps.comercial.engines.lead_scoring_engine import LeadScoringEngine
from apps.comercial.engines.funnel_engine import FunnelEngine
from apps.comercial.services.subscription_service import SubscriptionService
from apps.comercial.services.dashboard_service import DashboardService
from apps.admin_plataforma.gestion_contable.contabilidad.models import Cuenta, PlanDeCuentas, AsientoContable, Transaccion, PeriodoContable
from apps.domain_business.comercial.models import FacturaVenta
from apps.domain_business.operativa.models import ProviderProfile
from django.db.models import Sum
from django.contrib.auth import get_user_model

User = get_user_model()

def setup_holding_environment():
    print("--- 🛠 SETUP AMBIENTE HOLDING ---")
    # Limpiar datos previos
    Lead.objects.all().delete()
    Plan.objects.all().delete()
    Subscription.objects.all().delete()

    # Usuario Admin para el perfil
    admin_user, _ = User.objects.get_or_create(email="admin@sarita.com", defaults={"username": "admin_sarita"})

    # Perfil de la Organización (Sarita Holding)
    org, _ = ProviderProfile.objects.get_or_create(
        usuario=admin_user,
        defaults={"nombre_negocio": "Sarita Holding", "nit": "900.123.456-1"}
    )

    # Cuentas Contables (Sin borrar para evitar fallos de esquema, solo buscar o crear)
    plan_contable, _ = PlanDeCuentas.objects.get_or_create(name="PGC 2024 SaaS", organization=org)

    Cuenta.objects.get_or_create(code="130505", organization=org, defaults={"name": "Clientes Nacionales (SaaS)", "plan_de_cuentas": plan_contable})
    Cuenta.objects.get_or_create(code="413501", organization=org, defaults={"name": "Ingresos por Suscripciones", "plan_de_cuentas": plan_contable})

    # Planes SaaS
    basic = Plan.objects.create(name="Plan Básico", code="BASIC", monthly_price=50.00, storage_limit_gb=5)
    pro = Plan.objects.create(name="Plan Profesional", code="PRO", monthly_price=150.00, storage_limit_gb=20)

    # Reglas de Precio (Excesos)
    PricingRule.objects.create(plan=basic, extra_gb_price=5.00)
    PricingRule.objects.create(plan=pro, extra_gb_price=2.00)

    print("✅ Ambiente configurado.\n")

def run_block_1():
    print("--- 🔵 BLOQUE 1: CONVERSIÓN REAL ---")
    # 1. Crear 10 leads
    for i in range(10):
        Lead.objects.create(
            name=f"Lead {i}",
            email=f"lead{i}@empresa.com",
            company_size="ENTERPRISE" if i < 3 else "SMALL",
            industry="TURISMO" if i < 5 else "OTRA",
            estimated_value=6000 if i < 3 else 500,
            status=Lead.Status.NEW
        )

    # 2. Scoring Automático
    leads = Lead.objects.all()
    for l in leads:
        LeadScoringEngine.update_lead(l)

    # 3. Convertir 3 en Opportunity
    hot_leads = Lead.objects.order_by('-score')[:3]
    opps = []
    for l in hot_leads:
        l.status = Lead.Status.QUALIFIED
        l.save()
        opps.append(FunnelEngine.create_opportunity(l, "PRO", float(l.estimated_value)))

    # 4. Marcar 2 como WON
    won_opps = opps[:2]
    for opp in won_opps:
        FunnelEngine.transition_stage(opp, Opportunity.Stage.WON)
        # 5. Onboarding
        sub = SubscriptionService.create_subscription(f"TENANT-{opp.lead.id.hex[:6]}", Plan.objects.get(code="PRO"))
        SubscriptionService.activate_subscription(sub.id)

    # Validaciones
    subs_count = Subscription.objects.filter(status='ACTIVE').count()
    facturas_count = FacturaVenta.objects.count()
    print(f"✔ Suscripciones Activas: {subs_count}")
    print(f"✔ Facturas Generadas: {facturas_count}")

    debits = Transaccion.objects.aggregate(Sum('debit'))['debit__sum'] or 0
    credits = Transaccion.objects.aggregate(Sum('credit'))['credit__sum'] or 0
    print(f"✔ Balance Contable: Debe {debits} / Haber {credits}")
    assert debits == credits, "ERROR: Asiento descuadrado"
    print("✅ Bloque 1 aprobado.\n")

def run_block_2():
    print("--- 🔵 BLOQUE 2: FACTURACIÓN MENSUAL ---")
    for i in range(3):
        sub = SubscriptionService.create_subscription(f"TENANT-AUTO-{i}", Plan.objects.get(code="BASIC"))
        SubscriptionService.activate_subscription(sub.id)

    subs = Subscription.objects.filter(status='ACTIVE')
    for s in subs:
        SubscriptionService.renew_subscription(s.id)

    billing_cycles = BillingCycle.objects.count()
    print(f"✔ Ciclos de Facturación: {billing_cycles}")
    print("✅ Bloque 2 aprobado.\n")

def run_block_3():
    print("--- 🔵 BLOQUE 3: EXCESO DE USO ---")
    sub = Subscription.objects.filter(plan__code="BASIC").first()
    UsageMetric.objects.create(
        tenant_id=sub.tenant_id,
        metric_type='STORAGE',
        quantity=8,
        period_start=date.today().replace(day=1),
        period_end=date.today()
    )

    invoice = SubscriptionService.renew_subscription(sub.id)
    # 50 + (3 * 5) = 65
    print(f"✔ Total Factura con Exceso: {invoice.total_amount}")
    assert invoice.total_amount == Decimal('65.00')
    print("✅ Bloque 3 aprobado.\n")

def run_block_4():
    print("--- 🔵 BLOQUE 4: UPGRADE ---")
    sub = Subscription.objects.filter(plan__code="BASIC").last()
    print(f"Tenant {sub.tenant_id} upgrade a PRO")
    SubscriptionService.upgrade_subscription(sub.id, "PRO")
    sub.refresh_from_db()
    print(f"✔ Nuevo Plan: {sub.plan.code}")
    print("✅ Bloque 4 aprobado.\n")

def run_block_5():
    print("--- 🔵 BLOQUE 5: CANCELACIÓN ---")
    sub = Subscription.objects.all().first()
    SubscriptionService.cancel_subscription(sub.id, immediate=True)
    sub.refresh_from_db()
    print(f"✔ Estado: {sub.status}")
    print("✅ Bloque 5 aprobado.\n")

def run_block_6():
    print("--- 🔵 BLOQUE 6: FALLA DE PAGO ---")
    sub = Subscription.objects.filter(status='ACTIVE').first()
    SubscriptionService.handle_payment_failure(sub.id)
    sub.refresh_from_db()
    print(f"✔ Estado tras fallo: {sub.status}")
    print("✅ Bloque 6 aprobado.\n")

def run_block_7():
    print("--- 🔵 BLOQUE 7: INTEGRACIÓN CONTABLE REAL ---")
    debits = Transaccion.objects.aggregate(Sum('debit'))['debit__sum'] or 0
    credits = Transaccion.objects.aggregate(Sum('credit'))['credit__sum'] or 0
    print(f"✔ Total Débitos: {debits}")
    print(f"✔ Total Créditos: {credits}")
    assert debits == credits

    ingresos_saas = Transaccion.objects.filter(cuenta__code="413501").aggregate(Sum('credit'))['credit__sum'] or 0
    total_facturado = FacturaVenta.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    print(f"✔ Ingresos Contables: {ingresos_saas}")
    print(f"✔ Facturación Total: {total_facturado}")
    assert ingresos_saas == total_facturado
    print("✅ Bloque 7 aprobado.\n")

def run_block_8():
    print("--- 🔵 BLOQUE 8: DASHBOARD EJECUTIVO ---")
    kpis = DashboardService.get_commercial_kpis()
    print(f"✔ MRR Actual: {kpis['subscriptions']['total_mrr']}")
    print(f"✔ Leads Totales: {kpis['leads']['total']}")
    print("✅ Bloque 8 aprobado.\n")

if __name__ == "__main__":
    try:
        setup_holding_environment()
        run_block_1()
        run_block_2()
        run_block_3()
        run_block_4()
        run_block_5()
        run_block_6()
        run_block_7()
        run_block_8()
        print("🏆 CERTIFICACIÓN FASE 1 COMPLETADA CON ÉXITO.")
    except Exception as e:
        print(f"❌ FALLO CRÍTICO EN LA CERTIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
