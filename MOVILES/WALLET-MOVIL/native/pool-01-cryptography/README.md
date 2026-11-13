# Pool 01 · Criptografía local de documentos

**Implementado como bibliotecas nativas y puente Flet propios. El puente está
empaquetado y probado a nivel de contrato, pero no está activo en la aplicación
principal ni validado en teléfonos físicos.** No utiliza APIs externas,
no transmite documentos y no modifica las reglas financieras de la billetera.
Los demás pools tienen alcance y criterios propios; no se anuncian como terminados.

## Protección implementada

| Plataforma | Llave protegida | Cifrado del documento | Autenticación |
|---|---|---|---|
| Android 12+ | AES-256 no exportable de AndroidKeyStore; exige StrongBox o TEE según política explícita | AES/GCM/NoPadding, nonce aleatorio de 96 bits y etiqueta de 128 bits | BiometricPrompt fuerte ligado al Cipher de cada operación; sin PIN alternativo |
| iOS 15+ | P-256 privada de Secure Enclave; Keychain local `WhenPasscodeSetThisDeviceOnly`, `biometryCurrentSet` | AES-256-GCM con llave aleatoria por documento, envuelta con ECIES mediante la pública del enclave | El descifrado de la llave envuelta exige la operación privada biométrica del sistema |

Secure Enclave **no almacena llaves AES genéricas**. En iOS la llave AES se utiliza
brevemente en la memoria del proceso; la privada que permite recuperarla no sale
del enclave. Swift/CryptoKit y el sistema pueden conservar copias internas en RAM;
el borrado explícito es de mejor esfuerzo. No se promete resistencia absoluta a
un sistema operativo comprometido.

Android comprueba el nivel de seguridad de KeyInfo y la política biométrica; no
hace fallback silencioso a software. iOS rechaza equipos sin Secure Enclave y
comprueba el token del SecKey recuperado. Esto no es atestación remota de identidad
ni prueba de vida legal. Las llaves solo se crean mediante una llamada explícita:
no se regeneran al fallar un descifrado, cambiar la biometría o restaurar archivos.
No existe borrado automático por heurísticas de root/jailbreak.

El helper PBKDF2-HMAC-SHA256 usa 600 000 iteraciones, salt aleatorio de 16 bytes y
salida de 256 bits. Exige una frase de al menos 12 caracteres; **un PIN corto no
protege frente a fuerza bruta offline**. El salt debe generarse con el CSPRNG del
sistema y conservarse con la versión de sus parámetros. Este helper opcional no
reemplaza la llave de hardware ni se usa como fallback. El PIN del dispositivo
permanece bajo el control y los límites del sistema operativo.

## Formato y aislamiento

`SGAVLT01` identifica el sobre binario. Contiene plataforma, contexto
`sgacd/v1/{tenant UUID}/{account UUID}/{document UUID}`, ID opaco de llave,
llave envuelta (solo iOS), nonce y longitud. **Todo ese encabezado es AAD**.
Después van ciphertext y etiqueta GCM. El UUID esperado viene del contexto
confiable del llamador, no de lo que declare el archivo. Versiones desconocidas,
truncados, datos sobrantes, cambio de cuenta/llave/documento y fallos de etiqueta
se rechazan. Los metadatos UUID no contienen nombres ni números de documentos,
pero son identificadores seudónimos visibles: este formato no oculta su existencia.

El máximo es 8 MiB por documento; no hay descifrado parcial ni streaming a disco.
La lectura está acotada. Solo se devuelve plaintext después de verificar GCM.
Android escribe sobres mediante AtomicFile en `getNoBackupFilesDir()`. iOS usa
Application Support privado, exclusión de backup, permisos 0600 y protección
completa de archivos en iOS. Los nombres provienen de UUID, no de rutas aportadas
por usuarios. Se rechaza sobrescribir un documento existente: cada revisión debe
usar un UUID nuevo. Esto no es una garantía contra restauración maliciosa de todo
el dispositivo; la vigencia de una versión necesita una referencia confiable aparte. Las llaves se separan por organización/cuenta/versión.

