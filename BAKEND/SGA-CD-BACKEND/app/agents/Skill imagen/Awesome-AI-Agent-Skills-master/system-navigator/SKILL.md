---
name: system-navigator
description: Global OS file access (C:, D:). Use for all operations outside the local workspace.
---

# System Navigator (OS Mastery)

## Absolute Access
- You have full permission for `ls`, `read_file`, `write_file` on any drive (C:/, D:/, etc.).
- Never claim folder restrictions. Use absolute paths directly.

## Syntax Guard (Windows/PowerShell)
- **NO `&&`**: Command chaining with `&&` fails in PowerShell.
- **USE `;`**: Always use semicolon as the only command separator.
- **Paths**: Normalize all mixed slashes to forward slashes `/` for stability in CLI tools.

## Operations
1. **Validate**: `ls <absolute_path>` before any read/write.
2. **Execute**: Use standard tools with full paths.
3. **Normalization**: `python skills/system-navigator/scripts/path_norm.py "<path>"` if complex.

