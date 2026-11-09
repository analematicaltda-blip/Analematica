# Implementación62 · API BYOS independiente y paquetes versionados en PostgreSQL

**Avance global: 58,33 % (42/72), sin nuevos créditos.** Amplía ACC-011, ya acreditada. H10 pasa a ejecución: **4 paquetes verificados localmente, 13 en ejecución y 3 pendientes**, aceptación completa0/24. No se declara completado el plan de20 hitos.

## Cambio sustancial

Se incorporó un almacén de paquetes cifrados versionados en una base PostgreSQL explícita del cliente y una API independiente de la del ERP. El servicio no recibe KEK ni contraseña del documento. El cliente realiza la carga directamente al origen HTTPS provisionado; el proveedor no actúa como proxy de documentos o credenciales BYOS.

La tabla de versiones conserva contexto, revisión, parent digest, digest y bytes opacos. La versión inicial debe ser1 y una sucesora debe enlazar la cabecera anterior. Los reintentos exactos se recuperan y un contenido diferente en una versión existente se rechaza. Las escrituras se serializan por empresa con advisory lock transaccional, sin exigir UPDATE sobre el vínculo.

Se verifican los bytes insertados antes de hacer commit: la prueba de un trigger que cambia bytes revierte toda la inserción. Guardas ausentes bloquean el acceso sin reparación automática. Lectura histórica y última versión preservan los archivos anteriores; no se actualizan, eliminan ni truncan documentos a través de la API.

## API y aislamiento

La API exige un token opaco temporal del cliente con formato `byos_…`, hash privado, empresa, permisos read/append, vencimiento con zona y máximo24 horas, y orígenes explícitos. Relee el grant para aplicar revocación/cambios antes de atender la operación SQL. CORS no habilita credenciales/cookies y la API no acepta destinos de DB o empresa elegidos por el solicitante.

El cliente rechaza JWT del ERP por formato antes de transmitirlos y omite cookies/referrer/redirecciones. Rechaza campos en claro o ajenos al paquete antes de cualquier petición. El servidor también exige JSON sin claves duplicadas, sin no-finitos, sin compresión y dentro del límite1.500.000 bytes.

La configuración y migración son explícitas, con archivos privados. El arranque no conecta ni inicializa la base ante solicitudes sin autorización. El store rechaza bases que contienen el ledger del proveedor. El rol de prueba mínimo solo puede leer el vínculo e insertar/leer paquetes; no necesita acceso a los sobres legados.

## Paneles y ruta probada

Los paneles ERP y Analemática incorporan los mismos controles de carga y recuperación BYOS. Sin un perfil público de origen de cliente aprobado, permanecen deshabilitados; no hay URL libre ni fallback al backend del proveedor. Los tokens se introducen en memoria y no se guardan en cookies/localStorage. Recuperar exige además la contraseña local para autenticar/descifrar antes de mostrar texto.

La prueba integrada ejecuta Chromium → HTTPS loopback → API independiente → PostgreSQL separado con rol restringido → recuperación → autenticación cliente. Comprueba carga real, reintento, rotación versión2, versión histórica, competidor rechazado y separación entre token BYOS/JWT. La prueba no usa una base en memoria para este recorrido.

Los paneles existentes se verificaron con la configuración ausente y bloqueo de controles. Su despliegue provisionado con una API real del cliente, identidades, permisos y TLS reales aún necesita aceptación; no se afirma un recorrido productivo de ambos paneles contra un destino legítimo a partir de la prueba aislada del conector.

## Evidencia y operación

[Operación del servicio](OPERACION_BYOS_PAQUETES.md) contiene configuración, migración, rol mínimo, rutas, token y perfil público. [Evidencia62](evidencias/implementacion-62.json) consolida regresión, PostgreSQL, HTTPS/navegador y restauración.

El fixture usa certificado loopback efímero y confianza de certificado deshabilitada solo en su contexto de pruebas. Esto comprueba el protocolo HTTPS local, **no cualifica confianza TLS de producción**. El código cliente de producción usa la validación TLS normal del navegador y no ofrece esa excepción.

## Pendientes

- Propiedad/consentimiento, dominio/certificados TLS, conexión DB segura, firewall, grants/roles, revocación, retención, RPO/RTO y medios de restauración reales del cliente.
- Provisionar perfiles aprobados en los despliegues y probar ambos paneles con los destinos/credenciales legítimos. No hay destinos reales configurados por defecto.
- El acuse valida forma/digest/secuencia, no HMAC/GCM ni propiedad. Se mantienen `authenticated_ciphertext_verified=false`, `ownership_independently_verified=false`, `fiscal_accepted=false` y `ledger_written=false`.
- Cualificar bloqueo/timeout, pérdida de respuesta tras commit, escrituras privilegiadas/directas fuera del servicio y disponibilidad ante grants comprometidos. Las restricciones no equivalen a WORM o una prueba pública de auditoría.
- Completar conectores alternativos/OAuth si se requieren, administración de múltiples grants, cuotas, catálogo, retención y política de retirada. No se autoriza ningún pago ni documento fiscal por almacenarlo.

No se hicieron commits, push, cambios en main, despliegues externos, pagos ni solicitudes DIAN/bancarias. Todas las bases, roles, tokens, certificados y documentos de prueba son desechables y sintéticos.

## Verificación final ejecutada

- **452 pruebas Python aprobadas**, incluidas15 nuevas de estructura/API, con fuentes estables.
- **52 escenarios PostgreSQL aprobados**, cuatro nuevos: rol mínimo, cadena/recuperación, reintento simultáneo y versión competidora. Se probó además reversión de una inserción cuyos bytes altera un trigger y restauración integral del almacén de paquetes junto con sus guardas.
- **412 comprobaciones de paneles/SDK en Chromium** más **12 del navegador HTTPS conectado a PostgreSQL real**:424 en conjunto. El segundo grupo usa el conector en una página de fixture; no se presenta como un panel productivo provisionado.
- TypeScript estricto de cuatro componentes sin errores; runtime SDK reproducible y pip check comprobados. Sin acreditar build Next completo.
- Una ejecución combinada anterior agotó el límite de la suite corporativa durante concurrencia. La repetición limpia `/tmp/sgacd-byos-62-complete` completó las33 pruebas corporativas y el conjunto contable/PostgreSQL; hashes y coincidencia de fuentes actuales verificados.
- Siete pruebas del porcentaje y documento canónico de pendientes de billetera comprobados. No hay aceptación física, legal, de proveedor o productiva por estos datos sintéticos.
