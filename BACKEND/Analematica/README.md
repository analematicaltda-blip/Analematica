# Analemática · Componente principal

- `../FRONTEND/ANALEMATICA-FRONTEND/`: landing corporativa, ingreso del dueño, consola ERP/DIAN/auditoría,
  controles de SGA-CD e integración de Meta/Instagram.
- `../BACKEND/ANALEMATICA-BACKEND/`: servicios ERP, datos y despliegue del nodo.

La consola anterior se consolidó en este componente. Se conservaron los controles
de ambos paneles, la landing, los estilos, datos corporativos y pruebas. El
controlador actual de agentes se mantiene activo y la versión anterior se conserva
en `../FRONTEND/ANALEMATICA-FRONTEND/agents/compat/analematica_sga_cd_army.js`, sin cargar globales duplicados.
El inventario de destinos está en `../BACKEND/ANALEMATICA-BACKEND/reports/CONSOLIDACION.json`.

Despliegue del nodo corporativo sobre la demo existente:

```bash
python3 BACKEND/ANALEMATICA-BACKEND/deployment/start.py
```

El instalador compatible `../FRONTEND/ANALEMATICA-FRONTEND/deployment/start.py` delega al mismo backend.
Solo se publican recursos de la lista permitida; los datos y secretos del backend
no se copian al servidor estático. El gateway conserva el ingreso y las API seguras
de `BACKEND/SGA-CD-BACKEND`; los servicios ERP independientes del repositorio APP
se preservan y no se activan automáticamente como sustitutos de esa autorización.
Su validación de producción sigue pendiente, incluidas incidencias preexistentes.

`SGA-CD-FASTAPI-BACKEND` era un enlace simbólico de compatibilidad, no otro backend.
Se retiró y sus referencias operativas apuntan al backend activo.

Los cuatro backends están en `BACKEND/`. Analemática conserva su frontend
en `FRONTEND/ANALEMATICA-FRONTEND`; los otros frontends están agrupados bajo `FRONTEND/`.
