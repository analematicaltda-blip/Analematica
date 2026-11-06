---
name: vanillajs-injector
description: Use when a cloned UI needs its dynamic functionality restored (search, modals, filters) offline without relying on the original obfuscated framework bundles.
---

# Vanilla JS Injector

Restore interactivity to static HTML clones by writing targeted, clean Vanilla JS to replace obfuscated frontend frameworks.

## Purpose
To breathe life back into static DOM snapshots. By identifying CSS classes and IDs from the cloned HTML, you inject custom Vanilla JS scripts that emulate the original Vue/React behaviors perfectly offline.

## When to use this skill
- When a cloned website's buttons, search bars, or modals don't work.
- When replacing broken `_next.js` or `webpack.js` chunks.
- When building a functional offline MVP from a static clone.

## Inputs needed
- The static HTML of the clone.
- The desired functionality (e.g., "make the search bar filter the grid").
- A mock JSON data source (if populating lists).

## Workflow
1. Analyze the static HTML to identify the existing IDs, classes, and structure of the target component (e.g., `#search-input`, `.modal-active`).
2. Write a single, robust `custom_script.js` file.
3. Hook event listeners (`click`, `keyup`) to the existing UI elements.
4. If rendering items, build HTML string templates that exactly match the original CSS class structure.
5. Inject the `<script src="custom_script.js"></script>` at the end of the `<body>` of the static HTML.

## Output format
- Clean, dependency-free Vanilla JS code.
- Instructions on where to link the script.

## Rules
- Match the original CSS classes exactly so no visual design is broken.
- Use `fetch()` for mock APIs instead of hardcoding data arrays in the JS when possible.
- Ensure event listeners are null-safe (`if(el) el.addEventListener(...)`).

## Avoid
- Avoid installing Node.js frameworks or npm packages.
- Avoid deleting existing CSS styling hooks.

## Quality checklist
- [ ] No external dependencies (Vanilla JS only).
- [ ] Original UI classes are strictly maintained.
- [ ] Null checks exist for all queried DOM elements.

## Version
Version: 1.0.0
Last updated: 2026-05-08

