# AUDITORÍA IA TRANSPARENTE EN UI — SARITA 2026

## 🎯 Objetivo (Bloque 24)
Proporcionar al Super Admin visibilidad total y capacidad de auditoría sobre las decisiones tomadas por los agentes de IA, garantizando la explicabilidad y el control humano.

## 👁️ 24.1 El "Caja de Cristal" UI
Ubicación: `/dashboard/admin-plataforma/agentes/auditoria`

### Visualización del Proceso de Razonamiento
Para cada decisión crítica de la IA, la interfaz debe mostrar:
1. **Intención Original:** El comando del usuario o evento disparador.
2. **Cadena de Pensamiento (Chain of Thought):** Los pasos lógicos seguidos por el agente.
3. **Fuentes de Verdad:** Referencias a modelos del backend o regulaciones (ej. "Validado contra LedgerEngine").
4. **Nivel de Confianza:** Porcentaje de certeza de la IA en la ejecución.

## 🛠️ 24.2 Componentes de Control
- **Botón de Replay:** Permite simular nuevamente una ejecución en un entorno de sandbox.
- **Botón de Rollback:** Revierte las acciones realizadas por un agente (siempre que la política lo permita).
- **Explainability Layer:** Un tooltip que explica por qué se tomó una decisión específica basada en pesos de variables.

## 📜 24.3 Registro de Auditoría (Harding SHA-256)
- Cada entrada en el log de auditoría en la UI debe mostrar su hash de integridad.
- Si un registro ha sido alterado, la UI mostrará una alerta visual roja de **"BRECHA DE INTEGRIDAD DETECTADA"**.

---
**Resultado:** Una IA potente pero totalmente subordinada al control humano y auditable en cada paso.
