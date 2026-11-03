---
name: instagram-landing-generator
description: >
  Use when the user asks to create a landing page, mini website, or portfolio
  from an Instagram profile. Also triggers on: "genera web desde Instagram",
  "crea landing de Instagram", "instagram to website", "perfil a web",
  "landing page from IG", "web desde mi perfil", "instagram landing",
  or when creating brand pages from social media profiles.
tags: [instagram, landing-page, web-generator, scraping, branding]
author: AI-Architect
license: MIT
version: 1.0.0
---

# Instagram Landing Page Generator

## Purpose

Transform any public Instagram profile into a premium, responsive landing page
automatically. Extracts profile data (bio, stats, posts, hashtags) and generates
a complete HTML/CSS/JS website with premium design, ready for deployment.

## When to use this skill

- User wants to create a landing page from an Instagram profile
- User says: "genera web desde Instagram", "crea landing", "instagram to website"
- User needs a quick portfolio or brand page based on their IG presence
- User wants to sell landing page creation as a service

## Inputs

1. **Instagram username or link** (required) — e.g. `@username` or `https://instagram.com/username`
2. **Theme preference** (optional) — `dark-luxury`, `neon-glow`, or `minimal-clean`
   - If not provided, the system auto-suggests based on content analysis

## Workflow

### Step 1: Get Instagram link

Ask the user: "¿Cuál es tu link de Instagram?" Accept URL or username.

### Step 2: Extract profile data

Run the scraper:
```bash
python scraper.py <username>
```
Uses Scrapling StealthyFetcher (Playwright headless) to extract:
- Full name, username, bio, category
- Profile picture URL
- Follower/following/post counts
- Recent posts (thumbnails + alt text)
- Hashtags from bio and post descriptions
- External links, verification badge

**Fallback**: If scraping fails, generates `profile_data_template.json` for manual input.

### Step 3: Analyze content and suggest theme

The system analyzes bio text, hashtags, post descriptions, and category to suggest the best theme:

| Content signals | Suggested theme |
|----------------|-----------------|
| luxury, fashion, beauty, premium, gold, model | `dark-luxury` |
| tech, gaming, neon, music, art, creative, digital | `neon-glow` |
| nature, minimal, food, travel, wellness, editorial | `minimal-clean` |

### Step 4: Generate landing page

```bash
node generator.js --theme <theme> --input profile_data.json
```

Generates `output/` folder with:
- `index.html` — Semantic HTML5 with all sections
- `styles.css` — Premium CSS with animations, glassmorphism, responsive
- `script.js` — Animated counters, lightbox, scroll reveal, ripple effects

### Step 5: Preview and deliver

```bash
npx -y serve output -p 3000
```

## Output format

```
output/
├── index.html    (landing page)
├── styles.css    (themed styles)
└── script.js     (interactivity)
```

Sections in the landing page:
1. **Hero** — Profile pic with gradient ring, name, verified badge, bio
2. **Stats Bar** — Animated counters (followers/following/posts)
3. **Gallery** — 3×3 grid with hover effects and lightbox
4. **Hashtags** — Pill-style tag cloud
5. **CTA** — "Seguir en Instagram" + external link buttons with ripple
6. **Footer** — Username credit

## Themes

### dark-luxury
- Background: #0a0a0a (pure black)
- Accent: #c9a84c (gold)
- Fonts: Playfair Display + Outfit
- Effects: Gold glassmorphism, glow shadows

### neon-glow
- Background: #0d0d1a (dark blue-black)
- Accent: #00f0ff (cyan) with magenta gradient
- Fonts: Space Grotesk + Inter
- Effects: Neon glow, cyber glassmorphism

### minimal-clean
- Background: #fafaf8 (warm white)
- Accent: #1a1a1a (editorial black)
- Fonts: DM Serif Display + DM Sans
- Effects: Subtle shadows, clean borders

## Files in this project

| File | Purpose |
|------|---------|
| `run.py` | Interactive orchestrator — asks link, scrapes, analyzes, generates |
| `scraper.py` | Instagram profile extractor with Scrapling |
| `generator.js` | Template engine — builds HTML/CSS/JS from profile data |
| `templates/styles.css` | CSS template with theme variable placeholders |
| `templates/script.js` | JS template for interactivity |
| `package.json` | npm scripts for generation and preview |
| `requirements.txt` | Python dependencies |

## Requirements

- Python 3.10+ with `scrapling[fetchers]` installed
- Node.js 18+
- Run `scrapling install` once to install browser engines

## Rules

- Only scrape **public** profiles
- Always provide manual fallback when scraping fails
- Auto-suggest theme based on content analysis, let user override
- Generated pages must be 100% static (no server needed for hosting)
- All CSS must be responsive (mobile-first)
- Include SEO meta tags in generated HTML

## Avoid

- Scraping private profiles or requiring Instagram login
- Storing any credentials
- Generating pages without proper SEO meta tags
- Using external JS/CSS dependencies (everything is self-contained)
- Breaking responsive design on any viewport

## Self-audit checklist

- [ ] Scraper handles network errors gracefully with fallback
- [ ] All 3 themes generate valid HTML/CSS/JS
- [ ] Generated page is fully responsive
- [ ] Stats counters animate correctly
- [ ] Lightbox opens and closes properly
- [ ] Username click copies to clipboard
- [ ] CTA buttons have ripple effect
- [ ] SEO meta tags are present
- [ ] Content analysis suggests appropriate theme

## Regression tests

### Test 1: Demo mode generation
```bash
node generator.js --demo --theme dark-luxury
```
Expected: Generates output/ with 3 files, no errors.

### Test 2: All themes
Run with `--theme dark-luxury`, `--theme neon-glow`, `--theme minimal-clean`.
Expected: Each generates valid, visually distinct output.

### Test 3: Scraper fallback
```bash
python scraper.py nonexistent_user_12345
```
Expected: Generates template JSON, no crash.

### Test 4: Content analysis
Profile with hashtags ["luxury", "fashion"] → suggests dark-luxury.
Profile with hashtags ["gaming", "tech"] → suggests neon-glow.
Profile with hashtags ["nature", "minimal"] → suggests minimal-clean.

## Version

Version: 1.0.0
Last updated: 2026-05-12

## Changelog

### 1.0.0 — 2026-05-12
- Initial release
- Scrapling-based profile extraction with StealthyFetcher
- 3 premium themes (dark-luxury, neon-glow, minimal-clean)
- Content analysis for auto-theme suggestion
- Interactive orchestrator (run.py)
- Fully static output, ready for any hosting
- Global deployment to all skill roots

