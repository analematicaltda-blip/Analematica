---
name: skill-creator-pro
description: Use when creating, improving, auditing, testing, or packaging reusable AI agent skills, rules, workflows, SKILL.md files, AGENTS.md files, GEMINI.md files, prompt-only instructions, or portable skill bundles for Pi Agent, OpenCode, Antigravity, Codex, Gemini CLI, Claude Code, VS Code agents, Cursor, Roo, Cline, and compatible platforms.
---

# Skill Creator Pro

Create, improve, audit, test, version, and package reusable AI agent skills without making them vague, incomplete, or tied to one platform by accident.

## Purpose

This skill turns user workflows, repeated tasks, domain procedures, and existing instructions into reliable agent skills. It can produce a single canonical `SKILL.md` or a portable bundle for multiple agent platforms.

It is for skill and instruction-pack authoring. It is not a generic prompt-writing helper, marketing copy generator, or platform capability oracle.

## When to use this skill

Use this skill when the user:

- Says "create a skill", "make me a skill", "turn this into a skill", or "improve this skill".
- Wants a reusable workflow for agents, assistants, IDE agents, coding agents, or automation agents.
- Asks for `SKILL.md`, `AGENTS.md`, `GEMINI.md`, prompt-only instructions, rules, workflows, or a portable instruction bundle.
- Mentions Pi Agent, OpenCode, Antigravity, Codex, Gemini CLI, Claude Code, VS Code agents, Cursor, Roo, Cline, Continue, or another compatible agent platform.
- Needs test prompts, regression tests, self-audit, changelog, versioning, install paths, or compatibility notes.
- Says in Spanish: "Convierte esto en una skill", "Mejora esta skill", "Hazme una skill para...", "hazla compatible", or "que funcione en varias plataformas".

Do not use it for one-off answers that are not meant to become reusable agent instructions.

## Core principle

A good skill is operational, narrow, testable, and honest about what it knows. It tells a future agent exactly when to load it, what to do, what to output, how to verify itself, and what not to invent.

Master rule: this master skill must self-audit every child skill before delivery. A child skill is not ready if the audit shows missing required outputs, missing platform fallbacks, missing regression tests, invented compatibility, or unresolved placeholders.

## Inputs needed

Use what the user already gave before asking questions.

For a new skill, gather:

- Skill goal and target users.
- Trigger phrases or situations.
- Inputs the future agent will receive.
- Expected outputs and formats.
- Tools, APIs, files, templates, or platform targets.
- Constraints, safety boundaries, and known failure modes.

For an existing skill, gather:

- Current `SKILL.md` or equivalent instructions.
- What failed or felt incomplete.
- Required platform targets.
- Parts that must be preserved.
- Versioning or changelog expectations.

If non-critical information is missing, proceed with explicit placeholders such as `[PLATFORM]`, `[TOOL]`, `[INPUT_FORMAT]`, `[OUTPUT_FORMAT]`, `[INSTALL_PATH_TO_VERIFY]`, and list them before delivery.

Ask only when a missing answer would change the skill's purpose, safety boundary, or platform output.

## Modes

### 1. Standard skill mode

Use when the user wants one canonical skill.

Deliver:

- `SKILL.md` with valid YAML frontmatter.
- Operational workflow.
- Output format.
- Rules, avoid list, quality checklist.
- Test prompts and regression tests.
- Version and changelog.

### 2. Multiplatform mode

Use when the user asks for portability, names multiple platforms, or requests `AGENTS.md`, `GEMINI.md`, prompt-only output, rules, workflows, or fallback files.

Deliver a platform bundle with a canonical source and optional adapters:

1. `SKILL.md`: canonical skill format with YAML frontmatter.
2. `AGENTS.md`: agent-instructions fallback for systems that read repository instructions.
3. `GEMINI.md`: Gemini CLI compatible fallback when the user wants it.
4. Prompt-only version: no YAML, no file assumptions, pasteable into any agent.
5. Optional platform notes: only include routes and capabilities that are verified by provided project context, existing files, official docs, or explicit user instruction.

