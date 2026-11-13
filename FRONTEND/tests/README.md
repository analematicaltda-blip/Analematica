# Frontend regression checks

`node FRONTEND/tests/service-worker.cjs` exercises actual worker lifecycle,
online refresh, offline scripts, and exclusion of API/authenticated requests.

`landing.cjs` uses Playwright against a local web server. It checks four widths,
the requested section order, preservation of all twelve sections and form
options, dark rounded controls, image failure fallback, escaped slide titles,
single active slide after reinitialization, and keyboard controls.

Set `PLAYWRIGHT_MODULE` to an installed Playwright module when it is outside
the repository. `SGA_WEB_URL` selects the web origin (default localhost18090).
`CHROMIUM_PATH` optionally selects a system Chromium; otherwise the installed
Playwright browser is used. `SGA_SCREENSHOTS` optionally selects an output
directory. Tests use explicit API fixtures and reject third-party requests;
they do not prove backend behavior or availability of external photo services.

The frontend-regression GitHub workflow installs the pinned browser tooling
and runs both checks on frontend pushes and pull requests. Its remote result
must be checked separately; local success does not establish remote CI success.
