# Cuatro vistas web locales

Esta configuración permite revisar las cuatro interfaces en el equipo donde se
inicia Docker. No las publica en Internet ni las instala en el portátil desde
la sesión del agente. En Windows usa Docker Desktop y ejecuta los comandos dentro
de WSL2; así las dependencias Node nativas coinciden con los contenedores Linux.
Se necesitan Node 24, Python 3.12 y los backends locales de `BACKEND/deployment`.

| Sistema | Enlace local | Estado comprobado |
| --- | --- | --- |
| SGA-CD | https://localhost:8100/login.html | Vista, login real y sesión protegida |
| Analemática | https://localhost:8101/login.html | Vista, login real y sesión del dueño |
| ERP turístico | https://localhost:8102/erp/cotizaciones | Sesión y borradores implementados; habilitación local explícita |
| Turismo | https://localhost:8103/dashboard/login | Pantalla de acceso; login backend pendiente |

**`localhost` significa el equipo que ejecuta Docker.** Los enlaces del servidor
de validación del agente no son URLs públicas accesibles desde otro computador.
Al ejecutar estos comandos en tu equipo, los mismos enlaces abren allí las vistas.
El certificado es autofirmado para `localhost` y `127.0.0.1`, con vigencia de 30 días;
no reemplaza un certificado de dominio verificado para producción.

## Arranque

Primero prepara/inicia `sgacd` y `analematica` siguiendo `BACKEND/deployment/README.md`.
Después, desde la raíz:

```bash
python -m pip install -r FRONTEND/deployment/requirements-tools.txt
npm ci --prefix FRONTEND/deployment --ignore-scripts
python FRONTEND/deployment/prepare.py
docker compose -f FRONTEND/deployment/compose.yaml up -d
```

La red externa predeterminada es `sgacd-backends_default`. Si elegiste otro nombre
de proyecto backend, configura `BACKEND_NETWORK` con su red real. En la validación
se usó `sgacd-backends-local_default`. Los contenedores usan UID/GID 1000, habitual
para el primer usuario de WSL2; ajusta `user` en Compose si tu UID/GID difiere.
No montes carpetas privadas del equipo para corregir permisos.

Para crear un dueño **solo en la base nueva local**:

```bash
python BACKEND/deployment/create_local_owner.py
```

El helper rechaza otros destinos de base y conserva dueños/contraseñas existentes.
Con un nombre de proyecto personalizado usa `--project nombre-del-proyecto`.

## Credenciales

Se guardan fuera de Git, con permisos privados:

- `private/ACCESOS-LOCALES.md`: cuatro usuarios/contraseñas distintos para la capa
  de acceso HTTPS a las vistas. El navegador los solicita antes de mostrar HTML.
- `private/LOGIN-APLICACIONES.md`: login real del dueño local, compartido por
  SGA-CD y Analemática porque usan la misma cuenta y autorización backend.

ERP y Turismo **no tienen credenciales internas funcionales validadas**. La clave
que permite ver su interfaz no inicia una sesión ERP. Sus `/api/` responden 503
hasta reparar y conectar el backend real; no se usan usuarios ni sesiones simulados.
No subas `private/`, certificados privados, `.runtime/` ni archivos `.env` a Git.
El preparador conserva claves existentes y no imprime contraseñas.

## Qué se publica

SGA-CD y Analemática sirven copias de recursos públicos permitidos, no sus carpetas
completas. Analemática mantiene los controles de autorización de la API SGA-CD;
no se activa el servidor importado con autenticación de demostración.

Los fuentes turísticos originales no incluían un manifiesto npm ni un proyecto
independiente para el fragmento ERP. El preparador crea dos proyectos de revisión
usando los recursos compartidos de Turismo y superpone los archivos ERP en su ruta
real de dashboard. Los originales siguen separados y la copia generada es descartable.
El manifiesto y lockfile de dependencias están en esta carpeta.

Estas dos vistas usan **Next en modo desarrollo**, detrás del acceso HTTPS local.
Los mocks MSW están desactivados por defecto. Se corrigieron las declaraciones
repetidas del hook ERP y un icono inválido; los importes y plazos simulados de su
pantalla inicial se sustituyeron por datos no disponibles. La vista ERP indica que
sus operaciones no están conectadas. No se validaron todas las rutas del proyecto.

## Controles y límites de seguridad

- Solo se publican puertos en `127.0.0.1`; Node, Redis y PostgreSQL no se exponen.
- HTTPS TLS 1.2/1.3; claves de acceso largas aleatorias y hashes bcrypt separados.
- Intentos y solicitudes limitados; las claves Basic no se reenvían a las API.
- Sesiones backend verificadas; visitar `/admin.html` no concede permisos.
- Contenedores sin privilegios adicionales, sin capabilities y con filesystem
  de imagen de solo lectura; los backends están en una red separada.
