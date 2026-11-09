# Implementación 46 · Analemática consulta el ledger compartido del ERP

**Avance global: 38,89 % (28/72 hitos).** Se cierra un tramo funcional de lectura corporativa que antes estaba desconectado: interfaz Analemática, API FastAPI/SQLAlchemy, vínculo revisado y API Django del ERP. No se acredita escritura corporativa, SSO completo o aceptación productiva. ACC-005 ya disponía de dos hitos parciales; ampliar su integración no añade puntos artificiales.

## Resultado visible

La sección contable de la consola de Analemática ahora consulta balance de prueba y rentabilidad del libro mayor compartido, con corte/intervalo explícitos, moneda, importes exactos y cuentas reales del reporte. No recalcula el ledger en otro motor ni utiliza telemetría de asistentes como estados financieros.

El recorrido probado es: Chromium → API corporativa FastAPI → HTTP real → API Django autenticada del ERP → ReportsEngine compartido. Los reportes corporativos y los consultados directamente en el ERP coinciden. La prueba usa bases/identidades desechables y movimientos contables generados por servicios reales; no son respuestas JSON fijas del navegador.

Se conservan la navegación y la paleta azul/azul claro/blanco. La tabla permite desplazamiento horizontal cuando es necesario y no parte los importes decimales. Los cambios de consulta, cierre/evento de sesión, visibilidad y navegación restaurada limpian resultados; una respuesta tardía no se aplica tras cambiar token/contexto. Se eliminó el texto inicial/fallback CERTIFICADO INMUTABLE del indicador de auditoría, porque la telemetría de sistema no lo demuestra.

## Identidad: tres comprobaciones independientes

1. Dueño corporativo activo y vigente en CorporateOwner, con autorización existente consultada en DB; no basta un rol admin ni claims antiguos.
2. Vínculo CorporateLedgerBinding revisado explícitamente: dueño SQL, actor Django, prestador y Tenant reales, evidencia y plazo máximo de treinta días. No se equiparan IDs entre almacenes ni se elige la primera empresa disponible. Un operador autorizado distinto del titular realiza esa revisión; no existe endpoint público de provisión o sobrescritura.
3. Sesión ERP vigente y perteneciente al titular contable enlazado. Solo se retransmite la cookie HttpOnly sgacd_erp_tur_session al origen fijado del ledger, nunca el JWT corporativo. Se conservan los controles MFA/agente/sesión del ERP; no se añadió login alternativo, emisión de tokens o bypass de factores.

El ERP expone identidad-contable bajo su viewset privado, devuelve actor/prestador/empresa del contexto verificado y conserva no-store. El puente comprueba los tres identificadores antes de pedir un reporte. Después vuelve a validar dueño/vínculo/revisor en una transacción SQL independiente para no reutilizar la caché de identidad o snapshot inicial. Una revocación o cambio de rol durante la consulta descarta el resultado.

## API y límites de transporte

`GET /api/v1/workspace/corporate/accounting/report?report=trial_balance&until=AAAA-MM-DD`

Para rentabilidad: report=profitability, since y until; intervalo máximo de 366 días. No acepta tenant_id, provider_id, URL o herramientas arbitrarias. Solo invoca dos rutas GET fijas. Comprueba empresa, corte y strings monetarios del reporte. No expone escritura contable o pagos.

Origen definido exclusivamente por CORPORATE_LEDGER_ORIGIN del servidor: HTTPS, o HTTP solo loopback local. Rechaza credenciales en URL, ruta, query, fragmentos y puertos inválidos. No sigue redirecciones ni usa proxies implícitos del entorno. Cada RPC tiene timeout, respuesta JSON acotada a 1 MiB y sin codificación comprimida; errores del backend no se reflejan íntegros al usuario. Respuestas y errores controlados son privados/no-store y varían por Cookie/Authorization.

No se guardan contraseñas, tokens o cookies en el vínculo. El JWT corporativo sigue usando el flujo existente de la consola; no se afirma haber eliminado su almacenamiento previo en JavaScript.

## Verificación

- **235 métodos Python aprobados** en el perfil contable ampliado. Incluye dos nuevos de identidad ERP y diecinueve del puente/provisión/empaquetado: dueño exclusivo, sesión adicional, campos prohibidos, revisión/dry-run, esquema ausente, expiración/revocación, rol revocado durante RPC, actor/empresa incorrectos, redirects, importes float, respuesta excesiva y paridad entre APIs reales.
- **12 comprobaciones integradas corporativas Chromium → ambos backends reales**. En el dataset aislado Analemática muestra balance 15.00 COP/15.00 COP y resultado 10.00 COP, coincidentes con ERP. Se verifican tabla, pérdida de sesión, limpieza, acceso anónimo, no-store, paleta y viewport móvil de 390 px.
- Regresión del panel ERP sintético: 15 comprobaciones aprobadas. Cuatro pruebas corporativas existentes de configuración/CRM/consentimiento también pasaron. Los 14 tests del runner siguen aprobados.
- Nueva prueba de staging confirma que js/accounting-ledger.js se copia en la entrega pública, conserva backend/web/redes y crea respaldo del compose en una carpeta desechable. No se inicia Docker ni se despliega con esa prueba.

Evidencia: `evidencias/implementacion-46.json`; captura privada local `/tmp/sgacd-analematica-contabilidad-98.png`. El manifiesto incluye ahora servicios corporativos, herramientas y despliegue Analemática, evitando excluir el código del puente. Fuente estable durante el perfil contable final. No se repitió PostgreSQL: el nuevo vínculo SQLAlchemy se cualificó con SQLite; queda pendiente su despliegue/roles/isolation reales.

## Activación y alcance pendiente

Véase OPERACION_PUENTE_CORPORATIVO.md. El puente no crea empresas, prestadores, titulares o credenciales reales. Hasta que existan esquema, origen y vínculo legítimos, falla cerrado; no se han provisionado registros productivos. El gateway corporativo copia ahora el script nuevo, pero no se ejecutó su despliegue ni CI remoto.

Faltan permisos de escritura corporativa y sus aprobaciones/recibos idempotentes, ciclo de renovación/recuperación del vínculo sin borrar historia, despliegue PostgreSQL y privilegios reales, origen/CA/TLS/red/proxy, carga y más escenarios de varias pestañas. Los dominios deben compartir la instalación/gateway adecuado para la cookie ERP; no se ensancha su dominio o SameSite automáticamente. No se promete revocación instantánea de copias ya descargadas.

El vínculo y su evidencia son una revisión administrativa, no una firma independiente ni una comprobación jurídica automatizada. No es SSO global. Compartir estos dos reportes no completa DIAN, conciliación bancaria, nómina, sostenibilidad o los otros pools. El ledger existente conserva su política de lectura/replica; no se promete un snapshot atómico común entre reportes separados.

Todos los cambios permanecen locales: sin datos reales modificados, pagos, commit, push o actualización de main.