Default rule: `SKILL.md` is the source of truth. `AGENTS.md`, `GEMINI.md`, and prompt-only versions must preserve the same behavioral requirements unless the user asks for a platform-specific adaptation.

### 3. Self-audit mode

Use before delivering any new or improved skill, even if the user does not ask for it.

Hard gate: run the self-audit checklist against the child skill before delivery. If any required item fails, revise the child skill before delivery. Report unresolved gaps clearly instead of hiding them.

### 4. Update mode

Use when changing an existing skill.

Preserve what works, improve only what serves the user's goal, increment the version, add a changelog entry, and add or update regression tests for the new guarantees.

## Master-to-child workflow

Use this loop when creating or improving child skills:

```txt
1. Use skill-creator-pro to create or improve a child skill.
2. Self-audit the child skill before delivery.
3. Test the child skill with normal, edge, missing-info, platform, and failure-prevention prompts.
4. If the child skill fails, copy the exact failure or gap.
5. Use skill-creator-pro to update the child skill and add a regression test for that failure.
6. If this master skill caused the failure, update skill-creator-pro itself and add a master regression test.
```

The master must not skip step 2. Self-audit comes before final delivery, before copying fallback files, and before telling the user the child skill is complete.

## Workflow

### Step 1: Capture intent

1. Read the full user request and any existing skill content.
2. Identify whether this is a new skill, an improvement, a conversion, a portability bundle, or an audit.
3. Extract required platforms, output formats, tools, constraints, and "do not change" instructions.
4. Preserve useful content from existing skills: purpose, trigger language, domain rules, examples, and checklists that still apply.
5. Write down the failure this update is meant to prevent.

### Step 2: Define the skill contract

Specify:

- Inputs the future agent expects.
- Outputs the skill must produce.
- Trigger conditions.
- Non-goals.
- Platform targets.
- Verification method.
- Safety or honesty rules.

The contract must be narrow enough to be useful. Avoid skills named `assistant-helper`, `productivity-agent`, or `do-anything-workflow` unless the user explicitly wants a broad meta-skill.

### Step 3: Design the trigger

Write frontmatter like this:

```md
---
name: skill-name
description: Use when [specific triggering situations, user phrases, platforms, formats, or symptoms]
---
```

Rules for trigger descriptions:

- Start with `Use when`.
- Describe when to use the skill, not a long summary of the workflow.
- Include natural phrases users might say.
- Include platform or tool names only when relevant.
- Keep the description specific enough to avoid false positives.
- Use lowercase hyphenated names: `skill-name`.

### Step 4: Write the canonical `SKILL.md`

Include these sections unless the user explicitly asks for a smaller format:

- YAML frontmatter.
- Title.
- Purpose.
- When to use this skill.
- Core principle.
- Inputs needed.
- Modes, if the skill has more than one operating mode.
- Workflow with numbered operational steps.
- Output format.
- Multiplatform packaging, if relevant.
- Rules.
- Avoid.
- Self-audit checklist.
- Quality checklist.
- Regression tests.
- Test prompts.
- Changelog.

Keep sections focused on what future agents must do. Avoid long motivational essays.

### Step 5: Add multiplatform packaging

When multiplatform mode is active, create a bundle plan:

```txt
Canonical:
  SKILL.md

Optional fallbacks:
  AGENTS.md
  GEMINI.md
  prompt-only.md or "Prompt-only version" section

Platform notes:
  [PLATFORM]: [verified path/capability/source OR "user must verify"]
```

Use these labels:

- `verified`: confirmed from existing project files, official docs, tool output, or explicit user instruction.
- `user-provided`: stated by the user but not independently verified.
- `needs verification`: plausible but not proven in the current context.
- `not claimed`: no route, feature, or capability is asserted.

Do not convert `needs verification` into `verified` just to make the output look complete.

### Step 6: Add self-audit

Before delivering any child skill, audit it against:

- Trigger specificity.
- Required sections.
- Platform honesty.
- Output completeness.
- Regression coverage.
- Changelog/versioning.
- Missing placeholders.
- User requirements.
- Scope control.

