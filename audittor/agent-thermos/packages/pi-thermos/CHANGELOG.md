# @thinkscape/pi-thermos

## 0.1.4

### Patch Changes

- 129b4a2: Restore parent workflow guidance in generated Pi Thermos prompts so sessions gather diff and changed-file context before launching provider subagents and pass the same labeled evidence sections to both agents.
- 8c78fd1: Align the effective Thermos parent workflow across Codex, Claude, and Pi with Cursor's upstream Thermos main skill while keeping host-specific invocation and provider notes separate.

## 0.1.3

### Patch Changes

- 2bd70e3: Fix Pi slash-command registration and stop shipping internal Thermos skills as selectable Pi skill commands.

## 0.1.2

### Patch Changes

- Sync host plugin manifest versions with package versions during release.

## 0.1.1

### Patch Changes

- Ship the full upstream Thermos rubric skills in each host package and keep them synced from core.
