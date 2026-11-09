# Puente contable corporativo · preparación revisable

Estado: código y recorrido local verificados; activación productiva no realizada.

## Preparación

1. Usar el backend corporativo canónico FastAPI (rutas workspace/corporate) y ERP Django con sesiones web habilitadas. El servidor legacy integrated_server.py no incorpora este puente. No se crean credenciales ni se sustituyen controles MFA del ERP.
2. Configurar CORPORATE_LEDGER_ORIGIN en el backend corporativo con el origen fijo del ERP. Debe ser HTTPS para destinos no loopback; no incluir rutas, credenciales, query o fragmentos. La confianza CA/red y el alcance del origen requieren validación en el entorno real. No deshabilitar verificación TLS para sortear fallos.
3. Revisar la instalación/gateway para que la sesión HttpOnly del ERP llegue a la ruta corporativa /api/. Mantener nombre, Path, Secure y SameSite apropiados; no compartir cookies indiscriminadamente entre dominios. El token corporativo no se reenvía al ERP.
4. Identificar dueño corporativo y vínculo legítimo de actor/prestador/Tenant del ERP, con evidencia administrativa. El esquema no deduce equivalencias por ID numérico, correo o primer registro. No registrar prestadores ficticios para activar el puente.
5. Preparar únicamente la tabla corporate_ledger_binding mediante el procedimiento de esquema aprobado. El proceso web no crea tablas. Falta de tabla/vínculo retorna 503 sin datos; no usa fallback.

## Herramienta de revisión

```bash
python BACKEND/SGA-CD-BACKEND/tools/review_corporate_ledger.py --help
```

El operador aporta owner-id, reviewer-id, ledger-actor-id (PK Django positivo), provider-id y tenant-id canónicos, evidence-digest SHA-256 y valid-until ISO con zona horaria. El reviewer debe ser un administrador general activo distinto del titular. Sin --apply solo inspecciona/revisa y no persiste el vínculo.

--apply persiste un único vínculo; rechaza sobrescribir el existente. --initialize-table junto con --apply crea explícitamente solo la tabla si falta; DDL y guardado son pasos separados y el esquema puede quedar preparado aunque falle la revisión. No invocar sobre producción sin esquema/respaldos/roles revisados. No pasar contraseñas o cookies: la herramienta no las acepta.

El modelo se probó mediante metadatos SQLAlchemy en SQLite; faltan despliegue PostgreSQL, permisos y pruebas de restauración específicas del nuevo vínculo. El rol web requiere lectura; DDL/provisión deben pertenecer al operador autorizado. No se ha ejecutado esta herramienta contra datos reales.

## Recorrido de usuario

Abrir la sesión de dueño en Analemática y la sesión ERP del titular contable enlazado. En División contable → Consulta del libro mayor, elegir balance de prueba o rentabilidad y las fechas. Se consulta la empresa fijada; no existe selector de otros Tenant. Verificar moneda/corte y origen. El reporte no acredita aceptación fiscal ni autoriza una transacción.

Si falta sesión/vínculo, se revoca o no coincide el actor, se bloquea y no se muestran importes anteriores. Los resultados ya descargados no pueden borrarse remotamente por esta cabecera. Renovación/recuperación del vínculo necesita un flujo revisado aún pendiente; no eliminar y recrear registros para simular continuidad de auditoría.

## Ensayo reproducible local

```bash
python INTEGRACIONES/operacion/verify_local.py --profile accounting --output /tmp/resultado-contable-nuevo
python INTEGRACIONES/operacion/verify_local.py --verify /tmp/resultado-contable-nuevo
```

El perfil incluye dos procesos/backends, roles y almacenes desechables. El navegador corporativo se valida con FRONTEND/deployment/tests/corporate_ledger_browser.cjs usando las dependencias Playwright y Python ya preparadas del entorno. Las credenciales de fixture son efímeras, quedan en directorios privados y no se sirven por HTTP.

La preparación de assets de deployment/start.py incluye el nuevo script; su prueba solo modifica un compose temporal. No se realizó despliegue o modificación del compose real. Mantener pendientes de producción en el registro del ecosistema y revisar IMPLEMENTACION_46.md.
