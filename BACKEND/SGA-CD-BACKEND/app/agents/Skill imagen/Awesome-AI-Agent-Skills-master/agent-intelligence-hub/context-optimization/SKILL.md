---
name: context-optimization
description: This skill should be used when the user asks to "optimize context", "reduce token costs", "improve context efficiency", "implement KV-cache optimization", "partition context", or mentions context limits, observation masking, context budgeting, or extending effective context capacity.
---

# Context Optimization Techniques

Context optimization extends the effective capacity of limited context windows through strategic compression, masking, caching, and partitioning. Effective optimization can double or triple effective context capacity without requiring larger models or longer windows — but only when applied with discipline. The techniques below are ordered by impact and risk.

## When to Activate

Activate this skill when:
- Context limits constrain task complexity
- Optimizing for cost reduction (fewer tokens = lower costs)
- Reducing latency for long conversations
- Implementing long-running agent systems
- Needing to handle larger documents or conversations
- Building production systems at scale

## Core Concepts

Apply four primary strategies in this priority order:

1. **KV-cache optimization** — Reorder and stabilize prompt structure so the inference engine reuses cached Key/Value tensors. This is the cheapest optimization: zero quality risk, immediate cost and latency savings. Apply it first and unconditionally.

2. **Observation masking** — Replace verbose tool outputs with compact references once their purpose has been served. Tool outputs consume 80%+ of tokens in typical agent trajectories, so masking them yields the largest capacity gains. The original content remains retrievable if needed downstream.

3. **Compaction** — Summarize accumulated context when utilization exceeds 70%, then reinitialize with the summary. This distills the window's contents while preserving task-critical state. Compaction is lossy — apply it after masking has already removed the low-value bulk.

4. **Context partitioning** — Split work across sub-agents with isolated contexts when a single window cannot hold the full problem. Each sub-agent operates in a clean context focused on its subtask. Reserve this for tasks where estimated context exceeds 60% of the window limit, because coordination overhead is real.

The governing principle: context quality matters more than quantity. Every optimization preserves signal while reducing noise. Measure before optimizing, then measure the optimization's effect.

## Detailed Topics

### Compaction Strategies

Trigger compaction when context utilization exceeds 70%: summarize the current context, then reinitialize with the summary. This distills the window's contents in a high-fidelity manner, enabling continuation with minimal performance degradation. Prioritize compressing tool outputs first (they consume 80%+ of tokens), then old conversation turns, then retrieved documents. Never compress the system prompt — it anchors model behavior and its removal causes unpredictable degradation.

Preserve different elements by message type:

- **Tool outputs**: Extract key findings, metrics, error codes, and conclusions. Strip verbose raw output, stack traces (unless debugging is ongoing), and boilerplate headers.
- **Conversational turns**: Retain decisions, commitments, user preferences, and context shifts. Remove filler, pleasantries, and exploratory back-and-forth that led to a conclusion already captured.
- **Retrieved documents**: Keep claims, facts, and data points relevant to the active task. Remove supporting evidence and elaboration that served a one-time reasoning purpose.

Target 50-70% token reduction with less than 5% quality degradation. If compaction exceeds 70% reduction, audit the summary for critical information loss — over-aggressive compaction is the most common failure mode.

### Observation Masking

Mask observations selectively based on recency and ongoing relevance — not uniformly. Apply these rules:

- **Never mask**: Observations critical to the current task, observations from the most recent turn, observations used in active reasoning chains, and error outputs when debugging is in progress.
- **Mask after 3+ turns**: Verbose outputs whose key points have already been extracted into the conversation flow. Replace with a compact reference: `[Obs:{ref_id} elided. Key: {summary}. Full content retrievable.]`
- **Always mask immediately**: Repeated/duplicate outputs, boilerplate headers and footers, outputs already summarized earlier in the conversation.

Masking should achieve 60-80% reduction in masked observations with less than 2% quality impact. The key is maintaining retrievability — store the full content externally and keep the reference ID in context so the agent can request the original if needed.

### KV-Cache Optimization

Maximize prefix cache hits by structuring prompts so that stable content occupies the prefix and dynamic content appears at the end. KV-cache stores Key and Value tensors computed during inference; when consecutive requests share an identical prefix, the cached tensors are reused, saving both cost and latency.

Apply this ordering in every prompt:
1. System prompt (most stable — never changes within a session)
2. Tool definitions (stable across requests)
3. Frequently reused templates and few-shot examples
4. Conversation history (grows but shares prefix with prior turns)
5. Current query and dynamic content (least stable — always last)

Design prompts for cache stability: remove timestamps, session counters, and request IDs from the system prompt. Move dynamic metadata into a separate user message or tool result where it does not break the prefix. Even a single whitespace change in the prefix invalidates the entire cached block downstream of that change.

Target 70%+ cache hit rate for stable workloads. At scale, this translates to 50%+ cost reduction and 40%+ latency reduction on cached tokens.

### Context Partitioning

Partition work across sub-agents when a single context cannot hold the full problem without triggering aggressive compaction. Each sub-agent operates in a clean, focused context for its subtask, then returns a structured result to a coordinator agent.

Plan partitioning when estimated task context exceeds 60% of the window limit. Decompose the task into independent subtasks, assign each to a sub-agent, and aggregate results. Validate that all partitions completed before merging, merge compatible results, and apply summarization if the aggregated output still exceeds budget.

This approach achieves separation of concerns — detailed search context stays isolated within sub-agents while the coordinator focuses on synthesis. However, coordination has real token cost: the coordinator prompt, result aggregation, and error handling all consume tokens. Only partition when the savings exceed this overhead.

### Budget Management

Allocate explicit token budgets across context categories before the session begins: system prompt, tool definitions, retrieved documents, message history, tool outputs, and a reserved buffer (5-10% of total). Monitor usage against budget continuously and trigger optimization when any category exceeds its allocation or total utilization crosses 70%.

Use trigger-based optimization rather than periodic optimization. Monitor these signals:
- Token utilization above 80% — trigger compaction
- Attention degradation indicators (repetition, missed instructions) — trigger masking + compaction
- Quality score drops below baseline — audit context composition before optimizing

## Practical Guidance

### Optimization Decision Framework

Select the optimization technique based on what dominates the context:

| Context Composition | First Action | Second Action |
|---|---|---|
| Tool outputs dominate (>50%) | Observation masking | Compaction of remaining turns |
| Retrieved documents dominate | Summarization | Partitioning if docs are independent |
| Message history dominates | Compaction with selective preservation | Partitioning for new subtasks |
| Multiple components contribute | KV-cache optimization first, then layer masking + compaction |
| Near-limit with active debugging | Mask resolved tool outputs only — preserve error details |

### Performance Targets

Track these metrics to validate optimization effectiveness:

- **Compaction**: 50-70% token reduction, <5% quality degradation, <10% latency overhead from the compaction step itself
- **Masking**: 60-80% reduction in masked observations, <2% quality impact, near-zero latency overhead
- **Cache optimization**: 70%+ hit rate for stable workloads, 50%+ cost reduction, 40%+ latency reduction
- **Partitioning**: Net token savings after accounting for coordinator overhead; break-even typically requires 3+ subtasks

Iterate on strategies based on measured results. If an optimization technique does not measurably improve the target metric, remove it — optimization machinery itself consumes tokens and adds latency.

---

## Skill Metadata

**Created**: 2025-12-20
**Last Updated**: 2026-03-17
**Author**: Agent Skills for Context Engineering Contributors
**Version**: 2.0.0
