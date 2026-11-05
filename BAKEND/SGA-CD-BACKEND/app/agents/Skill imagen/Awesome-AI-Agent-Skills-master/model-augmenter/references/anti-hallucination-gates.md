# Anti-Hallucination Gates — Detailed Reference

## Overview

The 5-gate pipeline prevents AI hallucinations by forcing sequential verification of every factual claim. Each gate is a checkpoint that must be passed before the claim is included in the response.

## Gate 1: Evidence Check

**Question:** Do I have DIRECT evidence for this claim?

### What Counts as Evidence

| Source | Strength | Example |
|--------|----------|---------|
| File content you just read | Strong | "I read package.json and it shows React 18.2.0" |
| Command output you just ran | Strong | "Running `node --version` shows v20.11.0" |
| Error message you observed | Strong | "The error says `Cannot find module 'lodash'`" |
| Official documentation | Medium | "The Node.js docs state that..." |
| User's explicit statement | Medium | "The user mentioned they use PostgreSQL" |
| Pattern inference | Weak | "Based on the file structure, this appears to be..." |

### What Does NOT Count as Evidence

- Your training data / "I know that..."
- Common assumptions about how things work
- What "most projects" do
- What you "remember" from past conversations
- What seems "obvious" or "standard"

### Gate 1 Decision

```
Evidence exists? → PASS → Continue to Gate 2
No evidence?    → BLOCK → Choose one:
  a) Find evidence (read file, run command)
  b) Mark claim as "based on general knowledge, needs verification"
  c) Remove the claim from your response
```

---

## Gate 2: Invention Check

**Question:** Am I INVENTING an API, function, CLI flag, config key, file path, or capability?

### Common Invention Patterns

