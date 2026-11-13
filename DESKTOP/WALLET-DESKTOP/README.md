# DESKTOP/WALLET-DESKTOP · Flet y equipo asistente

`src/main.py` es la aplicación Flet de escritorio; usa la interfaz compartida y el paquete offline del backend. Permite apuntes y borradores cifrados, edición, dos revisiones locales y pendientes. No hay saldo simulado, login bancario ficticio ni autoridad para pagar sin servidor.

```sh
python -m pip install -e BACKEND/WALLET-BACKEND/offline -e FRONTEND/WALLET-FRONTEND
flet run DESKTOP/WALLET-DESKTOP/src/main.py
```

El cliente Flet y sus dependencias deben instalarse o empaquetarse antes de trabajar sin internet; el primer arranque de desarrollo podría descargar runtime. Compilar con Flet build windows/macos/linux en su plataforma correspondiente. No se afirma que esos binarios estén ya construidos o probados. El caché cifrado con contraseña es independiente de llaves financieras; integración nativa de Windows/macOS/Linux y ACL/capturas están pendientes. El espacio se bloquea al salir, perder foco y por inactividad; esto no garantiza impedir capturas del SO.

## Ocho soldados

Los trabajadores ejecutables están en `BACKEND/WALLET-BACKEND/offline/src/sgacd_wallet_offline/army.py`: custodia, digest, confianza pendiente de dispositivo, origen TLS requerido, revisión de etapas, distinción de borrador/recibo, caducidad y preparación productiva. Funcionan mediante reglas locales, sin servicio de IA o red. Devuelven resultados fijos sin exportar cuentas/importes/notas. No tienen herramientas para aprobar ni ejecutar pagos.

`agents/bridge.mjs` integra el catálogo y diagnósticos con `DESKTOP/asistencia-sgacd`, el conector existente de Open Duet/agent-desktop. Reutiliza su comando fijo de diagnóstico y política de control. El MCP solo publica equipo, pendientes, condiciones del control y diagnóstico; no observa ventanas, hace clic, escribe, aprueba ni gasta.

```sh
node DESKTOP/WALLET-DESKTOP/agents/prepare_profiles.mjs
node DESKTOP/WALLET-DESKTOP/agents/mcp.mjs
node --test DESKTOP/WALLET-DESKTOP/agents/tests/bridge.test.mjs
```

El preparador genera ocho workspaces/perfiles privados en `.runtime/army`, modo plan, memoria/helper/líder deshabilitados. No sobrescribe perfiles existentes ni registra/inicia modelos. Sin OPEN_DUET_ENGINE el proveedor permanece nulo y la inscripción queda pendiente. Configurar y validar un proveedor realmente local para inferencia sin internet; Open Duet y agent-desktop no son por sí solos modelos offline. No se invocó un proveedor real ni se conectó el portátil del usuario en esta sesión.

Cualquier control futuro conserva el permiso firmado del motor existente y dos autorizaciones del mismo solicitante, tres cuando corresponda por impacto. No hay permisos de control offline implementados ni una plataforma wallet de pagos añadida al motor. Las revisiones del caché no los sustituyen. Los agentes funcionales nuevos deben usar este contrato y nunca puentearlo mediante shell o un MCP general.

Pendientes para registro, vinculación y pruebas físicas: [documento único](../../ANALISIS/produccion/PENDIENTES-PRODUCCION-BILLETERA.md).
