# Pruebas locales de los cuatro backends

El entorno es local. No se contrató un servidor ni se publicó producción.
En Windows se recomienda Docker Desktop con WSL2 e integración con la distribución
Linux donde se clone el repositorio. Se necesitan Python 3.12 y Docker Compose v2.
Reserva al menos 20 GB libres para imágenes y compilaciones; las dependencias IA son
voluminosas. Los comandos siguientes se ejecutan desde la raíz del repositorio.

| Carpeta | Servicio Compose | Puerto local predeterminado | Configuración privada |
| --- | --- | --- | --- |
| `BACKEND/SGA-CD-BACKEND` | `sgacd` | 8000 | `.runtime/sgacd.env` |
| `BACKEND/ANALEMATICA-BACKEND` | `analematica` | 8001 | `.runtime/analematica.env` |
| `BACKEND/SGA-ERP-TUR-BAKEND` | `erp-tur` | 8002 | `.runtime/erp-tur.env` |
| `BACKEND/SGA-TUR-BAKEND` | `turismo` | 8003 | `.runtime/turismo.env` |

Cada proceso escucha en el puerto 8000 de su contenedor. Los puertos del equipo se
pueden cambiar con `SGACD_PORT`, `ANALEMATICA_PORT`, `ERP_TUR_PORT` y `TURISMO_PORT`.
La dirección predeterminada es **127.0.0.1**. PostgreSQL y Redis no publican puertos.
Este archivo Compose es una alternativa al Compose histórico de la raíz; no es un
override de aquella demo. Usa un nombre de proyecto propio para separar volúmenes.

## Preparar el entorno

```bash
python -m pip install -r BACKEND/deployment/requirements-tools.txt
python BACKEND/deployment/init_local.py
docker compose -f BACKEND/deployment/compose.yaml config --quiet
```

El generador crea claves aleatorias distintas por servicio, incluyendo RSA para los
dos Django. Guarda exclusivamente archivos privados en `.runtime/`, ignorados por
Git; no imprime claves ni sobrescribe configuraciones existentes. En Unix usa 0600.
En Windows mantén esta carpeta dentro del perfil privado del usuario y revisa sus ACL.
No borres/regeneres claves si ya hay datos cifrados o sesiones que deban conservarse.

Construye secuencialmente para reducir el consumo de disco:

```bash
docker compose -f BACKEND/deployment/compose.yaml build sgacd
docker compose -f BACKEND/deployment/compose.yaml build analematica
docker compose -f BACKEND/deployment/compose.yaml build erp-tur
```

ERP y Turismo usan la misma imagen Django, con variables, proceso, base PostgreSQL y
volumen propios. Comparten código porque el proyecto original tiene dependencias
cruzadas. Redis usa bases lógicas distintas para sus colas. No se arrancan Celery,
servicios de pago, envíos a Meta ni proveedores IA durante la preparación.
Si una red corporativa requiere una CA, el Dockerfile admite el secreto BuildKit
`proxy_ca`; consérvalo fuera del repositorio y mantén la verificación TLS activada.

## Inicializar SGA-CD en una base nueva

```bash
docker compose -f BACKEND/deployment/compose.yaml up -d --wait sgacd-db
docker compose -f BACKEND/deployment/compose.yaml run --rm --no-deps sgacd python /srv/entrypoint.py --init-db
docker compose -f BACKEND/deployment/compose.yaml up -d --wait sgacd analematica
```

`--init-db` crea las tablas declaradas en la base elegida sin borrar tablas. Úsalo
solo para una base nueva de pruebas; no sustituye migraciones de producción. Los
arranques normales no alteran esquemas (`SGACD_INIT_SCHEMA=0`, `DJANGO_MIGRATE=0`).
No se crea un usuario/contraseña por defecto. La consola corporativa mantiene su
vinculación explícita al dueño y devuelve 401 a una sesión sin autorización.

El servicio Analemática publica API, no archivos de frontend: delega `/api/*` al
SGA-CD de la red interna, conservando su autorización, errores y datos. El frontend
continúa en `FRONTEND/ANALEMATICA-FRONTEND`. `integrated_server.py` se conserva por compatibilidad
con el código importado; no es el entry point de Compose ni sustituye el login seguro.
La IA opcional sin credencial devuelve 503 cuando se solicita; no bloquea el arranque
de toda la API. No se incluyen claves de proveedor en código o imágenes.

## Estado real de los servicios turísticos

