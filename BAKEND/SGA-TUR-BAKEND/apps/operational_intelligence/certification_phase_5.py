import os
import django
import uuid
from decimal import Decimal
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.core_erp.event_bus import EventBus
from apps.operational_intelligence.models import SaaSMetric, ChurnRiskScore, RevenueForecast, UnitEconomics
from apps.operational_intelligence.metrics_engine import MetricsEngine
from apps.operational_intelligence.cohort_engine import CohortEngine
from apps.operational_intelligence.churn_engine import ChurnEngine
from apps.operational_intelligence.forecast_engine import ForecastEngine
from apps.operational_intelligence.unit_economics_engine import UnitEconomicsEngine
from apps.operational_intelligence.risk_scoring_engine import RiskScoringEngine

def run_certification():
    print("🚀 INICIANDO CERTIFICACIÓN FASE 5: INTELIGENCIA OPERATIVA\n")

    # Clean previous data for clean test
    SaaSMetric.objects.all().delete()
    ChurnRiskScore.objects.all().delete()
    RevenueForecast.objects.all().delete()
    UnitEconomics.objects.all().delete()

    customer_id = uuid.uuid4()

    # 1. Simulate REAL DATA Ingestion
    print("1. Inyectando datos reales (Suscripción y Uso)...")
    EventBus.emit('SUBSCRIPTION_ACTIVATED', {
        'customer_id': customer_id,
        'amount': Decimal('200.00'),
        'plan_name': 'Premium'
    })

    # Simulate usage for 14 days
    for day in range(14):
        EventBus.emit('USAGE_RECORDED', {
            'customer_id': customer_id,
            'units': 100 if day < 7 else 20, # 80% drop in last 7 days
            'feature_code': 'AI_TOKENS'
        })

    # 2. Test Metrics Engine
    print("2. Verificando Metrics Engine (MRR/ARR)...")
    metrics = MetricsEngine.calculate_all()
    print(f"   - MRR: {metrics['mrr']}")
    assert metrics['mrr'] == Decimal('200.00'), "MRR Incorrecto"

    # 3. Test Churn Engine (Risk Detection)
    print("3. Verificando Churn Engine (Detección de Riesgo por caída de uso)...")
    ChurnEngine.evaluate_customer(customer_id)
    risk = ChurnRiskScore.objects.get(customer_id=customer_id)
    print(f"   - Risk Score: {risk.risk_score} ({risk.risk_level})")
    assert risk.risk_level in ['MEDIUM', 'HIGH'], "No se detectó riesgo por caída de uso"

    # 4. Test Cohort Engine
    print("4. Verificando Cohort Engine...")
    CohortEngine.run_analysis()
    # Check if analysis was created
    assert SaaSMetric.objects.count() > 0

    # 5. Test Forecast Engine
    print("5. Verificando Forecast Engine (Proyecciones)...")
    ForecastEngine.generate_forecasts()
    forecast = RevenueForecast.objects.first()
    print(f"   - Proyección 1er mes: {forecast.projected_revenue}")
    assert forecast.projected_revenue > 0

    # 6. Test Unit Economics
    print("6. Verificando Unit Economics (LTV/CAC)...")
    UnitEconomicsEngine.calculate_all()
    econ = UnitEconomics.objects.get(customer_id=customer_id)
    print(f"   - LTV: {econ.ltv} | CAC: {econ.cac} | Margin: {econ.gross_margin}%")
    assert econ.gross_margin > 0

    # 7. Test Impact of Cancellation
    print("7. Verificando ajuste de Forecast tras Cancelación...")
    EventBus.emit('SUBSCRIPTION_CANCELLED', {
        'customer_id': customer_id,
        'amount': Decimal('200.00')
    })

    MetricsEngine.calculate_all()
    ForecastEngine.generate_forecasts()

    new_metrics = MetricsEngine.calculate_all()
    print(f"   - Nuevo MRR tras cancelación: {new_metrics['mrr']}")
    assert new_metrics['mrr'] == 0, "MRR no se ajustó tras cancelación"

    # 8. Risk Scoring Global
    print("8. Verificando Operational Risk Index...")
    RiskScoringEngine.calculate_global_risk()
    risk_index = OperationalRiskIndex.objects.last()
    print(f"   - Global Risk Index: {risk_index.overall_index}")
    print(f"   - Recomendación: {risk_index.recommendation}")

    print("\n✅ CERTIFICACIÓN FASE 5 COMPLETADA CON ÉXITO")

if __name__ == "__main__":
    run_certification()