| Category | Hallucination Example | How to Catch |
|----------|---------------------|--------------|
| API | `node:ai/pipeline` (doesn't exist) | Check official docs or run `node -e "require('node:ai')"` |
| CLI flag | `npm install --turbo` (doesn't exist) | Run `npm install --help` |
| Config key | `"experimentalFeatures": true` in tsconfig | Read actual tsconfig schema |
| Function | `Array.prototype.groupBy()` (proposal, not standard) | Check MDN or runtime |
| File path | `/etc/nginx/sites-enabled/` on macOS | Check OS-specific paths |
| Library | `import { useQuery } from 'react-query'` (package renamed) | Check current package name |
| Method | `response.json()` on a non-Response object | Check the object's actual API |

### Invention Red Flags

You're likely inventing if:
- You can't cite where you learned about this API/feature
- The function name is suspiciously convenient for the task
- You're combining features from different libraries
- The syntax "feels right" but you haven't verified it
- You're using a feature from a newer version than what's installed

### Gate 2 Decision

```
Am I inventing? → YES → BLOCK:
  a) Search for the real API/function
  b) Check documentation
  c) Use a verified alternative
  d) Mark as "assumed, needs verification"

Am I inventing? → NO (verified) → PASS → Continue to Gate 3
Am I inventing? → UNCERTAIN → TREAT AS YES (safer)
```

---

## Gate 3: Consistency Check

**Question:** Is my response CONSISTENT with what I inspected?

### Inconsistency Patterns

| Scenario | Inconsistency | Correction |
|----------|--------------|------------|
| Read file shows function A, recommend function B | Using wrong function | Use function A as found |
| Config file has YAML format, write JSON | Wrong format | Use YAML to match |
| Project uses tabs, generate spaces | Style mismatch | Match existing style |
| Existing code uses async/await, suggest callbacks | Pattern mismatch | Use async/await |
| File has 4 parameters, mention 3 | Missing parameter | Include all 4 |

### Self-Check Questions

1. Does my code change match the patterns I observed in the codebase?
2. Does my config change match the format of the existing config?
3. Do the function signatures I'm using match what I read?
4. Am I referencing the right file paths based on what I inspected?
5. Is my understanding of the error consistent with the actual error message?

### Gate 3 Decision

```
Response consistent with evidence? → YES → PASS
Response contradicts evidence?     → BLOCK → Re-inspect and correct
Not sure?                         → RE-INSPECT → Read the file/output again
```

---

## Gate 4: Similarity ≠ Certainty

**Question:** Am I confusing "this looks like X" with "this IS X"?

### Common Similarity Traps

| Looks Like | Could Actually Be | How to Distinguish |
|-----------|-------------------|-------------------|
| Express.js app | Fastify app with similar structure | Check package.json dependencies |
| MySQL syntax | PostgreSQL syntax | Check connection string or config |
| JWT auth | Session-based auth with tokens | Read auth middleware code |
| REST API | GraphQL endpoint at `/api` | Check route definitions |
| React component | Preact component | Check imports and package.json |
| Python 3 syntax | Python 2 compatibility code | Check python version and shebangs |
| Docker Compose v3 | Docker Compose v2 syntax | Check `version:` field |

### Language to Use

**Instead of:** "This is a React project"
**Use:** "Based on package.json showing react@18.2.0, this is a React 18 project"

**Instead of:** "The database is PostgreSQL"
**Use:** "The connection string in .env shows `postgresql://`, indicating PostgreSQL"

**Instead of:** "This uses TypeScript"
**Use:** "The presence of tsconfig.json and .ts files confirms TypeScript usage"

### Gate 4 Decision

```
Am I stating certainty based on similarity? → YES → BLOCK:
  a) Find confirming evidence
  b) Soften language: "appears to be" / "likely" / "based on [evidence]"

Am I stating certainty based on evidence? → PASS
```

---

## Gate 5: Honesty Audit

**Question:** Should I mark ANYTHING in my response as "needs verification"?

### When to Use "Needs Verification"

- Platform-specific behavior you haven't tested on this specific platform
- CLI flags you found in docs but haven't run
- Version-specific features when you're not sure of the installed version
- Configuration that works "in most setups" but might not in this specific one
- Performance claims without benchmarks
- Security assertions without audit
- Compatibility claims across different environments

### Honesty Templates

```
✅ Verified: [claim] — confirmed by [evidence]
⚠️ Needs verification: [claim] — based on [source], but not tested in this specific setup
🟡 Assumed: [claim] — reasonable based on [context], but not directly confirmed
❌ Unknown: [aspect] — insufficient information to determine
```

### Gate 5 Decision

```
Everything verified?     → PASS → Deliver response
Something unverified?    → ADD LABEL → Mark specific items and deliver
Major uncertainty?       → ESCALATE → Ask user or investigate further
```

---

## Common Hallucination Examples by Domain

### JavaScript / Node.js
- Using `fs.readFileSync()` with the wrong encoding parameter
- Assuming `fetch` is available in Node.js < 18
- Inventing Express middleware that doesn't exist
- Claiming `import` works without `"type": "module"` in package.json

### Python
- Using f-strings in Python 2 context
- Inventing pandas methods that don't exist
- Assuming `pip install` works when `pip3` is required
- Claiming `asyncio.run()` works in Python < 3.7

### System / DevOps
- Inventing systemd unit file directives
- Assuming apt/yum package names are identical
- Claiming a port is free without checking
- Inventing Docker Compose syntax

### Database
- Inventing SQL functions specific to one DBMS
- Assuming table/column names without checking schema
- Claiming indexes exist without verifying
- Using wrong quoting style for the specific DBMS

---

## Pipeline Summary

```
INPUT: Any factual claim in the response

G1: Evidence? ──── NO ──→ Find evidence or mark as unverified
     │ YES
     ▼
G2: Inventing? ── YES ──→ Find real alternative or mark
     │ NO
     ▼
G3: Consistent? ─ NO ──→ Re-inspect and correct
     │ YES
     ▼
G4: Certain? ──── NO ──→ Soften language or find proof
     │ YES
     ▼
G5: Honest? ──── NO ──→ Add "needs verification" labels
     │ YES
     ▼
OUTPUT: Verified claim included in response
```
