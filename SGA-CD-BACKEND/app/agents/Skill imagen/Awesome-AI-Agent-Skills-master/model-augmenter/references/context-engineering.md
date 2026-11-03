# Context Engineering — Detailed Reference

## Purpose
Optimize context window usage so that even models with small windows (4K-8K tokens) can handle complex tasks effectively.

## Strategy Priority Order

1. **KV-Cache Optimization** — Zero quality risk, immediate savings
2. **Observation Masking** — Compress tool outputs after extracting key info
3. **Compaction** — Summarize accumulated context at 70% utilization
4. **Partitioning** — Split work across sub-agents when window is insufficient

## KV-Cache Optimization

Structure prompts so stable content is at the prefix:
1. System prompt (most stable)
2. Tool definitions (stable)
3. Reusable templates
4. Conversation history (grows but shares prefix)
5. Current query (least stable — always last)

Remove timestamps, session IDs, and request counters from system prompt. Even one whitespace change invalidates cached blocks downstream.

**Target:** 70%+ cache hit rate → 50%+ cost reduction.

## Observation Masking

Replace verbose tool outputs with compact references once key info is extracted:

**Never mask:** Current task observations, last turn outputs, active reasoning chains, error outputs during debugging.

**Mask after 3+ turns:** Replace with `[Obs:{ref_id} — Key: {summary}. Retrievable.]`

**Always mask immediately:** Duplicate outputs, boilerplate headers, already-summarized content.

**Target:** 60-80% reduction with <2% quality impact.

## Compaction

Trigger at 70% context utilization:

| Content Type | Keep | Drop |
|-------------|------|------|
| Tool outputs | Key findings, metrics, errors | Raw output, stack traces, boilerplate |
| Conversations | Decisions, preferences, context shifts | Filler, exploratory exchanges |
| Documents | Facts relevant to active task | Supporting evidence already used |

**Never compress:** System prompt — it anchors model behavior.

**Target:** 50-70% token reduction with <5% quality degradation.

## Context Partitioning

When estimated context exceeds 60% of window limit:
1. Decompose task into independent subtasks
2. Assign each to a sub-agent with clean context
3. Aggregate results in coordinator
4. Validate all partitions completed before merging

Only partition when savings exceed coordination overhead (usually 3+ subtasks).

## Budget Allocation

| Category | Budget % |
|----------|---------|
| System prompt + skill | 15-20% |
| Tool definitions | 5-10% |
| Active context (files, evidence) | 30-40% |
| Message history | 20-30% |
| Buffer (reserved) | 5-10% |

## Optimization Triggers

| Signal | Action |
|--------|--------|
| >80% utilization | Trigger compaction |
| Repetition in output | Mask + compact |
| Quality score drops | Audit context before optimizing |
| Near limit + debugging | Mask resolved outputs only |
