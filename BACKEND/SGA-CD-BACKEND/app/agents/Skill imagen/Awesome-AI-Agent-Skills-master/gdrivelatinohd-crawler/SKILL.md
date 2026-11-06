---
name: gdrivelatinohd-crawler
description: Use only when explicitly maintaining the existing local GDriveLatinoHD crawler/reporting skill and working with its public-link catalog generation workflow.
---

# GDriveLatinoHD Crawler

## Descripción
Este skill es un rastreador masivo (Web Crawler) construido con `requests` y `BeautifulSoup` para extraer de manera recursiva todos los enlaces de descargas públicas (acortados) de la página `gdrivelatinohd.net` y compilarlos en una hoja de Excel profesional usando `pandas`.

## Archivos
*   `crawler_engine.py`: El script principal que realiza el rastreo, sortea los iFrames de `/paste/` y exporta la información.
*   `Catalogo_GDriveLatino.xlsx`: La salida oficial de los datos rastreados.

## Uso
Para ejecutar el script y generar el reporte Excel:
```bash
python crawler_engine.py
```

*Nota: Por defecto, está configurado para escanear `max_pages=1`. Si deseas rastrear la totalidad del sitio (miles de registros), edita `crawler_engine.py` y cambia `max_pages=999` (o el número de páginas totales).*

## Requisitos
*   `pandas`
*   `openpyxl`
*   `beautifulsoup4`
*   `requests`

## Limitaciones (Bypass)
Los enlaces VIP y directos (sin acortadores) no pueden ser extraídos automáticamente por este script porque la plataforma los oculta del frontend público. Este Crawler compilará exclusivamente los enlaces que contengan acortadores comerciales.

