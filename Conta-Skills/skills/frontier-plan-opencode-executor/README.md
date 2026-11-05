# frontier-plan-opencode-executor

Execute frontier-AI implementation plans safely inside OpenCode using non-frontier coding models like DeepSeek v4 Pro, GPT-4o, Gemini Flash, etc.

This skill turns large implementation plans into controlled, verifiable execution workflows.

Instead of blindly following a spec, the agent:
- validates the plan against the real repository;
- breaks work into safe incremental steps;
- verifies each step;
- inspects diffs;
- avoids destructive actions;
- detects thrashing/debugging loops;
- adapts the plan to existing architecture.

Designed specifically for OpenCode workflows where:
- a frontier model creates the implementation plan;
- a cheaper/faster coding model executes it.

## Why This Exists

Non-frontier coding models are often surprisingly capable at focused implementation work. But they frequently fail when:
- handling large multi-step plans;
- maintaining execution discipline;
- adapting plans to the actual repository;
- debugging repeated failures;
- avoiding scope creep;
- preventing accidental repo damage.

This skill acts like an execution safety layer. It helps smaller models behave more like disciplined senior engineers instead of "autocomplete with tools".

## Core Idea

A frontier model generates the plan.
Example:
- Claude Opus
- GPT-5
- Gemini Pro

Then OpenCode executes the implementation using:
- DeepSeek v4 Pro
- GPT-4o
- Gemini Flash
- other cheaper/faster coding models

The skill forces the agent to:
- validate assumptions against the real repo;
- implement one step at a time;
- verify after each step;
- inspect diffs;
- avoid blind patching/debugging loops;
- stop and report blockers clearly when stuck.

## What Problems It Solves

### 1. Frontier Plans Are Often Wrong
Even strong models invent: file paths, imports, libraries, abstractions, APIs, architecture assumptions. This skill treats the plan as a strong hypothesis, not ground truth.

### 2. Smaller Models Drift
Non-frontier models tend to:
- lose track of long plans;
- batch too many edits;
- skip verification;
- "fix" errors randomly;
- thrash during debugging.

This skill enforces progress tracking, step isolation, tiered verification, diff inspection, and failure analysis.

### 3. Accidental Repo Damage
Agents sometimes touch unrelated files, mass-format codebases, silently install dependencies, rewrite architecture, delete working code, change lockfiles unexpectedly. This skill explicitly prevents that.

## Workflow

1. **Frontier Model** → Generates detailed implementation plan
2. **OpenCode + This Skill** → Reality-check against repo
3. **Break into safe steps**
4. **Implement step**
5. **Verify**
6. **Inspect diff**
7. **Continue**

## Features

- **Repository Reality Check**: Before implementing, validates files, checks installed libraries, detects existing patterns, verifies commands, identifies repo conflicts.
- **Tiered Verification**: Uses the smallest meaningful verification per step (lint, typecheck, targeted tests, build checks, smoke tests). Avoids unnecessary full builds after every edit.
- **Diff Discipline**: After every step checks changed files, detects unintended formatting, detects accidental deletions, catches lockfile changes, prevents hidden scope creep.
- **Repeated Failure Handling**: Prevents infinite "fix → fail → tweak → fail" loops. Instead: re-reads stack traces, inspects diffs, re-evaluates assumptions, changes strategy only when new information exists.
- **Safety Rules**: Blocks dangerous operations without explicit approval (`rm -rf`, `git reset --hard`, `npm install`, migrations, deploy commands, mass formatting).

## Best Use Cases

Perfect for:
- large PR execution;
- multi-step feature implementation;
- architecture migration plans;
- frontend/backend refactors;
- AI-generated specs;
- OpenCode subagents;
- cheap-model execution pipelines.

Especially useful when you want GPT-5/Claude-level planning but DeepSeek-level execution cost.

## Example

**Step 1 — Generate Plan with Frontier Model**
Ask GPT-5 / Claude Opus:
> Analyze this repo and create a detailed implementation plan for adding authentication using the existing architecture.

**Step 2 — Execute with OpenCode**
Then run OpenCode using this skill. The agent will: validate the plan, adapt it to the real repo, track progress, implement incrementally, verify every step, stop cleanly if blocked.

## Philosophy

This skill is based on one core observation:
**Most coding-agent failures are not intelligence failures. They are execution-discipline failures.**

The goal is not to make small models smarter. The goal is to make them: more careful, more systematic, less destructive, less overconfident, easier to debug, easier to trust.

## Recommended Pairings

Works especially well with:
- OpenCode
- DeepSeek v4 Pro
- GPT-4o
- Gemini Flash
- Claude Sonnet
- local coding models

And frontier planning models like:
- GPT-5
- Claude Opus
- Gemini Pro

## Installation

Place the skill inside your OpenCode skills directory.
Example:
`~/.config/opencode/skills/frontier-plan-opencode-executor/`

Add:
- `SKILL.md`
- `README.md`

Then invoke it when executing a detailed implementation plan.

## Recommended Workflow
1. Frontier model creates plan
2. OpenCode loads this skill
3. Agent validates repo reality
4. Step-by-step execution
5. Verification after every step
6. Diff inspection
7. Final verification + report

## Not Intended For
Not useful for: tiny edits, one-file fixes, rapid experimentation, exploratory coding, brainstorming, greenfield prototyping.

This is an execution-discipline skill. Not a creativity skill.

## License
MIT

## Contributing
PRs improving verification heuristics, failure recovery, repo adaptation, OpenCode workflows, safety rules, model-specific behavior are welcome.
