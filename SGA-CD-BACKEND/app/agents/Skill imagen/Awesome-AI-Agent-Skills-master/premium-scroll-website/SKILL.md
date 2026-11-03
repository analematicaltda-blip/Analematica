---
name: premium-scroll-website
description: Use when the user asks to create a premium single-page scrolling website, landing page, portfolio, or business site with scroll animations, responsive design, and modern aesthetics. Also use when the user says "crea una web premium", "haz una landing", "quiero una web con scroll", "website para mi negocio", "premium website", "scroll website", or provides a URL as design inspiration. Supports instructions-only, reference-URL-only, or hybrid input modes.
---

# Premium Scroll Website

Create premium, single-page scrolling websites with modern animations, responsive design, SEO fundamentals, and professional aesthetics — guided by a flexible input system that adapts to how the user wants to work.

## Purpose

This skill creates production-ready, premium single-page websites from user instructions, a reference URL, or both. It outputs `index.html`, `styles.css`, `script.js`, and `README.md` with scroll-triggered animations, responsive layouts, and basic SEO. The skill acts as a guided premium web creator that asks the right questions, never repeats what the user already provided, and delivers a polished result.

## When to use this skill

Use when the user:

- Asks to create a premium website, landing page, portfolio, or business site.
- Wants a single-page scrolling website with modern animations.
- Provides a URL and asks to create something similar or inspired by it.
- Says "crea una web premium", "haz una landing", "quiero una web con scroll", "hazme una web para mi negocio".
- Says "premium website", "scroll website", "landing page", "one-page site".
- Provides both text instructions and a reference URL.
- Wants a website with WhatsApp CTA, booking, contact form, or purchase button.

Do not use for multi-page applications, e-commerce stores with cart/checkout, web apps with authentication, or backend development.

## Core principle

A premium website must look and feel premium from the first scroll. The skill prioritizes visual excellence, smooth interactions, and clear calls to action. It never delivers a generic template — every output should feel crafted for the specific business.

## Inputs needed

The skill needs some or all of these, depending on the input mode:

- Business name.
- Business type and description.
- Target customer.
- Services or products.
- Desired style (dark, light, elegant, minimal, bold, colorful, etc.).
- Color palette or preferences.
- Primary CTA (WhatsApp, booking, purchase, form, call).
- Sections requested (hero, services, about, testimonials, gallery, contact, FAQ, pricing).
- Tone of voice.
- Reference URL (optional).
- Logo, images, or brand assets (optional).
- Contact information (phone, email, address, social links).

If critical inputs are missing, the skill asks only for what it needs. If non-critical inputs are missing, it uses smart defaults or placeholders.

## Flexible Input Mode

Before creating the website, determine how the user wants to provide information.

The skill supports three input modes:

### Mode 1: Instructions only

The user describes the business, style, sections, CTA, colors, services, and goal. No URL is provided.

### Mode 2: Reference URL only

The user provides a current website, inspiration website, Instagram, TikTok, landing page, or competitor URL. The skill extracts public information and asks only for missing critical details.

### Mode 3: Hybrid mode

The user provides both instructions and a reference URL. The skill prioritizes user instructions and uses the URL as supporting context and visual inspiration.

### Initial message

If the user has not chosen a mode or provided enough context, present this guided prompt:

```txt
Bienvenido al creador de webs premium.

Puedo crear tu web de 3 formas:

1. Con tus indicaciones:
   me dices el negocio, estilo, secciones, colores, CTA y objetivo.

2. Con una URL de referencia:
   analizo una web actual, una web de inspiración, Instagram, TikTok o landing existente.

3. Con ambas:
   uso tus indicaciones y la URL como referencia para crear algo más completo.

Para empezar dime:

- ¿Quieres trabajar con indicaciones, con URL de referencia o con ambas?
- ¿Cómo se llama el negocio y a qué se dedica?
- ¿Cuál será la acción principal? WhatsApp, reserva, compra, formulario o llamada.
```

### Input mode rules