### Instalación nueva cuando no hay respaldo histórico

Existe un perfil alternativo **solo local y SQLite**: `fresh-local-v1`. Crea una
base nueva con migraciones versionadas de los modelos actuales, sin modificar la
historia antigua. Cada servicio usa directorio y claves propios. No importa ni
reconstruye información histórica. El directorio indicado debe ser nuevo:

```bash
python BACKEND/deployment/fresh_local.py --directory BACKEND/deployment/.runtime/local-erp --service erp-tur
python BACKEND/deployment/fresh_local.py --directory BACKEND/deployment/.runtime/local-turismo --service turismo
python BACKEND/deployment/tests/fresh_database_check.py --directory BACKEND/deployment/.runtime/local-erp --service erp-tur -v
python BACKEND/deployment/tests/fresh_database_check.py --directory BACKEND/deployment/.runtime/local-turismo --service turismo -v
```

Conservar íntegros los directorios privados `.runtime`, incluidas sus claves, fuera
de Git. Una copia de SQLite sin las claves no recupera por sí sola campos cifrados.
No borrar una instalación para volver a ejecutar el inicializador. Para administrar
una instalación ya creada:

```bash
python BACKEND/deployment/fresh_manage.py --directory BACKEND/deployment/.runtime/local-erp --service erp-tur createsuperuser
python BACKEND/deployment/fresh_manage.py --directory BACKEND/deployment/.runtime/local-erp --service erp-tur runserver 127.0.0.1:8002 --noreload
python BACKEND/deployment/fresh_manage.py --directory BACKEND/deployment/.runtime/local-turismo --service turismo runserver 127.0.0.1:8003 --noreload
```

No hay contraseñas predeterminadas. Solo se permite servir en loopback; no es un
despliegue público. Este perfil no cambia Compose/PostgreSQL ni activa procesos
financieros pendientes. Un esquema listo no demuestra que todos los módulos estén
terminados. Para una base histórica se mantiene el bloqueo y la reconciliación
descritos a continuación.

Los checks completos de Django pasan en una configuración aislada después de corregir imports, namespaces y dependencias opcionales. Compras, proyectos, presupuesto y reportes incompletos responden **503 autenticado**, sin activar operaciones financieras de ejemplo. Esto permite comprobar el bootstrap, pero no convierte esos módulos en funciones terminadas.

El grafo de migraciones sigue bloqueado por una dependencia inexistente de `prestadores.0001_full_reset`. No se han migrado ni validado bases de negocio, reservas o pagos. **No ejecutar `up` para anunciar cuatro servicios funcionales ni aplicar migraciones reales sin resolver ese grafo y probar restauración.**

Las pruebas de bootstrap usan `BACKEND/deployment/tests/tourism_runtime_check.py`, SQLite en memoria y claves temporales. El inventario, los hallazgos, las restricciones de permisos y el plan de dominio están en `INTEGRACIONES/turismo-erp/`. El registro de consolidación está en `INTEGRACIONES/plan-maestro/README.md`. El estado de runtime y de producción no queda certificado por los checks.

## Comprobar y detener

```bash
docker compose -f BACKEND/deployment/compose.yaml ps
docker compose -f BACKEND/deployment/compose.yaml logs --tail 80 sgacd analematica
docker compose -f BACKEND/deployment/compose.yaml stop
```

SGA-CD y Analemática exponen `/healthz`; comprueban su base y dependencia interna,
respectivamente. `stop` conserva los datos. Evita `down -v` si deben mantenerse.

ERP y Turismo también exponen `/readyz`, separado de `/healthz`: devuelve 503 si
hay historia de migración inválida, migraciones pendientes, tablas o columnas
ausentes o una base inaccesible. No aplica migraciones y no publica errores SQL.
Un 200 comprueba esos contratos de esquema, no certifica reservas, pagos ni RNT.
El estado turístico actual esperado es 503 por la historia heredada inválida.
`migration_preflight.py`, con el entorno Django configurado, inventaría todas las
dependencias ausentes sin abrir una base. No usar `--fake` para cambiar ese estado.

Se validaron construcción desde fuente de SGA-CD, imagen/gateway Analemática,
PostgreSQL aislado, HTTP de salud y rechazo de sesión sin autorización en el servidor
de pruebas del agente, usando puertos 28000 y 28001 para no interferir con las demos.
No se instaló Docker ni se inició un servicio en el portátil del usuario.
Pruebas: 32 de regresión de workspace, seis del conector/configuración local y dos
sobre la ausencia de proveedor IA. El estado de los contenedores turísticos es un
bloqueo funcional documentado, no una validación exitosa del sistema completo.

