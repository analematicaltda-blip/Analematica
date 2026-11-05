from typing import Dict, Any

class State:
    """
    Manages the state of the agent's execution.
    """
    def __init__(self, objective: str):
        self.data: Dict[str, Any] = {
            "objective": objective,
            "plan": None,
            "execution_history": [],
            "final_answer": None
        }

    def set(self, key: str, value: Any):
        """
        Sets a value in the state.
        """
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Gets a value from the state.
        """
        return self.data.get(key, default)

    def __str__(self):
        return f"State(data={self.data})"