If the user asked for a complete `SKILL.md`, the delivered file must not contain unfinished sections such as `TODO`, `TBD`, or `[FILL THIS IN]` unless the placeholder is deliberately listed as user-supplied missing information.

If the self-audit fails, do not deliver the child skill as complete. Fix it first, then run the audit again.

### Step 7: Add regression tests

Every skill must include regression tests that future agents can run mentally or with test prompts.

Regression tests must cover:

- Normal creation.
- Improving an incomplete existing skill.
- Missing information with placeholders.
- Multiplatform output when requested.
- Self-audit catching an incomplete skill.
- No invented platform paths or capabilities.
- Changelog/version increment for updates.

For specialized skills, add domain-specific regressions. Example: a VRoid skill must test UV template compatibility; a scraping skill must test privacy and robots/terms boundaries.

### Step 8: Version and changelog

Every delivered skill must include:

- `Version`.
- `Last updated`.
- `Compatibility notes`.
- `Changelog`.

Versioning guidance:

- `1.0.0`: first complete usable version.
- Patch: typo, wording, small clarification.
- Minor: new mode, output format, checklist, or platform adapter.
- Major: changed purpose, trigger, expected output, or workflow contract.

When improving an existing skill, increment the version and add a dated changelog entry describing user-facing behavior changes.

### Step 9: Test, learn, and update

After drafting and auditing a child skill:

1. Test it with the regression tests and at least 3 realistic prompts.
2. If a test exposes a gap, copy the exact failure into the improvement request.
3. Update the child skill.
4. Add a regression test that would catch the same failure next time.
5. If the gap came from weak master instructions, update this master skill and add a master regression test.

## Output format

### For a single canonical skill

```txt
Folder path:
[verified or user-provided path]

Files:
- SKILL.md

Includes:
- Purpose
- When to use
- Inputs needed
- Workflow
- Output format
- Rules
- Avoid
- Self-audit checklist
- Quality checklist
- Regression tests
- Test prompts
- Version and changelog
```

### For multiplatform bundles

```txt
Canonical source:
- SKILL.md

Optional copies/adapters:
- AGENTS.md
- GEMINI.md
- prompt-only.md

Platform matrix:
- Platform
- Output file
- Path
- Status: verified | user-provided | needs verification | not claimed
- Notes

Self-audit result:
- Passed checks
- Known gaps
- Required user verification
```

### Prompt-only version format

Use this when the target system cannot read YAML or files:

```md
# [Skill Name] - Prompt-Only Instructions

Use these instructions when [trigger].

Purpose:
[purpose]

Workflow:
1. [step]
2. [step]

Rules:
- [rule]

Avoid:
- [avoid]

Self-audit before final answer:
- [check]
```

## Multiplatform compatibility rules

Do not invent routes, compatibility, integrations, or platform capabilities.

Allowed sources for platform claims:

- User explicitly provides the route or requirement.
- The current repository already contains the route or config.
- Official platform documentation has been checked.
- A local tool or platform command confirms the behavior.

If none of those is true, say `needs verification`.

Safe generic statements:

- "Provide a canonical `SKILL.md`."
- "Provide an `AGENTS.md` fallback when the target agent reads repository instructions."
- "Provide a `GEMINI.md` fallback when Gemini CLI support is requested."
- "Provide prompt-only instructions for platforms without file-based skill loading."

Unsafe statements unless verified:

- "This platform automatically loads this exact path."
- "This file is guaranteed to work in every version."
- "This platform supports tools, MCP, rules, workflows, memory, or frontmatter."
- "This route is official."

When listing platform paths, use a status column:

```txt
Platform | File | Path | Status | Notes
Pi Agent | SKILL.md | .agents/skills/[skill-name]/SKILL.md | user-provided | Use if the project/platform is configured to read .agents skills.
OpenCode | SKILL.md | [PATH_TO_VERIFY] | needs verification | Do not claim official loading without docs or project config.
Codex | AGENTS.md | AGENTS.md | needs verification | Use only if this Codex environment reads repository instructions.
Gemini CLI | GEMINI.md | GEMINI.md | needs verification | Verify against target Gemini CLI behavior.
Universal | prompt-only | paste into system/developer instructions | not claimed | File loading not assumed.
```

