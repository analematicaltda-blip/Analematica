from typing import Callable, Dict, Any

class Tool:
    """
    A wrapper for a function that the agent can use.
    """
    def __init__(self, name: str, description: str, function: Callable, params: Dict[str, str]):
        """
        Initializes a Tool.

        Args:
            name: The name of the tool. Must be unique.
            description: A clear description of what the tool does. Used by the planner.
            function: The actual function to execute.
            params: A dictionary describing the parameters the function takes.
        """
        self.name = name
        self.description = description
        self.function = function
        self.params = params

    def __str__(self):
        return f"Tool(name={self.name}, description={self.description}, params={self.params})"
