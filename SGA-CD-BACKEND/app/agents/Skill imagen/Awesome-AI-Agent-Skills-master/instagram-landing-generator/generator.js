/**
 * Instagram Landing Page Generator
 * Reads profile_data.json and generates a premium landing page
 */
const fs = require("fs");
const path = require("path");

// Parse CLI args
const args = process.argv.slice(2);
let theme = "dark-luxury";
let isDemo = false;
let inputFile = "profile_data.json";

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--theme" && args[i + 1]) theme = args[++i];
  if (args[i] === "--demo") isDemo = true;
  if (args[i] === "--input" && args[i + 1]) inputFile = args[++i];
}

// Demo data
const demoProfile = {
  username: "studio.brand",
  full_name: "Studio Brand Creative",
  biography: "✨ Diseño digital & branding premium\n🎨 Transformamos ideas en experiencias visuales\n📩 Contacto: hello@studiobrand.co",
  profile_pic_url: "",
  followers: 48500,
  following: 892,
  posts_count: 347,
  external_url: "https://studiobrand.co",
  hashtags: ["branding", "design", "creative", "digitalart", "studio", "premium", "visual", "aesthetic"],
  posts: Array.from({ length: 9 }, (_, i) => ({
    url: "#",
    thumbnail: "",
    alt_text: `Post creativo #${i + 1} — diseño visual premium`
  })),
  is_verified: true,
  category: "Digital Creator"
};

// Load profile
let profile;
if (isDemo) {
  profile = demoProfile;
  console.log("🎭 Modo demo activado");
} else {
  if (!fs.existsSync(inputFile)) {
    console.error(`❌ No se encontró ${inputFile}. Ejecuta primero: python scraper.py <username>`);
    console.log("   O usa --demo para generar con datos de ejemplo");
    process.exit(1);
  }
  profile = JSON.parse(fs.readFileSync(inputFile, "utf-8"));
}

console.log(`\n⚡ Generando landing page para @${profile.username}`);
console.log(`   Tema: ${theme}\n`);

// Create output dir
const outDir = path.join(__dirname, "output");
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

// Theme configs
const themes = {
  "dark-luxury": {
    bg: "#0a0a0a", bgCard: "rgba(255,255,255,0.04)", accent: "#c9a84c",
    accentRgb: "201,168,76", text: "#f0ece2", textMuted: "#8a8578",
    gradient: "linear-gradient(135deg, #c9a84c 0%, #f5e6b8 50%, #c9a84c 100%)",
    fontDisplay: "'Playfair Display', serif",
    fontBody: "'Outfit', sans-serif",
    glow: "0 0 40px rgba(201,168,76,0.15)",
    glass: "backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);background:rgba(255,255,255,0.03);border:1px solid rgba(201,168,76,0.12);",
    name: "Dark Luxury"
  },
  "neon-glow": {
    bg: "#0d0d1a", bgCard: "rgba(255,255,255,0.03)", accent: "#00f0ff",
    accentRgb: "0,240,255", text: "#e8e8ff", textMuted: "#6b6b8d",
    gradient: "linear-gradient(135deg, #00f0ff 0%, #b400ff 50%, #ff006a 100%)",
    fontDisplay: "'Space Grotesk', sans-serif",
    fontBody: "'Inter', sans-serif",
    glow: "0 0 60px rgba(0,240,255,0.2)",
    glass: "backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);background:rgba(13,13,26,0.7);border:1px solid rgba(0,240,255,0.15);",
    name: "Neon Glow"
  },
  "minimal-clean": {
    bg: "#fafaf8", bgCard: "#ffffff", accent: "#1a1a1a",
    accentRgb: "26,26,26", text: "#1a1a1a", textMuted: "#6b6b6b",
    gradient: "linear-gradient(135deg, #1a1a1a 0%, #4a4a4a 100%)",
    fontDisplay: "'DM Serif Display', serif",
    fontBody: "'DM Sans', sans-serif",
    glow: "0 4px 24px rgba(0,0,0,0.06)",
    glass: "background:#ffffff;border:1px solid #e8e8e8;box-shadow:0 2px 12px rgba(0,0,0,0.04);",
    name: "Minimal Clean"
  }
};

const t = themes[theme] || themes["dark-luxury"];
const p = profile;

// Format numbers
function fmt(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return String(n);
}

// Generate gallery items
const galleryItems = (p.posts || []).slice(0, 9).map((post, i) => {
  const thumb = post.thumbnail || "";
  const alt = post.alt_text || `Post ${i + 1}`;
  if (thumb) {
    return `<div class="gallery-item" data-index="${i}"><img src="${thumb}" alt="${alt}" loading="lazy"><div class="gallery-overlay"><span>Ver</span></div></div>`;
  }
  const hue = (i * 40 + 200) % 360;
  return `<div class="gallery-item" data-index="${i}" style="background:hsl(${hue},40%,${theme === 'minimal-clean' ? '92' : '18'}%);display:flex;align-items:center;justify-content:center;aspect-ratio:1;"><span style="font-size:2rem;opacity:0.4">📷</span><div class="gallery-overlay"><span>Ver</span></div></div>`;
}).join("\n          ");

// Generate hashtag pills
const hashtagPills = (p.hashtags || []).map(tag =>
  `<span class="hashtag-pill">#${tag}</span>`
).join("\n            ");

// Bio with line breaks
const bioHtml = (p.biography || "").replace(/\n/g, "<br>");

