---
name: python-pro
description: Modern Python 3.11+ development with strict type safety, async patterns, and clean architecture. Use for professional Python application design, testing, and maintenance.
---

# Python Pro

Professional standards for modern Python development.

## Core Workflow

1. **Type Safety**: Mandatory type hints for all function signatures.
2. **Async-First**: Use `asyncio` for I/O bound tasks.
3. **Clean Architecture**: Decouple logic from infrastructure.
4. **Testing**: Aim for >90% coverage with `pytest`.

## Standards

- Python 3.11+ syntax (e.g., `X | None` instead of `Optional[X]`).
- Use `dataclasses` or `pydantic` for data models.
- Strict type checking with `mypy`.
- Formatting with `black` and linting with `ruff`.

## Implementation Rules

- No global state.
- Use dependency injection where appropriate.
- Prefer composition over inheritance.
- Docstrings follow Google or NumPy style.

