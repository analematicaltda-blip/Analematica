---
name: multi-agent-patterns
description: Use when designing or orchestrating systems with multiple AI agents. Focuses on context isolation, delegation strategies (Supervisor, Swarm, Hierarchical), and state management protocols.
---

# Multi-Agent Patterns Skill

Master the architecture of distributed AI systems. This skill focuses on overcoming context window limitations through strategic task distribution and context isolation.

## Core Patterns

### 1. The Orchestrator (Supervisor)
Centralized control where a lead agent manages delegation and quality gates.
- **Best For**: Complex, non-linear projects requiring high-level synthesis.
- **Mechanism**: The supervisor decomposes the goal, dispatches tasks, and reviews results before final delivery.

### 2. The Swarm (Peer-to-Peer)
Decentralized collaboration with direct-handoff mechanisms.
- **Best For**: Sequential or highly flexible workflows where tasks follow a natural chain.
- **Mechanism**: Agents pass the state directly to the next relevant specialist without a central bottle-neck.

### 3. Hierarchical Layers
Multi-tiered structures for large-scale enterprise automation.
- **Strategic Layer**: High-level planning and policy.
- **Tactical Layer**: Coordination and sub-project management.
- **Operational Layer**: Low-level task execution.

## Technical Protocols

### Context Isolation
Sub-agents exist primarily to keep context clean. Never inherit the parent's full history unless strictly necessary. Provide "Need-to-Know" context only.

### State Handoff
Prevent the "telephone game" by using structured data for handoffs. Explicitly state:
- **Input**: The exact data received.
- **Transformation**: What the agent did.
- **Output**: The clean, synthesized result.

### Token Economics
Partitioning is an economic decision. Only split tasks when the context savings exceed the coordination overhead (supervisor prompts + aggregation cost).

## When to Activate
- Architecting a multi-agent system or "Swarm".
- Designing delegation logic for complex workflows.
- Reducing "context poisoning" in single-agent environments.

---
*Inspired by the Agent Skills for Context Engineering collection.*
