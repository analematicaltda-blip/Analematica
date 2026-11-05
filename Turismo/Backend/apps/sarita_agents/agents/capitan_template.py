# backend/apps/sarita_agents/agents/capitan_template.py
 
import logging
from celery import group, chord
from apps.sarita_agents.models import Mision, PlanTáctico, TareaDelegada
from ..tasks import ejecutar_tarea_teniente, consolidar_plan_tactico

logger = logging.getLogger(__name__)
 

class CapitanTemplate:
    """
    Plantilla base para todos los Capitanes.
    Define el ciclo de vida de planificación, delegación y reporte.
    """
    def __init__(self, coronel):
        self.coronel = coronel
        self.tenientes = self._get_tenientes()
 
        logger.info(f"CAPITÁN ({self.__class__.__name__}): Inicializado. Tenientes listos.")
 

    def handle_order(self, mision: Mision):
        """
        Recibe una orden (misión) del Coronel, la procesa y gestiona su ejecución.
        """
 
        logger.info(f"CAPITÁN ({self.__class__.__name__}): Orden recibida para misión {mision.id}")

        plan = self.plan(mision)
        # El método delegate ahora es asíncrono y no devuelve resultados directamente.
        self.delegate(plan)

        # Si estamos en EAGER_MODE, el plan ya debería estar completado.
        from django.conf import settings
        if getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
            plan.refresh_from_db()
            return {
                "status": plan.estado,
                "captain_report": {
                    "captain": self.__class__.__name__,
                    "status": plan.estado,
                    "details": [t.estado for t in plan.tareas.all()]
                }
            }

        # El reporte se genera y envía de forma asíncrona por la tarea de consolidación.
        # Devolvemos un reporte intermedio.
        return {
            "status": "PROCESSING",
            "message": f"El plan {plan.id} ha sido encolado para ejecución asíncrona."
        }

    def handle_directive(self, mision: Mision):
        """Alias para handle_order."""
        return self.handle_order(mision)
 

    def plan(self, mision: Mision) -> PlanTáctico:
        """
        Crea un plan táctico para cumplir la misión y lo persiste en la BD.
        Este método debe ser implementado por cada Capitán concreto.
        """
        raise NotImplementedError("El método plan() debe ser implementado por cada Capitán.")

 
    def delegate(self, plan: PlanTáctico):
        """
        Crea un grupo de tareas de tenientes y las ejecuta en un chord.
        El callback del chord se encargará de la consolidación.
        """
        logger.info(f"CAPITÁN ({self.__class__.__name__}): Construyendo chord para el plan {plan.id}...")
        plan.estado = 'EN_EJECUCION'
        plan.save()

        # --- SOPORTE EAGER MODE PARA ESTABILIZACIÓN ---
        from django.conf import settings
        eager_mode = getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False)
        if eager_mode:
            logger.info(f"CAPITÁN ({self.__class__.__name__}): Ejecutando síncronamente (EAGER MODE)...")
        # ---------------------------------------------

        header = []
        for _, tarea_info in plan.pasos_del_plan.items():
            teniente_name = tarea_info.get("teniente", "default")

            # S-0.4: Prevenir escalado de permisos y ejecución fuera del roster
            if teniente_name not in self.tenientes:
                logger.error(f"S-0: Capitán {self.__class__.__name__} intentó delegar a Teniente {teniente_name} fuera de su roster.")
                continue

            tarea = TareaDelegada.objects.create(
                plan_tactico=plan,
                teniente_asignado=teniente_name,
                descripcion_tarea=tarea_info.get("descripcion", "N/A"),
 
                parametros=tarea_info.get("parametros", {}),
                estado='EN_COLA'
            )

            if eager_mode:
                # Ejecución secuencial inmediata
                ejecutar_tarea_teniente(tarea_id=str(tarea.id))
            else:
                header.append(ejecutar_tarea_teniente.s(tarea_id=str(tarea.id)))

        if eager_mode:
            # En modo EAGER, pasamos una lista vacía de resultados ya que la tarea
            # consolidar_plan_tactico espera los resultados del grupo como primer argumento.
            consolidar_plan_tactico([], plan_id=str(plan.id))
            logger.info(f"Delegación para el plan {plan.id} completada.")
        else:
            callback = consolidar_plan_tactico.s(plan_id=str(plan.id))
            # Crear y ejecutar el chord
            chord(group(header))(callback)
            logger.info(f"Chord para el plan {plan.id} ha sido encolado.")
 

    def _get_tenientes(self) -> dict:
        """
        Carga el roster de Tenientes bajo el mando de este Capitán.
        Este método debe ser implementado por cada Capitán concreto.
        """
        raise NotImplementedError("El método _get_tenientes() debe ser implementado por cada Capitán.")
