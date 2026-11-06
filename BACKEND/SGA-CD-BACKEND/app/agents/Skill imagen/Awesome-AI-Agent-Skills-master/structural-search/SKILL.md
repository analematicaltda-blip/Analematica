---
name: structural-search
description: Navigate codebases with hybrid text and syntax-aware structural search using ripgrep and ast-grep progressive refinement.
---

# Structural Search Skill (Hybrid Edition)

Optimized codebase navigation using both text-based (ripgrep) and syntax-aware (ast-grep) engines. This skill implements the "MassGen" progressive refinement protocol to maximize accuracy and minimize token consumption.

## Engines
1. **Text Engine (grep_search)**: Best for strings, comments, and literal identifiers.
2. **Structural Engine (ast-grep)**: Best for finding function definitions, class hierarchies, and complex patterns (e.g., "find all React components with more than 3 props").

## The Hybrid Protocol (Progressive Refinement)
1. **Count First**: Always run a count check if the codebase is large.
2. **Structural Pattern**: Use `$X` as wildcards in `ast-grep` to find logic, not just text.
3. **Scope Limiting**: Force `--type` or `--lang` to avoid scanning unrelated binaries.
4. **Token Guard**: If results > 50, show only the file paths first.

## Usage Examples
- "Find all python functions that return a dictionary: `sg -p 'def $NAME($$$) -> dict: $$$' -l py`"
- "Search for hardcoded API keys in strings: `grep_search pattern='API_KEY='`"
- "Locate all classes extending BaseService: `sg -p 'class $CLASS extends BaseService { $$$ }' -l ts`"

---
*Hybrid Logic: Ripgrep Speed + AST-Grep Intelligence.*

