# backend/apps/core_erp/integrity/system_integrity_certifier.py
import json
import logging
from datetime import datetime
from typing import Dict, List

from .architecture_validator import ArchitectureValidator
from .persistence_validator import PersistenceValidator
from .accounting_validator import AccountingValidator
from .event_flow_validator import EventFlowValidator

logger = logging.getLogger(__name__)

class SystemIntegrityCertifier:
    """
    Orquestador Central de Certificación (Fase 7).
    Ejecuta todas las auditorías y emite el certificado final.
    """

    def __init__(self):
        self.validators = [
            ArchitectureValidator(),
            PersistenceValidator(),
            AccountingValidator(),
            EventFlowValidator()
        ]

    def run_full_certification(self) -> Dict:
        """
        Ejecuta el proceso completo de auditoría automática.
        """
        logger.warning(">>> INICIANDO CERTIFICACIÓN DE INTEGRIDAD TOTAL (FASE 7) <<<")

        results = []
        for validator in self.validators:
            try:
                results.append(validator.validate())
            except Exception as e:
                logger.error(f"Fallo crítico en validador {validator.__class__.__name__}: {e}")
                results.append({
                    "component": validator.__class__.__name__,
                    "status": "CRITICAL_ERROR",
                    "score": 0,
                    "message": str(e)
                })

        # Calcular nivel de certificación (A-D)
        avg_score = sum(r.get("score", 0) for r in results) / len(results)
        level = self._calculate_level(avg_score)

        report = {
            "certification_id": f"CERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "overall_status": "VERIFIED" if level == 'A' else "WARNING" if level in ['B', 'C'] else "CRITICAL",
            "certification_level": level,
            "integrity_score": round(avg_score, 2),
            "components": results,
            "verdict": "SISTEMA LISTO PARA PRODUCCIÓN" if level == 'A' else "SISTEMA REQUIERE SUBSANACIÓN INMEDIATA"
        }

        # Guardar reporte en disco
        with open("system_integrity_report.json", "w") as f:
            json.dump(report, f, indent=4)

        logger.warning(f">>> CERTIFICACIÓN FINALIZADA: NIVEL {level} (Score: {avg_score}) <<<")
        return report

    def _calculate_level(self, score: float) -> str:
        if score >= 95: return "A" # Perfecto
        if score >= 80: return "B" # Menor riesgo
        if score >= 60: return "C" # Riesgo moderado
        return "D" # Crítico