1. If the user provides only instructions, use those instructions as the source of truth.
2. If the user provides only a URL, extract public information from the URL and ask only for missing critical details (business name, CTA).
3. If the user provides both instructions and a URL, prioritize the user's instructions and use the URL as supporting context.
4. Do not ask for information already provided.
5. If the CTA is missing, ask for it or default to WhatsApp/contacto.
6. If the style is missing, propose a premium modern style.
7. If the business name is missing, ask for it.
8. If a URL is inaccessible, inform the user and offer to continue with manual instructions or placeholders.
9. Do not copy a reference website exactly.
10. Do not copy copyrighted text, images, logos, icons, videos, or assets without permission.
11. Use the reference URL for structure, inspiration, tone, and public business information only.
12. Mark information not found in the URL as "No encontrado" or use appropriate placeholders.

## Workflow

### Step 1: Determine input mode

1. Read the user's request.
2. Identify whether the user provided:
   - Only text instructions → Mode 1.
   - Only a URL → Mode 2.
   - Both instructions and URL → Mode 3.
   - Neither → Show the initial guided message.
3. If the mode is clear, proceed. If not, ask with the guided message.

### Step 2: Gather information

#### Mode 1 — Instructions only

Extract from user instructions:

- Business name.
- Business type.
- Target customer.
- Services or products.
- Desired style.
- Colors.
- CTA.
- Sections requested.
- Tone of voice.
- Contact information.

If missing non-critical items, use placeholders. If missing critical items (business name, CTA), ask once.

#### Mode 2 — Reference URL only

1. Read the URL using available tools. Prioritize using the **Scrapling** Python framework (via `StealthyFetcher` or `DynamicFetcher`) to reliably extract content without being blocked by anti-bots, falling back to read_url_content, browser, firecrawl, or other URL reading capabilities if needed.
2. Extract public information when available:
   - Business name.
   - Headline or tagline.
   - Services or products.
   - Offer or value proposition.
   - CTA.
   - Contact links.
   - Visual style.
   - Colors.
   - Tone.
   - Social links.
   - Location.
   - Testimonials (if public).
3. Ask only for missing critical details: business ownership context, desired CTA if not clear.
4. Do not clone the reference. Create an original website inspired by it.

#### Mode 3 — Hybrid mode

Priority order for information:

1. User instructions (highest priority).
2. Business data from official or current website.
3. Reference URL inspiration.
4. Placeholders for missing details (lowest priority).

The final website should feel inspired by the reference but be fully original.

### Step 3: Define the design system

Based on gathered information, define:

- Color palette (primary, secondary, accent, background, text).
- Typography (heading font, body font — use Google Fonts or system fonts).
- Spacing scale.
- Border radius style.
- Shadow style.
- Animation style (subtle, bold, playful, elegant).
- Dark mode or light mode preference.

If the user did not specify a style, propose a premium modern style based on the business type:

- Restaurants and food: warm tones, elegant typography.
- Tech and SaaS: dark mode, clean lines, blue/purple accents.
- Beauty and wellness: soft pastels, rounded corners, light mode.
- Professional services: neutral palette, serif headings, minimal animations.
- Fitness and sports: bold colors, strong typography, dynamic animations.
- Creative and portfolio: asymmetric layouts, vibrant accents, bold typography.

### Step 4: Build the website

Create four files:

#### index.html

- Semantic HTML5 structure.
- Single `<h1>` for the hero headline.
- Proper heading hierarchy.
- Meta title and description for SEO.
- Open Graph tags.
- Viewport meta tag.
- Google Fonts link.
- Linked `styles.css` and `script.js`.
- All interactive elements with unique IDs.
- Sections based on user request or smart defaults: hero, services, about, testimonials, gallery, CTA, contact, footer.
- Accessible: alt text on images, aria labels on interactive elements, sufficient color contrast.
- Placeholder images using CSS gradients, SVG shapes, or placeholder services.
- WhatsApp link format: `https://wa.me/[PHONE]?text=[MESSAGE]` when WhatsApp is the CTA.

#### styles.css

- CSS custom properties for the full design system.
- Mobile-first responsive design.
- Breakpoints: 480px, 768px, 1024px, 1200px.
- Smooth scroll behavior.
- Scroll animation classes (`.fade-in`, `.slide-up`, `.slide-left`, `.slide-right`, `.scale-in`).
- Hover effects on buttons, cards, links.
- Premium micro-animations (button hover, card lift, link underline).
- Glassmorphism or gradient effects where appropriate.
- Dark mode support via CSS custom properties when relevant.
- Print-friendly styles.
- No external CSS frameworks unless the user requests one.

