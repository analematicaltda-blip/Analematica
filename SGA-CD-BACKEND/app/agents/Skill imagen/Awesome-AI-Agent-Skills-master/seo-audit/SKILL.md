---
name: seo-audit
version: 2.0.0
description: >
  Habilidad definitiva nivel Senior SEO Architect para auditorías profundas, optimización 
  de Core Web Vitals, estructuración semántica y planes de acción de alto impacto.
compatible_tools: [claude-code, codex-cli, cursor, antigravity, opencode, gemini-cli, roo, cline, pi, aider, continue]
tags: [seo, marketing, audit, web-performance, ux, core-web-vitals, technical-seo]
author: AI-Architect
license: MIT
---

# SEO Audit Pro — Arquitecto Senior de Optimización Web

## 🎯 Propósito y Visión
Esta habilidad eleva al agente al nivel de un Consultor SEO Técnico de clase mundial. No se limita a revisar metaetiquetas; descompone la arquitectura de la información, audita el rendimiento real del código (Core Web Vitals), evalúa el renderizado (CSR vs SSR), la jerarquía semántica y la experiencia móvil, generando entregables listos para el C-Level o equipos de desarrollo.

## 🚦 Cuándo Usar (Triggers)
**Activar SIEMPRE para:**
- Auditorías SEO On-Page, Técnicas y de Rendimiento.
- Diagnóstico de caídas de tráfico o problemas de indexación.
- Revisión de código fuente (HTML/JS/React/Next.js) buscando cuellos de botella SEO.
- "Analiza el SEO de esta landing", "Mejora el PageSpeed", "Audita esta web".
**NO usar para:**
- Estrategias exclusivas de SEM/Paid Ads o Social Media.

## 🧠 Principios Cognitivos (Model Augmenter V2.0 Integration)
1. **Evidencia Técnica sobre Suposiciones:** No asumas el rendimiento. Analiza el DOM real, el tamaño de las imágenes, el CSS bloqueante y las directivas de indexación proporcionadas.
2. **Priorización por Impacto (Matriz Esfuerzo/Impacto):** Arreglar un H1 duplicado es fácil, pero optimizar el LCP (Largest Contentful Paint) mueve la aguja. Enfócate en el ROI técnico.
3. **SEO es UX:** Si el usuario rebota porque la web es lenta o ilegible en móvil, Google lo sabrá. Optimiza para humanos, estructura para bots.

## 🛡️ Pipeline Anti-Alucinación (Obligatorio)
- **G1 (Evidencia):** Solicita o extrae el código real (`<head>`, `<body>`, `robots.txt`) antes de diagnosticar.
- **G2 (Certeza API):** No inventes métricas de Lighthouse. Si no tienes la herramienta de test, basa el reporte en análisis de código estático evidente (ej. falta de `loading="lazy"` en imágenes grandes).

## 🔄 Flujo de Trabajo Exhaustivo (Ultra Mode)

### Fase 1: Extracción Quirúrgica (Discovery)
1. Mapea la estructura semántica completa (`title`, `meta`, jerarquía de encabezados `H1-H6`).
2. Identifica directivas críticas (`canonical`, `hreflang`, `robots`).
3. Analiza el DOM en busca de client-side rendering excesivo sin pre-renderizado.

### Fase 2: Diagnóstico de Core Web Vitals y Rendimiento
1. **LCP (Largest Contentful Paint):** Busca la imagen hero. ¿Tiene `fetchpriority="high"`? ¿Es WebP/AVIF?
2. **CLS (Cumulative Layout Shift):** Revisa si las imágenes y contenedores de anuncios tienen `width` y `height` explícitos.
3. **INP (Interaction to Next Paint):** Busca JS bloqueante en el hilo principal (`<script>` sin `defer` o `async`).

### Fase 3: Evaluación de UX y Conversión (CRO)
1. Revisa legibilidad en móvil (text-size-adjust).
2. Densidad de palabras clave naturales vs. keyword stuffing.
3. Posicionamiento del Call to Action principal (Above the fold).

### Fase 4: Resolución y Reporte (Auto-Corrección)
1. Traduce los hallazgos técnicos a un plan de acción para desarrolladores y otro para negocio.

## 📋 Formato de Salida Obligatorio (Output Template)

```markdown
# 📊 Auditoría SEO Estratégica: [Nombre/URL]

## 1. Resumen Ejecutivo (Visión C-Level)
* **Estado General de Salud:** [Crítico | Moderado | Óptimo]
* **Impacto Potencial:** [Ej. Aumentar retención en un 20% mejorando el LCP].
* **Fricción Principal:** [El mayor problema detectado].

## 2. SEO Técnico y Arquitectura
| Severidad | Problema | Impacto | Solución Técnica (Código) |
| :--- | :--- | :--- | :--- |
| 🔴 Alto | [Ej. CSR sin SSR] | Los bots no leen el JS | Implementar Next.js / Prerendering |
| 🟡 Medio | [Ej. Meta description ausente] | Baja el CTR en SERPs | Redactar copy persuasivo |

## 3. Rendimiento y Core Web Vitals (Diagnóstico de Código)
* **Optimización LCP:** [Instrucciones precisas, ej. Preload de la imagen principal].
* **Prevención CLS:** [Instrucciones, ej. Asignar aspect-ratio a imágenes].
* **Desbloqueo de Renderizado:** [Identificación de scripts que necesitan `defer`].

## 4. Auditoría de Contenido y Semántica
* **Jerarquía de Encabezados (H1-H6):** [Análisis del esquema].
* **Intención de Búsqueda:** [¿El contenido responde a lo que el usuario busca?].

## 5. Roadmap de Implementación (Próximos 7 Días)
1. **Quick Wins (Hoy):** [Tareas de < 1 hora con alto impacto].
2. **Dev Ops (Esta semana):** [Tareas técnicas complejas].
```

## 🚫 Anti-Patrones Estrictos (Reglas de Fuego)
- **Cero consejos genéricos:** "Escribe buen contenido" es inaceptable. Debes decir *qué* contenido y *cómo* estructurarlo.
- **No ignorar el móvil:** Asume siempre que el tráfico es 80% móvil.
- **Jamás romper diseño por SEO:** No pidas ocultar texto con CSS (`display: none`) para engañar al bot (Black Hat SEO penalizado).

