# INDICADORES GLOBALES DE MADUREZ (GMI) — SARITA 2026

## 🎯 Objetivo
Establecer las métricas cuantitativas que declaran al sistema como **"Enterprise-Grade Ready"**.

## 📊 Matriz de Indicadores Clave

| Indicador | Meta | Descripción |
| :--- | :--- | :--- |
| **% Autonomía Zero-Touch** | **> 95%** | Pasos ejecutados por agentes sin intervención humana. |
| **% Comunicación EventBus** | **100%** | Llamadas inter-dominio que usan eventos vs llamadas directas. |
| **% Decisiones Ejecutadas** | **> 80%** | Propuestas de la IA que se traducen en acciones reales. |
| **Cross-Import Ratio** | **0.00** | Número de importaciones directas entre dominios prohibidos. |
| **Mock Density** | **0%** | Porcentaje de Soldados N6 con retornos simulados. |

## 🔒 Hard Lock CI/CD (Garantía de Madurez)

El pipeline de despliegue aplicará los siguientes bloqueos:

1.  **Arquitectura:** Bloquear merge si `detect_cross_imports.py` encuentra violaciones.
2.  **Mocks:** Bloquear si existe una clase que herede de `SoldierTemplate` pero no de `SoldadoOroV2`.
3.  **Hooks:** Bloquear si un método en `useApi.ts` no tiene un endpoint correspondiente en la especificación OpenAPI generada del backend.

---
**Firmado:** Jules, Software Engineer Audit.
