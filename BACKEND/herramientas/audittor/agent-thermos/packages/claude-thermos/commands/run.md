---
description: Run deep correctness/security and strict code-quality reviews of the current branch.
argument-hint: [base-ref | PR URL | scope]
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git show:*), Bash(git rev-parse:*), Bash(gh pr view:*), Bash(glab mr view:*)
---

# Thermos

Usage: `/thermos:run [base-ref | PR URL | scope]`

Run the two thermo review passes as async background subagents in parallel, then synthesize their results.

## Workflow

1. Determine the review scope from the user request, PR, current branch, or relevant changed files.
2. Gather the diff and any file/context excerpts needed for reviewers to evaluate the change without guessing.
3. Launch both subagents in the same message with `run_in_background: true`:
   - `subagent_type: "thermo-nuclear-review-subagent"` for bugs, breakages, security, devex regressions, feature-flag leaks, and other branch-audit risks.
   - `subagent_type: "thermo-nuclear-code-quality-review-subagent"` for maintainability, structure, file-size growth, spaghetti, abstractions, and codebase-health risks.
4. Pass each subagent the same scoped diff/file context and ask it to return prioritized findings with file references and evidence.
5. After both finish, synthesize the results with findings first, deduplicated across reviewers. Weight overlapping findings more heavily, resolve disagreements with your own judgment, and keep summaries brief.

If individual background summaries are already visible to the user, do not restate them wholesale. Surface the unified verdict, the highest-signal findings, and any remaining uncertainty.

## Claude Notes

If no scope is provided, review the current branch against `main`. Use the plugin-scoped Claude agent names `thermos:thermo-nuclear-review-subagent` and `thermos:thermo-nuclear-code-quality-review-subagent` for the matching upstream `subagent_type` values.

Pass both agents the same labeled context sections:
- `### Git / diff output`
- `### Changed file contents`
- `### User scope / intent`

If the plugin-scoped agents are unavailable, run the same two review passes with general-purpose subagents using the rubrics embedded in this command package.
