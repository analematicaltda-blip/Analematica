"""
Instagram Landing Page Generator — Orquestador Principal
Pregunta el link/username, extrae datos, analiza contenido, genera landing page.
"""

import subprocess
import sys
import os
import json
import re


def main():
    print()
    print("=" * 56)
    print("  ✨ Instagram → Landing Page Generator ✨")
    print("=" * 56)
    print()

    # ── Paso 1: Pedir link o username ──
    print("  ¿Cuál es tu link de Instagram?")
    print("  (Pega el link completo o solo el username)")
    print()
    raw = input("  👉 ").strip()

    if not raw:
        print("\n  ❌ No ingresaste nada. Intenta de nuevo.")
        return

    # Extraer username del input
    username = _extract_username(raw)
    if not username:
        print(f"\n  ❌ No pude extraer un username de: {raw}")
        return

    print(f"\n  📱 Username detectado: @{username}")
    print()

    # ── Paso 2: Scraping ──
    print("  ⏳ Extrayendo información del perfil...")
    profile_path = os.path.join(os.path.dirname(__file__), "profile_data.json")

    try:
        from scraper import extract_profile
        profile = extract_profile(username, profile_path)
    except Exception as e:
        print(f"\n  ⚠️  Error en scraping: {e}")
        print("  Generando template manual...")
        from scraper import _generate_template
        profile = _generate_template(username, profile_path)

    # ── Paso 3: Analizar contenido y sugerir tema ──
    suggested_theme = _analyze_and_suggest_theme(profile)

    print(f"\n  🎨 Tema sugerido basado en tu perfil: {suggested_theme}")
    print()
    print("  Temas disponibles:")
    print("    1) dark-luxury   → Negro elegante con acentos dorados")
    print("    2) neon-glow     → Oscuro con efectos neón cyan/magenta")
    print("    3) minimal-clean → Blanco editorial, tipografía refinada")
    print()
    choice = input("  Elige tema (1/2/3) o ENTER para el sugerido: ").strip()

    theme_map = {"1": "dark-luxury", "2": "neon-glow", "3": "minimal-clean"}
    theme = theme_map.get(choice, suggested_theme)

    # ── Paso 4: Generar landing page ──
    print(f"\n  ⚡ Generando landing page con tema: {theme}")
    gen_script = os.path.join(os.path.dirname(__file__), "generator.js")
    result = subprocess.run(
        ["node", gen_script, "--theme", theme, "--input", profile_path],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0 and result.stderr:
        print(f"  ⚠️  {result.stderr}")

    # ── Paso 5: Abrir preview ──
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    index_path = os.path.join(output_dir, "index.html")

    if os.path.exists(index_path):
        print("  " + "=" * 50)
        print("  🎉 ¡Landing page lista!")
        print(f"  📁 Archivos en: {output_dir}")
        print()
        print("  ¿Quieres abrir el preview? (s/n)")
        open_preview = input("  👉 ").strip().lower()

        if open_preview in ("s", "si", "sí", "y", "yes", ""):
            # Intentar serve, sino abrir archivo directo
            print("\n  🌐 Abriendo preview...")
            try:
                import webbrowser
                webbrowser.open(f"file:///{index_path.replace(os.sep, '/')}")
            except Exception:
                os.startfile(index_path)

            print()
            print("  💡 Para un servidor local con recarga:")
            print(f"     cd \"{os.path.dirname(__file__)}\"")
            print("     npx -y serve output -p 3000")
        print()
        print("  📦 Para subir a hosting, sube la carpeta 'output/' completa.")
        print("     Compatible con: Netlify, Vercel, GitHub Pages, cualquier hosting.")
    else:
        print("  ❌ No se generó el archivo. Revisa los errores arriba.")


def _extract_username(raw: str) -> str:
    """Extrae username de un link de Instagram o texto directo."""
    raw = raw.strip().rstrip("/")

    # Link completo: https://www.instagram.com/username/...
    match = re.search(r"instagram\.com/([A-Za-z0-9_.]+)", raw)
    if match:
        return match.group(1)

    # Solo @username o username
    raw = raw.lstrip("@")
    if re.match(r"^[A-Za-z0-9_.]+$", raw):
        return raw

    return ""


def _analyze_and_suggest_theme(profile: dict) -> str:
    """
    Analiza el contenido del perfil (bio, hashtags, alt texts de posts)
    para sugerir el tema más apropiado.
    
    Heurística:
    - Palabras de lujo/elegancia/moda → dark-luxury
    - Palabras tech/gaming/neon/arte digital → neon-glow
    - Palabras naturaleza/minimalismo/clean/editorial → minimal-clean
    """
    # Recopilar todo el texto disponible
    texts = []
    texts.append((profile.get("biography") or "").lower())
    texts.append((profile.get("category") or "").lower())
    texts.extend([t.lower() for t in profile.get("hashtags", [])])
    for post in profile.get("posts", []):
        texts.append((post.get("alt_text") or "").lower())

    blob = " ".join(texts)

    # Keywords por tema
    luxury_kw = [
        "luxury", "lujo", "elegante", "fashion", "moda", "beauty", "belleza",
        "gold", "oro", "premium", "vip", "glamour", "style", "estilo",
        "designer", "couture", "exclusive", "brand", "marca", "lifestyle",
        "jewelry", "watch", "relojes", "boutique", "glam", "chic",
        "model", "modelo", "photography", "fotografia", "portrait", "retrato"
    ]
    neon_kw = [
        "tech", "gaming", "gamer", "neon", "digital", "code", "dev",
        "cyber", "music", "musica", "dj", "producer", "beat", "edm",
        "arte", "art", "creative", "creativo", "design", "diseño",
        "urban", "urbano", "street", "graffiti", "anime", "manga",
        "streamer", "content", "creator", "youtube", "twitch", "rgb",
        "futuristic", "sci-fi", "synthwave", "vaporwave", "pixel",
        "nightlife", "club", "party", "fiesta", "festival"
    ]
    minimal_kw = [
        "minimal", "minimalista", "clean", "nature", "naturaleza",
        "organic", "zen", "wellness", "bienestar", "yoga", "meditation",
        "simple", "editorial", "architect", "arquitectura", "interior",
        "home", "hogar", "plant", "planta", "sustainable", "eco",
        "cafe", "coffee", "book", "libro", "writer", "escritor",
        "calm", "peace", "quiet", "sereno", "healthy", "salud",
        "food", "comida", "chef", "cocina", "recipe", "receta",
        "travel", "viaje", "landscape", "paisaje", "slow"
    ]

    # Scoring
    scores = {
        "dark-luxury": sum(1 for kw in luxury_kw if kw in blob),
        "neon-glow": sum(1 for kw in neon_kw if kw in blob),
        "minimal-clean": sum(1 for kw in minimal_kw if kw in blob),
    }

    # Followers-based heuristic boost
    followers = profile.get("followers", 0)
    if followers > 100000:
        scores["dark-luxury"] += 2  # grandes cuentas suelen querer look premium

    best = max(scores, key=scores.get)

    # Si todos son 0, default basado en categoría o dark-luxury
    if scores[best] == 0:
        cat = (profile.get("category") or "").lower()
        if any(w in cat for w in ["artist", "music", "creator"]):
            return "neon-glow"
        if any(w in cat for w in ["food", "travel", "writer", "health"]):
            return "minimal-clean"
        return "dark-luxury"

    return best


if __name__ == "__main__":
    main()
