---
name: static-assets-localizer
description: Use when localizing static assets for an authorized web clone or migration, including rewriting remote URLs, downloading public assets, fixing paths, and verifying offline asset loading.
---

# Skill: Static Assets Localizer

## Propósito
Lograr autonomía total de un clon frontend (operación 100% offline) escaneando archivos raíz (HTML, CSS, JS) para descubrir, extraer y descargar todos los assets visuales (fuentes, SVGs, imágenes WebP) que todavía están siendo traídos desde URLs absolutas u orígenes remotos.

## Cuándo usar
- Cuando estás "ripando" o clonando un sitio web para propósitos de prueba y deseas asegurar una paridad visual ("dos gotas de agua").
- Cuando ves peticiones a CDNs (ej. `fonts.googleapis.com`, `b-cdn.net`, AWS S3) en el tab "Network" de DevTools.
- Cuando quieres garantizar que el entorno no fallará si cambian las políticas CORS del sitio original.

## Implementación
1. **Crear Estructura:** Mantén la carpeta `/assets` del sitio clonado como directorio destino.
2. **Scripting Automatizado:** Crea un script (ej. Python) que procese `style.css` e `index.html`.
3. **Expresiones Regulares Útiles:**
   - Para CSS: `r'url\([\'"]?(https?://[^\'"\)]+)[\'"]?\)'` (Atrapa URLs absolutas como fuentes o fondos).
   - Para CSS (Rutas relativas): `r'url\([\'"]?(/assets/[^\'"\)]+)[\'"]?\)'` (Atrapa rutas relativas del servidor original).
   - Para HTML: `r'src=[\'"](https?://[^\'"]+)[\'"]'`
4. **Lógica de Descarga:**
   - Por cada URL descubierta: extrae el nombre base del archivo.
   - Si es relativo, concaténalo con el dominio original.
   - Crea subdirectorios si es necesario (ej. `assets/Logos/`).
   - Usa la librería de requests (`requests.get`) para descargar y guardar los bytes (`f.write`).
5. **Reemplazo Local:** Automáticamente reemplaza las cadenas de texto del URL remoto en tus archivos locales por el path relativo (`./assets/archivo.png`), de esta forma bloqueando futuras peticiones externas.

## Resultados
Garantiza un "zero-dependency clone", reduciendo la latencia de desarrollo y estabilizando el entorno para interceptar APIs o experimentar con rediseños de la UI.