## Sesión web ERP (opt-in)

ERP_WEB_SESSION_ENABLED=1 habilita /api/v1/erp-session/, login/ y logout/.
Las rutas de cotización aceptan la sesión marcada, con CSRF obligatorio en
escrituras; conservan el JWT de dominio para clientes existentes. Las cookies
se separan por servicio, son HttpOnly, SameSite=Strict y de ámbito /api/.
En turismo_settings son Secure. Para una instalación fresh-local detrás de
HTTPS, SGACD_FRESH_LOCAL_HTTPS=1 activa Secure; el valor predeterminado sigue
siendo HTTP de loopback para pruebas. Configurar CSRF_TRUSTED_ORIGINS con el
origen exacto del frontend. No habilitarlo sobre un esquema incompleto.

La contraseña no crea empresas ni valida RNT/DIAN. El vínculo empresarial se
revisa por un operador independiente; fresh_manage.py admite review_company_link
con validación sin escritura por defecto. El ingreso TOTP ya verifica su segundo factor. Activación/recuperación,
WebAuthn, identidad externa y SSO siguen como criterios separados de aceptación.

El nuevo ingreso TOTP persiste intentos, caducidad y último contador utilizado.
Solo completa la sesión después del código; no sustituye autorizaciones del
motor ni firmas de billetera. MFA_ADAPTER cifra nuevas altas con
FIELD_ENCRYPTION_KEY; conservar y respaldar esa clave fuera de Git. El comando
encrypt_mfa_secrets se incluye en fresh_manage.py, con simulación por defecto
y --apply explícito. No reiniciar contadores para evitar bloqueos; gestionar
cambios de reloj/política y recuperación mediante revisión de identidad.

### Primera activación TOTP (corte 20)

El espacio de cotizaciones permite activar un primer factor con sesión real,
contraseña repetida y confirmación de código. Requiere habilitar explícitamente
ERP_TOTP_ENROLLMENT_ENABLED=1 además del acceso web ERP. Nunca reemplaza factores
existentes. La clave manual se entrega una vez, no se almacena en localStorage
y no se envía a generadores QR externos. Cancelar no elimina autenticadores.
Se requiere migración fresh-local turismo.0005; no aplicar sobre bases heredadas
sin revisar previamente su ruta de migración y respaldo.
Recuperación, validación física, custodia de claves y purga de propuestas
abandonadas siguen pendientes. Ver INTEGRACIONES/plan-maestro/ACTIVACION_TOTP_20.md.

### Limpieza de propuestas TOTP abandonadas

`purge_totp_enrollments` está disponible en `fresh_manage.py`. Por defecto
solo cuenta un lote elegible y muestra `ELIGIBLE_NO_WRITE`; `--apply` elimina
exclusivamente `sealed_secret` de propuestas vencidas o consumidas. No elimina
filas, factores activos, contadores ni sesiones. El lote predeterminado es 500;
`--batch-size` admite entre 1 y 10000. Repetir hasta `ERASED 0` para completar
el conjunto elegible. Cada ejecución revalida la condición en SQL antes de escribir.

Ejemplo para una instalación local seleccionada explícitamente:

```bash
python BACKEND/deployment/fresh_manage.py --directory /ruta/instalacion-local --service erp-tur purge_totp_enrollments
python BACKEND/deployment/fresh_manage.py --directory /ruta/instalacion-local --service erp-tur purge_totp_enrollments --apply --batch-size 500
```

La tarea debe programarse y supervisarse en el entorno definitivo. Este trabajo
no instala cron ni ejecuta limpieza sobre datos de usuarios. No necesita descifrar
claves; los registros activos y las propuestas aún válidas quedan fuera del filtro.

### Acceso con códigos de recuperación previamente emitidos

ERP_RECOVERY_CODES_ENABLED=1 habilita explícitamente el uso de códigos de
allauth previamente emitidos y cifrados. Requiere también acceso web ERP.
Tras validar la contraseña, el desafío ofrece alternar entre TOTP y un código
de recuperación. POST /api/v1/erp-session/recovery/ conserva el desafío,
CSRF, sesión vinculada, caducidad e intentos compartidos con TOTP. Un código
correcto se consume dentro de la transacción antes de completar la sesión.
No elimina ni reemplaza TOTP. Consumirlo actualiza la versión de factores,
por lo que otras sesiones ERP deben volver a autenticarse.

