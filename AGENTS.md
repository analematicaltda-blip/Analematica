## Nota para Futuros Agentes

Este proyecto tiene una configuración de entorno particular que afecta a cómo se resuelven las importaciones de Python.

**El Problema:**
El repositorio `BACKEND/SGA-CD-BACKEND` depende de `SGA-CD-DB.git`, que debería ser un paquete instalable. Sin embargo, en el entorno de ejecución actual, ni `pip install -e` ni la configuración de la variable `PYTHONPATH` funcionan como se esperaba. Esto causa un `ModuleNotFoundError` al intentar importar módulos de la base de datos (ej. `from models...` o `from sga_cd_db.models...`).

**La Solución (Workaround):**
Para hacer que la aplicación funcione en este entorno, las sentencias de importación dentro de `BACKEND/SGA-CD-BACKEND/app/` han sido modificadas para usar una mezcla de importaciones relativas y absolutas que son relativas al directorio `app/`.

*   En el directorio `app/crud/`, se usan importaciones relativas como `from ..models import ...`.
*   En el directorio `app/api/`, se usan importaciones absolutas como `from app.models import ...`.

**Advertencia:**
Esta no es una solución ideal y se considera deuda técnica. Si el entorno de ejecución se corrige en el futuro para que `PYTHONPATH` funcione correctamente, estas importaciones deberían revertirse a su forma más simple y estándar (ej. `from models import ...` en todo el proyecto, asumiendo que `SGA-CD-DB.git` está en `PYTHONPATH`).

No reviertas estas importaciones a menos que hayas confirmado que el entorno de `PYTHONPATH` ha sido reparado.

## Herramientas de escritorio locales

La copia de agent-desktop está en `DESKTOP/agent-desktop`; el conector y su
procedencia están en `DESKTOP/agent-desktop-sgacd`. El runner local es
`node DESKTOP/agent-desktop-sgacd/run.mjs`. Antes de usar acciones, consulta
`skills get desktop`, `skills get platform` y `status` del runtime instalado.
El proceso opera su propio host: Codespaces no proporciona acceso al portátil.
La configuración MCP del proyecto no conecta automáticamente esta sesión de chat.

## Organización de la billetera

Las fuentes canónicas están en WALLET-BACKEND, WALLET-FRONTEND, WALLET-MOVIL
y WALLET-DESKTOP. Conservar los imports apps.wallet, la etiqueta Django wallet
y las migraciones existentes mediante adaptadores de compatibilidad. No mover
bases, secretos o llaves junto con el código.

Actualizar PENDIENTES-PRODUCCION-BILLETERA.md mediante el registro canónico
production_pending.json y WALLET-BACKEND/tools/update_pending_doc.py en cada
entrega que cambie evidencia o deje un bloqueo nuevo. No cerrar pruebas físicas,
identidad, proveedores o releases usando evidencia sintética.

Los agentes funcionales nuevos deben apoyarse en el contrato Open Duet +
agent-desktop mediante el conector limitado y el control de autorizaciones
existente. No autoaprobar, exponer secretos a modelos ni crear bypasses de shell.
El modo offline prepara borradores/apuntes, no liquida dinero; las dos revisiones
locales no son autorizaciones financieras ni permisos de control.
