---
name: surgical-editor
description: Perform atomic file edits with surgical search/replace blocks, minimal context changes, and strict post-edit verification.
---

# Surgical Editor Skill

Experto en la manipulación atómica de archivos utilizando el protocolo `mcp-text-editor` y técnicas de parcheado por bloques (Search/Replace).

## Mandatos Obligatorios

1.  **NUNCA** reescribir un archivo completo si solo cambia una sección lógica.
2.  **SIEMPRE** leer el rango de líneas específico antes de actuar (`read_file` con `start_line` y `end_line`).
3.  **USAR** el MCP `surgical-editor` (si está activo) o la herramienta `replace` con el bloque mínimo de contexto necesario (mínimo 3 líneas de arriba y abajo para evitar colisiones).
4.  **VERIFICAR** el archivo después de la edición para asegurar que no se borraron llaves (`}`) o decoradores accidentalmente.

## Flujo de Trabajo (Surgical Loop)

1.  **Locate**: Usar `grep_search` para encontrar el punto exacto.
2.  **Context**: Leer 5 líneas antes y después del objetivo.
3.  **Patch**: Aplicar el cambio usando el string más corto e inequívoco posible.
4.  **Confirm**: Validar que el archivo sigue siendo válido (ej. compilación o lint).

## Anti-Patrones (Prohibido)

*   Borrar bloques grandes de código "para simplificar".
*   Reemplazar funciones enteras cuando solo cambia un parámetro.
*   Ignorar avisos de "No occurrences found" intentando forzar un `write_file`.