Solo se admite el formato de semilla cifrada; no hay fallback de códigos
legados sin revisar. Política acotada a 8–32 dígitos y 1–100 códigos.
La función está apagada por defecto. No se emitieron códigos de usuarios reales.
Emisión/rotación segura desde UI, recuperación si se pierden ambos factores y
recuperación de contraseña por correo verificado siguen pendientes. No son
rutas de recuperación de fondos ni autorizaciones del motor de control.

### Emisión/rotación de códigos desde la interfaz ERP

`ERP_RECOVERY_ISSUANCE_ENABLED=1`, junto con el acceso ERP y los códigos de
recuperación, habilita POST `/api/v1/erp-session/recovery/issue/`.
Exige sesión MFA personal, CSRF, contraseña actual y TOTP fresco. El código
usado al ingresar no puede reutilizarse para emitir. Los fallos comparten
el bloqueo persistente TOTP. Se rechazan políticas débiles y factores no
compatibles; no hay sustitución de WebAuthn por este flujo.

Se cifra una nueva semilla, se invalidan los códigos anteriores y se rota la
sesión. Los códigos nuevos se devuelven una sola vez con no-store; no existe
GET para recuperarlos. La UI solicita confirmar la invalidación, limpia los
campos y mantiene los códigos solo en memoria, ocultándolos al cambiar de
pestaña, al confirmarlos guardados o después de un minuto. Esto no impide
capturas por parte del usuario ni garantiza borrado físico de memoria JavaScript.

Una respuesta perdida puede corresponder a una emisión completada. No se
reenvían los códigos ni se realiza reintento automático; requiere revisar el
acceso TOTP y emitir de nuevo con otra prueba fresca. Los registros históricos
de autenticadores activos se conservan; únicamente se reemplaza la semilla
propia de recuperación después de las pruebas requeridas.

Faltan auditoría y notificaciones de emisión/uso, prueba concurrente PostgreSQL,
validación física y recuperación cuando se pierden TOTP y códigos. La función
permanece deshabilitada por defecto y no se activó para cuentas reales.

### Concurrencia PostgreSQL MFA y recuperación

`BACKEND/tests/mfa_postgres_check.py` comprueba cinco escenarios de consumo/emisión
con conexiones independientes, sin caché de protección contra reutilización.
Incluye recuperación con mismo/diferente desafío y emisión con TOTP compartido.
Usa PostgreSQL temporal con esquema mínimo; no conecta bases del proyecto.
No sustituye migración integral ni carga con procesos WSGI separados.
Ver INTEGRACIONES/plan-maestro/CONCURRENCIA_RECUPERACION_24.md.

### Auditoría e historial de recuperación

La migración fresh-local turismo.0006_erpsecurityevent crea ErpSecurityEvent.
Emisión, regeneración y uso aceptados generan eventos en la misma transacción
que cambia el estado MFA. Si la auditoría falla, el cambio SQL se revierte y no
se completa el acceso. Una prueba TOTP ya marcada en caché puede requerir esperar
al siguiente código incluso tras la reversión SQL; no se vacía esa protección.

Solo se registran UUID del evento, referencia interna de actor/factor/desafío,
tipo y fecha; no códigos, contraseñas, semillas, cookies ni payloads. No hay FK
con borrado en cascada. El modelo bloquea edición/borrado mediante las operaciones
normales de Django; esto no protege frente a SQL directo o un administrador de DB.
Requiere permisos SQL y política de retención para producción.

GET /api/v1/erp-session/security-events/ devuelve únicamente id, tipo y fecha
de los últimos 20 eventos de la cuenta autenticada, sin caché. El componente
Historial de recuperación los consulta a petición del usuario. No permite pedir
el historial de otro actor. No incluye intentos fallidos ni todos los accesos.
Notificaciones, exportación a SOC, retención y validación operativa siguen pendientes.
No se enviaron correos o mensajes ni se conectó un servicio externo.

### Validación con procesos Linux separados

El contrato PostgreSQL MFA incluye cinco escenarios adicionales con dos procesos
Linux por escenario, conexiones ORM abiertas después de fork y caché de
reutilización desactivada. Comprueba consumo/contador únicos, auditoría y
consistencia del conjunto de códigos emitido. Sigue requiriendo pruebas con
trabajadores HTTP reales, carga sostenida y esquema integral.
Ver INTEGRACIONES/plan-maestro/MULTIPROCESO_MFA_26.md.

