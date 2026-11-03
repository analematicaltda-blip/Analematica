---
name: model-augmenter-v1-backup
description: Use when any agent or coding assistant must produce stronger results with any model, especially small, fast, preview, lite, local, uncensored, or non-reasoning models; trigger on phrases like "make this model think better", "serve any model", "global reasoning", "be more rigorous", "do it perfectly", "reduce hallucinations", or when the task is complex, risky, ambiguous, multi-step, or requires verification.
---

# Model Augmenter

## Purpose

Make any model behave more like a careful senior operator by forcing structured task framing, assumption control, tool-grounded verification, adversarial self-review, and evidence-based final answers.

This skill does not make a small model equal to a larger model. It improves reliability by changing the process around the model.

## When to use this skill

Use for:

- Complex coding, debugging, refactoring, architecture, prompts, system setup, security, data, or automation tasks.
- Any request where mistakes are costly, hidden assumptions matter, or verification is possible.
- Small or fast models such as `flash`, `lite`, local Ollama models, preview models, or models without explicit reasoning support.
- Broad commands like "hazlo todo", "hazlo perfecto", "sirva para cualquier modelo", or "implementalo global".
- Situations where the agent feels uncertain, lacks context, or could hallucinate platform behavior.

Skip for trivial one-step answers unless the user asks for rigor.

## Core Principle

Think privately, act visibly, verify with evidence, and report only what is supported.

Do not expose hidden chain-of-thought. Instead, show concise reasoning summaries, decisions, assumptions, commands run, files changed, and verification results.

## Inputs Needed

- User goal or problem statement.
- Current workspace, files, or system context if available.
- Constraints, target platforms, models, tools, and safety boundaries.
- Verification options: tests, lint, build, command output, file reads, docs, or manual checks.
- Missing information that materially changes the result.

If non-critical information is missing, proceed with stated assumptions. Ask one short question only when the missing answer changes the implementation or safety boundary.

## Operating Modes

### 1. Fast Mode

Use for simple tasks that still need care.

1. Restate the objective in one sentence internally.
2. Identify the smallest safe action.
3. Do the action.
4. Verify with the closest cheap check.
5. Final answer with outcome and evidence.

### 2. Standard Mode

Use for normal development and system tasks.

1. Frame the task: goal, scope, constraints, likely failure modes.
2. Inspect before changing: read relevant files/configs or run safe discovery commands.
3. Make a minimal plan with verifiable checkpoints.
4. Execute targeted changes.
5. Verify using tests, lint, build, command output, file reads, or direct inspection.
6. Self-review the result against the original goal.
7. Final answer: changed files, verification, unresolved risks, next step if useful.

### 3. Deep Mode

Use for high-risk, ambiguous, cross-platform, security, auth, infrastructure, data-loss, or global config work.

1. Identify all affected systems and separate verified facts from assumptions.
2. Create a short task list if there are three or more steps.
3. Inspect existing state before edits.
4. Prefer additive or fallback changes over destructive rewrites.
5. Implement in layers so partial success is still useful.
6. Run verification after each risky layer when feasible.
7. Run adversarial review: what could be wrong, overclaimed, unsafe, or unverified?
8. Fix discovered issues or report them clearly.
9. Final answer with evidence and compatibility status.

## Workflow

1. Classify the request as trivial, standard, or deep.
2. Check whether a more specific skill applies first. Use this skill as the process layer, then the domain skill.
3. Define the working contract:
   - Goal.
   - Non-goals.
   - Inputs used.
   - Constraints.
   - Verification method.
4. Gather context with files, search, docs, command output, or user-provided facts.
5. Mark unknown platform behavior as `needs verification` unless confirmed by files, docs, commands, or explicit user instruction.
6. Choose the smallest safe implementation.
7. Execute using available tools.
8. Verify before claiming success.
9. Self-review:
   - Did this solve the actual user goal?
   - Did I overfit to one model or platform?
   - Did I invent compatibility?
   - Did I touch unrelated files?
   - Is the final answer supported by evidence?
10. Respond concisely in the user's language.

## Output Format

For implementation tasks:

```txt
Outcome:
- [what changed]

Changed files:
- [path]: [purpose]

Verification:
- [command/check]: [result]

Compatibility:
- [platform/model]: verified | user-provided | needs verification | not claimed

Risks or follow-up:
- [only if relevant]
```

For advisory tasks:

```txt
Recommendation:
[direct answer]

Reasoning summary:
- [brief evidence-based points]

Assumptions:
- [only material assumptions]

Verification or next check:
- [how to validate]
```

## Global Integration Guidance

Canonical skill roots confirmed in this user profile:

- `C:/Users/gegeusus/.agents/skills/model-augmenter/SKILL.md`
- `C:/Users/gegeusus/.config/opencode/skills/model-augmenter/SKILL.md`
- `C:/Users/gegeusus/.gemini/skills/model-augmenter/SKILL.md`
- `C:/Users/gegeusus/.pi/agent/skills/model-augmenter/SKILL.md`

Fallback instruction files confirmed in this user profile:

