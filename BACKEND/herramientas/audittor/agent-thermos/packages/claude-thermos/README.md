# @thinkscape/claude-thermos

![Pixel-art Thermos logo](./assets/logo.png)

Thermo-nuclear branch review for Claude Code: deep correctness and security
audits, strict maintainability rubrics, and parallel subagent orchestration.

Adapted from Cursor's MIT-licensed
[Thermos plugin](https://github.com/cursor/plugins/tree/main/thermos).

## Installation

Install the published Thermos plugin through Claude Code's plugin marketplace
flow:

```bash
claude plugin marketplace add Thinkscape/agent-thermos
claude plugin install thermos@agent-thermos
```

Inside an interactive Claude Code session, the equivalent slash commands are:

```text
/plugin marketplace add Thinkscape/agent-thermos
/plugin install thermos@agent-thermos
```

The Claude marketplace entry is
[`/.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json) and
installs the published npm package
[`@thinkscape/claude-thermos`](https://www.npmjs.com/package/@thinkscape/claude-thermos).
The plugin manifest is named `thermos` so commands stay short.
The installed plugin exposes `/thermos:run`; the individual review rubrics are
embedded in the bundled subagents and are not user-facing slash commands.

## Primary invocation

```text
/thermos:run [base-ref | PR URL | scope]
```

For an unprefixed command, install the optional standalone shim:

```bash
npm install -g @thinkscape/claude-thermos
claude-thermos install-command --scope project
```

Then use:

```text
/thermos [base-ref | PR URL | scope]
```

The shim is copied into `.claude/commands/thermos.md`, so it appears as the
normal unprefixed `/thermos` command without adding another plugin-scoped
`/thermos:*` entry.

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

  subgraph L0["Rubrics"]
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

## Agents

| Agent | Description |
|:------|:------------|
| `thermos:thermo-nuclear-review-subagent` | Deep diff-scoped review for correctness, security, devex, and feature-gate risk. |
| `thermos:thermo-nuclear-code-quality-review-subagent` | Strict code-quality review for structure, code-judo, 1k-line rule, and boundaries. |

## Typical usage

```text
/thermos:run main
/thermos:run https://github.com/acme/app/pull/123
/thermos:run review the API changes only
```

Thermos gathers diff context, launches both agents with the same input, and
synthesizes prioritized findings. Use the optional `/thermos` shim if you prefer
the shorter local command.

## Attribution

This package adapts methodology, diagrams, and prompt structure from Cursor's
Thermos plugin. See the repository `NOTICE.md` for the upstream MIT notice.
