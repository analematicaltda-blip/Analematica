---
name: efficient-explorer
description: Protocolo de exploración de alto rendimiento y consulta de memoria semántica. Úsalo para localizar información en el repositorio sin recurrir a búsquedas manuales lentas.
---

# Efficient Explorer (Navegación Relámpago)

Este skill optimiza el uso de tokens y tiempo mediante el uso de herramientas de búsqueda avanzada y la memoria de episodios del sistema.

## Protocolo de Búsqueda de 3 Niveles

1.  **Nivel 1: Memoria Semántica (Embedding)**
    Si buscas un concepto, patrón o algo que sabes que has hecho antes, usa el Oráculo:
    `python query_memory.py "cómo se manejan los errores de visión"`
    *Beneficio*: Encuentra archivos relevantes sin listar carpetas.

2.  **Nivel 2: Búsqueda por Patrones (Grep Pro)**
    Si buscas un símbolo, una cadena exacta o una extensión:
    `grep_search pattern="pattern" include_pattern="*.py"`
    *Beneficio*: Instantáneo y preciso.

3.  **Nivel 3: Estructura (Glob)**
    Para encontrar archivos por nombre o ubicación:
    `glob pattern="**/docs/*.md"`

## Reglas Anti-Ineficiencia
- **PROHIBIDO**: Listar (`ls`) secuencialmente carpetas para "ver qué hay".
- **PROHIBIDO**: Leer archivos completos (`read_file`) solo para buscar una cadena.
- **OBLIGATORIO**: Usar `query_memory.py` al inicio de una investigación compleja para "calentar" el contexto.

