# Analematica · Ecosistema integrado

El plan de integración y su evidencia están en [INTEGRACIONES/plan-maestro](INTEGRACIONES/plan-maestro/README.md). Analemática es el sistema líder. Este repositorio conserva SGA-CD, Analemática, SGA-ERP-TUR y SGA-TUR junto con sus integraciones. Turismo Nacional conserva su naturaleza institucional.

Los proyectos completos de Jarvi, Neko y SOUP están en `BACKEND/ANALEMATICA-BACKEND/agents/OpenJarvis`, `BACKEND/ANALEMATICA-BACKEND/agents/N.E.K.O` y `BACKEND/ANALEMATICA-BACKEND/agents/Soup`. Jarvi dirige la operación, Neko la conversación y SOUP la optimización; los adaptadores de cada sistema conservan sus permisos y ámbitos propios.

## Billetera organizada

- [WALLET-BACKEND](WALLET-BACKEND/README.md): API, migraciones, pruebas, cifrado local y ocho trabajadores offline.
- [WALLET-FRONTEND](WALLET-FRONTEND/README.md): interfaz compartida Flet, puente nativo y panel público sin CDN.
- [WALLET-MOVIL](WALLET-MOVIL/README.md): aplicación Flet móvil y cuatro pools nativos.
- [WALLET-DESKTOP](WALLET-DESKTOP/README.md): aplicación Flet de escritorio y perfiles limitados sobre Open Duet/agent-desktop.
- [Pendientes de producción](ANALISIS/produccion/PENDIENTES-PRODUCCION-BILLETERA.md): registro vivo de responsables, evidencia y criterios de aceptación.

El trabajo offline admite apuntes y borradores cifrados; no habilita pagos o liquidación sin servidor. Los binarios firmados, la identidad financiera real y las validaciones en equipos físicos siguen pendientes. No se movieron bases ni credenciales junto con el código.

Los análisis y pendientes están organizados en [ANALISIS](ANALISIS/README.md).
