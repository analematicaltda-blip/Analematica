---
name: iterative-cloning
description: Use when tasked with cloning or reverse-engineering a multi-page web application to ensure methodical, step-by-step execution.
---

# Iterative Cloning Methodology

Force a modular, step-by-step approach when cloning complex web applications to isolate bugs and prevent destructive "master plan" overwrites.

## Purpose
To prevent the agent from making sweeping, site-wide changes that break existing functionality. It enforces fixing and perfecting one page or component at a time.

## When to use this skill
- When the user asks to clone a whole website.
- When fixing interconnected bugs in an MPA/SPA.
- When migrating systems.

## Inputs needed
- The list of pages/components to clone.

## Workflow
1. Acknowledge the full scope but propose starting with ONE component (e.g., "Let's perfect `index.html` first").
2. Extract, clean, and inject the logic for that single component.
3. Test the single component and ask the user for verification ("Does the index look perfect?").
4. ONLY upon user approval, proceed to the next component in the list.

## Output format
- A sequenced task list.
- Incremental file updates.

## Rules
- Never update more than two distinct sub-pages in a single turn.
- Always pause for user visual verification between major components.

## Avoid
- Avoid "big bang" deployments where all HTML files are overwritten at once.
- Avoid moving to step 2 if step 1 has known bugs.

## Quality checklist
- [ ] Scope is reduced to one page/component.
- [ ] User is prompted for verification.
- [ ] Existing working code is not accidentally modified during the iteration.

## Version
Version: 1.0.0
Last updated: 2026-05-08