// Verified badge
const verifiedBadge = p.is_verified
  ? `<svg class="verified-badge" viewBox="0 0 24 24" width="22" height="22"><path fill="${t.accent}" d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-1.7 14.3L6 12l1.4-1.4 2.9 2.9 6.3-6.3L18 8.6l-7.7 7.7z"/></svg>`
  : "";

// External link button
const extLinkBtn = p.external_url
  ? `<a href="${p.external_url}" target="_blank" rel="noopener" class="cta-btn secondary-btn">🔗 Mi sitio web</a>`
  : "";

// Profile pic
const profilePicHtml = p.profile_pic_url
  ? `<img src="${p.profile_pic_url}" alt="${p.full_name}" class="profile-pic">`
  : `<div class="profile-pic profile-pic-placeholder"><span>${(p.full_name || p.username || "?")[0].toUpperCase()}</span></div>`;

// ── HTML ──
const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${p.full_name || "@" + p.username} — Landing Page</title>
  <meta name="description" content="${(p.biography || "").replace(/"/g, "&quot;").replace(/\n/g, " ").slice(0, 160)}">
  <meta property="og:title" content="${p.full_name || "@" + p.username}">
  <meta property="og:description" content="${(p.biography || "").replace(/"/g, "&quot;").replace(/\n/g, " ").slice(0, 200)}">
  ${p.profile_pic_url ? `<meta property="og:image" content="${p.profile_pic_url}">` : ""}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=${encodeURIComponent(t.fontDisplay.split("'")[1])}:wght@400;700&family=${encodeURIComponent(t.fontBody.split("'")[1])}:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>
<body data-theme="${theme}">

  <!-- Ambient background -->
  <div class="ambient-bg"></div>

  <!-- Main content -->
  <main class="container">

    <!-- Hero Section -->
    <section class="hero" id="hero">
      <div class="hero-card">
        <div class="profile-pic-wrapper">
          ${profilePicHtml}
          <div class="pic-ring"></div>
        </div>
        <div class="hero-info">
          <h1 class="display-name">
            ${p.full_name || "@" + p.username}
            ${verifiedBadge}
          </h1>
          <p class="username-label">@${p.username}</p>
          ${p.category ? `<span class="category-badge">${p.category}</span>` : ""}
          <p class="bio">${bioHtml}</p>
        </div>
      </div>
    </section>

    <!-- Stats Bar -->
    <section class="stats-bar" id="stats">
      <div class="stat" data-target="${p.followers}">
        <span class="stat-number" data-count="${p.followers}">0</span>
        <span class="stat-label">Seguidores</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat" data-target="${p.following}">
        <span class="stat-number" data-count="${p.following}">0</span>
        <span class="stat-label">Siguiendo</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat" data-target="${p.posts_count}">
        <span class="stat-number" data-count="${p.posts_count}">0</span>
        <span class="stat-label">Publicaciones</span>
      </div>
    </section>

    <!-- Gallery -->
    <section class="gallery-section" id="gallery">
      <h2 class="section-title">Contenido</h2>
      <div class="gallery-grid">
        ${galleryItems}
      </div>
    </section>

    ${(p.hashtags || []).length > 0 ? `
    <!-- Hashtags -->
    <section class="hashtags-section" id="hashtags">
      <h2 class="section-title">Hashtags</h2>
      <div class="hashtags-cloud">
        ${hashtagPills}
      </div>
    </section>` : ""}

    <!-- CTA -->
    <section class="cta-section" id="contact">
      <h2 class="section-title">Conecta</h2>
      <div class="cta-buttons">
        <a href="https://instagram.com/${p.username}" target="_blank" rel="noopener" class="cta-btn primary-btn">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
          Seguir en Instagram
        </a>
        ${extLinkBtn}
      </div>
    </section>

  </main>

  <!-- Footer -->
  <footer class="site-footer">
    <p>@${p.username} &bull; Generado con ❤️</p>
  </footer>

  <!-- Lightbox -->
  <div class="lightbox" id="lightbox">
    <button class="lightbox-close" id="lightbox-close">&times;</button>
    <img src="" alt="" class="lightbox-img" id="lightbox-img">
  </div>

  <script src="script.js"></script>
</body>
</html>`;

// ── Write files ──
fs.writeFileSync(path.join(outDir, "index.html"), html, "utf-8");
console.log("  ✅ index.html");

// Write CSS from template
const cssContent = fs.readFileSync(path.join(__dirname, "templates", "styles.css"), "utf-8")
  .replace(/VAR_BG/g, t.bg)
  .replace(/VAR_BG_CARD/g, t.bgCard)
  .replace(/VAR_ACCENT/g, t.accent)
  .replace(/VAR_ACCENT_RGB/g, t.accentRgb)
  .replace(/VAR_TEXT/g, t.text)
  .replace(/VAR_TEXT_MUTED/g, t.textMuted)
  .replace(/VAR_GRADIENT/g, t.gradient)
  .replace(/VAR_FONT_DISPLAY/g, t.fontDisplay)
  .replace(/VAR_FONT_BODY/g, t.fontBody)
  .replace(/VAR_GLOW/g, t.glow)
  .replace(/VAR_GLASS/g, t.glass);
fs.writeFileSync(path.join(outDir, "styles.css"), cssContent, "utf-8");
console.log("  ✅ styles.css");

// Write JS from template
const jsContent = fs.readFileSync(path.join(__dirname, "templates", "script.js"), "utf-8");
fs.writeFileSync(path.join(outDir, "script.js"), jsContent, "utf-8");
console.log("  ✅ script.js");

console.log(`\n🎉 Landing page generada en: ${outDir}`);
console.log(`   Tema: ${t.name}`);
console.log(`   Preview: npx -y serve output -p 3000`);
