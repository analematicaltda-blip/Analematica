---
name: surgical-bundle-patcher
description: Use when applying minimal, targeted patches to JavaScript bundles during authorized local debugging or migration, especially when preserving bundle structure and avoiding broad rewrites is required.
---

# Skill: Surgical Bundle Patcher

## Propósito
Automatizar la modificación precisa y repetible de archivos "bundles" masivos del frontend (Webpack, minified JS/CSS) utilizando scripts de Python (Regex/String replace), para inyectar payloads, evadir domain-locking, o deshabilitar bloques anti-debugging sin corromper la sintaxis general.

## Cuándo usar
- Cuando estás clonando un sitio localmente y el script `main.js` restringe la ejecución a `location.hostname == 'misitio.com'`.
- Cuando necesitas remover `debugger;` loops del ofuscador en miles de líneas.
- Cuando quieres convertir esto en un proceso de un solo click, en lugar de buscar y reemplazar manualmente cada vez que actualizas los archivos del clon original.

## Implementación

### Estructura Base de Patcher (Python)
Crea un script que reciba el input original limpio, aplique expresiones regulares sucesivas, y produzca el `.min.js` final a servir.

```python
import re

def patch_file(filepath, outpath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Bypass Anti-Debugging (Loops de debugger)
    # Protegemos la sintaxis reemplazando la instrucción por comentarios del mismo "peso" lógico.
    content = re.sub(r'debugger\s*;', '/* debugger bypassed */', content)
    content = re.sub(r'debugger', '/* debugger bypassed */', content)
    
    # 2. Bypass Domain Locking
    # Forzamos estáticamente que cualquier chequeo del host original de verdadero.
    content = content.replace('window.location.hostname', '"mi-sitio-original.com"')
    content = content.replace('location.hostname', '"mi-sitio-original.com"')
    content = content.replace('location.host', '"www.mi-sitio-original.com"')
    content = content.replace('document.domain', '"mi-sitio-original.com"')
    
    # 3. Solución de Bugs de Sintaxis por Regex Invasivo
    # Si otra parte del bypass dejó bloques condicionales vacíos (ej. `if(cond) /*bypassed*/ else`), inyecta brackets:
    content = content.replace('if(true) /* location block bypassed */', 'if(true) {}')

    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Parchado {filepath} -> {outpath}')

# Ejecutar
patch_file('src_original/main.js', 'dist/main.js')
```

## Beneficios
- **Reproducibilidad:** Si el objetivo se actualiza, simplemente descargas su nuevo JS y corres el script; las reglas siguen aplicando.
- **Auditoría:** Es más fácil depurar qué causó un `SyntaxError` si los cambios están secuenciados programáticamente.
- Evita el uso inestable de Sed/Awk en entornos Windows.

