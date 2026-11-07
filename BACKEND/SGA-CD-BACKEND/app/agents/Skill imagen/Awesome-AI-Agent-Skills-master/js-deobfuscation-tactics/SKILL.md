---
name: js-deobfuscation-tactics
description: Use when analyzing JavaScript bundles in an authorized local debugging, migration, or compatibility context and you need safe tactics for understanding obfuscated control flow without broad rewrites.
---

# Skill: JS Deobfuscation Tactics

## Propósito
Abordar sistemáticamente archivos JavaScript de producción minificados y ofuscados, recuperando el flujo de control, aislando protecciones maliciosas y mapeando cadenas ocultas en el "Shift Array" o diccionarios dinámicos.

## Cuándo usar
- Cuando las variables y strings han sido reemplazados por llamadas a funciones (ej. `_0x123('0x1a')` o `x(458)`).
- Cuando el código original de un clon falla porque verifica su propio texto (ReDoS Anti-Tampering).
- Durante la auditoría o neutralización de payloads.

## Táctica 1: Normalización Segura (Evitar ReDoS)
Si usas `Prettier` sobre código minificado ofuscado, puedes activar accidentalmente protecciones anti-tampering como las basadas en `toString().search(...)`.
1. Siempre corre Prettier: `npx prettier file.min.js --write`.
2. Si el archivo crashea el navegador al abrirlo: Busca de inmediato funciones con `search` o `match` de Regex largos al inicio del documento. Enciérralas en comentarios `/* func() */`. No borres la función entera para no romper dependencias internas.

## Táctica 2: Extracción del "Shift Array"
Los ofuscadores comerciales extraen todos los textos literales a un array masivo al inicio o final del documento, y utilizan una función rotadora (shifter) autoejecutable (IIFE) para desordenarlos según el entorno.

1. **Localizar el Array:** Busca un array enorme de strings, generalmente cerca de `function e() { let x = ['str1', 'str2', ...]; return e = function() { return x; }, e(); }`.
2. **Localizar el Shifter:** Busca el bucle de inicialización (`while(true) try { t.push(t.shift()); ... } catch(e) {}`).
3. **Localizar el Extractor:** Busca la función que usa los offsets numéricos, usualmente se ve así: `function f(x, $) { x -= 333; return arr[x]; }`.

## Táctica 3: Dumpeo de Constantes Vía Entorno Dinámico
En lugar de revertir el algoritmo a mano, usa Node.js para ejecutar esa porción de código de forma aislada e imprimir el diccionario.
```javascript
// dump_strings.js
const fs = require('fs');
const content = fs.readFileSync('min.js', 'utf8');

// 1. Extraer las 3 partes mediante regex o copia manual
const e_match = content.match(/function e\(\)\s*\{[\s\S]*?\}\)\(\);/)[0];
const shifter_match = content.match(/!\(function\s*\(x,\s*\$\)\s*\{[\s\S]*?\}\)\(e,\s*\d+\);/)[0];
const f_match = content.match(/function f\(x,\s*\$\)\s*\{[\s\S]*?return t;\s*\}/)[0];

// 2. Evaluarlas en memoria
eval(e_match);
eval(shifter_match);
eval(f_match);

// 3. Imprimir diccionario iterando el rango posible
for(let i = 0; i < 1000; i++) {
    try {
        let str = f(i); // Reemplaza 'f' por el nombre de la función extractora
        if (typeof str === 'string') console.log(i + ': ' + str);
    } catch(e) {}
}
```

## Táctica 4: Reemplazo Quirúrgico (Grep & Sed)
Una vez mapeado el diccionario (ej. sabiendo que `x(335)` es `"getElementById"` y `x(458)` es `"mi-elemento"`), usa búsqueda inteligente para identificar lógicas. 
Si necesitas parchar, es preferible inyectar comentarios o variables booleanas (`true || original_logic()`) que tratar de reformatear la estructura AST del ofuscador manual.

