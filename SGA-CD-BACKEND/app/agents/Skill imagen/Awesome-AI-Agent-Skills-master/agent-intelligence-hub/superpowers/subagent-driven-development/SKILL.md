---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session
---

# Subagent-Driven Development

Execute plan by dispatching fresh subagent per task, with two-stage review after each: spec compliance review first, then code quality review.

## The Process
1. **Dispatch implementer subagent**
2. **Implementer implements, tests, commits**
3. **Dispatch spec reviewer subagent**
4. **Dispatch code quality reviewer subagent**
5. **Mark task complete**

## Advantage
- Fresh context per task
- Review loops ensure fixes work
- TDD by default