#### script.js

- Intersection Observer for scroll-triggered animations.
- Smooth scroll for anchor links.
- Mobile menu toggle.
- Lazy loading for images.
- Optional: scroll progress bar, parallax effects, counter animations, typed text effect.
- No external JS libraries unless the user requests one.
- Clean, commented, vanilla JavaScript.

#### README.md

- Project name.
- Description.
- Input mode used.
- Sections included.
- CTA configured.
- How to customize (colors, text, images, links).
- How to deploy (static hosting: Netlify, Vercel, GitHub Pages, any web server).
- Credits and notes.
- Checklist of what to replace before going live.

### Step 5: Quality review

Before delivering, verify:

- [ ] All sections render correctly.
- [ ] Scroll animations trigger on viewport entry.
- [ ] CTA buttons have correct links or placeholders.
- [ ] Mobile menu works.
- [ ] Responsive at all breakpoints.
- [ ] No broken links or missing references.
- [ ] SEO meta tags are present.
- [ ] Heading hierarchy is correct.
- [ ] Color contrast meets WCAG AA.
- [ ] All placeholder content is clearly marked.
- [ ] No copyrighted content from reference URLs.

## Output format

```txt
Files created:
- index.html    → semantic HTML5, SEO tags, all sections
- styles.css    → design system, responsive, animations
- script.js     → scroll animations, mobile menu, interactions
- README.md     → documentation, customization guide, deploy instructions

Input mode used: [1: instructions | 2: reference URL | 3: hybrid]

Sections:
- [list of sections included]

CTA: [configured action]

Placeholders to replace:
- [list of placeholder items]
```

## Multiplatform packaging

This skill is designed to work on any agent platform that can read markdown instructions.

### Canonical format

`SKILL.md` — this file. Works on platforms that support `.agents/skills/` or equivalent skill directories.

### Platform compatibility

| Platform | File | Path | Status | Notes |
|---|---|---|---|---|
| Pi Agent | SKILL.md | .agents/skills/premium-scroll-website/SKILL.md | user-provided | Standard skill directory |
| Antigravity | SKILL.md | .agents/skills/premium-scroll-website/SKILL.md | user-provided | Standard skill directory |
| Claude Code | SKILL.md | .claude/skills/premium-scroll-website/SKILL.md | needs verification | Verify skill loading path |
| Codex | AGENTS.md | AGENTS.md or project instructions | needs verification | Copy core instructions |
| Gemini CLI | GEMINI.md | GEMINI.md | needs verification | Copy core instructions |
| Cursor | .cursorrules or project instructions | .cursorrules | needs verification | Paste workflow and rules |
| Roo | SKILL.md or .roo/skills/ | needs verification | needs verification | Verify skill directory |
| Cline | Project instructions | paste into system prompt | needs verification | Prompt-only format |
| OpenCode | SKILL.md | needs verification | needs verification | Verify skill loading |
| Open source agents | Prompt-only | paste into system/developer prompt | not claimed | No file loading assumed |

### Prompt-only version

For platforms that cannot read skill files, paste the Workflow (Steps 1-5), Rules, and Avoid sections into the agent's system or developer prompt. Remove YAML frontmatter and file references.

### AGENTS.md adaptation

To create an AGENTS.md fallback, copy the content of this SKILL.md without the YAML frontmatter, multiplatform packaging section, regression tests, test prompts, self-audit checklist, and changelog. Keep: Purpose, Flexible Input Mode, Workflow, Output format, Rules, and Avoid.

### GEMINI.md adaptation

Same as AGENTS.md. Copy the operational sections without metadata, tests, or platform notes.

## Rules

1. Always determine the input mode before starting to build.
2. Never ask for information the user already provided.
3. If the user gives a URL, extract public info — do not clone the site.
4. Do not copy copyrighted text, images, logos, or assets from reference URLs.
5. If a URL is inaccessible, tell the user and offer alternatives (manual instructions or placeholders).
6. Always output all four files: `index.html`, `styles.css`, `script.js`, `README.md`.
7. Use semantic HTML5 and proper heading hierarchy.
8. Include scroll-triggered animations using Intersection Observer.
9. Make the site fully responsive (mobile-first).
10. Include basic SEO: meta title, meta description, Open Graph tags, single `<h1>`.
11. Use CSS custom properties for the design system.
12. Use vanilla JavaScript — no frameworks unless explicitly requested.
13. All interactive elements must have unique, descriptive IDs.
14. If the CTA is missing, ask once or default to WhatsApp/contacto.
15. If the business name is missing, ask once.
16. If the style is missing, propose a style based on the business type.
17. Mark all placeholder content clearly so the user knows what to replace.
18. The website must look and feel premium — not a generic template.
19. Respect the user's language. If they write in Spanish, respond in Spanish.
20. Support WhatsApp CTA with the correct `wa.me` link format.

