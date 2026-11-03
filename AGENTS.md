## Nota para Futuros Agentes

Este proyecto tiene una configuración de entorno particular que afecta a cómo se resuelven las importaciones de Python.

**El Problema:**
El repositorio `SGA-CD-FASTAPI-BACKEND` depende de `SGA-CD-DB.git`, que debería ser un paquete instalable. Sin embargo, en el entorno de ejecución actual, ni `pip install -e` ni la configuración de la variable `PYTHONPATH` funcionan como se esperaba. Esto causa un `ModuleNotFoundError` al intentar importar módulos de la base de datos (ej. `from models...` o `from sga_cd_db.models...`).

**La Solución (Workaround):**
Para hacer que la aplicación funcione en este entorno, las sentencias de importación dentro de `SGA-CD-FASTAPI-BACKEND/app/` han sido modificadas para usar una mezcla de importaciones relativas y absolutas que son relativas al directorio `app/`.

*   En el directorio `app/crud/`, se usan importaciones relativas como `from ..models import ...`.
*   En el directorio `app/api/`, se usan importaciones absolutas como `from app.models import ...`.

**Advertencia:**
Esta no es una solución ideal y se considera deuda técnica. Si el entorno de ejecución se corrige en el futuro para que `PYTHONPATH` funcione correctamente, estas importaciones deberían revertirse a su forma más simple y estándar (ej. `from models import ...` en todo el proyecto, asumiendo que `SGA-CD-DB.git` está en `PYTHONPATH`).

No reviertas estas importaciones a menos que hayas confirmado que el entorno de `PYTHONPATH` ha sido reparado.