## Rules

1. Preserve user context.
   - Do not ask for information already provided.
   - Respect explicit paths, platform names, languages, and constraints.
   - Keep useful parts of an existing skill unless they conflict with the update.

2. Be operational.
   - Use numbered steps.
   - Define exact inputs and outputs.
   - Include concrete checklists.
   - Include test prompts and expected results.

3. Be narrow but complete.
   - The skill must have a clear job.
   - Do not make it so generic that any request could trigger it.
   - Do not omit necessary failure handling just to keep it short.

4. Be honest about platforms.
   - Never invent support, paths, features, integrations, or compatibility.
   - Mark unverified claims as `needs verification`.
   - Prefer canonical plus fallback formats over pretending one format works everywhere.

5. Make outputs portable when requested.
   - `SKILL.md` is canonical.
   - `AGENTS.md` and `GEMINI.md` may be identical copies or adapted instruction files, depending on user request.
   - Prompt-only output must not depend on YAML frontmatter or file loading.

6. Include versioning.
   - Add version and changelog to every complete skill.
   - Increment version on updates.
   - Changelog entries must say what changed and why it matters.

7. Add regression tests.
   - Tests must prevent incomplete future skills.
   - Tests must include at least one failure-prevention case.
   - Tests must define expected results clearly enough for another agent to evaluate.

8. Self-audit before delivery.
   - Run the self-audit checklist.
   - Fix failures before delivery when possible.
   - Report remaining unknowns honestly.

9. Treat self-audit as the master delivery gate.
   - Do not deliver a child skill as complete until it passes self-audit.
   - Do not create only `SKILL.md` when the user requested multiplatform output.
   - Do not copy fallback files until the canonical skill has passed self-audit.
   - If the audit finds a recurring failure, add a regression test.

## Avoid

- Creating a skill with only vague advice.
- Writing a trigger description like "helps with skills" without concrete use cases.
- Forgetting `Inputs needed`, `Output format`, `Rules`, `Avoid`, `Quality checklist`, or tests.
- Omitting self-audit, regression tests, version, or changelog.
- Claiming a platform loads a path without evidence.
- Listing every popular agent platform as fully supported without checking.
- Making `AGENTS.md` or `GEMINI.md` contradict the canonical `SKILL.md`.
- Using unsupported YAML fields as if all platforms accept them.
- Leaving unresolved placeholders without listing them.
- Overfitting the skill to a single example when the user asked for reusable behavior.
- Making the skill so broad that it loses a clear trigger.

## Self-audit checklist

Run before delivery:

- [ ] The frontmatter has valid `name` and `description`.
- [ ] The description starts with `Use when` and describes trigger conditions.
- [ ] The skill name is lowercase and hyphenated.
- [ ] The purpose is clear and not generic.
- [ ] The "When to use" section includes realistic trigger phrases.
- [ ] Inputs are listed.
- [ ] Workflow steps are numbered and operational.
- [ ] Output format is explicit.
- [ ] Multiplatform mode exists if portability is requested.
- [ ] `SKILL.md`, `AGENTS.md`, `GEMINI.md`, and prompt-only options are covered when requested.
- [ ] The child skill has been self-audited before delivery.
- [ ] The delivered files match the requested mode: canonical only or multiplatform bundle.
- [ ] Platform paths and capabilities are marked `verified`, `user-provided`, `needs verification`, or `not claimed`.
- [ ] No unverified platform claim is presented as fact.
- [ ] Rules and Avoid sections prevent known failure modes.
- [ ] Quality checklist exists.
- [ ] Regression tests exist and cover incomplete-skill failures.
- [ ] Test prompts include normal, edge, missing-info, platform, and failure-prevention cases.
- [ ] Version, last updated, compatibility notes, and changelog are present.
- [ ] User requirements are all addressed.
- [ ] The skill is not too generic.
- [ ] No unresolved `TODO`, `TBD`, or accidental placeholder remains.

