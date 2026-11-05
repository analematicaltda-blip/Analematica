from typing import List
from .planner import Planner
from .executor import Executor
from .tool import Tool
from .state import State
from .logger import Logger

class Agent:
    """
    The main agent class that orchestrates the planning and execution process.
    """
    def __init__(self, objective: str, tools: List[Tool]):
        self.objective = objective
        self.tools = tools

        self.state = State(objective=objective)
        self.logger = Logger()

        self.planner = Planner(tools=self.tools, logger=self.logger)
        self.executor = Executor(tools=self.tools, logger=self.logger)

    async def run(self) -> str:
        """
        Runs the agent to achieve its objective asynchronously.
        """
        self.logger.log("System", f"Agent started with objective: {self.objective}")

        # 1. Planning (can remain synchronous)
        self.logger.log("System", "Generating plan...")
        plan = self.planner.create_plan(self.objective, self.state)
        self.state.set("plan", plan)
        self.logger.log("Planner", f"Generated Plan:\n{plan}")

        if not plan or "No plan" in plan:
            final_answer = "Could not create a plan to achieve the objective."
            self.logger.log("System", final_answer)
            return final_answer

        # 2. Execution (must be awaited)
        self.logger.log("System", "Executing plan...")
        final_answer = await self.executor.execute_plan(self.state)

        self.logger.log("System", f"Agent finished. Final Answer: {final_answer}")

        return final_answer

    def add_tool(self, tool: Tool):
        """
        Adds a new tool to the agent's toolset.
        """
        self.tools.append(tool)
        self.planner.tools = self.tools
        self.executor.tools = self.tools
        self.logger.log("System", f"Tool '{tool.name}' added.")

    def get_logs(self) -> str:
        """
        Returns the complete execution log.
        """
        return self.logger.get_full_log()
