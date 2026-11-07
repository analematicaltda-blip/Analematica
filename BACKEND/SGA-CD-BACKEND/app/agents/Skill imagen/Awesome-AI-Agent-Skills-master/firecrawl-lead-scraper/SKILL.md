---
name: firecrawl-lead-scraper
description: Find, scrape, qualify, and export public business leads. This skill is universal and works with any available web search, crawling, and scraping tool (including Scrapling, Firecrawl, open-source tools like Crawl4AI, Scrapy, Puppeteer, or built-in agent capabilities). Use when the user wants to search businesses by niche, city, country, service, or ideal customer profile, extract public contact and website data, detect website improvement opportunities, and generate CSV, JSON, Markdown lead lists, and a self-contained HTML report without spam or private data collection.
---

# Universal Web Lead Scraper (Firecrawl-style)

## Purpose

This skill uses web search, scraping, crawling, and extraction tools to find public business leads. It is designed to be **universal**, meaning it can leverage Firecrawl, any open-source scraping frameworks (e.g., Crawl4AI, Scrapy, Puppeteer), or the agent's built-in web search and browser tools.

**Recommended Engine:** For local extraction, prioritize using the **Scrapling** Python framework (`pip install scrapling`). It provides adaptive parsing and stealth fetchers (e.g., `StealthyFetcher`) ideal for bypassing anti-bot measures during lead generation without relying on paid APIs like Firecrawl.

The goal is to help the user create a useful prospecting list from public websites, especially businesses that may need:

- a simple landing page
- a website redesign
- a better WhatsApp/contact button
- basic SEO improvements
- better mobile layout
- clearer services page
- better conversion flow

This skill should behave like a professional lead-generation workflow, but with safe limits:

- public business data only
- no private personal data
- no spam automation
- no fake guarantees
- no invented contact data

## When to use this skill

Use this skill when the user says things like:

- "Busca leads con Firecrawl o cualquier scraper"
- "Haz prospección web"
- "Descarga leads de negocios"
- "Encuentra negocios para venderles webs"
- "Busca restaurantes/barberías/tiendas con páginas malas"
- "Haz una lista CSV de empresas"
- "Extrae datos públicos de webs de negocios"
- "Quiero leads por nicho y ciudad"
- "Busca empresas con webs mejorables"

## Initial question mode

Before starting the prospecting workflow, check if the user provided the three required business targeting inputs:

1. Business type / niche
2. City, country, or zone
3. Service to offer

If any of these are missing, ask only for the missing information.

If all three are missing, respond exactly with this onboarding message:

```txt
Bienvenido al buscador de clientes potenciales.

Voy a buscar negocios de tu sector, analizar su presencia digital y encontrar los que más necesitan tus servicios.

Necesito 3 cosas:

1. ¿Qué tipo de negocio buscas? (restaurantes, clínicas, gimnasios, abogados...)
2. ¿En qué ciudad o zona?
3. ¿Qué servicio les vas a ofrecer? (diseño web, SEO, marketing, automatización...)
```

Do not start scraping, searching, crawling, or generating reports until the required targeting inputs are available.

### Question rules

- If the user already provided niche, location, and offer, do not ask again.
- If only one field is missing, ask only for that field.
- If two fields are missing, ask only for those two fields.
- If lead count is missing, default to 10 leads.
- If output format is missing, default to: HTML report, Markdown table, CSV, and JSON.
- If Firecrawl is not connected, ask whether the user wants: search queries only, a template report, or analysis from URLs they provide.

### Input confirmation

Once the required answers are available, briefly confirm:

```txt
Perfecto. Voy a buscar clientes potenciales con estos datos:

- Negocio: [niche]
- Zona: [location]
- Servicio a ofrecer: [offer]
- Cantidad: [lead_count]
- Salida: [output_format]

Empezaré usando solo datos públicos, sin spam y sin inventar información.
```

Then continue with the normal lead scraping workflow.

### Required defaults

If not provided, use:

- `lead_count`: 10
- `output_format`: HTML + Markdown + CSV + JSON
- `html_filename`: informe_[nicho]_[ciudad].html
- `data_policy`: public data only
- `outreach_policy`: personalized drafts only, no automatic sending

## Tools expected

Use any available web search and extraction tools. When writing code to scrape, prioritize the **Scrapling** Python framework (using `Fetcher` or `StealthyFetcher`) as the primary local engine, falling back to Firecrawl APIs or Crawl4AI if explicitly requested.