## Quality checklist

Before delivering a skill, verify:

- [ ] A beginner agent could use it without asking unnecessary questions.
- [ ] A future agent can tell when to load it.
- [ ] The workflow produces the requested deliverable.
- [ ] The output format is concrete enough to compare against.
- [ ] The skill preserves important user-provided constraints.
- [ ] Sensitive workflows include safety, privacy, legal, or permission notes.
- [ ] Any tools, APIs, or files are named only when actually needed.
- [ ] Platform-specific claims are sourced or marked as unverified.
- [ ] The final response tells the user what files were created or updated.

## Regression tests

Use these as non-negotiable tests for future versions of this skill.

### Regression 1: Multiplatform output cannot be incomplete

Prompt:

```txt
Create a portable skill for API design. It must work as SKILL.md, AGENTS.md, GEMINI.md, and prompt-only instructions.
```

Expected result:

- Delivers canonical `SKILL.md`.
- Includes optional `AGENTS.md`, `GEMINI.md`, and prompt-only formats or clearly states where each should be generated.
- Includes platform matrix with status labels.
- Does not claim universal auto-loading.

### Regression 2: No invented platform compatibility

Prompt:

```txt
Make this skill work in Pi Agent, OpenCode, Antigravity, Codex, Gemini CLI, Claude Code, VS Code agents, Cursor, Roo, and Cline. I did not provide docs or config.
```

Expected result:

- Provides portable files.
- Marks unknown paths or capabilities as `needs verification`.
- Does not invent official routes, commands, marketplace support, MCP support, workflow support, or frontmatter support.

### Regression 3: Existing skill improvement preserves good parts

Prompt:

```txt
Improve this existing skill. Keep the examples and domain rules, but add self-audit and changelog.
```

Expected result:

- Keeps useful existing examples and domain rules.
- Adds self-audit and changelog.
- Increments version.
- Adds regression tests for the new guarantees.

### Regression 4: Missing information uses placeholders

Prompt:

```txt
Create a skill for my weekly workflow. I know it uses a dashboard, but I do not know the platform name yet.
```

Expected result:

- Proceeds with `[DASHBOARD_PLATFORM]` or similar placeholders.
- Asks only if the missing platform changes the skill's core job.
- Lists placeholders before delivery.

### Regression 5: Self-audit catches incomplete output

Prompt:

```txt
Create a skill quickly. Just give me the workflow.
```

Expected result:

- Does not deliver only a workflow if a complete skill is requested.
- Includes frontmatter, purpose, inputs, output format, rules, avoid, tests, self-audit, version, and changelog unless user explicitly asked for a tiny draft.

### Regression 6: Changelog required for updates

Prompt:

```txt
Update this skill from v1.2.0 to add a new AGENTS.md fallback.
```

Expected result:

- New version is at least v1.3.0.
- Changelog includes the fallback addition.
- Regression tests include a case for AGENTS.md fallback.

### Regression 7: Domain-specific constraints are not lost

Prompt:

```txt
Improve a VRoid texture skill so it is portable across platforms.
```

Expected result:

- Keeps VRoid-specific constraints such as UV templates, texture size, transparency, import compatibility, and validation.
- Adds platform packaging without turning the skill into a generic asset prompt.

### Regression 8: Master self-audit prevents incomplete child delivery

Prompt:

```txt
Create a child skill for API documentation. I want it portable across Pi Agent, OpenCode, Antigravity, Codex, Gemini CLI, Claude Code, VS Code agents, Cursor, Roo, and Cline.
```

Expected result:

- The master audits the child skill before delivery.
- The child skill is not delivered as complete if it only contains `SKILL.md`.
- The output includes requested fallback options or clearly marks missing outputs as unresolved gaps.
- The platform matrix avoids invented paths and capabilities.
- A regression test is included for any gap found during audit.

