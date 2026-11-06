from celery import shared_task
from .models import AgentExecution
from .agent import Agent
from .tool_registry import get_tools
import asyncio

@shared_task(bind=True)
def run_agent_execution(self, execution_id: str):
    """
    Celery task to run a SADI agent execution asynchronously.
    """
    async def _run_async():
        try:
            # Use Django's async ORM methods
            execution = await AgentExecution.objects.aget(id=execution_id)
            execution.status = AgentExecution.Status.RUNNING
            await execution.asave()

            # Load the actual tools from the registry
            tools = get_tools()

            # Initialize and run the agent
            agent = Agent(objective=execution.objective, tools=tools)
            final_result = await agent.run()

            # Save the complete results to the database
            execution.plan = agent.state.get("plan")
            execution.execution_history = agent.state.get("execution_history")
            execution.logs = agent.get_logs()
            execution.final_result = final_result
            execution.status = AgentExecution.Status.COMPLETED
            await execution.asave()

            return f"Execution {execution_id} completed successfully."

        except AgentExecution.DoesNotExist:
            return f"Error: AgentExecution with id {execution_id} not found."
        except Exception as e:
            try:
                # Attempt to save the error state
                execution = await AgentExecution.objects.aget(id=execution_id)
                execution.status = AgentExecution.Status.FAILED
                execution.final_result = f"An unexpected error occurred: {str(e)}"
                execution.logs += f"\n\n[FATAL ERROR] Task failed unexpectedly: {str(e)}"
                await execution.asave()
            except AgentExecution.DoesNotExist:
                pass  # Cannot update status if the object doesn't exist

            # Re-raise the exception to have Celery mark the task as FAILED
            raise e

    # Run the async function within the synchronous Celery task
    return asyncio.run(_run_async())
