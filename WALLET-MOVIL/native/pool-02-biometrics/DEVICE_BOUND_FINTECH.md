# Llaves financieras vinculadas al dispositivo

Se conserva la separación existente: AES/documentos en Pool01; una llave P-256 distinta para las autorizaciones en Pool02. No se genera una frase semilla, no se exportan privadas y no se reemplazan llaves automáticamente. Las bibliotecas Android/iOS ya exigen biometría por operación e invalidación vinculada al conjunto biométrico. No se presenta ese control local como prueba remota de identidad civil.

## Implementación nueva

### Android: verificación criptográfica real del formato de atestación

`services/android_attestation.py` valida certificados DER y sus firmas con cryptography>=44, cadena ordenada hasta una raíz explícitamente aprobada, fechas, restricciones/uso de CA, algoritmos y extensiones críticas. Rechaza delegación de confianza desde un certificado de llave de usuario que no es CA. No confía en nombres de certificado ni en una raíz recibida del cliente por el simple hecho de ser autofirmada.

El parser DER acotado exige KeyDescription y comprueba:

- Nonce de alta emitido por el servidor, ligado a la credencial y cuenta.
- Llave pública P-256 exacta de la hoja y nivel de hardware; StrongBox por defecto, TEE solo mediante política explícita del operador. Nunca software como alternativa.
- Propósito SIGN/VERIFY, digest SHA-256, curva P-256 y origen GENERATED, exigidos en hardware.
- Autenticación biométrica por operación; sin noAuthRequired, autorización por contraseña, timeout reutilizable ni allowWhileOnBody.
- Dispositivo desbloqueado requerido, verified boot en estado Verified y bootloader bloqueado; versión y parches OS/vendor/boot sujetos a mínimos y antigüedad máxima90d.
- Paquete/versiones de aplicación y todos sus certificados de firma aprobados. Se rechazan paquetes compartidos o estructuras no soportadas en lugar de inventar equivalencias.

**La atestación de esta llave describe su creación.** Revisar seriales/política en cada solicitud no prueba por sí solo el estado actual de arranque, OS o proceso. Una evaluación remota continua necesita evidencias frescas adicionales y su diseño; este corte no incorpora Play Integrity ni App Attest.

Esto es una política estricta: un dispositivo legítimo que no aporte los campos requeridos puede ser rechazado. Falta cualificar proveedores/dispositivos reales antes de producción. La bandera nativa de invalidación por cambio biométrico se mantiene, pero no se afirma que exista un tag remoto específico que certifique `biometryCurrentSet`/`invalidatedByBiometricEnrollment`.

### Alta y recuperación independientes de la sesión

Una sesión o contraseña válidas, y también la atestación de un teléfono genuino, **no autorizan por sí solas registrar una llave en una cuenta**.

`authorize_enrollment(user, credential_id, public_key, reference, replaces_id=None)` solo puede emitir una autorización cuando el adaptador de servidor `WALLET_ENROLLMENT_IDENTITY_VERIFIER` devuelve `IndependentEnrollmentApproval` exacto, validado y ligado a usuario, credencial, audiencia, nonce, hash de llave y reemplazo. Métodos admitidos: WEBAUTHN_UV o REVIEWED_RECOVERY. Debe verificar realmente una passkey con UV o un procedimiento independiente de recuperación aprobado; el nombre del método no es prueba por sí solo.

**No se incorpora un verificador de identidad ficticio ni un endpoint para autoaprobarse.** El adaptador por defecto es None y la emisión queda bloqueada. Un diccionario/booleano cliente nunca lo sustituye. Conectar un flujo WebAuthn/KYC real es un pendiente de activación, no una funcionalidad declarada terminada.

La autorización es un token firmado por el servidor, de propósito exclusivo, vigencia máxima5min y ligado a la llave/alta exactas. Solo activa una credencial PENDING con atestación válida. La transición atómica impide reutilizarlo después de activación; no sirve como aprobación de transferencias. Se guarda su digest y método para trazabilidad, no el token ni los documentos de identidad.

`POST /api/v1/finance/wallet/devices/{id}/attest/` ahora exige:

- `public_key`: punto público base64.
- `certificate_chain`: cadena DER/base64 del hardware.
- `enrollment_authorization`: token emitido por el flujo independiente del servidor.

No existe `devices/{id}/authorize/` ni PATCH que permita cambiar estado o verificación.

### Revocación y reemplazo sin destruir llaves

El servidor conserva plataforma, digest de política y seriales de la cadena verificada. Revisa la política y revocación vigente al emitir retos y antes de consumir cada firma. Un feed vencido, certificado revocado o cambio de política bloquea nuevas operaciones aunque la firma sea correcta. El estado VERIFIED registra un alta pasada; **no sustituye esta revisión viva**.

Un reemplazo aprobado revoca la credencial anterior e invalida sus retos pendientes en la misma transacción que activa la nueva. Si falla la atestación o la persistencia, se conserva la credencial anterior. No se eliminan llaves del teléfono, documentos, saldos ni evidencias. Una intención revisada con el dispositivo anterior no puede ejecutarse con el nuevo: requiere otra intención y ambas autorizaciones.

