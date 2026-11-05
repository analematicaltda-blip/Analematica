import os
import django
from decimal import Decimal

# Setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "puerto_gaitan_turismo.settings")
django.setup()

from apps.enterprise_core.models import StrategicRule, DecisionProposal
from apps.enterprise_core.services.decision_engine import DecisionEngine
from apps.core_erp.models import EventAuditLog

def verify_autonomy_fase_5():
    print("SARITA EOS: Iniciando Verificación de Autonomía Fase 5...")

    # Limpiar logs previos para evitar falsos positivos
    EventAuditLog.objects.filter(event_type="EXECUTIVE_ESCALATION_REQUIRED").delete()
    DecisionProposal.objects.filter(origin_metric="cash_reserve").delete()
    StrategicRule.plain_objects.filter(trigger_metric="cash_reserve").delete()

    # 1. Crear regla de autonomía nivel 2 (Umbral)
    rule, _ = StrategicRule.plain_objects.update_or_create(
        trigger_metric="cash_reserve",
        defaults={
            "condition_expression": "metric < 5000",
            "recommended_action": "TRIGGER_LIQUIDITY_ALARM",
            "autonomy_level": 2,
            "impact_threshold": Decimal('2000.00'),
            "is_active": True
        }
    )
    print(f"Regla configurada: {rule}")

    # 2. Simular actualización de métrica que supere el umbral (Escalamiento)
    print("Simulando impacto alto (2500 > 2000)...")
    DecisionEngine.process_metric_update("cash_reserve", 4000, {"estimated_impact": 2500})

    # Verificar escalamiento en logs
    escalation = EventAuditLog.objects.filter(event_type="EXECUTIVE_ESCALATION_REQUIRED").first()
    if escalation:
        print(f"✅ ESCALAMIENTO VERIFICADO: Impacto {escalation.payload['impact']} detectado.")
    else:
        print("❌ FALLO: No se detectó evento de escalamiento.")

    # 3. Verificar persistencia de propuesta con Chained Hashing
    proposal = DecisionProposal.plain_objects.filter(origin_metric="cash_reserve").first()
    if proposal and proposal.integrity_hash:
        print(f"✅ INTEGRIDAD VERIFICADA: Propuesta {proposal.id} tiene hash {proposal.integrity_hash[:8]}")
    else:
        print("❌ FALLO: Propuesta sin hash de integridad.")

if __name__ == "__main__":
    try:
        verify_autonomy_fase_5()
    except Exception as e:
        print(f"Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
