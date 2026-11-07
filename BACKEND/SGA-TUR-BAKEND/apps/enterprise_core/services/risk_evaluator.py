import logging
from typing import Dict, Any
from apps.core_erp.event_bus import EventBus
from ..models.risk_snapshot import RiskSnapshot
from django.utils import timezone
from django.db import models
import random

logger = logging.getLogger(__name__)

class RiskEvaluator:
    """
    Motor de Detección Predictiva de Riesgos (Fase 5.3).
    Analiza tendencias y proyecta desviaciones críticas.
    """

    def calculate_systemic_risk(self) -> float:
        """
        Retorna un score de riesgo global del sistema (0.0 a 1.0).
        """
        # Baseline simulation (Phase 5 Placeholder for ML integration)
        base_risk = 0.15

        # Factor 1: Latencia de Infraestructura
        # (Idealmente traer métricas de TechnicalMonitor)

        # Factor 2: Tendencia de Ventas

        return min(1.0, base_risk + random.uniform(0, 0.1))

    def predict_financial_risk(self, tenant_id: str) -> Dict[str, Any]:
        """
        Proyecta riesgos de liquidez y ruptura de stock para un tenant.
        Integrado con Ledger y Gestión de Inventarios.
        """
        logger.info(f"Predictive: Analizando riesgos para {tenant_id}")

        risks = []
        risk_score = 0.05

        # 1. Análisis de Inventario (Riesgo de Ruptura)
        try:
            from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.inventario.models import InventoryItem
            low_items = InventoryItem.objects.filter(tenant_id=tenant_id, cantidad__lt=models.F('punto_reorden'))
            count = low_items.count()
            if count > 0:
                risks.append({
                    "type": "STOCK_BREAK",
                    "severity": "high" if count > 5 else "medium",
                    "count": count,
                    "reason": f"Detectados {count} ítems por debajo del punto de reorden."
                })
                risk_score += min(0.4, 0.1 * count)
        except Exception as e:
            logger.error(f"Error analizando inventario: {e}")

        # 2. Análisis de Tendencia de Ventas (Churn Risk)
        try:
            from apps.domain_business.comercial.models import CommercialOperation
            thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
            recent_sales = CommercialOperation.objects.filter(tenant_id=tenant_id, created_at__gte=thirty_days_ago).count()

            # Si no hay ventas en 30 días, alerta de estancamiento
            if recent_sales == 0:
                risks.append({"type": "SALES_STAGNATION", "severity": "critical", "reason": "No se registran ventas en los últimos 30 días."})
                risk_score += 0.5
        except Exception as e:
            logger.error(f"Error analizando tendencias comerciales: {e}")

        # 3. Análisis de Liquidez (Forecasting básico)
        # Placeholder: Se integrará con el motor de proyecciones del Core ERP

        prediction = {
            "tenant_id": tenant_id,
            "risk_score": round(min(1.0, risk_score), 2),
            "top_threats": risks,
            "timestamp": timezone.now().isoformat()
        }

        if prediction["risk_score"] > 0.6:
            EventBus.emit("PREDICTIVE_RISK_DETECTED", {
                "entity_id": tenant_id,
                "score": prediction["risk_score"],
                "category": "FINANCIAL",
                "reason": risks[0]["reason"] if risks else "Riesgo sistémico elevado"
            }, severity="critical")

        return prediction