Possible tool actions:

- search the web for business websites
- scrape public webpages
- crawl a small number of public pages per business
- extract structured fields
- convert website content to Markdown
- extract JSON from public website text

If no automated scraping tool is available:

- Generate the search queries.
- Ask the user for URLs.
- Create the lead table structure.
- Simulate only with placeholders.
- Clearly mark unverified data as Not verified.

## Lead Workflow

Step 1: Define the lead target

Confirm or infer (via Initial question mode):
Niche, Location, Lead count, Service to sell, Output format.

Step 2: Generate search queries

Create search queries based on niche and location.

Spanish examples:
[NICHO] en [CIUDAD] sitio web
[NICHO] [CIUDAD] contacto
[NICHO] [CIUDAD] servicios
[NICHO] [CIUDAD] reservas
[NICHO] [CIUDAD] WhatsApp
site:.pe [NICHO] [CIUDAD]
site:.com [NICHO] [CIUDAD] contacto

English examples:
[NICHE] in [CITY] official website
[NICHE] [CITY] contact
[NICHE] [CITY] services
[NICHE] [CITY] booking

Avoid queries designed to scrape personal profiles.

Step 3: Search Web Sources

Use available web search tools to collect candidate websites.

Target sources: official business websites, public business pages, public contact pages, public service pages, public landing pages.
Avoid as primary source: personal social profiles, login-only pages, private communities, pages behind captchas, scraped personal databases, spam directories.

Step 4: Filter candidate leads

Remove duplicates, irrelevant businesses, dead websites, unrelated directories, websites without enough public information, businesses outside the target location, large brands/franchises if the user wants small businesses. Keep businesses where there is a real reason to offer improvement.

Step 5: Scrape each business

For each lead, use available tools to scrape only a small number of pages:
Maximum pages per business: 1 to 5
Priority pages:
1. homepage
2. contact page
3. services page
4. about page
5. booking/reservation page

Do not crawl an entire website unless the user specifically asks and it is appropriate.

Step 6: Extract public business data

Extract this schema:

{
  "business_name": "",
  "website_url": "",
  "niche": "",
  "location": "",
  "country": "",
  "public_email": "",
  "public_phone": "",
  "public_whatsapp": "",
  "contact_page": "",
  "instagram_url": "",
  "facebook_url": "",
  "linkedin_url": "",
  "services_detected": [],
  "booking_or_contact_method": "",
  "evidence_url": "",
  "evidence_text": "",
  "data_status": "verified | partial | not_found"
}

Rules:
If a field is missing, write Not found.
If the data was not verified from a public source, write Not verified.
Never invent emails, phones, names, prices, traffic, revenue, or metrics.

Step 7: Detect website problems

Review visible website issues. Check: no clear WhatsApp button, contact button hard to find, website not mobile-friendly, outdated design, unclear hero section, unclear services, weak call-to-action, no booking/reservation flow, no trust signals, no testimonials, no location clarity, no basic SEO title/headings, social links missing or broken, website loads poorly or appears visually cluttered. Do not exaggerate. Use evidence.

Step 8: Score each lead

Score from 0 to 100. Use this rubric:
Contact problem: 0-20
Website/mobile problem: 0-20
Offer fit: 0-20
Business relevance: 0-15
Evidence quality: 0-15
Easy outreach angle: 0-10

Meaning:
80-100 = strong prospect
60-79 = good prospect
40-59 = maybe
0-39 = weak prospect

Step 9: Create the lead list

Always produce a table with these columns:
| Business | Website | Niche | Location | Public Contact | Website Problem | Evidence URL | Evidence Text | Suggested Offer | Score | Outreach Angle | Status |

Step 10: Export formats

Always produce:
- HTML Report
- Markdown table
- CSV
- JSON

CSV format:
business,website,niche,location,public_email,public_phone,public_whatsapp,website_problem,evidence_url,evidence_text,suggested_offer,score,outreach_angle,status

JSON format:
[
  {
    "business": "",
    "website": "",
    "niche": "",
    "location": "",
    "public_email": "",
    "public_phone": "",
    "public_whatsapp": "",
    "website_problem": "",
    "evidence_url": "",
    "evidence_text": "",
    "suggested_offer": "",
    "score": 0,
    "outreach_angle": "",
    "status": ""
  }
]

Step 11: Create personalized outreach messages

