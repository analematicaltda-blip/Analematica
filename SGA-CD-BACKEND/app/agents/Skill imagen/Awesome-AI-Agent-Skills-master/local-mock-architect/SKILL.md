---
name: local-mock-architect
description: Use when building a local Python server to serve a cloned SPA, handle static assets, intercept API routes, and resolve 404 navigation errors.
---

# Local Mock Architect

Build lightweight Python HTTP servers that act as reverse-proxies/mock-backends for offline SPA clones.

## Purpose
To ensure cloned SPAs can navigate sub-pages (SPA routing) without 404 errors, and to intercept production API endpoints to return local JSON data.

## When to use this skill
- When a cloned SPA needs a backend to function locally.
- When navigating from `/` to `/login` causes a 404 in standard Python `http.server`.
- When the clone makes `fetch()` calls to `/api/products` and needs mock data.

## Inputs needed
- The directory structure of the clone.
- The API endpoints to intercept.
- The HTML routes to map.

## Workflow
1. Create a `server.py` using `http.server.SimpleHTTPRequestHandler`.
2. Override `do_GET(self)`.
3. Map SPA routes manually (e.g., `if self.path == '/login': self.path = '/login.html'`).
4. Map API routes (e.g., `if self.path == '/api/data': serve_json_file()`).
5. Fallback to `super().do_GET()` for static assets (`.css`, `.png`, `.js`).

## Output format
- A complete, runnable Python script (`server.py`).
- A `start.bat` or `start.sh` wrapper.

## Rules
- Always strip query parameters when routing static files.
- Always set appropriate headers (`Content-type: application/json` for APIs).
- Keep it standard-library only (no Flask/Django required).

## Avoid
- Avoid complex frameworks for simple clones.
- Avoid hardcoding absolute paths.

## Quality checklist
- [ ] Handles base `/` routing.
- [ ] Handles sub-page routing.
- [ ] Intercepts and serves JSON with correct headers.
- [ ] Serves static assets gracefully.

## Version
Version: 1.0.0
Last updated: 2026-05-08

