---
name: spa-live-cloner
description: Use when the user wants to extract the real, post-hydration HTML from a heavily protected Single Page Application (Vue, React) to bypass obfuscation, Cloudflare, or loaders.
---

# SPA Live Cloner

Extract the true, hydrated HTML of protected SPAs using Scrapling or Playwright to bypass security walls and generate static clones.

## Purpose
To bypass frontend obfuscation (Webpack, Next.js, minified chunks) and domain-locking loaders by launching a headless browser, waiting for network/hydration completion, and dumping the final DOM.

## When to use this skill
- When requested to clone a protected Vue or React site.
- When `curl` or simple requests return empty `div#app` or infinite loaders.
- When you need to bypass "Cargando experiencia" or Cloudflare screens to get the real UI.

## Inputs needed
- Target URL
- Sub-pages (if any)
- Approximate wait time needed for hydration/animations (default 5-10s)

## Workflow
1. Initialize a Python script using `playwright.sync_api` (or Scrapling).
2. Launch a headless Chromium browser instance.
3. Navigate to the target URL (`page.goto(url, wait_until='domcontentloaded')`).
4. Wait for dynamic elements (e.g., `time.sleep(10)` or specific selectors).
5. Extract `page.content()` and save to a local text file.
6. Clean the HTML by stripping out broken/minified security scripts (e.g., `_next.js`, `productos.min.js`).

## Output format
- A Python script to run the extraction.
- The extracted, clean `.html` files ready for local use.

## Rules
- Never use simple `urllib` or `requests` for SPAs.
- Always wait for the DOM to settle to ensure data is populated.
- Strip out the minified security scripts from the extracted HTML so they don't break the local clone.

## Avoid
- Avoid extracting before animations finish (leads to hidden modals).
- Avoid leaving the original framework's minified scripts if they contain domain locks.

## Quality checklist
- [ ] Uses headless browser.
- [ ] Includes adequate wait times.
- [ ] HTML output is clean of security loops.

## Version
Version: 1.0.0
Last updated: 2026-05-08