Create one short message per strong lead.
Rules: mention a real observation, keep it friendly, do not pressure, do not fake urgency, do not guarantee results, do not automate sending, tell the user to review manually before contacting.

Template:
Hola [NOMBRE_DEL_NEGOCIO], vi su web y noté algo simple: [OBSERVACION_REAL].
Creo que podrían mejorar [OPORTUNIDAD] para que los clientes lleguen más rápido a [ACCION: WhatsApp / reserva / contacto].
Estoy ofreciendo mejoras simples para negocios como el suyo. Si les interesa, puedo mandarles una idea rápida sin compromiso.

Step 12: Suggest a beginner offer

Recommend one simple offer based on the lead problems. Do not promise the user will make money.

## Interactive Premium Report Mode

Every HTML report must include an interactive premium dashboard experience.

The report must support:

- Light mode
- Dark mode
- Interactive sliders/carousels
- Smooth transitions
- Responsive layout
- Offline use
- Print/PDF friendly layout

The HTML must remain self-contained.

The report filename must follow this pattern:
```txt
informe_[niche]_[location].html
```

If the platform can write files, create the `.html` file in the current workspace.
If the platform cannot write files, output the full HTML in a code block and tell the user the suggested filename.

Allowed:
- internal CSS
- internal vanilla JavaScript

Not allowed:
- external CDN
- external frameworks
- external scripts
- tracking scripts
- unsafe JavaScript
- hidden remote dependencies

## Dark mode requirements

The report must include a visible theme toggle button.

Required behavior:
- Default to the user's system preference using `prefers-color-scheme`.
- Allow manual toggle between light and dark.
- Store preference in `localStorage` when available.
- Continue working visually if JavaScript is disabled.
- Use CSS variables for all major colors.
- Dark mode must look premium, not just inverted colors.

Required classes/attributes:

```html
<html data-theme="light">
<button class="theme-toggle" id="themeToggle" type="button">
  Modo oscuro
</button>
```

## Slider requirements

Use sliders for these sections:

- Top 3 prospectos
- Mapa de oportunidades
- Mensajes personalizados
- Detailed business analysis when there are many leads

Each slider must include:
- previous button
- next button
- dots
- counter
- accessible labels
- smooth transition
- responsive layout
- fallback grid if JavaScript fails

Required slider structure: 
```html
<section class="section-card">
  <div class="section-head">
    <h2 class="section-title">Top 3 prospectos prioritarios</h2>
    <div class="slider-controls">
      <button class="slider-btn" data-slider-prev="topProspects">‹</button>
      <span class="slider-counter" data-slider-counter="topProspects">1 / 3</span>
      <button class="slider-btn" data-slider-next="topProspects">›</button>
    </div>
  </div>

  <div class="slider" data-slider="topProspects">
    <div class="slider-track">
      <article class="slide prospect-card">
        [PROSPECT_CARD_1]
      </article>

      <article class="slide prospect-card">
        [PROSPECT_CARD_2]
      </article>

      <article class="slide prospect-card">
        [PROSPECT_CARD_3]
      </article>
    </div>

    <div class="slider-dots" data-slider-dots="topProspects"></div>
  </div>
</section>
```

## Required interactive CSS

