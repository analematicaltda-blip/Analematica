---
name: gdrivelatinohd-pdf-generator
description: Use only when explicitly maintaining the existing local GDriveLatinoHD PDF reporting skill and generating structured reports from already-collected local data.
---

# GDriveLatinoHD PDF Extractor Skill

## Description
This skill provides an automated scraping and PDF generation pipeline tailored for warez/streaming sites like GDriveLatinoHD. It parses a local SQLite database, fetches intermediate "paste" pages, extracts link shorteners (like `exe.io`, `shortxlinks.in`), and packages them into a beautifully formatted, premium PDF document using `reportlab`.

## Usage
Run the engine via Python:
```bash
python scraper_engine.py
```

## Features
- **Intelligent Paste Parsing**: Automatically resolves intermediate `gdrivelatinohd.net/paste/` pages.
- **Server Name Extraction**: Heuristically extracts the target server (Mega, Drive, 1Fichier, PixelDrain, AkiraBox) from the DOM.
- **Best-Effort Bypass**: Prepares links for a Captcha-solving API / VIP cookie bypass. If not available, gracefully degrades to providing the shortener URL labeled with its bypass requirement.
- **Premium PDF Rendering**: Uses `reportlab` with A4 formatting, custom colors, and structured tables.

## Requirements
- `reportlab`
- `beautifulsoup4`
- `requests`

