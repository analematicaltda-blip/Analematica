from typing import List
from .tool import Tool
from .state import State
from .logger import Logger
import json
import os
from openai import OpenAI
from django.conf import settings

class Planner:
    """
    Generates a step-by-step plan for the agent to follow.
    """
    def __init__(self, tools: List[Tool], logger: Logger):
        self.tools = tools
        self.logger = logger
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def create_plan(self, objective: str, state: State) -> str:
        """
        Creates a plan based on the objective and available tools.
        """
        prompt = self._build_prompt(objective)
        self.logger.log("Planner", f"Generating plan with prompt...")

        try:
            response = self._call_llm(prompt)
            plan_json = self._extract_json(response)
            self.logger.log("Planner", f"Received plan from LLM: {plan_json}")
            return plan_json

        except Exception as e:
            self.logger.log("Planner", f"Error creating plan: {e}", "ERROR")
            return '{"error": "No plan could be created."}'

    def _call_llm(self, prompt: str) -> str:
        """
        Calls the OpenAI API to generate a plan based on the prompt.
        """
        try:
            response = self.client.chat.completions.create(
                model=settings.SADI_AGENT_LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a world-class planner AI. Your job is to create a step-by-step JSON plan based on a user's objective and the tools you have available."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.log("Planner", f"Error calling LLM: {e}", "ERROR")
            return '{"error": "Failed to generate plan from LLM."}'

    def _build_prompt(self, objective: str) -> str:
        """
        Builds the prompt to be sent to the LLM for planning.
        """
        tools_str = "\n".join([f"- {tool.name}: {tool.description} (params: {tool.params})" for tool in self.tools])

        prompt = f"""
Objective: {objective}

You have the following tools at your disposal:
{tools_str}

Your final output MUST be a valid JSON object containing a single key "plan" which is an array of steps.
Example:
{{
  "plan": [
    {{
        "step": 1,
        "thought": "I need to do this first.",
        "tool": "tool_name_1",
        "params": {{"param1": "value1"}}
    }}
  ]
}}
"""
        return prompt.strip()

    def _extract_json(self, text: str) -> str:
        """
        Extracts the plan array from the JSON structure.
        """
        try:
            data = json.loads(text)
            if "plan" in data and isinstance(data["plan"], list):
                return json.dumps(data["plan"])
            self.logger.log("Planner", "JSON response from LLM is missing 'plan' key.", "WARNING")
            return "[]"
        except json.JSONDecodeError:
            self.logger.log("Planner", "Failed to decode JSON from LLM response.", "ERROR")
            return "[]"
