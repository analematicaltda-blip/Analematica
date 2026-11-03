---
name: console-hijack-bypass
description: Use when doing authorized local debugging of owned or permitted web apps where browser console methods have been overwritten, muted, or hijacked and console visibility must be restored for diagnosis.
---

# Skill: Console Hijack Bypass

## Propósito
Restaurar la funcionalidad de las herramientas de desarrollo del navegador (`console.log`, `console.error`, etc.) cuando un script de terceros ha sobreescrito intencionalmente el objeto global `console` como medida de seguridad (anti-debugging).

## Cuándo usar
- Durante el análisis o ingeniería inversa de aplicaciones.
- Si ves que los errores de red (como peticiones fallidas o peticiones CORS) no se reflejan en la pestaña "Console" pero sabes que están ocurriendo.
- Si los scripts ofuscados contienen arrays de métodos como `['log', 'warn', 'info', 'error', 'exception', 'table', 'trace']` y manipulan el prototipo de funciones.

## Síntomas Comunes
- `console.log("test")` no imprime nada.
- Ejecutar `console.log` devuelve una función anónima vacía `() => {}` en lugar del código nativo.
- La página ofuscada crea un iframe temporal, roba el objeto `console` limpio y lo puentea con el suyo para filtrar logs.

## Implementación
1. **Identificar la Inyección:** Busca patrones que reasignen variables de `window`. Generalmente involucran un alias para `console` u ofuscación de strings.
2. **Neutralizar la Llamada:** Al igual que el ReDoS, la técnica más segura es comentar la llamada a la función secuestradora en lugar de borrar su definición, para no romper referencias de memoria.
   ```javascript
   // Código ofuscado invoca: a()
   // Comentar llamada: /*a()*/
   ```
3. **Inyección en Tiempo de Ejecución (Alternativa):** Si no puedes editar el archivo origen, puedes intentar congelar el prototipo de console antes de que cargue el script de terceros (Inyectar como primer script del `<head>`):
   ```javascript
   Object.freeze(window.console);
   ```
4. **Validación:** Tras neutralizar el secuestro, navega a la página local e inyecta `console.log('funciona')`. Debe imprimir en consola nativamente.