### Contratos HTTP con dos procesos Django

La suite PostgreSQL ahora incluye mfa_http_contract.py: contraseña, cookies,
CSRF y carreras HTTP de TOTP, recuperación y emisión contra dos procesos.
Comprueba que ambos lean sesiones SQL y acepten una sola prueba concurrente.
Usa HTTP local, esquema mínimo y reloj sintético; no acredita balanceador,
TLS o carga sostenida. Procesos y contenedor se eliminan al terminar.
Ver INTEGRACIONES/plan-maestro/HTTP_MULTITRABAJADOR_27.md.

### Disponibilidad y retenciones de cupos (bloque2)

La migración fresh-local turismo.0007_availabilityhold habilita el almacenamiento
de retenciones privadas. ERP_CAPACITY_HOLDS_ENABLED=1 permite las rutas POST
service-availability/, capacity-holds/ y capacity-holds/{id}/release/ en el
último módulo comercial. La creación exige clave UUID de idempotencia, fechas
con zona y cantidad; caduca en10 minutos, sin reserva confirmada ni pago.
Se requiere titular y vínculo empresarial vigente. Las reservas históricas
coincidentes deben conciliarse; no se infieren sus unidades. No habilitar este
flujo con escritores heredados que omitan el bloqueo de capacidad.
Ver INTEGRACIONES/plan-maestro/BLOQUE02_CUPOS_29.md para contrato y pendientes.

### Ámbito empresarial común (bloque3)

CRM y catálogo seleccionan TourismProvider mediante company_scope.owned_provider:
titular activo, empresa activa, query provider_id o contexto/encabezados coherentes.
Con varias empresas debe seleccionarse una explícitamente. No se concede acceso
por rol de superusuario ni se interpreta el ID como core Tenant. Catálogo no
acepta traslado de provider y filtra políticas de cancelación. Ambos módulos
exigen JWT o cookie ERP con versión MFA válida; cookies mantienen CSRF.
GET comercial/company-scopes/ lista empresas propias, sin SSO ni privilegios
financieros. No hay migración ni delegaciones nuevas a empleados.
Ver INTEGRACIONES/plan-maestro/BLOQUE03_AMBITO_EMPRESARIAL_30.md.

### Recuperación por correo verificado (bloque4)

Se habilita explícitamente con ERP_PASSWORD_RESET_ENABLED=1,
ERP_PASSWORD_RESET_MAIL_READY=1 y ERP_PASSWORD_RESET_URL apuntando a la pantalla
ERP de cotizaciones en HTTPS. Requiere proveedor/remitente y correo de usuario
verificados; no usa el Host del cliente. Los backends console/filebased/dummy
se rechazan. Solicitud y confirmación exigen CSRF y responden no-store.
El enlace vence en15 minutos, usa fragmento de URL y conserva MFA. No crea
sesión ni elimina factores. La migración fresh-local turismo.0008 incorpora el
evento de auditoría password_reset. No habilitado ni probado con correo real.
Cola de envío, caché compartida y monitoreo de entrega requieren validación
productiva. WebAuthn permanece pendiente de integración; no hay bypass.
Ver INTEGRACIONES/plan-maestro/BLOQUE04_RECUPERACION_31.md.


## Verificación consolidada y reversión

La herramienta `BACKEND/INTEGRACIONES/operacion/verify_local.py` ejecuta perfiles aislados
`core`, `fresh`, `browser`, `devices`, `postgres` y `web-build`, con informes privados
y comprobación de hashes. Nunca despliega, modifica Git ni selecciona bases existentes.
Los perfiles incompletos/omitidos devuelven salida 2, aunque otros grupos pasen.
El manual `INTEGRACIONES/operacion/README.md` incluye diagnóstico y reversión
manual compatible con esquema y claves; no autoriza borrado de volúmenes ni
migraciones inversas automáticas. Para instalación desde cero y restauración
se usan directorios y bases nuevas, manteniendo intactos los originales.

Para copias SQLite locales cifradas y restauración hacia una base nueva, consultar
`INTEGRACIONES/operacion/RESPALDOS.md` y `BACKEND/deployment/encrypted_backup.py`.
La herramienta no incluye las claves internas del aplicativo, no sobrescribe
destinos y no sustituye una solución de respaldo PostgreSQL/volúmenes productivos.