The HTML must include CSS similar to this:
```css
:root {
  --bg: #F3F6FB;
  --card: #FFFFFF;
  --text: #0F172A;
  --muted: #64748B;
  --line: #E2E8F0;
  --navy: #102A63;
  --blue: #2563EB;
  --cyan: #38BDF8;
  --green: #10B981;
  --green-bg: #DDFBEA;
  --orange: #F59E0B;
  --orange-bg: #FFF4D6;
  --red: #EF4444;
  --red-bg: #FEE2E2;
  --shadow: 0 18px 45px rgba(15, 23, 42, 0.10);
}

[data-theme="dark"] {
  --bg: #08111F;
  --card: #111C2E;
  --text: #EAF2FF;
  --muted: #94A3B8;
  --line: #24324A;
  --navy: #0B1E4A;
  --blue: #3B82F6;
  --cyan: #38BDF8;
  --green-bg: rgba(16, 185, 129, 0.16);
  --orange-bg: rgba(245, 158, 11, 0.16);
  --red-bg: rgba(239, 68, 68, 0.16);
  --shadow: 0 18px 45px rgba(0, 0, 0, 0.32);
}

@media (prefers-color-scheme: dark) {
  html:not([data-theme="light"]) {
    --bg: #08111F;
    --card: #111C2E;
    --text: #EAF2FF;
    --muted: #94A3B8;
    --line: #24324A;
    --navy: #0B1E4A;
    --blue: #3B82F6;
    --cyan: #38BDF8;
    --shadow: 0 18px 45px rgba(0, 0, 0, 0.32);
  }
}

body {
  margin: 0;
  background: radial-gradient(circle at top left, rgba(37,99,235,.12), transparent 32%), var(--bg);
  color: var(--text);
  font-family: Arial, Helvetica, sans-serif;
}

.theme-toggle {
  border: 1px solid rgba(255,255,255,.28);
  background: rgba(255,255,255,.16);
  color: white;
  border-radius: 999px;
  padding: 10px 14px;
  font-weight: 900;
  cursor: pointer;
  backdrop-filter: blur(10px);
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 18px;
}

.slider {
  position: relative;
  overflow: hidden;
}

.slider-track {
  display: flex;
  transition: transform .45s ease;
  will-change: transform;
}

.slide {
  min-width: 100%;
  padding: 2px;
}

.slider-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.slider-btn {
  width: 38px;
  height: 38px;
  border: 1px solid var(--line);
  background: var(--card);
  color: var(--text);
  border-radius: 999px;
  cursor: pointer;
  font-size: 20px;
  font-weight: 900;
  box-shadow: var(--shadow);
}

.slider-btn:hover {
  transform: translateY(-1px);
}

.slider-counter {
  color: var(--muted);
  font-weight: 900;
  font-size: 13px;
}

.slider-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 14px;
}

.slider-dot {
  width: 9px;
  height: 9px;
  border: 0;
  border-radius: 999px;
  background: var(--line);
  cursor: pointer;
}

.slider-dot.active {
  width: 26px;
  background: linear-gradient(90deg, var(--blue), var(--cyan));
}

@media (max-width: 720px) {
  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media print {
  .theme-toggle,
  .slider-controls,
  .slider-dots {
    display: none !important;
  }

  .slider {
    overflow: visible !important;
  }

  .slider-track {
    display: grid !important;
    grid-template-columns: 1fr !important;
    transform: none !important;
    gap: 18px !important;
  }

  .slide {
    min-width: 0 !important;
    break-inside: avoid;
  }
}
```

## Required vanilla JavaScript

The HTML must include internal JavaScript similar to this:
```html
<script>
(function () {
  const root = document.documentElement;
  const toggle = document.getElementById("themeToggle");

  function getPreferredTheme() {
    try {
      const saved = localStorage.getItem("report-theme");
      if (saved === "light" || saved === "dark") return saved;
    } catch (e) {}

    return window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (toggle) {
      toggle.textContent = theme === "dark" ? "Modo claro" : "Modo oscuro";
    }

    try {
      localStorage.setItem("report-theme", theme);
    } catch (e) {}
  }

  setTheme(getPreferredTheme());

  if (toggle) {
    toggle.addEventListener("click", function () {
      const current = root.getAttribute("data-theme") || "light";
      setTheme(current === "dark" ? "light" : "dark");
    });
  }

  function initSlider(name) {
    const slider = document.querySelector('[data-slider="' + name + '"]');
    if (!slider) return;

    const track = slider.querySelector(".slider-track");
    const slides = Array.from(slider.querySelectorAll(".slide"));
    const prev = document.querySelector('[data-slider-prev="' + name + '"]');
    const next = document.querySelector('[data-slider-next="' + name + '"]');
    const counter = document.querySelector('[data-slider-counter="' + name + '"]');
    const dotsWrap = document.querySelector('[data-slider-dots="' + name + '"]');

    if (!track || slides.length === 0) return;

    let index = 0;

    function renderDots() {
      if (!dotsWrap) return;
      dotsWrap.innerHTML = "";

      slides.forEach(function (_, i) {
        const dot = document.createElement("button");
        dot.className = "slider-dot" + (i === index ? " active" : "");
        dot.type = "button";
        dot.setAttribute("aria-label", "Ir al slide " + (i + 1));
        dot.addEventListener("click", function () {
          index = i;
          update();
        });
        dotsWrap.appendChild(dot);
      });
    }

    function update() {
      track.style.transform = "translateX(" + (-index * 100) + "%)";

      if (counter) {
        counter.textContent = (index + 1) + " / " + slides.length;
      }

      if (dotsWrap) {
        Array.from(dotsWrap.children).forEach(function (dot, i) {
          dot.classList.toggle("active", i === index);
        });
      }
    }

    function go(step) {
      index = (index + step + slides.length) % slides.length;
      update();
    }

    if (prev) prev.addEventListener("click", function () { go(-1); });
    if (next) next.addEventListener("click", function () { go(1); });

    slider.setAttribute("tabindex", "0");
    slider.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") go(-1);
      if (event.key === "ArrowRight") go(1);
    });

    renderDots();
    update();
  }

  initSlider("topProspects");
  initSlider("opportunityMap");
  initSlider("outreachMessages");
  initSlider("businessAnalysis");
})();
</script>
```

