---
name: tool-design
description: This skill should be used when designing, creating, or refactoring agent tools and descriptions. Focuses on architectural reduction, consolidation, and reliability using MCP standards.
---

# Tool Design Skill

Optimize the interface between deterministic systems and non-deterministic agents. This skill focuses on the "Architectural Reduction" principle to improve model reliability and reduce context bloat.

## Core Principles

### 1. The Consolidation Principle
Reduce tool count and ambiguity. Fewer, more capable tools outperform many granular ones.
- **Merge Coupled Steps**: Combine dependent actions (e.g., `validate` + `execute`) into a single intent-based tool.
- **Reduce Search Space**: Minimizing the number of available tools reduces the probability of selection errors.

### 2. Tools as Contracts
Strict typing and clear error handling ensure predictable behavior.
- **Schema-First**: Define precise inputs using JSON Schema or equivalent.
- **Contextual Errors**: Return actionable failure reasons and correction hints to enable agent self-correction.

### 3. Response Optimization
Manage tool output volume to preserve the context window.
- **Verbosity Control**: Include parameters to specify detail levels (e.g., `summary` vs `full`).
- **Signal-to-Noise**: Strip boilerplate and redundant metadata from results.

### 4. Semantic Clarity
Names and descriptions dictate selection accuracy.
- **Action-Object Naming**: Use clear `verb_noun` conventions (e.g., `fetch_record`).
- **Effect-Based Descriptions**: Explain *when* to use the tool and what its side effects are.

## When to Activate
- Creating new tools or MCP servers.
- Refactoring "confused" agents with high tool-count environments.
- Optimizing token usage for tool-heavy workflows.

---
*Inspired by the Agent Skills for Context Engineering collection.*
