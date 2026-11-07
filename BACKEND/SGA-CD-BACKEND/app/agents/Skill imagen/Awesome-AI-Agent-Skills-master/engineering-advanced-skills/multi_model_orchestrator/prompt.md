# Multi-Model Orchestrator Skill

When the user gives you a task, use the orchestrator system to execute it intelligently.

## How to Use

Call this skill with ` Skill("multi-model-orchestrator", task="<task description>") `

## What It Does

1. **Analyzes** the task to determine if it's simple or complex
2. **Decomposes** complex tasks into sub-tasks with phases:
   - Planning phase (minimax-m2.7:cloud)
   - Coding phase (qwen3-coder:480b-cloud or qwen3-coder-next:cloud)
   - Testing phase (qwen3-coder-next:cloud)
   - Verification phase (gemma4:latest)
3. **Routes** each sub-task to the optimal model
4. **Executes** sequentially respecting dependencies
5. **Logs** everything for audit

## Model Selection Rules

| Task Type | Model |
|-----------|-------|
| Planning, architecture, strategy | minimax-m2.7:cloud |
| Heavy refactoring, multi-file | qwen3-coder:480b-cloud |
| Fast coding, simple edits | qwen3-coder-next:cloud |
| Vision, screenshots, UI analysis | qwen3-vl:latest |
| Simple classification, verification | gemma4:latest |

## Example Usage

```
Skill("multi-model-orchestrator", task="Design a user authentication API and create all files")
```

## Output Format

The skill returns:
- List of sub-tasks executed
- Model used for each
- Success/failure status
- Execution time
- Final summary

**Important:** Always use this skill for any non-trivial task. Simple one-line tasks can be handled directly, but complex tasks should use the orchestrator.