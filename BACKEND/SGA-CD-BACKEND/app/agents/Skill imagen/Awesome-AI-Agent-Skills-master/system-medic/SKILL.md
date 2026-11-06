---
name: system-medic
description: Auto-repair for Claudebot (Ollama, Playwright, Env). Uses episodic_memory to learn from infrastructure failures.
---

# System Medic (Self-Healing)

## Triggers
- Errors: `ConnectionError`, `ModuleNotFoundError`, `playwright not found`.
- Keywords: "ollama caído", "reparar entorno", "health check", "diagnóstico".

## Execution (`scripts/medic.py`)
- **Check**: `python scripts/medic.py check [all|ollama|playwright|env]`
- **Fix**: `python scripts/medic.py fix [ollama|playwright|env]`
- **Auto**: `python scripts/medic.py repair`
- **Status**: `python scripts/medic.py status`

## Recovery Logic
- **Ollama**: Check `http://localhost:11434/api/tags`. If dead -> `Start-Process "ollama" "serve" -WindowStyle Hidden`.
- **Playwright**: Check chromium launch. If missing -> `python -m patchright install chromium`.
- **Env**: Validate existence of `.env` and `credentials.json`.

## Learning (Episodic Memory)
- Log all attempts to `memory/logs/tasks_YYYY-MM-DD.jsonl`.
- Pattern: Track `success` vs `attempt`. Use preferred methods based on prior wins.

## Rules
1. **Check First**: Always run `check all` before any fix.
2. **One at a time**: Verify state after each individual fix.
3. **Log**: Record outcome in memory for future autonomous decisions.

