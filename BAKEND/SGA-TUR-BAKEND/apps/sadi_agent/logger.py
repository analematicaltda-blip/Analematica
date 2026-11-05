from typing import List
import datetime

class Logger:
    """
    A simple logger to track the agent's internal monologue and actions.
    """
    def __init__(self):
        self.logs: List[str] = []

    def log(self, source: str, message: str, level: str = "INFO"):
        """
        Adds a log entry.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}][{level}][{source}] {message}"
        self.logs.append(log_entry)

    def get_full_log(self) -> str:
        """
        Returns all log entries as a single string.
        """
        return "\n".join(self.logs)

    def clear(self):
        """
        Clears all log entries.
        """
        self.logs = []