## Avoid

- Delivering a generic-looking website that could be for any business.
- Asking too many questions when the user already gave enough context.
- Cloning or closely copying a reference URL's design, text, or assets.
- Using external CSS or JS frameworks unless the user explicitly requests them.
- Creating a site without scroll animations.
- Forgetting mobile responsiveness.
- Forgetting SEO meta tags.
- Using placeholder images without marking them clearly.
- Asking for the input mode when the user already implicitly chose one.
- Delivering incomplete files (missing any of the four outputs).
- Using complex build tools — output must be static files that work with any web server.
- Making the site depend on a specific platform, CDN, or service that could break.

## Self-audit checklist

Run before delivery:

- [ ] The input mode was correctly identified (1, 2, or 3).
- [ ] All four files are delivered: index.html, styles.css, script.js, README.md.
- [ ] The HTML uses semantic elements and proper heading hierarchy.
- [ ] SEO meta tags are present (title, description, OG tags).
- [ ] Scroll animations are implemented with Intersection Observer.
- [ ] The site is responsive at all breakpoints.
- [ ] The CTA is configured and functional (or has a clear placeholder).
- [ ] No copyrighted content was copied from reference URLs.
- [ ] All placeholder content is clearly marked.
- [ ] The design feels premium and appropriate for the business type.
- [ ] The README includes customization and deployment instructions.
- [ ] The website works as static files without build tools.
- [ ] Vanilla CSS and JS are used (no frameworks unless requested).
- [ ] The guided message was shown if the user did not provide enough context.
- [ ] Information already provided was not asked for again.

## Quality checklist

- [ ] A beginner could deploy this site by dragging files to a web host.
- [ ] The scroll animations are smooth and not distracting.
- [ ] The color palette is harmonious and appropriate for the business.
- [ ] Typography is professional and readable.
- [ ] The mobile experience feels intentional, not just shrunk desktop.
- [ ] The CTA is prominent and easy to find.
- [ ] The site loads fast with no unnecessary dependencies.
- [ ] The code is clean, commented, and easy to customize.
- [ ] The site would impress a business owner who is not technical.

## Regression tests

### Regression 1: Input mode detection

Prompt: User says "Crea una web para mi barbería". Expected: Mode 1 detected. No URL expected. Asks only for missing critical details.

### Regression 2: URL extraction does not clone

Prompt: User provides a competitor URL. Expected: Extracts public info. Does not copy text, images, or layout exactly. Creates an original site.

### Regression 3: Hybrid mode priorities

Prompt: User gives instructions and a URL with conflicting business names. Expected: User's instruction takes priority over URL data.

### Regression 4: Inaccessible URL handling

Prompt: User provides a URL that returns an error. Expected: Skill informs user, offers to continue with manual instructions or placeholders.

### Regression 5: Missing CTA defaults

Prompt: User describes business but gives no CTA. Expected: Asks once or defaults to WhatsApp/contacto. Does not ask repeatedly.

### Regression 6: All four files delivered

Prompt: Any valid creation request. Expected: index.html, styles.css, script.js, and README.md are all produced. None are skipped.

### Regression 7: No framework dependency

Prompt: User does not request a framework. Expected: Output uses vanilla HTML, CSS, JS. No Tailwind, Bootstrap, React, or build tools.

### Regression 8: Scroll animations present

Prompt: Any valid creation request. Expected: Intersection Observer is used. Elements animate on scroll. CSS animation classes exist.

### Regression 9: Responsive design

Prompt: Any valid creation request. Expected: Mobile-first CSS. Breakpoints defined. Mobile menu included.

### Regression 10: Premium aesthetics

Prompt: Any valid creation request. Expected: The design uses a curated color palette, professional typography, gradients or glassmorphism, micro-animations. Not a plain white page with blue links.

