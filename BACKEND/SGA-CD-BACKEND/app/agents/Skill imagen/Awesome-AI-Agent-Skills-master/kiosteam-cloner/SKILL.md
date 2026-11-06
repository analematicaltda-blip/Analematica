---
name: kiosteam-cloner
description: Use only when explicitly maintaining the existing Kiosteam local cloning skill for authorized SPA capture, local testing, and static asset troubleshooting.
---

# Kiosteam Cloner Skill

## Descripción
Esta skill está diseñada específicamente para realizar extracciones profundas (clonación estática perfecta) de aplicaciones SPA (Single Page Applications) complejas como `kiosteam.com`, las cuales bloquean la carga con un loader infinito y dependen de APIs en segundo plano.

## Herramientas Necesarias
- **Playwright / Scrapling**: Necesario para ejecutar el JavaScript de la página objetivo y esperar a que el DOM se renderice por completo antes de extraer el código.

## Procedimiento (Flujo de Trabajo)
1. **Navegación Headless**: Abre la página usando `playwright` o `scrapling`.
2. **Espera Dinámica**: No dependas del evento `networkidle` en páginas con polling. Usa `wait_until="load"` y un `timeout` manual (ej. 8000 ms) para asegurar que el loader (`#loader` o `.se-pre-con`) desaparezca y los productos se inyecten en el DOM.
3. **Congelamiento de DOM**: Extrae el `page.content()` estático.
4. **Parcheo de Rutas y Scripts**:
   - Elimina los scripts pesados de la app (ej. `productos.min.js`) que causan recargas infinitas en el clon local.
   - Oculta forzadamente el cargador mediante CSS en línea: `style="display:none !important;"`.
   - Convierte rutas relativas a absolutas y luego a locales.
5. **Servidor Local**: Sirve la carpeta usando un puerto específico y asigna un dominio de pruebas como `http://kiosteam.localtest.me:8081` para evitar bloqueos CORS.