Los sobres de Android e iOS comparten encuadre, **no son una vía de exportación de
llaves entre teléfonos**. Un backup de ciphertext no garantiza recuperación si la
llave del dispositivo se perdió o invalidó. Conservar versiones previas y definir
recuperación explícita antes de activar documentos reales; nunca borrar llaves
como supuesto mecanismo de actualización. Rotar según el volumen de operaciones
mucho antes de agotar el presupuesto de nonces por llave.

## Compilar y comprobar

```sh
python MOVILES/WALLET-MOVIL/native/pool-01-cryptography/tests/verify.py
python MOVILES/WALLET-MOVIL/native/pool-01-cryptography/tests/verify.py --android-jar "$ANDROID_HOME/platforms/android-35/android.jar"
cd pool-01-cryptography
# Gradle 8.11.1, JDK 17, Android SDK 35 y build-tools 35.0.0
gradle :android:assembleDebug
cd ios
swift test
xcodebuild -scheme SGAVault -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build
```

Verificación local realizada: compilación Java contra el android.jar oficial API35;
AES-GCM con vector NIST; cambio de cada byte del sobre, truncados, ámbito distinto,
llave distinta, longitudes malformadas, nonce nuevo y PIN corto; interoperabilidad
JCE/Python para AES-256-GCM y PBKDF2. Las llaves de software de esos tests son
vectores públicos, no proveedores alternativos de producción.

El host Linux no tiene Xcode/Swift ni teléfonos. Se añade CI macOS para compilar
Swift/CryptoKit/Security y ejecutar sus tests; **no se atribuyen resultados de esa
CI aún no observados**. La compilación Android no demuestra StrongBox, biometría,
cancelación, bloqueo de pantalla ni invalidación por nueva huella. Verificar esas
situaciones en dispositivos físicos y builds firmadas antes de habilitar el pool.

## Integración pendiente con los clientes

La aplicación `MOVILES/SGA-CD-APK.git` es Flet/Python. El puente nativo se incorpora
en `flet_bridge` con selector y almacenamiento dentro del cliente, sin contenido
por el transporte Python. Ver `flet_bridge/README.md` para empaquetarlo. No se ha sustituido su almacenamiento ni afirmado que sus
documentos existentes estén cifrados. Se necesita validar esa extensión en los hosts firmados y conectarla al ámbito
autenticado de la aplicación principal antes de activarla. No utilizar base64 por logs, URLs,
SharedPreferences, localStorage o una implementación Python de llaves en disco.

Android: crear AndroidDocumentVault con tenant/cuenta/versión y política; en alta
explícita llamar `createKey`. Usar `encrypt(Activity, documentUUID, bytes, ...)` y
solo en `success` enviar el sobre a EncryptedDocumentStore.write. Para leer, obtener
el sobre y llamar `decrypt`; limpiar los buffers del consumidor al cerrar la vista.

iOS: agregar la biblioteca SwiftPM y la descripción Face ID de
`ios/HostInfo.example.plist` al host firmado. Crear SecureEnclaveVault en alta
explícita; cifrar y almacenar el resultado con `storeEncrypted`. Recuperar con
`readEncrypted` y `decrypt`. Ejecutar las operaciones potencialmente bloqueantes
fuera del hilo principal y manejar cancelación sin regenerar la llave.

Si el documento ya estaba en una galería, archivo del proveedor, caché del picker
o backup, esta biblioteca no borra ni cifra retroactivamente esa copia. Para
captura nueva se debe integrar una ruta cámara→memoria→cifrado sin temporal plano.
Tampoco cifra automáticamente las bases y saldos del servidor. El saldo financiero
sigue siendo autoridad del backend; cifrarlo en un teléfono no autoriza movimientos.
Se conservan las dos solicitudes de autorización existentes de la billetera.
