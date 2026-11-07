# Pool 02 · Autorizaciones vinculadas a dispositivo

Estado: **primera implementación del protocolo, no activación productiva**.
Incluye servidor Django y bibliotecas Android/iOS para firmar cada paso. Hay un verificador Android estricto de cadena/política, todavía sin raíces reales
configuradas ni pruebas de teléfonos genuinos;
por tanto, el alta real permanece cerrada y no se certifica biometría remota.

## Dos autorizaciones del mismo solicitante y dispositivo

1. El administrador prepara una intención de transferencia con su sesión del dominio.
2. Solicita un desafío REVIEW para un dispositivo suyo, verificado y vigente.
3. El cliente presenta importe, moneda, destino y etapa desde el mensaje recibido.
   Una operación de la llave P-256 exige la biometría nativa. Se envía la firma.
4. El servidor verifica y consume ese desafío; entrega la confirmación de revisión.
5. Se emite un desafío EXECUTE diferente. Requiere otra operación biométrica del
   mismo dispositivo y administrador, la firma y la confirmación anterior.
6. Desafío consumido y movimientos se confirman en la misma transacción. Un fallo
   revierte ambos. Un reintento de una transferencia ya ejecutada devuelve el recibo,
   sin mover saldo ni tratarlo como una nueva autorización.

Se rechazan desafíos caducados (máximo dos minutos), reemplazados, de otro usuario,
servicio, intención o etapa; también llaves incorrectas, cambios de importe/destino,
dispositivos pendientes/revocados/vencidos y cambio de dispositivo entre etapas.
Ningún `biometric=true`, vídeo, selfie o resultado de IA es una prueba aceptada.
No se capturan rostros, huellas ni una base propia de plantillas biométricas.
La biometría del SO acredita una persona enrolada en ese dispositivo, no identidad
civil/KYC ni autenticidad de una cámara de la aplicación.

## Alta y raíz de confianza

`POST /api/v1/finance/wallet/devices/` devuelve una credencial **PENDING** y un nonce
de alta. Solo permite administradores activos; máximo cinco altas pendientes
vigentes por usuario. Los datos cliente no pueden definir usuario, estado o audiencia.
La llave nativa es nueva y de propósito separado del cifrado de documentos; no se
reemplaza una llave existente. Android incluye el nonce en Key Attestation y exporta
solo el punto público y certificados, jamás la privada.

`POST devices/{id}/attest/` necesita `public_key` (punto X9.62 no comprimido de 65
bytes, base64) y `certificate_chain` (hasta ocho certificados DER/base64), además de
`enrollment_authorization` emitida por un flujo independiente del servidor. Un adaptador
**de configuración de servidor** `WALLET_ATTESTATION_VERIFIER` debe verificar de verdad
raíces y vigencia del fabricante, revocación, nonce de alta, llave, verified boot,
bloqueo de dispositivo, paquete/firma de release y política biométrica por operación.
Solo entonces puede producir el `VerifiedAttestation` tipado y ligado al usuario,
audiencia, credencial, llave y hash de nonce. Su vigencia máxima es siete días.
Un diccionario del cliente o un certificado autofirmado no activan una credencial.

**Se entrega un verificador Android de certificados y política, sin simular hardware.**
Ver `DEVICE_BOUND_FINTECH.md` para raíces, revocación y autorización independiente. Sin configuración aprobada, el
servidor responde 503 y conserva PENDING. Debe verificarse con evidencias y raíces
reales antes de producción; no marcar registros VERIFIED manualmente. La biometría
local de iOS por sí sola no produce una atestación remota verificable de Secure
Enclave: ese método de confianza sigue pendiente y no se suplanta con una bandera.
No se incorpora App Attest ni otra API externa para aparentar un alta local completa.
El alta y recuperación exigen un verificador de identidad independiente; no existe endpoint para autoaprobarse.
El propio SO Android puede necesitar aprovisionamiento de su fabricante para obtener
certificados de atestación; la biblioteca no realiza llamadas HTTP de terceros.

## API del dominio

Base en ERP y Turismo: `/api/v1/finance/wallet/`. Sesiones separadas de los tokens
centrales; respuestas privadas `no-store`.

- `GET devices/` y `GET devices/{id}/`: solo dispositivos del solicitante.
- `POST devices/`: nonce de alta válido cinco minutos, sin crear confianza.
- `POST devices/{id}/attest/`: atestación y autorización independiente; falla cerrado si faltan.
- `POST devices/{id}/revoke/`: revoca e invalida desafíos pendientes, sin borrar
  llaves del teléfono ni movimientos históricos; no permite reactivar la credencial.
