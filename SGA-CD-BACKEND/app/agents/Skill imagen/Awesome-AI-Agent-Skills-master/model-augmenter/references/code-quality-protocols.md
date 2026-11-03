# Code Quality Protocols — Detailed Reference

## Karpathy's 4 Principles for AI Code

### 1. Think Before Coding
- State assumptions explicitly before writing code
- If multiple approaches exist, present tradeoffs
- Push back when a simpler approach exists
- Ask clarifying questions when ambiguity changes the implementation

### 2. Simplicity First
- Minimum code that solves the actual problem
- No speculative features, premature abstractions, or "flexibility" not requested
- If 200 lines could be 50 → rewrite
- Test: "Would a senior engineer say this is overcomplicated?"

### 3. Surgical Changes
- Touch ONLY what the task requires
- Match existing code style, don't "improve" it
- Don't refactor adjacent code, delete pre-existing dead code, or reformat
- Remove only imports/variables YOUR changes made unused
- Test: "Does every changed line trace to the user's request?"

### 4. Goal-Driven Execution
- Define success criteria BEFORE coding
- Transform vague goals: "Fix bug" → "Reproduce with test, then make it pass"
- Create verification plan for multi-step tasks

## Anti-Patterns

| Anti-Pattern | Example | Fix |
|-------------|---------|-----|
| Kitchen Sink | User asks for date formatter, you build a DateFormatter class with locale, timezone, caching | Write one function: `formatDate(date)` |
| Drive-By Refactor | Fixing a typo but also "improving" error handling and async patterns | Only fix the typo |
| Speculative Architecture | TODO app with DDD, use cases, repositories, 15 files | `app.js` + `index.html` + `style.css` |
| Premature Generalization | Making everything configurable via env vars | Hardcode unless flexibility was requested |

## Code Review Checklist

- [ ] Every changed line traces to the stated goal
- [ ] No speculative features or "future-proofing"
- [ ] No drive-by refactors or style changes
- [ ] Complexity proportional to the problem
- [ ] Existing patterns followed, not invented
- [ ] Only YOUR unused imports removed
- [ ] Error handling covers realistic cases only
