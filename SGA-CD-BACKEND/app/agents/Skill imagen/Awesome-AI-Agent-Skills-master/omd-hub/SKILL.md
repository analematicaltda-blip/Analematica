---
name: omd-hub
description: >
  Central hub for oh-my-design (OmD) — connects all omd-* skills and agents 
  for any AI coding agent. Trigger on: "design system", "DESIGN.md", 
  "brand tokens", "design harness", "diseñar interfaz", "sistema de diseño",
  "crear DESIGN.md", "references de diseño", "oh-my-design", "omd".
  This skill provides path resolution and environment setup for the 
  globally-installed OmD suite.
compatible_tools: [antigravity, gemini-cli, claude-code, codex-cli, cursor, opencode, roo, cline]
tags: [design-system, ui, brand, design-md, omd, google-stitch]
---

# omd-hub — oh-my-design Global Integration

## What is OmD?

oh-my-design turns your AI coding agent into a **senior product designer** with working memory of your brand. It uses 67 real company design systems as references to generate project-specific `DESIGN.md` files following the Google Stitch format.

## Global Installation Paths

All OmD resources are installed centrally. Use these paths:

### References (67 company DESIGN.md files)
```
C:/Users/gegeusus/.gemini/antigravity/scratch/oh-my-design/references/<company>/DESIGN.md
```

Available companies: airbnb, airtable, apple, baemin, bmw, cal, claude, clay, clickhouse, cohere, coinbase, composio, cursor, dcard, elevenlabs, expo, ferrari, figma, framer, freee, hashicorp, ibm, intercom, kakao, karrot, kraken, lamborghini, line, linear.app, lovable, mercari, minimax, mintlify, miro, mistral.ai, mongodb, notion, nvidia, ollama, opencode.ai, pinkoi, pinterest, posthog, raycast, renault, replicate, resend, revolut, runwayml, sanity, sentry, spacex, spotify, stripe, supabase, superhuman, tesla, together.ai, toss, uber, vercel, voltagent, warp, webflow, wise, x.ai, zapier

### Data Files (fingerprints, vocabulary, tags)
```
C:/Users/gegeusus/.gemini/skills/omd-data/reference-fingerprints.json
C:/Users/gegeusus/.gemini/skills/omd-data/reference-tags.md
C:/Users/gegeusus/.gemini/skills/omd-data/vocabulary.json
C:/Users/gegeusus/.gemini/skills/omd-data/synonyms.json
```

### Skills (SKILL.md prose instructions)
```
C:/Users/gegeusus/.gemini/skills/omd-apply/SKILL.md     — Brand context injection + dispatch
C:/Users/gegeusus/.gemini/skills/omd-init/SKILL.md      — DESIGN.md bootstrap from reference
C:/Users/gegeusus/.gemini/skills/omd-harness/SKILL.md   — Full 10-phase design pipeline
C:/Users/gegeusus/.gemini/skills/omd-learn/SKILL.md     — Fold corrections into DESIGN.md
C:/Users/gegeusus/.gemini/skills/omd-remember/SKILL.md  — Capture user corrections
C:/Users/gegeusus/.gemini/skills/omd-sync/SKILL.md      — Maintain shim files
```

### Agent Definitions (sub-agent prose)
```
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-master.md        — Orchestrator
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-ux-researcher.md  — UX research
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-ui-junior.md      — Wireframes/components
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-ux-engineer.md    — Interaction audit
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-asset-curator.md  — Asset selection
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-3d-blender.md     — 3D rendering
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-microcopy.md      — Voice-consistent copy
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-ux-writer.md      — Copy audit + A/B
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-a11y-auditor.md   — WCAG checks
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-persona-tester.md — 4-persona walkthrough
C:/Users/gegeusus/.gemini/skills/omd-agents/omd-critic.md         — Root-cause analysis
```

## How to Use (Natural Language)

### Initialize a design system:
- "Set up the design system for a calm B2B fintech dashboard"
- "Crea un DESIGN.md estilo Stripe para mi app de pagos"
- "Initialize DESIGN.md — Airbnb style for a travel marketplace"

### Apply brand context to UI work:
- "Make this card component use our design tokens"
- "Adjust the color palette to be warmer"
- "Aplica el sistema de diseño a este componente"

### Full design pipeline:
- "Design the entire onboarding from scratch — Toss-style"
- "Diseña la pantalla principal al estilo Linear"
- "/omd-harness Landing page for a SaaS analytics tool"

## Workflow for Global Use

Since OmD is installed globally but `DESIGN.md` is per-project:

1. **First time in a project**: Read the omd-init skill and create a `DESIGN.md` in the project root. Reference files are at the central path above — read them with Read tool directly.

2. **Subsequent UI work**: Read the project's `DESIGN.md` and `.omd/preferences.md` (if exists). Apply brand tokens per the omd-apply skill.

3. **For reading references**: Instead of CLI commands, directly read the reference DESIGN.md files:
   ```
   Read: C:/Users/gegeusus/.gemini/antigravity/scratch/oh-my-design/references/<company>/DESIGN.md
   ```

4. **For fingerprint matching**: Read the fingerprints JSON directly:
   ```
   Read: C:/Users/gegeusus/.gemini/skills/omd-data/reference-fingerprints.json
   ```

## Adaptation Notes (Antigravity/Gemini)

- **No CLI dependency**: The original `omd` CLI commands referenced in skills (like `omd init recommend`) are NOT available globally. Instead, the agent should read data files directly and perform matching in-context.
- **Sub-agents**: Antigravity doesn't have Claude Code's `/agents` dispatch. Instead, load the relevant agent `.md` file as context when specialized behavior is needed.
- **File-based operations**: All Write/Read operations work the same — the agent writes DESIGN.md, .omd/preferences.md, etc. directly using file tools.

## Hard Rules

- Never fabricate DESIGN.md §11-13 facts. Use `[FILL IN]` placeholders if user-provided facts are absent.
- Never introduce a token absent from DESIGN.md without user approval.
- Never download from Pinterest. Pinterest URLs are listed for user to download manually.
- Never auto-skip user checkpoints.
- Never delete a run directory.