- `POST transfers/{id}/challenge/`: `credential` UUID y `phase` REVIEW/EXECUTE;
  devuelve UUID de desafío, `payload` base64 y vencimiento. Reemplaza el desafío
  anterior pendiente de esa etapa.
- `POST transfers/{id}/review/`: `digest`, `device_proof={challenge,signature}`.
- `POST transfers/{id}/execute/`: los anteriores más `confirmation`.

La firma es ECDSA P-256/SHA-256, DER/base64, verificada contra la llave ya registrada.
Los bytes a firmar son ASCII, con una línea por campo y salto final:

```text
SGACD-WALLET-APPROVAL-V1
audience UUID estable del servicio
ID entero del administrador autenticado
UUID de credencial
UUID de intención
UUID de desafío
REVIEW o EXECUTE
nonce aleatorio de 32 bytes, base64 estándar
SHA256 digest de la intención
UUID de origen
UUID de destino
importe decimal canónico con dos posiciones
COP o USD o EUR
vencimiento Unix en segundos
```

La UI debe mostrar los campos del mensaje que se firma, no un resumen alternativo
no vinculado. Las bibliotecas rechazan otro servicio/actor/credencial, mensajes
arbitrarios, formatos ambiguos y vencimientos fuera de ventana. Una llave distinta
se usa para documentos y autorizaciones; no se ofrece un oráculo de firma genérico.

## Configuración segura por defecto

- `WALLET_INTERNAL_TRANSFERS_ENABLED` sigue desactivado por defecto.
- `WALLET_DEVICE_APPROVALS_REQUIRED` es **True por defecto**, incluso sin definirlo.
  False es una excepción explícita de pruebas antiguas, no un fallback automático.
- `WALLET_DEVICE_ENROLLMENT_ENABLED` está desactivado por defecto.
- `WALLET_APPROVAL_AUDIENCE` es un UUID estable distinto por servicio/entorno. Se
  genera para configuraciones nuevas y nunca a partir del Host o de datos cliente.
  Configuraciones anteriores sin audiencia responden 503; no se inventa una identidad.
- Verificador de atestación: ninguno configurado por defecto. No hay confianza
  implícita en PEM subido, emulador, root detectado/oculto o booleanos cliente.

Antes de cambiar datos se crearon snapshots privados de las dos instalaciones
SQLite nuevas y se verificó restauración. Solo esas bases recibieron la migración
nueva; no se alteraron los archivos auxiliares recuperados ni la historia antigua.

## Evidencia y límites

13 tests del protocolo con firmas reales de **llaves software de prueba** ejercitan
nonce, fases, vinculación, revocación, sustitución de parámetros, rechazo de confianza
cliente, atomicidad y HTTP. Los registros VERIFIED de fixtures son sintéticos y no
prueban hardware ni se crean por el API de alta. La suite de bases migradas añade
un recorrido firmado, con datos sintéticos revertidos.

Android se compila contra API35. El test de interoperabilidad usa el escritor real
del backend, un firmante JCE y el verificador Python. Las bibliotecas nativas usan
BiometricPrompt/Keystore y Keychain/Secure Enclave, pero los positivos del hardware,
compilación Apple y pruebas físicas todavía no están certificados. CI queda preparada.

```sh
python BACKEND/deployment/tests/device_approval_check.py -v
python pool-02-biometrics/tests/verify.py --android-jar "$ANDROID_HOME/platforms/android-35/android.jar"
# Android: JDK17, SDK35 y Gradle8.11.1
cd pool-02-biometrics && gradle :android:assembleDebug
# En Mac con Xcode
cd ios && swift test
```

Pendientes: verificador real de atestación y raíces aprobadas, confianza iOS,
recuperación de cuenta/dispositivo, puente y pantallas de las dos aprobaciones,
teléfonos físicos y pruebas de carga/concurrencia en PostgreSQL. No se activa
producción ni se declara un detector de cámara inyectada o prueba de vida propia.

## Dependencia de Pool 03

Las llaves nativas ahora exigen un guard de integridad explícito al construirlas;
consulte `../pool-03-integrity/README.md` para configurar paquete/bundle, versión y
certificados Android reales. Se bloquea alta local de llave y firma ante riesgo o
inspección incompleta. Esto no completa la atestación remota ni habilita dispositivos.

## Evolución de confianza financiera

`DEVICE_BOUND_FINTECH.md` describe el verificador Android implementado, permisos de
alta ligados a llave/cuenta, revisión viva de revocaciones y reemplazo atómico sin
borrado. Sus pruebas son sintéticas y no habilitan dispositivos de producción.
