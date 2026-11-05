# backend/apps/sarita_agents/agents/teniente_template.py

 
import logging
from apps.sarita_agents.models import TareaDelegada, RegistroDeEjecucion

logger = logging.getLogger(__name__)
 

class TenienteTemplate:
    """
    Plantilla base para todos los Tenientes.
    Son los ejecutores finales de las tareas atómicas.
    """
    def execute_task(self, tarea: TareaDelegada) -> dict:
        """
        Ejecuta una tarea, registrando el proceso en la BD.
        """
 
        teniente_name = self.__class__.__name__
        logger.info(f"TENIENTE ({teniente_name}): Ejecutando tarea {tarea.id} - {tarea.descripcion_tarea}")
 

        tarea.estado = 'EN_PROGRESO'
        tarea.save()

        log = RegistroDeEjecucion.objects.create(
            tarea_delegada=tarea,
            exitoso=False # Asumimos fallo hasta que se complete
        )

        try:
            # --- LA LÓGICA DE NEGOCIO REAL SE IMPLEMENTA AQUÍ ---
            # En Fase 4.1, pasamos el ID de la tarea para trazabilidad de Sargentos/Soldados
            params = tarea.parametros.copy()
            params["tarea_delegada_id"] = str(tarea.id)

            resultado = self.perform_action(params)

            tarea.estado = 'COMPLETADA'
            log.exitoso = True
            log.resultado = resultado

 
            logger.info(f"TENIENTE ({teniente_name}): Tarea {tarea.id} completada con éxito.")
 
            return {"status": "SUCCESS", "result": resultado}

        except Exception as e:
            tarea.estado = 'FALLIDA'
            log.salida_log = str(e)

 
            logger.error(f"TENIENTE ({teniente_name}): Tarea {tarea.id} falló - {e}", exc_info=True)
 
            return {"status": "ERROR", "message": str(e)}

        finally:
            tarea.save()
            log.save()

    def handle_directive(self, tarea: TareaDelegada):
        """Alias para execute_task."""
        return self.execute_task(tarea)

    def perform_action(self, parametros: dict):
        """
        Este es el método que las subclases deben implementar.
        Contiene la lógica de negocio atómica.
        """
        raise NotImplementedError("El método perform_action() debe ser implementado por cada Teniente.")
