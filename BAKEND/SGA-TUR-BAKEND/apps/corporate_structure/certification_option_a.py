import os
import django
import uuid
from decimal import Decimal
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.corporate_structure.models import CorporateHolding, LegalEntity, TransferPricingRule, IntercompanyTransaction
from apps.corporate_structure.intercompany_engine import IntercompanyEngine
from apps.corporate_structure.transfer_pricing_engine import TransferPricingEngine
from apps.corporate_structure.consolidation_engine import ConsolidationEngine
from apps.corporate_structure.institutional_reporting import InstitutionalReporting
from apps.capital_architecture.models import Shareholder, EquityClass, ShareCertificate
from apps.capital_architecture.cap_table_engine import CapTableEngine
from apps.capital_architecture.valuation_engine import ValuationEngine
from apps.strategic_treasury.capital_allocation_engine import CapitalAllocationEngine
from apps.expansion_engine.m_and_a_simulator import MASimulator

def run_certification():
    print("🚀 INICIANDO CERTIFICACIÓN OPCIÓN A: ESCALAMIENTO FINANCIERO E INSTITUCIONAL\n")

    # Clean previous data
    CorporateHolding.objects.all().delete()
    LegalEntity.objects.all().delete()
    IntercompanyTransaction.objects.all().delete()
    TransferPricingRule.objects.all().delete()
    Shareholder.objects.all().delete()
    EquityClass.objects.all().delete()

    # 1. Corporate Structure Setup
    print("1. Configurando estructura de Holding y Entidades...")
    holding = CorporateHolding.objects.create(
        holding_name="Sarita Global Group",
        jurisdiction="Delaware",
        reporting_currency="USD"
    )

    opco = LegalEntity.objects.create(
        entity_name="Sarita OpCo Colombia",
        country="Colombia",
        tax_id="900-1",
        entity_type="OPERATING",
        parent_holding=holding,
        core_company_id=uuid.uuid4()
    )

    ipco = LegalEntity.objects.create(
        entity_name="Sarita IP Luxembourg",
        country="Luxembourg",
        tax_id="LUX-2",
        entity_type="IP_CO",
        parent_holding=holding,
        core_company_id=uuid.uuid4()
    )

    # 2. Transfer Pricing & Intercompany
    print("2. Verificando Transfer Pricing e Intercompany Billing...")
    TransferPricingRule.objects.create(
        rule_name="Standard IP Royalty",
        source_type="OPERATING",
        dest_type="IP_CO",
        markup_percentage=Decimal('5.00') # 5% Royalty
    )

    tx = TransferPricingEngine.apply_ip_royalty(opco.id, ipco.id, Decimal('100000.00'))
    print(f"   - Royalty generada: {tx.amount} {tx.currency} (Sincronizada: {tx.is_mirrored})")
    assert tx.amount == Decimal('5000.00')

    # 3. Consolidation
    print("3. Verificando Motor de Consolidación Financial...")
    consolidated = ConsolidationEngine.consolidate_holding(holding.id)
    print(f"   - EBITDA Consolidado: {consolidated['ebitda']}")
    print(f"   - Eliminaciones Intercompany: {consolidated['eliminations']}")
    assert consolidated['eliminations'] > 0

    # 4. Cap Table & Capital Architecture
    print("4. Verificando Arquitectura de Capital (Cap Table)...")
    common = EquityClass.objects.create(class_name="Common", is_preferred=False)
    founder = Shareholder.objects.create(name="Sarita Founder", shareholder_type="INDIVIDUAL", email="founder@sarita.ai", is_founder=True)

    ShareCertificate.objects.create(
        shareholder=founder,
        equity_class=common,
        quantity=1000000,
        issue_date=timezone.now().date(),
        price_per_share=Decimal('0.01')
    )

    cap_table = CapTableEngine.get_full_cap_table()
    print(f"   - Total Acciones: {cap_table['total_shares']} | Founder: {cap_table['data'][0]['percentage']}%")
    assert cap_table['total_shares'] == 1000000

    # 5. Strategic Treasury
    print("5. Verificando Capital Allocation Engine...")
    allocation = CapitalAllocationEngine.get_allocation_recommendation()
    print(f"   - Estrategia: {allocation['strategy']}")
    print(f"   - Recomendación: {allocation['recommendation']}")

    # 6. Expansion (M&A)
    print("6. Verificando M&A Simulator...")
    m_and_a = MASimulator.simulate_acquisition(Decimal('10000.00'), Decimal('80000.00'), Decimal('500000.00'))
    print(f"   - Payback estimado para adquisición: {m_and_a['payback_period_years']} años")
    assert m_and_a['payback_period_years'] > 0

    # 7. Institutional Reporting
    print("7. Generando Investor Report consolidado...")
    report = InstitutionalReporting.generate_investor_report(holding.id)
    print(f"   - Reporte generado con {len(report.keys())} secciones clave.")
    assert 'valuation' in report

    print("\n✅ CERTIFICACIÓN OPCIÓN A COMPLETADA CON ÉXITO")

if __name__ == "__main__":
    run_certification()
