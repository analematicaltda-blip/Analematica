---
name: proactivity
description: Use when work needs momentum, proactive next steps, self-healing retries, reverse prompting, or continuous improvement without waiting for repeated user prompts.
---

# Proactive Engine

## Core Triggers
- **Reverse Prompting**: Surface ideas, drafts, and next steps before being asked.
- **Momentum**: Leave a "next useful move" after every major task.
- **Resourcefulness**: Try multiple approaches before escalating.
- **Self-Healing**: Diagnose and retry failed tool calls automatically.
- **Recovery**: Use `~/proactivity/` state to resume context after interruptions.

## State Management (`~/proactivity/`)
- `memory.md`: Durable boundaries and activation rules.
- `session-state.md`: Current objective and next move.
- `heartbeat.md`: Recurring follow-up items.
- `working-buffer.md`: Volatile breadcrumbs for long tasks.

## Boundaries
- **ASK FIRST**: External comms, spending, deletion, or commitments.
- **SHOW FIRST**: Any file edit outside `~/proactivity/` needs a visible diff.
- **NO NOISE**: If no clear value is found, stay silent.

## Execution Pattern
1. Analyze current state.
2. Identify likely next blocker.
3. Prepare the fix/option.
4. Present result + "Next move is X".