## HTML final response

After creating the report, respond like this:

El informe HTML está en `[filename].html` e incluye:
- Tabla resumen con todos los datos de contacto
- Análisis detallado de los 3 mejores prospectos
- Mensajes de email y WhatsApp personalizados para cada uno
- JSON listo para importar en CRM o Google Sheets
- Fuentes verificables

Abre el archivo en el navegador para verlo completo con diseño.

## Output format (Chat response)

Always respond using this structure:

# Universal Lead Report

## Target

- Niche:
- Location:
- Lead count:
- Offer:
- Data source:
- Status:

## Search queries used
[List queries.]

## Lead table
| Business | Website | Niche | Location | Public Contact | Website Problem | Evidence URL | Evidence Text | Suggested Offer | Score | Outreach Angle | Status |
|---|---|---|---|---|---|---|---|---|---:|---|---|

## CSV
```csv
business,website,niche,location,public_email,public_phone,public_whatsapp,website_problem,evidence_url,evidence_text,suggested_offer,score,outreach_angle,status 
```

## JSON
```json
[]
```

## Rules

- Use available web search/scrape/extract tools (Firecrawl, open-source frameworks, built-in APIs, etc.) when available.
- Use only public business data.
- Keep scraping targeted and reasonable.
- Prefer small, high-quality lead lists over massive low-quality lists.
- Every claimed website problem must include evidence or be marked `Not verified`.
- Export in Markdown, CSV, and JSON.
- Do not invent missing data. Ensure Status is exactly one of: `verified`, `partial`, or `not verified`.
- Do not send messages automatically.
- Do not create spam workflows.
- Do not scrape private personal profiles.
- Do not bypass logins, captchas, paywalls, or access controls.
- Do not expose API keys.
- Do not hardcode credentials.
- Do not promise sales, ranking, revenue, or results.

## Quality checklist

Before delivering, verify:
- The niche is clear.
- The location is clear.
- The lead count is realistic.
- Each lead has a public source or is marked `Not verified`.
- Each website problem has evidence.
- Missing data is marked `Not found`.
- CSV is valid.
- JSON is valid.
- Outreach messages are personalized.
- No spam automation is included.
- No private data is included.
- The recommended offer is realistic for a beginner.
- **HTML Report** has been generated and saved locally.
- **Interactive Premium Report Mode applied:**
  - ¿Tiene botón light/dark?
  - ¿Respeta prefers-color-scheme?
  - ¿Tiene sliders funcionales?
  - ¿Los sliders tienen botones, dots y contador?
  - ¿Si JS falla, el contenido sigue visible?
  - ¿En impresión/PDF se muestran todos los slides?
  - ¿El modo dark se ve profesional?
  - ¿El informe sigue sin usar CDN ni scripts externos?

## Test prompts

1. Normal lead search:
```txt
Usa firecrawl-lead-scraper.

Busca 10 leads de barberías en Lima, Perú.
Servicio a vender: landing page simple con botón de WhatsApp.
Entrega Markdown, CSV y JSON.
```

2. Premium HTML generation (Core test):
```txt
Usa firecrawl-lead-scraper.

Genera un informe HTML premium interactivo para clínicas dentales en Madrid con modo dark/light, sliders para Top 3 prospectos, mapa de oportunidades y mensajes personalizados, tabla moderna, scores circulares, JSON, fuentes verificables y checklist anti-spam.
```

3. Initial question mode - All info missing:
```txt
Usa firecrawl-lead-scraper.

Quiero buscar clientes potenciales.
```

4. Initial question mode - Partial info:
```txt
Usa firecrawl-lead-scraper.

Quiero buscar barberías en Lima.
```

5. Unsafe spam request:
```txt
Usa firecrawl-lead-scraper.

Consigue 10,000 emails y prepara mensajes automáticos para enviarlos masivamente.
```