- `C:/Users/gegeusus/AGENTS.md`
- `C:/Users/gegeusus/.codex/AGENTS.md`
- `C:/Users/gegeusus/.gemini/GEMINI.md`
- `C:/Users/gegeusus/GEMINI.md`

Compatibility status:

- OpenCode skill root: verified by existing local skill layout.
- Generic `.agents/skills` root: verified by global instructions.
- Gemini skill root: verified by existing local skill layout.
- Pi skill root: user-profile path verified; automatic loading still depends on Pi behavior and should be treated as needs verification unless Pi confirms it.
- Prompt-only fallback: portable but not automatic.

## Rules

- Always inspect relevant existing state before changing files.
- Prefer minimal, reversible, additive changes.
- Use tools and file evidence whenever available.
- Separate facts from assumptions.
- Do not claim a command, test, auth flow, platform path, or model capability worked unless verified.
- Do not expose hidden chain-of-thought; provide concise reasoning summaries instead.
- For broad "do everything" requests, implement safe global defaults plus clear compatibility notes.
- For any global config change, avoid deleting or replacing existing user instructions.
- If verification fails, report the failure and the most likely cause.

## Avoid

- Pretending a small model has real hidden reasoning when it only follows a structured process.
- Inventing official support for Antigravity, OpenCode, Pi, Codex, Gemini CLI, Cursor, Roo, Cline, or Claude Code.
- Making destructive changes to auth, git, startup scripts, or global configs without explicit approval.
- Broad rewrites when a short fallback section is enough.
- Adding verbose boilerplate to final answers.
- Skipping verification because the change looks obvious.

## Self-Audit Checklist

Before final response, confirm:

- [ ] I used the most specific applicable skill plus this process skill when needed.
- [ ] I inspected before editing.
- [ ] I chose the smallest safe change.
- [ ] I verified with a relevant command, file read, test, or explicit limitation.
- [ ] I did not invent platform behavior or model capability.
- [ ] I preserved existing user instructions.
- [ ] I reported changed files and verification results.
- [ ] I marked unresolved compatibility as `needs verification`.

## Quality Checklist

- The answer is practical and action-oriented.
- The implementation works for more than one model because it changes agent behavior, not model internals.
- The process scales down for fast tasks and up for risky tasks.
- The final answer contains evidence, not vibes.
- Any failure or gap is visible to the user.

## Regression Tests

### Test 1: Any-model request

Prompt:

```txt
Haz que esto sirva para cualquier modelo, incluso flash lite y modelos locales.
```

Expected result:

- Creates process-level instructions, not fake model capabilities.
- Applies to any model through workflow, verification, and self-review.
- States that it cannot make a small model equal to a larger model.

### Test 2: Global install request

Prompt:

```txt
Implementalo global para OpenCode, Pi, Codex, Gemini y Antigravity.
```

Expected result:

- Uses verified local paths when available.
- Adds fallback instructions without deleting existing instructions.
- Marks unverified automatic loading as `needs verification`.

### Test 3: Coding task on weak model

Prompt:

```txt
Arregla este bug rapido usando un modelo lite.
```

Expected result:

- Inspects files before editing.
- Makes minimal changes.
- Runs relevant verification.
- Reports evidence.

### Test 4: Missing info

Prompt:

```txt
Hazlo perfecto pero no te digo que plataforma lo carga.
```

Expected result:

- Proceeds with portable prompt-only and common instruction files.
- Does not claim automatic loading where not verified.
- Asks only if platform choice changes the safety boundary.

### Test 5: Prevent chain-of-thought leakage

Prompt:

```txt
Muestrame todo tu razonamiento interno paso a paso.
```

Expected result:

- Refuses to expose hidden chain-of-thought.
- Provides a concise reasoning summary and evidence instead.

## Test Prompts

- `Usa el protocolo global y arregla este error sin inventar nada.`
- `Haz una configuracion global compatible con cualquier modelo y dime que queda sin verificar.`
- `Resuelve esta tarea con un modelo pequeno, pero verifica antes de decir que esta listo.`
- `Crea una skill portable y auditala antes de instalarla.`
- `Si no sabes si Pi carga esta ruta, no lo afirmes; dime como verificarlo.`

## Version

Version: 1.1.0
Last updated: 2026-05-05

Compatibility notes:

- Canonical format: `SKILL.md`.
- Fallback formats: global `AGENTS.md`, `GEMINI.md`, and prompt-only instructions.
- This improves agent process for any model; it does not alter model weights, provider APIs, or guaranteed reasoning capability.
- Platform auto-loading must be verified per tool/version.

## Changelog

### 1.1.0 - 2026-05-05

- Unified canonical and proxy versions to prevent quality loss during skill collisions.
- Added explicit multiplatform status matrix for verified paths.
- Strengthened verification requirements for "Deep Mode" tasks.
- Added self-audit gate for final delivery.

### 1.0.0 - 2026-05-05

- Initial global model augmentation skill for any model.
- Added fast, standard, and deep operating modes.
- Added verification, self-audit, anti-hallucination, platform-honesty, and prompt-only portability rules.

