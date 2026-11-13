# @thinkscape/codex-thermos

![Pixel-art Thermos logo](./assets/logo.png)

Thermo-nuclear branch review for Codex: deep correctness and security audits,
strict maintainability rubrics, and subagent orchestration.

Adapted from Cursor's MIT-licensed
[Thermos plugin](https://github.com/cursor/plugins/tree/main/thermos).

## Installation

Install the published Thermos plugin through Codex's plugin marketplace flow:

```bash
codex plugin marketplace add Thinkscape/agent-thermos
codex plugin add thermos@agent-thermos
```

The marketplace entry is in the repository at
[`/.agents/plugins/marketplace.json`](../../.agents/plugins/marketplace.json).
The npm package entry is
[`@thinkscape/codex-thermos`](https://www.npmjs.com/package/@thinkscape/codex-thermos).

To update an existing install after a release:

```bash
codex plugin marketplace upgrade agent-thermos
codex plugin remove thermos@agent-thermos
codex plugin add thermos@agent-thermos
```

## Primary invocation

```text
$thermos
```

Pass a base ref, PR URL, or scope when useful:

```text
$thermos main
$thermos https://github.com/acme/app/pull/123
$thermos review packages/api only
```

## Architecture

```mermaid
flowchart TB
  subgraph L2["Orchestrator"]
    TH[thermos]
  end

  subgraph L1["Subagents"]
    SNR[thermo-nuclear-review-subagent]
    SNCQ[thermo-nuclear-code-quality-review-subagent]
  end

  DIFF[git diff + file contents]

  subgraph L0["Skills"]
    TNR[thermo-nuclear-review]
    TNCQ[thermo-nuclear-code-quality-review]
  end

  TH --> SNR
  TH --> SNCQ
  SNR --> TNR
  SNR --> DIFF
  SNCQ --> TNCQ
  SNCQ --> DIFF
```

## Skills

| Skill | Description |
|:------|:------------|
| `thermo-nuclear-review` | Deep branch audit for bugs, breakages, security, devex, and feature-gate leaks. |
| `thermo-nuclear-code-quality-review` | Strict maintainability audit for code-judo, 1k-line rule, spaghetti, and boundaries. |
| `thermos` | Run both review passes and synthesize findings. |

## Typical usage

1. Gather `git diff main...HEAD` and relevant changed-file contents.
2. Run both Thermos review passes on the same context.
3. Synthesize prioritized, deduped findings.

If the current Codex surface has subagent support, `$thermos` should run the two
review passes in parallel. If not, it should run them sequentially and keep the
outputs separated before synthesis.

## Attribution

This package adapts methodology, diagrams, and prompt structure from Cursor's
Thermos plugin. See the repository `NOTICE.md` for the upstream MIT notice.