## Test prompts

### 1. Create a simple new skill

Prompt:

```txt
/skill-creator-pro Create a skill that helps users generate SEO audit reports for small websites.
Inputs: website URL and top 5 keywords.
Output: findings, recommendations, and prioritized next steps.
```

Expected result:

- Complete `SKILL.md`.
- Clear trigger description.
- Workflow with SEO audit steps.
- Output format for the report.
- Rules, avoid list, quality checklist, self-audit, regression tests, and changelog.

### 2. Improve an incomplete skill

Prompt:

```txt
/skill-creator-pro Improve this:

---
name: email-template-writer
description: Write email templates
---

# Email Template Writer
1. Ask what email is for.
2. Write it.
```

Expected result:

- Better trigger.
- Inputs for audience, goal, tone, CTA, constraints.
- Output format for the email.
- Self-audit and tests.
- Version and changelog.

### 3. Convert a repeated workflow

Prompt:

```txt
/skill-creator-pro Turn my weekly analytics review into a reusable skill:
compare bounce rate, session duration, conversion rate, and write three improvements.
```

Expected result:

- Skill contract matches the weekly workflow.
- Uses placeholders for unknown analytics platform.
- Outputs a reusable review format.
- Includes regression tests for missing data and comparison logic.

### 4. Create a multiplatform bundle

Prompt:

```txt
/skill-creator-pro Create a portable skill for database schema reviews.
I want SKILL.md, AGENTS.md, GEMINI.md, and prompt-only.
```

Expected result:

- Canonical `SKILL.md`.
- Optional fallback formats.
- Platform matrix with status labels.
- No invented platform loading behavior.

### 5. Handle missing platform docs

Prompt:

```txt
/skill-creator-pro Make this compatible with every agent platform. I do not have documentation.
```

Expected result:

- Provides portable instructions.
- Marks all unverified platform behavior as `needs verification`.
- Does not claim guaranteed compatibility.

### 6. Visual or asset skill

Prompt:

```txt
/skill-creator-pro Create a skill for making VRoid-compatible clothing textures from references.
```

Expected result:

- Keeps VRoid-specific constraints.
- Requires template or UV-zone analysis.
- Includes output dimensions and validation.
- Includes failure-prevention test for template-zone violations.

### 7. Business or automation skill

Prompt:

```txt
/skill-creator-pro Create a skill for prospecting with Firecrawl.
Users provide a target website.
Output a CSV with leads ready for outreach.
```

Expected result:

- Includes ethical scraping boundaries.
- Includes privacy and permission cautions.
- Defines data fields and failure handling.
- Does not promise access to blocked or restricted data.

## Version

Version: 1.2.0
Last updated: 2026-05-05

Compatibility notes:

- Canonical format: `SKILL.md`.
- Optional fallbacks: `AGENTS.md`, `GEMINI.md`, prompt-only instructions.
- Platform support must be verified from project context, official docs, tool output, or explicit user instruction before being claimed.
- Without verification, platform routes and capabilities must be marked `needs verification`.

## Changelog

### 1.2.0 - 2026-05-05

- Added a hard master self-audit gate before delivering any child skill.
- Added the master-to-child create, test, fix, and master-update loop.
- Added a regression test to prevent incomplete child skill delivery when multiplatform output is requested.
- Clarified that fallback files must not be copied or delivered as complete until the canonical child skill passes self-audit.

### 1.1.0 - 2026-05-04

- Added explicit multiplatform mode for portable skill bundles.
- Added optional outputs for `SKILL.md`, `AGENTS.md`, `GEMINI.md`, and prompt-only instructions.
- Added mandatory self-audit mode before delivery.
- Added versioning and changelog requirements for every complete skill.
- Added regression tests to prevent incomplete future skills.
- Added strict rule against inventing platform routes, compatibility, or capabilities.
- Preserved the original skill's core workflow for creating, improving, converting, packaging, and testing skills.

### 1.0.0 - 2026-05-04

- Initial complete version for creating, improving, testing, and packaging reusable AI agent skills.

