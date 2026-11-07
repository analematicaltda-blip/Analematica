"""
Instagram Profile Scraper — Scrapling + StealthyFetcher
Extrae datos públicos de un perfil de Instagram para generar landing pages.
"""

import json
import re
import sys
import os
import time
import random
from pathlib import Path


def extract_profile(username: str, output_path: str = "profile_data.json") -> dict:
    """
    Extrae datos públicos de un perfil de Instagram usando Scrapling StealthyFetcher.
    
    Args:
        username: Nombre de usuario de Instagram (sin @)
        output_path: Ruta donde guardar el JSON resultante
    
    Returns:
        dict con los datos del perfil
    """
    username = username.lstrip("@").strip()
    url = f"https://www.instagram.com/{username}/"

    print(f"\n🔍 Extrayendo perfil de @{username}...")
    print(f"   URL: {url}")

    try:
        from scrapling.fetchers import StealthyFetcher
    except ImportError:
        print("❌ Scrapling no instalado. Ejecuta: pip install 'scrapling[fetchers]'")
        print("   Luego: scrapling install")
        return _generate_template(username, output_path)

    try:
        # Fetch con StealthyFetcher — navegador stealth headless
        page = StealthyFetcher.fetch(
            url,
            headless=True,
            network_idle=True,
            wait_selector="header",
            timeout=30000,
        )

        if page is None or page.status != 200:
            print(f"⚠️  No se pudo acceder al perfil (status: {getattr(page, 'status', 'N/A')})")
            return _generate_template(username, output_path)

        # ── Extraer datos del HTML renderizado ──

        profile_data = {
            "username": username,
            "full_name": "",
            "biography": "",
            "profile_pic_url": "",
            "followers": 0,
            "following": 0,
            "posts_count": 0,
            "external_url": "",
            "hashtags": [],
            "posts": [],
            "is_verified": False,
            "category": "",
        }

        # Intentar extraer del meta tag og:title (suele tener el nombre)
        og_title = page.css('meta[property="og:title"]')
        if og_title:
            content = og_title[0].attrib.get("content", "")
            # Formato típico: "Nombre (@username) • Instagram photos and videos"
            name_match = re.match(r"^(.+?)\s*\(@", content)
            if name_match:
                profile_data["full_name"] = name_match.group(1).strip()

        # Meta description suele tener bio y stats
        meta_desc = page.css('meta[property="og:description"]')
        if meta_desc:
            desc = meta_desc[0].attrib.get("content", "")
            # Formato: "X Followers, Y Following, Z Posts - See Instagram photos..."
            stats_match = re.search(
                r"([\d,.KkMm]+)\s*Followers?,\s*([\d,.KkMm]+)\s*Following,\s*([\d,.KkMm]+)\s*Posts?",
                desc,
                re.IGNORECASE,
            )
            if stats_match:
                profile_data["followers"] = _parse_count(stats_match.group(1))
                profile_data["following"] = _parse_count(stats_match.group(2))
                profile_data["posts_count"] = _parse_count(stats_match.group(3))

            # La bio suele estar después del dash
            bio_match = re.split(r"\s*[-–—]\s*", desc, maxsplit=1)
            if len(bio_match) > 1:
                profile_data["biography"] = bio_match[1].strip()

        # Foto de perfil desde og:image
        og_image = page.css('meta[property="og:image"]')
        if og_image:
            profile_data["profile_pic_url"] = og_image[0].attrib.get("content", "")

        # Intentar extraer posts (thumbnails de la galería)
        post_links = page.css("article a[href*='/p/']")
        if post_links:
            for link in post_links[:12]:
                post_url = link.attrib.get("href", "")
                img = link.css("img")
                post_entry = {
                    "url": f"https://www.instagram.com{post_url}" if post_url.startswith("/") else post_url,
                    "thumbnail": img[0].attrib.get("src", "") if img else "",
                    "alt_text": img[0].attrib.get("alt", "") if img else "",
                }
                profile_data["posts"].append(post_entry)

        # Extraer hashtags de las alt texts y bio
        all_text = profile_data["biography"] + " " + " ".join(
            p.get("alt_text", "") for p in profile_data["posts"]
        )
        hashtags = re.findall(r"#(\w+)", all_text)
        # Contar frecuencia y tomar top 15
        from collections import Counter
        tag_counts = Counter(hashtags)
        profile_data["hashtags"] = [tag for tag, _ in tag_counts.most_common(15)]

        # Verificación badge
        verified_elements = page.css('[title="Verified"]') or page.css('svg[aria-label="Verified"]')
        profile_data["is_verified"] = bool(verified_elements)

        # External URL
        external_links = page.css('a[href*="l.instagram.com"]')
        if external_links:
            profile_data["external_url"] = external_links[0].attrib.get("href", "")

        # Guardar JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Perfil extraído correctamente:")
        print(f"   Nombre: {profile_data['full_name'] or 'No detectado'}")
        print(f"   Bio: {profile_data['biography'][:60]}{'...' if len(profile_data['biography']) > 60 else ''}")
        print(f"   Seguidores: {profile_data['followers']:,}")
        print(f"   Posts encontrados: {len(profile_data['posts'])}")
        print(f"   Guardado en: {output_path}")

        return profile_data

    except Exception as e:
        print(f"\n⚠️  Error durante scraping: {e}")
        print("   Generando template manual como fallback...")
        return _generate_template(username, output_path)


def _parse_count(text: str) -> int:
    """Convierte '1.2M', '45.3K', '1,234' a entero."""
    text = text.strip().replace(",", "")
    multiplier = 1
    if text[-1].upper() == "K":
        multiplier = 1_000
        text = text[:-1]
    elif text[-1].upper() == "M":
        multiplier = 1_000_000
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0


def _generate_template(username: str, output_path: str) -> dict:
    """Genera un template JSON vacío para llenado manual."""
    template = {
        "username": username,
        "full_name": f"@{username}",
        "biography": "Tu biografía aquí — edita este archivo con tu información real",
        "profile_pic_url": "",
        "followers": 0,
        "following": 0,
        "posts_count": 0,
        "external_url": "",
        "hashtags": ["tuhashtag", "tumarca"],
        "posts": [
            {
                "url": f"https://www.instagram.com/{username}/",
                "thumbnail": "",
                "alt_text": "Descripción del post"
            }
        ],
        "is_verified": False,
        "category": "",
    }

    template_path = output_path.replace(".json", "_template.json") if os.path.exists(output_path) else output_path
    with open(template_path, "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=2)

    print(f"\n📝 Template generado en: {template_path}")
    print("   Edita el archivo con los datos reales y vuelve a ejecutar el generador.")
    return template


def load_profile(path: str = "profile_data.json") -> dict:
    """Carga un perfil desde JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scraper.py <username>")
        print("Ejemplo: python scraper.py cristiano")
        sys.exit(1)

    username = sys.argv[1]
    extract_profile(username)
