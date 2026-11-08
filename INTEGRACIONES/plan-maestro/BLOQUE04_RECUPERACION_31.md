# Bloque 4 — contraseña por correo verificado

Se implementó recuperación de contraseña ERP, conservando MFA. La integración
WebAuthn y la recuperación con pérdida de ambos factores siguen pendientes;
no se declara completo el bloque4.

## Flujo implementado

POST /api/v1/erp-session/password-reset/request/ recibe email. Para direcciones
con formato válido responde202 con el mismo mensaje, exista o no una cuenta
habilitada. Solo envía a una cuenta personal activa con contraseña utilizable
y una única coincidencia de correo verificado de allauth que sea además el
correo actual del usuario. No devuelve el enlace ni identifica al destinatario.
El correo debe verificarse por un flujo confiable; este código no marca correos
como verificados ni crea cuentas.

El token está firmado, vence como máximo a los15 minutos y cambia con la
contraseña, último ingreso, correo o versión de factores. La confirmación bloquea
al usuario en SQL; solo una solicitud puede consumir el enlace al cambiar la
contraseña. Exige12 caracteres, complejidad razonable y diferencia de la contraseña
anterior; no elimina TOTP, códigos de recuperación ni WebAuthn existentes.

POST /api/v1/erp-session/password-reset/confirm/ exige uid, token y password,
CSRF y enlace válido. No inicia sesión automáticamente. Las sesiones anteriores
se invalidan por el hash de contraseña de Django y el siguiente ingreso conserva
el segundo factor. password_reset se audita en la misma transacción; si la
auditoría falla, se revierte el cambio. El historial privado muestra el evento.
Las vistas marcan parámetros y variables sensibles para ocultarlos en reportes
de excepciones; no se imprimen tokens ni contraseñas en logs del flujo.

El enlace usa fragmento de URL; la interfaz lo lee al abrir o cambiar de enlace
y lo retira de la barra sin reenviarlo al servidor como query. Conserva el token
solo en memoria mientras se usa; nunca en localStorage. Limpia contraseñas al
enviar, cambiar de pestaña o iniciar sesión. Mantiene azul metalizado, celeste
y blanco, incluida vista móvil390px sin desbordamiento.

## Activación explícita

ERP_PASSWORD_RESET_ENABLED=1, ERP_PASSWORD_RESET_MAIL_READY=1 y
ERP_PASSWORD_RESET_URL=https://dominio-controlado/ruta-de-la-pantalla.
La URL se toma exclusivamente de configuración; no de Host, Referer o parámetros
de retorno. Se rechazan credenciales, query/fragmento en la URL y backends de
correo console, filebased y dummy. HTTP local solo se usa por configuración
explícita del arnés aislado, no por defecto en despliegue.

El entorno real debe tener proveedor y remitente verificados, caché compartida,
monitoreo de entrega y límites del ingreso revisados. El backend aplica5 intentos
por minuto y un cooldown de5 minutos por dirección mediante clave HMAC de caché.
La respuesta pública es uniforme; el envío síncrono no garantiza tiempo constante
ni elimina todos los canales de inferencia. Cola de entrega y observabilidad
siguen pendientes. Errores del proveedor no cambian la respuesta pública.

Las funciones permanecen apagadas por defecto. No se enviaron correos reales.
La migración fresh-local turismo.0008_alter_erpsecurityevent_kind solo incorpora
el nuevo tipo de evento; aplicada en dos bases temporales, sin tocar clientes.

## Evidencia

-10 pruebas de recuperación aprobadas: respuesta uniforme, correo no verificado,
inactividad/agentes, vencimiento, uso único, cambio de factores, CSRF, cooldown,
política de contraseña, configuración insegura, auditoría y sesiones previas.
-53 regresiones de sesión/MFA,13 de ámbito empresarial y5 del gateway aprobadas:
81 pruebas en estos conjuntos, sin contar suites históricas no repetidas.
-26 comprobaciones HTTPS en Chromium/React/Django/Nginx, con correo simulado en
memoria: desconocido/validado, enlace, contraseña débil, confirmación, replay,
MFA posterior, cotizaciones y recuperación móvil. TypeScript estricto correcto.
-PostgreSQL: dos procesos y un enlace producen un cambio, un rechazo y un evento;
MFA permanece idéntico. Se conservaron16 escenarios anteriores y la regresión
de restauración, sobre esquema sintético mínimo.
-git diff --check correcto. Ver password-recovery-evidence-31.json y captura
  evidencias/password-recovery-erp.png, sin secretos.

## WebAuthn: revisión y pendientes

La librería allauth/fido2 instalada contiene los flujos de registro y autenticación.
El ingreso ERP actual continúa rechazando factores WebAuthn no integrados y
conserva esos factores al cambiar la contraseña. No se habilitó el modo de origen
inseguro ni se sustituyeron passkeys por una contraseña.

Falta integrar alta y verificación con challenge de un uso, RP ID y origen HTTPS
controlados, verificación de usuario, versión de credenciales, gestión segura de
revocación y UI navegador. Se requieren pruebas con autenticador virtual y luego
con dispositivos reales. La validación local virtual no certifica protección del
hardware ni la custodia de claves de la billetera.

También faltan recuperación de ambos factores con identidad verificada, entrega
real de correo, prueba operativa de emisor/dominio y cola/notificaciones seguras.
Sin commit, push, mensajes a terceros ni publicación productiva.
