# Ingreso ERP con segundo factor TOTP

Este corte implementa el ingreso de cuentas que ya tienen un factor TOTP
registrado. No declara terminado MFA integral, el plan maestro ni producción.

## Flujo implementado

1. La contraseña se valida con Django, pero una cuenta TOTP recibe 202 y queda
   anónima. El navegador obtiene un desafío vinculado a su sesión y nuevo CSRF.
2. El desafío vence en dos minutos, admite como máximo cinco intentos y conserva
   la versión de la contraseña y del enrolamiento. Un cambio invalida el desafío.
3. Un código correcto completa la sesión y rota sus identificadores. Un desafío
   consumido no se puede volver a utilizar ni trasladar a otra sesión.
4. El contador TOTP aceptado se persiste en SQL. Vaciar la caché no permite
   reutilizarlo. Cinco fallos bloquean el factor durante cinco minutos, incluso
   solicitando otro desafío con la contraseña correcta.
5. El flujo conserva CSRF, cookies HttpOnly/Secure/SameSite Strict y no-store.
   Se probó con códigos de seis y ocho dígitos. No se aceptan bypasses de prueba.
6. Si existe WebAuthn u otro factor no soportado, no se degrada el acceso a TOTP.
   Recuperación, WebAuthn y activación de factores desde la interfaz siguen pendientes.

La tolerancia del reloj está acotada. Deben verificarse sincronización y política
de periodo del servidor antes de producción; los cambios de política requieren
revisión del enrolamiento, no reiniciar contadores para saltar la protección.
La prueba de navegador genera códigos estándar con Node y los valida en Python;
no acredita uso de una aplicación autenticadora en un teléfono físico.

## Cifrado y compatibilidad

Se configura MFA_ADAPTER, la opción real de allauth, con EncryptedMFAAdapter.
El adaptador predeterminado de la librería no cifra los secretos. Los nuevos
registros usan Fernet con la clave privada FIELD_ENCRYPTION_KEY del entorno y
prefijo de versión. No se incluyen claves ni códigos reales en Git o en logs.
La custodia, respaldo y rotación de esa clave quedan sujetos al procedimiento
productivo; perderla impide descifrar los factores.

Para no alterar otros flujos históricos, el adaptador mantiene lectura de
registros antiguos. El nuevo ingreso ERP exige un secreto cifrado y rechaza
registros legados sin revisar. encrypt_mfa_secrets audita por defecto sin escribir;
--apply cifra en el lugar, sin cambiar el secreto del autenticador. La operación
es atómica y repetible: un registro inválido revierte toda la conversión.
No se ejecutó sobre datos de trabajo ni de clientes; únicamente se probó en
fixtures aislados. No elimina ni vuelve a enrolar factores automáticamente.

## Persistencia y rutas

Nueva migración fresh-local turismo.0004_erptotpusage_erploginchallenge:
ErpLoginChallenge y ErpTotpUsage. La historia heredada no se reescribe.
POST /api/v1/erp-session/mfa/ completa el desafío con CSRF obligatorio.
El gateway permite esa ruta; los endpoints financieros no revisados siguen
bloqueados. El login y gateway conservan su habilitación explícita, apagada por defecto.

La pantalla conserva azul metalizado, azul claro y texto blanco. La contraseña
se limpia al enviar y el código al verificar; ninguno se guarda en localStorage.
El desafío puede recuperarse al recargar mientras su sesión y vigencia sean válidas.
Cancelar la verificación elimina su vinculación utilizable con el navegador.

## Verificación

- 25 pruebas de sesión/MFA: códigos válidos/incorrectos/vencidos, desafío de otro
  navegador, CSRF, modificación de contraseña/factor, caché vaciada, bloqueo y
  recuperación del plazo, ocho dígitos y conversión explícita/atómica de secretos.
- 27 regresiones de identidad y cotizaciones.
- ERP migrado:11 pruebas correctas, incluido ingreso real con contraseña/TOTP.
- Turismo migrado:10 correctas y1 omitida porque no expone las rutas de sesión ERP.
- Total:73 pruebas correctas,1 omitida; no se cuenta la omitida como aprobación.
- Navegador HTTPS:19 comprobaciones con factor TOTP y15 del acceso sin factor,
  usando React, Django WSGI y Nginx reales con cuentas generadas de prueba.
- Ambas bases temporales:169 migraciones,591 tablas, sin violaciones de FK.

Los datos funcionales de las comprobaciones de bases se revierten al terminar.
No se migraron bases existentes del proyecto ni se publicaron servicios reales.
Se verificaron además dos escenarios del contador MFA con conexiones concurrentes
en PostgreSQL y la caché de replay desactivada: sesiones distintas/mismo código
y dos solicitudes/mismo desafío. Cada escenario aceptó una sola verificación.
Se crearon solo las tablas declaradas necesarias para este contrato, sin migrar
todo el producto a PostgreSQL. No certifica múltiples procesos, carga ni los
demás módulos; esas pruebas siguen pendientes.

Ver mfa-evidence-19.json y evidencias/mfa-erp.png.

## Relación con las autorizaciones del motor y de la billetera

Contraseña más TOTP verifica identidad. No sustituye las dos autorizaciones
separadas del administrador para acciones del motor ni las firmas de dispositivo
exigidas por la billetera. No habilita cobros, campañas ni control de equipos.

## Pendientes expresos

Activación y recuperación seguras desde UI, WebAuthn y dispositivos reales,
carga y concurrencia de los demás módulos, custodia/rotación de claves, auditoría independiente,
SSO entre productos, build completo y los demás módulos del plan maestro.
Los cambios permanecen locales, sin commit ni publicación.
