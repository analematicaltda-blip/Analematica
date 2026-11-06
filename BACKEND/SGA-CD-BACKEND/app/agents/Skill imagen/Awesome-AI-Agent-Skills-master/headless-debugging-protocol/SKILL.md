---
name: headless-debugging-protocol
description: Use when doing authorized local debugging of SPAs or bundled web apps with silent startup failures, hidden console errors, network failures, or page initialization issues that require Puppeteer or Playwright diagnostics.
---

# Skill: Headless Debugging Protocol

## Propósito
Exponer errores silenciosos, excepciones síncronas ocultas y fallos de red indetectables que ocurren durante la inicialización de aplicaciones SPA y bundles ofuscados, utilizando un entorno Headless controlado (Puppeteer/Playwright).

## Cuándo usar
- Cuando la consola del navegador está sobreescrita (hijack) o "limpiada" antes de que el usuario logre leerla.
- Cuando la página se queda en blanco, no tira errores visibles, y los requests de red no aparecen en tu servidor backend.
- Para atrapar un `TypeError: Illegal invocation` u otros errores síncronos lanzados dentro de handlers como `DOMContentLoaded` que detienen la ejecución silenciosamente.

## Implementación

Usa un script de diagnóstico aislado (como Node + Puppeteer) para envolver y escuchar los eventos nativos de la página en su nivel más fundamental.

```javascript
// check_errors.js
const puppeteer = require('puppeteer');

(async () => {
    // 1. Iniciar con flags seguros
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    // 2. Escuchar Logs de Consola
    page.on('console', msg => {
        console.log('PAGE LOG:', msg.text());
        // Argumentos desglosados útiles para objetos JSON tirados como Error
        msg.args().forEach(async arg => {
            console.log('ARG:', await arg.jsonValue().catch(()=>''));
        });
    });
    
    // 3. Atrapar Errores Síncronos y Globales
    // Crucial para Uncaught TypeErrors en ofuscaciones rotas
    page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
    
    // 4. Atrapar Fallos de Red Específicos (CORS, 404, Blocked)
    page.on('requestfailed', request => {
        console.log('REQUEST FAILED:', request.url(), request.failure()?.errorText);
    });
    page.on('response', response => {
        if (!response.ok()) {
            console.log('BAD RESPONSE:', response.status(), response.url());
        }
    });
    
    console.log('Navegando a target...');
    try {
        await page.goto('http://mi-clon.localtest.me:8081/', { waitUntil: 'load', timeout: 10000 });
        console.log('Carga finalizada con éxito.');
    } catch (e) {
        console.log('Navegación interrumpida (común en SPAs o redirecciones infinitas):', e.message);
    }
    
    // Dar un buffer para peticiones asíncronas tardías
    await new Promise(r => setTimeout(r, 2000));
    await browser.close();
})();
```

## Tips Avanzados
- Si sospechas de que la variable `fetch` perdió el contexto (`Illegal invocation`), inyecta `await page.evaluate(() => window.fetch.toString());` para comprobar si es código nativo o si otro script lo sobreescribió maliciosamente.
- Las capturas de red de Puppeteer (`response.status()`) siempre dirán la verdad incluso si el código frontend bloquea el objeto original del Developer Tools.