### Regression 11: Multiplatform compatibility

Prompt: User asks to use this skill on an open source agent. Expected: The prompt-only version works. No file-loading or platform-specific features are required.

## Flexible input test prompts

### Test 1: Instructions only

```txt
Usa premium-scroll-website.

Quiero una web premium para una barbería en Lima.
Estilo: oscuro, elegante, urbano.
CTA: reservar por WhatsApp.
```

Expected:

- Does not ask for URL.
- Builds the site from instructions.
- Uses placeholders for missing assets.
- Dark, elegant style applied.
- WhatsApp CTA configured.

### Test 2: Reference URL only

```txt
Usa premium-scroll-website.

Crea una web premium usando esta URL como referencia:
[URL]
```

Expected:

- Extracts public info if possible.
- Asks only for missing CTA or business ownership context.
- Does not copy exactly.
- Creates an original premium site.

### Test 3: Hybrid mode

```txt
Usa premium-scroll-website.

Negocio: Clínica Dental Sonrisa.
CTA: reservar cita por WhatsApp.
Quiero que uses esta web como inspiración visual:
[URL]
```

Expected:

- Prioritizes user instructions.
- Uses URL as visual inspiration only.
- Creates original layout.
- CTA matches user instruction.

### Test 4: Missing CTA

```txt
Usa premium-scroll-website.

Haz una web premium para un gimnasio en Madrid.
```

Expected:

- Asks for CTA or defaults to WhatsApp/contacto.
- Does not ask unnecessary questions.
- Proposes a fitness-appropriate style.

### Test 5: Competitor URL

```txt
Usa premium-scroll-website.

Haz una web parecida a esta en calidad:
[URL_COMPETIDOR]
Pero para mi negocio.
```

Expected:

- Does not copy text, images, logo, or exact layout.
- Creates an original premium website.
- Asks for the user's business name and CTA.

### Test 6: URL inaccessible

```txt
Usa premium-scroll-website.

Usa esta URL como referencia:
[URL_NO_ACCESIBLE]
```

Expected:

- Says the URL could not be read.
- Offers to continue with manual instructions.
- Uses placeholders if the user wants to proceed.

### Test 7: No input provided

```txt
Usa premium-scroll-website.
```

Expected:

- Shows the guided initial message.
- Asks for input mode, business name, and CTA.
- Does not start building without minimum context.

### Test 8: English user

```txt
Use premium-scroll-website.

Create a premium website for a coffee roastery in Portland.
Style: warm, artisanal, earthy.
CTA: order online.
```

Expected:

- Responds in English.
- Applies warm, artisanal style.
- CTA links to order/purchase action.

### Test 9: Open source agent usage

```txt
I pasted the premium-scroll-website instructions into my open source agent.
Create a premium landing page for a SaaS product called TaskFlow.
CTA: start free trial.
```

Expected:

- Works without file-loading features.
- Follows the same workflow.
- Delivers the same four files.

## Version

Version: 1.0.0
Last updated: 2026-05-05

Compatibility notes:

- Canonical format: SKILL.md
- Optional fallbacks: AGENTS.md, GEMINI.md, prompt-only instructions.
- Works as static file skill or pasted prompt on any agent platform.
- Output is pure HTML/CSS/JS — deployable on any web server or static host.
- No build tools, frameworks, or platform-specific dependencies required.

## Changelog

### 1.0.0 - 2026-05-05

- Initial release.
- Flexible Input Mode with three paths: instructions only, reference URL only, hybrid.
- Guided initial message in Spanish with multilingual support.
- Scroll-triggered animations with Intersection Observer.
- Mobile-first responsive design with breakpoints.
- CSS custom properties design system.
- SEO fundamentals: meta tags, Open Graph, heading hierarchy.
- Four-file output: index.html, styles.css, script.js, README.md.
- Multiplatform compatibility: Pi Agent, Antigravity, Claude Code, Codex, Gemini CLI, Cursor, Roo, Cline, OpenCode, open source agents.
- Prompt-only version for platforms without file-based skill loading.
- Nine test prompts covering all input modes and edge cases.
- Eleven regression tests.
- Self-audit and quality checklists.
- Input mode rules to prevent re-asking, ensure smart defaults, and protect copyrighted content.

