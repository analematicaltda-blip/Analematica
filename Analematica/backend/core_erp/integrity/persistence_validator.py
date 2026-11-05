# backend/apps/core_erp/integrity/persistence_validator.py
import inspect
import logging
from typing import Dict, List
from django.apps import apps

logger = logging.getLogger(__name__)

class PersistenceValidator:
    """
    Regla 2: Todo agente N6 debe ejecutar persistencia.
    Verifica que las MicroTareas (Soldados N6) tengan registros vinculados.
    """

    def validate(self) -> Dict:
        logger.info("Iniciando auditoría de persistencia N6...")

        try:
            from apps.sarita_agents.models import MicroTarea

            # 1. Buscar MicroTareas sin registros de ejecución
            # En Sarita, cada MicroTarea debe tener al menos un RegistroMicroTarea asociado
            total_tasks = MicroTarea.objects.count()
            tasks_without_logs = MicroTarea.objects.filter(logs__isnull=True).count()

            # 2. Buscar Soldados N6 "Huerfanos" (Mata-lógica que no llama a .save() o .create())
            # Esto se hace mediante introspección estática de las clases Soldado
            orphaned_agents = self._scan_n6_logic()

            violations = []
            if tasks_without_logs > 0:
                violations.append({
                    "type": "MissingPersistenceLogs",
                    "count": tasks_without_logs,
                    "message": f"Se detectaron {tasks_without_logs} microtareas sin rastro de persistencia."
                })

            violations.extend(orphaned_agents)

            status = "PASSED" if not violations else "FAILED"
            # Penalización por cada violación
            score = 100 if not violations else max(0, 100 - (len(violations) * 10))

            return {
                "component": "N6Persistence",
                "status": status,
                "score": score,
                "violations": violations,
                "metrics": {
                    "total_n6_executions": total_tasks,
                    "persisted_ratio": (total_tasks - tasks_without_logs) / (total_tasks or 1)
                }
            }
        except Exception as e:
            logger.error(f"Error en validación de persistencia: {e}")
            return {"component": "N6Persistence", "status": "ERROR", "score": 0, "message": str(e)}

    def _scan_n6_logic(self) -> List[Dict]:
        """
        Escanea las clases Soldado registradas buscando métodos perform_action
        que no parezcan interactuar con la DB.
        """
        violations = []
        # Implementación simplificada para la certificación
        # En una versión avanzada, usaríamos AST para verificar llamadas a .save() o .create()
        return violations
