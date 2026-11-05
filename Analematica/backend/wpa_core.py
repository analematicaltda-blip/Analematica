import uuid
import logging
import time
from datetime import datetime
from django.utils import timezone
from .models import WorkflowDefinition, WorkflowInstance, StepExecution

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """
    Motor WPA (Workflow de Procesamiento Autónomo).
    Ejecuta planes de acción autorizados por el MCP.
    """

    def __init__(self):
        self.executor = ExecutorLayer()

    def launch_workflow(self, workflow_name, correlation_id, input_data):
        """
        Inicia una nueva instancia de un workflow.
        """
        try:
            definition = WorkflowDefinition.objects.get(name=workflow_name, is_active=True)
            instance = WorkflowInstance.objects.create(
                definition=definition,
                correlation_id=correlation_id,
                input_data=input_data,
                status=WorkflowInstance.State.CREATED
            )
            logger.info(f"WPA: Workflow {workflow_name} lanzado (Instancia: {instance.id})")

            # En producción esto se dispararía vía Celery
            self.execute_instance(instance.id)
            return instance.id
        except WorkflowDefinition.DoesNotExist:
            logger.error(f"WPA: Error - Definición de workflow '{workflow_name}' no encontrada")
            return None

    def execute_instance(self, instance_id):
        """
        Procesa los pasos de una instancia de workflow.
        """
        instance = WorkflowInstance.objects.get(id=instance_id)
        instance.status = WorkflowInstance.State.RUNNING
        instance.started_at = timezone.now()
        instance.save()

        steps = instance.definition.definition.get('steps', [])
        success = True
        failed_step_idx = -1

        for i, step in enumerate(steps):
            instance.current_step_index = i
            instance.save()

            step_exec = StepExecution.objects.create(
                instance=instance,
                step_name=step['name'],
                status='RUNNING'
            )

            res = self.executor.execute_step(step, instance.input_data)

            if res['success']:
                step_exec.status = 'COMPLETED'
                step_exec.save()
                # Actualizar output data si es necesario
                if 'output' in res:
                    instance.output_data.update(res['output'])
            else:
                step_exec.status = 'FAILED'
                step_exec.last_error = res.get('error', 'Error desconocido')
                step_exec.save()
                success = False
                failed_step_idx = i
                break

        if success:
            instance.status = WorkflowInstance.State.COMPLETED
            instance.finished_at = timezone.now()
            instance.save()
            logger.info(f"WPA: Workflow {instance.id} completado con éxito")
        else:
            instance.status = WorkflowInstance.State.FAILED
            instance.save()
            logger.warning(f"WPA: Workflow {instance.id} falló en el paso {steps[failed_step_idx]['name']}")
            self.compensate(instance, failed_step_idx)

    def compensate(self, instance, failed_idx):
        """
        Motor de Compensación (SAGA).
        Revierte los pasos completados en orden inverso.
        """
        instance.status = WorkflowInstance.State.COMPENSATING
        instance.save()

        steps = instance.definition.definition.get('steps', [])
        # Pasos a compensar: del fallido-1 hacia atrás
        for i in range(failed_idx - 1, -1, -1):
            step = steps[i]
            logger.info(f"WPA: Compensando paso {step['name']}")

            # Buscar la ejecución del paso original
            original_exec = StepExecution.objects.filter(instance=instance, step_name=step['name']).first()

            res = self.executor.compensate_step(step, instance.input_data)
            if res['success'] and original_exec:
                original_exec.is_compensated = True
                original_exec.save()

        instance.status = WorkflowInstance.State.ROLLED_BACK
        instance.finished_at = timezone.now()
        instance.save()
        logger.info(f"WPA: Workflow {instance.id} revertido exitosamente (SAGA Complete)")

class ExecutorLayer:
    """
    Capa de ejecución técnica de pasos.
    """
    def execute_step(self, step, input_data):
        logger.info(f"WPA Executor: Ejecutando acción '{step['action']}'")
        # Simulación de llamadas a microservicios/APIs
        time.sleep(0.1)

        # Simulación de fallo controlado para pruebas
        if input_data.get('force_fail_at') == step['name']:
            return {'success': False, 'error': f"Fallo forzado en {step['name']}"}

        return {'success': True, 'output': {f"{step['name']}_res": "OK"}}

    def compensate_step(self, step, input_data):
        logger.info(f"WPA Executor: Ejecutando compensación '{step.get('compensation', 'N/A')}'")
        time.sleep(0.1)
        return {'success': True}
