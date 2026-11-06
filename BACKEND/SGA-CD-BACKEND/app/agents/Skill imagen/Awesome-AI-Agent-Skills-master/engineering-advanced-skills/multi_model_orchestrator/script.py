#!/usr/bin/env python3
"""
Multi-Model Orchestrator script - executes tasks with intelligent routing.
Usage: python script.py "<task description>"
"""

import sys
import json

# Add orchestrator to path
sys.path.insert(0, "D:/IA/CODE/claudebot/orchestrator")

from core.task_decomposer import MultiModelOrchestrator


def run_task(task: str) -> dict:
    """Execute a task through the multi-model orchestrator."""
    orchestrator = MultiModelOrchestrator()
    result = orchestrator.execute_complex_task(task, verbose=False)

    return {
        "original_task": result['original_task'],
        "total_subtasks": len(result['subtasks']),
        "successful": result['successful'],
        "total_time_ms": result['total_time_ms'],
        "models_used": [
            {
                "model": r['model'],
                "phase": r['phase'],
                "success": r['success'],
                "time_ms": r['execution_time_ms']
            }
            for r in result['results']
        ],
        "all_success": result['all_success']
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Read from stdin if available
        task = sys.stdin.read().strip()
    else:
        task = " ".join(sys.argv[1:])

    if not task:
        print(json.dumps({"error": "No task provided"}))
        sys.exit(1)

    result = run_task(task)

    # Output as JSON for Claude to parse
    print(json.dumps(result, indent=2))