- CSP, bloqueo de iframes, `nosniff`, permisos del navegador limitados, directorios
  ocultos denegados y logs sin Authorization ni parámetros de URL.
- No hay claves privadas de IA en las variables públicas de navegador.

**No es una garantía contra ataques ni una aprobación de producción.** Persisten
código heredado por revisar, tokens del frontend en localStorage y dos servidores
Next de desarrollo; su CSP requiere `unsafe-eval`. Antes de exponerlos harán falta
reparar Turismo/ERP, compilaciones de producción verificadas, revisar autorización
por rol/tenant, XSS/CSRF, ciclo de sesiones, recuperación de credenciales, MFA,
copias/restauración, TLS de dominio y actualización de dependencias. No se anuncia
un sistema completo funcional mientras esos puntos sigan pendientes.

## Validación y parada

Se comprobaron HTTPS con confianza/pinning al certificado local, 401 sin acceso,
200 autenticado de las cuatro vistas, pantallas reales con Chromium, login y sesión
real en las dos aplicaciones operativas. La auditoría npm de dependencias de
producción informó cero vulnerabilidades conocidas al validar esta entrega;
esto no detecta todas las vulnerabilidades ni sustituye una revisión del código.

```bash
python -m unittest discover -s FRONTEND/deployment/tests -v
docker compose -f FRONTEND/deployment/compose.yaml ps
docker compose -f FRONTEND/deployment/compose.yaml stop
```

`prepare.py` vuelve a copiar los recursos de revisión; detén antes las vistas si
estás navegando para evitar una recarga intermedia. Las claves se conservan.

## Sesión ERP y cotizaciones: habilitación explícita

El nuevo acceso usa contraseña de Django, cookie HttpOnly y CSRF, sin JWT en
localStorage. Es independiente de la contraseña Basic de la vista y del login
antiguo de otros módulos. El flujo se verificó con cuentas generadas de prueba,
incluido Nginx HTTPS; no se suministran esas cuentas como credenciales reales.

Mantener el backend actualizado y /readyz correcto antes de habilitarlo. En su
configuración privada definir ERP_WEB_SESSION_ENABLED=1 y
CSRF_TRUSTED_ORIGINS=https://localhost:8102,https://127.0.0.1:8102. Reiniciar el
backend para cargar esos valores. Para preparar el gateway definir
SGACD_ENABLE_ERP_API=1 al ejecutar prepare.py; por defecto sigue bloqueado.
Solo pasan las rutas de sesión/cotizaciones revisadas; no se abre toda /api.
Los usuarios/empresas deben existir y tener vínculo vigente revisado; el login
no crea usuarios ni concede propiedad empresarial.

Las cuentas con TOTP cifrado completan contraseña y código mediante un desafío
vinculado a sesión y con protección antirreutilización. WebAuthn y factores no
soportados se rechazan; no se degradan a contraseña ni a otro factor. La
activación/recuperación desde UI y validación física siguen pendientes. Los otros módulos
heredados y el SSO no quedan certificados por el nuevo acceso de cotizaciones.
El build completo de Next y el despliegue propio aún requieren su validación.

Las pruebas se repiten con quotation_browser.cjs. QUOTE_GATEWAY=1 añade Nginx
HTTPS en una red Docker temporal, publicada solo en loopback y eliminada al
terminar. Si Docker vive en otro namespace, QUOTE_BIND indica la IP privada
donde el fixture Django puede escuchar; no usar una IP pública ni host networking.
El certificado autofirmado solo se acepta en el contexto aislado del navegador
de prueba; no desactiva la validación TLS de los servicios ni sustituye un
certificado de dominio productivo.

Los secretos TOTP legados requieren revisión. encrypt_mfa_secrets valida sin
escribir por defecto; --apply cifra de forma atómica con la clave privada del
backend, sin cambiar el secreto del usuario. No ejecutar sobre datos reales
sin respaldo, custodia de la clave y revisión del operador. La prueba de
navegador con QUOTE_MFA=1 usa un factor generado exclusivamente para pruebas.

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

### Comprobación estricta de proyectos completos (bloque5)

Instalar con npm ci --include=dev. build_check.py --dependencies node_modules
--output NUEVO_DIRECTORIO prepara ERP/Turismo completos en copias aisladas y
ejecuta next build --webpack, conservando errores reales. check_sources.cjs
comprueba sintaxis y avisa páginas sin export default; check_components.cjs
comprueba tipos estrictos de Button/Badge/Switch. No equivalen al build completo.
El workflow manual Full web build audit permite repetir y conservar el informe.
Los builds de este corte FALLAN por bibliotecas compartidas ausentes; no son
artefactos listos para producción. No se añadieron rutas ERP a Turismo al
resolver sus módulos reutilizados como fuentes compartidas.
Ver INTEGRACIONES/plan-maestro/BLOQUE05_BUILDS_WEB_32.md.
