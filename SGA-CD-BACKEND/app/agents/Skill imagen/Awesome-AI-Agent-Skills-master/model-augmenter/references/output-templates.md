# Output Templates — Detailed Reference

## Template Selection

| Task Type | Template | Key Elements |
|-----------|----------|-------------|
| Code implementation | Implementation Report | Changed files, diffs, verification |
| Bug fix / debugging | Diagnostic Report | Root cause, fix, prevention |
| Advisory / consulting | Recommendation | Options, tradeoffs, next steps |
| Architecture design | Architecture Decision | ADR format, diagrams, rationale |
| Documentation | Doc Deliverable | Structure, examples, quick start |
| Quick fix | Minimal Report | What changed, verification |

---

## Template 1: Implementation Report

```
## Resultado

[1-2 sentence summary of what was done and why]

### Archivos modificados
- `path/file.ext` — [what changed and purpose]

### Verificación
- [test/command]: [pass/fail + evidence]

### Compatibilidad
- [platform]: verificado | necesita verificación

### Supuestos
- [material assumptions with classification: ✅/🟡/🟠]

### Riesgos o siguiente paso
- [only if relevant]
```

## Template 2: Diagnostic Report

```
## Diagnóstico

**Síntoma:** [what the user observed]
**Causa raíz:** [identified cause with evidence]
**Evidencia:** [file content, error output, or command result that confirms]

### Solución
[minimal targeted fix]

### Verificación
- [how to confirm it's fixed]

### Prevención
- [how to prevent recurrence — only if practical]
```

## Template 3: Recommendation

```
## Recomendación

[Direct answer — the recommended option]

### Razonamiento
- [evidence-based point 1]
- [evidence-based point 2]

### Alternativas consideradas
| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| [Alt A] | [...] | [...] | [...] |
| [Alt B] | [...] | [...] | [...] |

### Supuestos
- [material assumptions]

### Siguiente paso
- [concrete action the user should take]
```

## Template 4: Architecture Decision Record (ADR)

```
## ADR: [Decision Title]

**Status:** Proposed | Accepted | Deprecated
**Date:** [date]

### Contexto
[What is the issue that we're seeing that is motivating this decision?]

### Decisión
[What is the change that we're proposing/doing?]

### Consecuencias
**Positivas:**
- [benefit 1]

**Negativas:**
- [tradeoff 1]

**Riesgos:**
- [risk with mitigation]
```

## Template 5: Documentation Deliverable

```
## [Title]

[1-paragraph overview]

### Quick Start
[Fastest path to "it works"]

### Usage
[Detailed usage with examples]

### Configuration
[Available options]

### Troubleshooting
[Common issues and fixes]
```

## Template 6: Minimal Report (Quick Fix)

```
**Cambio:** [what changed]
**Archivo:** `path/file.ext`
**Verificación:** [evidence it works]
```

---

## Adaptive Template Rules

1. **Match template to task complexity** — Don't use Implementation Report for a typo fix
2. **Skip empty sections** — If no risks, don't include the risks section
3. **Use the user's language** — If they write in Spanish, respond in Spanish
4. **Code > prose** — Show diffs and code over descriptions when possible
5. **Evidence > claims** — Always include how you verified