Un resultado heurístico de root/jailbreak/depuración sigue bloqueando localmente, sin purga automática. La revocación del fabricante bloquea confianza; no se presenta como una detección infalible de malware.

## Configuración de servidor

El perfil local nuevo admite `WALLET_ANDROID_ATTESTATION_POLICY_FILE` con una ruta absoluta a JSON privado, controlado por el operador. No se configura aquí ni se habilita `WALLET_DEVICE_ENROLLMENT_ENABLED`. La política contiene exactamente:

| Campo | Valor requerido |
| --- | --- |
| trusted_roots | Lista1–4 de objetos path absoluto a certificado DER y sha256 previamente aprobado |
| package_name | Paquete real de distribución |
| signer_sha256 | Lista1–4 de SHA-256 de certificados de firma de la app, hex minúscula |
| minimum_package_version | Entero positivo |
| minimum_os_version | Entero Android, mínimo120000 |
| minimum_patch_level | YYYYMM, umbral aprobado |
| require_strongbox | Booleano de política del servidor; True por defecto del tipo |
| maximum_patch_age_days | Entero1–90 |
| revocations_file | Ruta absoluta al snapshot privado de revocación |

No se distribuyen raíces de pruebas ni se aprende confianza de los certificados subidos. Aprobar raíces auténticas del fabricante/servicio y su rotación mediante un canal independiente. Cambiar raíces/paquetes/firmantes requiere reiniciar el proceso: la política se carga y cachea explícitamente; un digest distinto invalida confianza registrada hasta una nueva alta aprobada. Planificar la rotación antes de bloquear dispositivos.

El snapshot contiene exactamente `observed_at`, `valid_until` (fechas ISO8601 con zona) y `revoked_serial_numbers` (lista hex minúscula sin ceros iniciales). Se vuelve a leer en cada comprobación, con tamaño/lista limitados, y caduca como máximo24h después de su observación. La ingesta debe autenticar y transformar la fuente oficial y reemplazar el archivo atómicamente. **El validador no descarga el feed ni acredita por sí mismo su procedencia**; un JSON vacío creado manualmente no es evidencia de revocación real. Fallar cerrado implica indisponibilidad si la ingesta o el reloj confiable fallan: no habilitar excepciones por ello.

`WALLET_ENROLLMENT_IDENTITY_VERIFIER` se configura en código de servidor auditado, nunca mediante una ruta proporcionada por un usuario. El adaptador debe verificar cuenta, reto, origen/RP ID y UV para WebAuthn, o la evidencia y autorización del procedimiento de recuperación. No aceptar solo posesión del código del teléfono, sesión, SMS o un click administrativo como sustitución automática. La aprobación vigente debe quedar vinculada a la nueva llave y alta dentro de la ventana temporal.

## Alcance iOS y recuperación de documentos

Secure Enclave P-256 y ACL biometryCurrentSet continúan implementados localmente. **No hay aún un verificador remoto Apple integrado que permita activar una cuenta iOS**. App Attest no es, por sí solo, una atestación genérica de la política biométrica de cualquier SecKey. Se necesita definir y validar ese enlace sin sustituirlo por una bandera ni afirmar que las pruebas Android lo cubren.

Recuperar la cuenta/llave de autorización no recupera privadas de documentos del teléfono perdido. No se exportan ni reconstruyen. Diseñar continuidad, originales autorizados y reprovisión por separado. La vigencia de confianza actual sigue siendo como máximo7d (sujeta a certificados); renovación usable sin perder acceso requiere diseño/pruebas adicionales antes de producción.

## Evidencia local y rendimiento

28 pruebas nuevas usan cadenas y firmas criptográficas reales generadas bajo **CA sintética**, además de un adaptador de identidad de fixture. Cubren raíces no autorizadas, firmas, nonce, hardware/políticas, arranque, aplicación, parches, feeds, autorización independiente, recuperación atómica, replay y una transferencia de dos etapas bloqueada por revocación antes de mover fondos. No son dispositivos genuinos ni KYC/pasarelas reales.

138 ejecuciones Python correctas con regresiones y bases migradas de ambos servicios. La migración0004 agrega metadatos/linaje tras backups privados con restauración verificada; las bases locales nuevas quedan en166 migraciones y587 tablas. No se toca el grafo histórico ni bases productivas.

La validación completa de cadena se realiza en el alta; las autorizaciones conservan P-256, revisión de revocación/política y sus límites existentes. No se ejecutan llamadas externas ni se promete consumo cero de RAM, ausencia de coste o seguridad absoluta.

```sh
python WALLET-BACKEND/tests/attestation_security_check.py -v
python WALLET-BACKEND/tests/device_approval_check.py -v
```

Pendientes reales: raíces/paquetes/firmantes aprobados, ingesta de revocación autenticada, verificador independiente de identidad y pantallas del flujo; confianza remota iOS, renovación y pruebas en hardware. El código y sus gates están entregados; la activación productiva permanece bloqueada.
