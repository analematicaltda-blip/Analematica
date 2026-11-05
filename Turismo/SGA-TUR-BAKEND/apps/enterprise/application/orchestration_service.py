import logging
from django.utils import timezone
from ..domain.workflow import EnterpriseWorkflow, WorkflowStep
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class OrchestrationService:
    """
    Orchestrates complex multi-domain workflows.
    """

    @staticmethod
    def start_workflow(tenant_id, name, context_data=None):
        """
        Initializes and starts a new enterprise workflow.
        """
        workflow = EnterpriseWorkflow.objects.create(
            tenant_id=tenant_id,
            name=name,
            context_data=context_data or {},
            status=EnterpriseWorkflow.Status.RUNNING,
            started_at=timezone.now()
        )

        logger.info(f"EOS Orchestrator: Starting workflow {name} ({workflow.id})")
        OrchestrationService._execute_next_step(workflow)
        return workflow

    @staticmethod
    def _execute_next_step(workflow):
        """
        Finds the next pending step and executes it.
        """
        next_step = workflow.steps.filter(status='PENDING').first()

        if not next_step:
            workflow.status = EnterpriseWorkflow.Status.COMPLETED
            workflow.finished_at = timezone.now()
            workflow.save()
            logger.info(f"EOS Orchestrator: Workflow {workflow.name} completed successfully.")
            return

        next_step.status = 'RUNNING'
        next_step.save()

        try:
            # Dispatch action via EventBus or direct Service call
            # Standard for Phase D: Use EventBus to maintain decoupling
            payload = {
                "workflow_id": str(workflow.id),
                "step_id": str(next_step.id),
                "tenant_id": str(workflow.tenant_id),
                "params": next_step.params,
                "context": workflow.context_data
            }

            EventBus.emit(f"EOS_ACTION_{next_step.action_name}", payload)

            # Note: In a real system, the step completion would be asynchronous.
            # For Phase D, we'll assume synchronous or semi-synchronous progression.

        except Exception as e:
            next_step.status = 'FAILED'
            next_step.error_log = str(e)
            next_step.save()
            workflow.status = EnterpriseWorkflow.Status.FAILED
            workflow.save()
            logger.error(f"EOS Orchestrator: Step {next_step.name} failed: {e}")

    @staticmethod
    def complete_step(step_id, result_data=None):
        """
        Callback to signal step completion.
        """
        step = WorkflowStep.objects.get(id=step_id)
        step.status = 'COMPLETED'
        if result_data:
            step.workflow.context_data.update(result_data)
            step.workflow.save()
        step.save()

        OrchestrationService._execute_next_step(step.workflow)
