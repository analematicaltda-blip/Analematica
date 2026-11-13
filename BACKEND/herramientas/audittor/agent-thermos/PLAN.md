# Upstream Thermos Skills Watch Workflow

## Context
- The repository carries canonical local Thermos skills under `packages/core/skills/` and generated Codex references under `packages/codex-thermos/skills/`.
- Upstream source to monitor: `https://github.com/cursor/plugins/tree/main/thermos/skills`.
- Goal: detect upstream skill changes and create a clear opportunity to review/update our copy, without silently overwriting local changes.
- Preferred handoff: open or update an issue rather than an automated PR.

## Files to modify
- `.github/upstream/thermos-skills.json` — tracked source metadata and the last upstream commit that has been reviewed/acknowledged.
- `.github/workflows/upstream-thermos-skills.yml` — weekly/manual watcher and issue upsert logic.
- No local skill files are changed by the watcher itself; updates remain deliberate maintainer changes.

## Reuse
- `scripts/sync-skills.ts` remains the local-to-Codex generation step. The issue checklist should call `bun run sync:skills` after canonical core changes, followed by the existing CI checks.
- Canonical mappings for the issue body:
  - upstream `thermo-nuclear-review/SKILL.md` → `packages/core/skills/thermo-nuclear-review/SKILL.md` → generated Codex reference;
  - upstream `thermo-nuclear-code-quality-review/SKILL.md` → `packages/core/skills/thermo-nuclear-code-quality-review/SKILL.md` → generated Codex reference;
  - upstream `thermos/SKILL.md` → `packages/core/src/content.ts` and generated host files, with host-specific adaptations preserved.
- Root scripts include `test:ci`, `sync:skills`, `validate:generated`, and `pack:check`.
- Existing GitHub Actions use `actions/checkout@v4`; `actions/github-script` can use the repository `GITHUB_TOKEN` without adding dependencies.

## Findings
- Upstream currently exposes three `SKILL.md` files: `thermo-nuclear-review`, `thermo-nuclear-code-quality-review`, and `thermos`.
- The two rubric skills map directly to `packages/core/skills/*/SKILL.md`, then `sync-skills.ts` copies them to Codex references. They are currently adapted from upstream but structurally aligned.
- The upstream `thermos/SKILL.md` is not a direct local file: its workflow is represented in `packages/core/src/content.ts` and rendered into `packages/codex-thermos/skills/thermos/SKILL.md`; host-specific notes are intentionally added by this repository.
- Therefore, exact local/upstream file equality is the wrong detector for the orchestrator. A reviewed upstream commit baseline plus a changed-path/compare link will detect drift without false positives or overwriting adaptations.
- No upstream watcher, issue template, or scheduled workflow exists today.
- The schedule should be weekly, with `workflow_dispatch` for an immediate/manual check.

## Approach
Use the smallest maintainable workflow: a weekly/manual GitHub Actions check, a tracked reviewed-commit baseline, and one deduplicated issue rather than an automated PR.

1. Store a small JSON baseline with `owner/repo`, `path`, `ref`, and `lastReviewedCommit`. Initialize it to the upstream path commit that corresponds to the current local review; do not silently advance it in automation.
2. On the weekly/manual run, use `actions/github-script` and the authenticated GitHub API to fetch the newest commit affecting `cursor/plugins:thermos/skills` on `main`.
3. If the SHA differs, compare the baseline and head, filter/report changed paths under `thermos/skills`, and create or update one issue identified by a hidden marker such as `<!-- upstream-thermos-skills-watch -->`. Include the upstream compare URL, SHAs, commit summaries, changed paths, local mapping, and a checklist to review/adapt, run `bun run sync:skills`/`bun run test:ci`, and advance the baseline in a normal PR.
4. If the SHA matches, do nothing. If an open watcher issue remains after a maintainer advances the baseline, close it with a short automated comment. The workflow never edits skill files, creates a branch, or opens a PR.
5. Give the job only `contents: read` and `issues: write`, add concurrency to avoid duplicate manual/scheduled runs, and let API/configuration failures fail visibly rather than creating a misleading issue.

## Steps
- [x] Add `.github/upstream/thermos-skills.json` with the source path and reviewed commit baseline.
- [x] Add a weekly `schedule` plus `workflow_dispatch` workflow with least-privilege permissions and concurrency.
- [x] Implement upstream commit lookup, baseline comparison, changed-path extraction, compare links, and clear error handling.
- [x] Implement marker-based issue creation/update and stale-issue closure without changing repository content.
- [x] Document the maintainer close-out loop in the issue body (review upstream, adapt canonical sources, regenerate, run CI, update baseline).
- [x] Validate YAML/script syntax and run the normal repository checks after any implementation changes.

## Verification
- Manually dispatch the workflow against the current baseline and confirm it produces no issue.
- Test the logic with a synthetic older baseline: verify a changed upstream commit produces one actionable issue and a second run updates the same issue instead of duplicating it.
- Verify a newer reviewed baseline closes the open watcher issue and an upstream API/configuration failure fails the job without touching code.
- Run `bun run test:ci` and confirm generated Codex references still match core after a simulated/manual skill update.

## Execution notes
- The embedded watcher JavaScript passed smoke tests for unchanged, changed, deduplicated, closed, and compare-error cases.
- `bun run test:ci` passed after its normal `sync:versions` step. That step rewrote three pre-existing generated version fields, so those unrelated changes were restored; the repository’s direct generated-file check consequently still reports that pre-existing version drift.
