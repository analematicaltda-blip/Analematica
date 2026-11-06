---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

Write comprehensive implementation plans assuming the engineer has zero context for our codebase.

**Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`

## Task Structure

```markdown
### Task N: [Component Name]
**Files:**
- Create: `exact/path/to/file`
- Modify: `exact/path/to/existing`

- [ ] **Step 1: Write failing test**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Minimal implementation**
- [ ] **Step 4: Verify pass**
- [ ] **Step 5: Commit**
```

## No Placeholders
Every step must contain the actual code/content needed. No "TBD" or "add error handling".
