---
name: redos-bypass
description: Use when authorized local testing is blocked by anti-tampering or ReDoS-style traps in JavaScript bundles and you need to neutralize disruptive local-only behavior while preserving app functionality.
---

# Skill: ReDoS Bypass (Anti-Tampering Neutralization)

## Propósito
Detectar y neutralizar mecanismos de protección anti-modificación (anti-tampering) en código JavaScript ofuscado que provocan congelamientos intencionales del navegador mediante Catastrophic Backtracking (ReDoS) cuando el archivo es alterado o formateado.

## Cuándo usar
- Cuando la página que estás clonando se congela por completo (CPU al 100%, "Page Unresponsive") tras haber modificado o formateado un archivo `.min.js`.
- Cuando el navegador falla silenciosamente y nunca realiza las peticiones `fetch` de inicialización.
- Durante ingeniería inversa de scripts ofuscados.

## Síntomas Comunes
- Expresiones regulares altamente anidadas y redundantes como `(((.+)+)+)+$`.
- Uso de `funcion.toString().search(/regex/)` o `funcion.toString().match(/regex/)` para validar la integridad del código fuente de la función.
- El código original funciona bien porque la firma literal de la función encaja rápido o no falla maliciosamente, pero al correr `Prettier` o añadir un espacio, la validación falla y desencadena un loop infinito de backtracking.

## Implementación
1. **Identificar la Trampa:** Busca en los archivos JS minificados (generalmente cerca del inicio) patrones de validación de funciones.
2. **Desactivación Quirúrgica:** No intentes arreglar la expresión regular. Busca dónde se invoca la función validadora (ej. `c();`) y coméntala o reemplázala por un bloque vacío.
   ```javascript
   // Antes
   function c() { /* ... lógica ReDoS ... */ }
   c(); // Esto congela el navegador si el archivo fue formateado
   
   // Después
   function c() { /* ... lógica ReDoS ... */ }
   /*c();*/ // Bypass exitoso
   ```
3. **Revisar Callbacks:** A veces la trampa está inyectada junto con otras funciones legítimas usando el operador coma:
   `(_(), c(), a());` -> Cámbialo a `(_(), /*c(),*/ a());`
4. **Validación:** Carga la página modificada con DevTools cerrado y abierto para comprobar que el hilo principal (`Main Thread`) no se bloquea.

