# backend/apps/sarita_agents/agents/sargento_template.py

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SergeantTemplate:
    """
    NIVEL 5 — SARGENTOS (Coordinadores Operativos)
    Reciben órdenes del Teniente, dividen el trabajo y supervisan a 5 Soldados.
    """
    def __init__(self, teniente=None):
        self.teniente = teniente
        self.soldiers = self._get_soldiers()
        if len(self.soldiers) != 5:
            logger.warning(f"SARGENTO ({self.__class__.__name__}): Regla estructural violada. Se requieren exactamente 5 soldados, se encontraron {len(self.soldiers)}.")

    def _get_soldiers(self) -> List[Any]:
        """Debe retornar una lista de 5 instancias de Soldados."""
        raise NotImplementedError("El método _get_soldiers() debe ser implementado por cada Sargento.")

    def handle_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recibe la orden del Teniente, la divide en microtareas para sus 5 soldados.
        """
        return self.handle_directive(order_params)

    def handle_directive(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alias para integración sistémica Fase 4.1.
        """
        logger.info(f"SARGENTO ({self.__class__.__name__}): Orden recibida. Fraccionando para ejecución manual.")

        microtasks = self.plan_microtasks(directive)

        # Intentar obtener la tarea_padre de la DB si es posible (vía Teniente)
        tarea_padre_id = directive.get("tarea_delegada_id")
        from apps.sarita_agents.models import TareaDelegada, MicroTarea

        results = []
        # Ejecución secuencial por ahora para estabilidad en esta fase
        for i, soldier in enumerate(self.soldiers):
            task_data = microtasks[i] if i < len(microtasks) else {"action": "idle"}

            # Persistencia de la MicroTarea
            mt_obj = None
            if tarea_padre_id:
                mt_obj = MicroTarea.objects.create(
                    tarea_padre_id=tarea_padre_id,
                    soldado_asignado=soldier.__class__.__name__,
                    descripcion=task_data.get("type", "Ejecución manual"),
                    parametros=task_data,
                    estado='EN_PROGRESO'
                )
                task_data["micro_tarea_id"] = str(mt_obj.id)

            logger.info(f"SARGENTO ({self.__class__.__name__}): Delegando a Soldado {i+1} ({soldier.__class__.__name__})")
            res = soldier.execute(task_data)

            if mt_obj:
                mt_obj.estado = 'COMPLETADA' if res.get("status") == "SUCCESS" else 'FALLIDA'
                mt_obj.save()

                from apps.sarita_agents.models import RegistroMicroTarea
                RegistroMicroTarea.objects.create(
                    micro_tarea=mt_obj,
                    exitoso=(res.get("status") == "SUCCESS"),
                    resultado=res.get("result")
                )

            results.append(res)

        return self.consolidate_results(results)

    def plan_microtasks(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Divide el trabajo en un máximo de 5 bloques."""
        raise NotImplementedError("El método plan_microtasks() debe ser implementado.")

    def consolidate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolida lo ejecutado por los soldados para reportar al Teniente."""
        success_count = sum(1 for r in results if r.get("status") == "SUCCESS")
        return {
            "status": "COMPLETED" if success_count > 0 else "FAILED",
            "executed_by": self.__class__.__name__,
            "success_rate": f"{success_count}/5",
            "details": results
        }
