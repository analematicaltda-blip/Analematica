# Pool 03 · Integridad del cliente

Estado: **primera implementación local integrada con las llaves de autorización del Pool 02**. No activada en la aplicación final ni certificada en dispositivos físicos. El alta del servidor sigue cerrada sin atestación real del Pool 02.

## Controles implementados

| Control | Android 12+ | iOS 15+ |
| --- | --- | --- |
| Identidad local | Paquete esperado y versión mínima obligatorios | Bundle ID esperado y versión mínima obligatorios |
| Firma de distribución | SHA-256 de cada certificado firmante actual del APK contra una lista explícita | Aplicación de firmas a cargo de iOS; no se presenta Bundle ID como prueba de firma/equipo |
| Desarrollo y depuración | FLAG_DEBUGGABLE, FLAG_TEST_ONLY, depurador conectado o en espera | Build de depuración y señal P_TRACED; simulador y macOS bloqueados para operaciones sensibles |
| Señales de entorno | Rutas conocidas de `su`/Magisk y test-keys | Rutas conocidas de jailbreak |
| Fallos de inspección | Bloqueo, sin asumir entorno seguro | Bloqueo si falla sysctl o falta la identidad/versión |
| Acción | Impedir alta local de llave y firma de autorización | Impedir alta local de llave y entrega de firma de autorización |

Se comprueba el entorno antes de abrir la autenticación y nuevamente al terminarla. Las clases de firma ahora requieren un guard de integridad explícito en su constructor: no hay un constructor antiguo que omita el control. Los validadores de mensajes y las dos autorizaciones del servidor se mantienen.

Los hallazgos se devuelven como códigos sin rutas, documentos, saldos, identificadores personales ni contenido de memoria. No se escribe telemetría ni se envía a terceros. No se borran llaves, documentos o registros financieros; tampoco se cambia el estado del dispositivo a VERIFIED en el servidor. La recuperación sigue siendo un proceso pendiente y no una excepción automática al bloqueo.

## Configuración de distribución

Android requiere `IntegrityPolicy(packageName, Set<sha256CertActual>, minimumVersionCode)` y `AndroidIntegrityGuard(policy)`. La colección proviene de PackageManager y usa todos los firmantes **actuales**, no certificados históricos que puedan ampliar confianza sin intención. Una rotación permite hasta cuatro pines aprobados; si aparece cualquier firmante no autorizado, se bloquea. Los pines deben salir del certificado real de distribución; para Play App Signing se utiliza el certificado de firma de aplicaciones, no el de subida. No se incluyen certificados ni pines ficticios como valores por defecto.

Pasar el guard como quinto argumento de `AndroidApprovalKey(audience, actor, credential, requireStrongBox, guard)`. Gradle de Pool 02 incorpora `pool-03-integrity/android` como dependencia de biblioteca. El módulo también puede compilarse desde esta carpeta con `gradle :android:assembleDebug`; compilar debug solo valida fuentes, no habilita una operación financiera.

iOS requiere `IntegrityPolicy(expectedBundle:minimumVersion:)`, `AppleIntegrityGuard(policy:)` y el argumento `integrity:` de `AppleApprovalKey`. El paquete Swift de Pool 02 depende del paquete de esta carpeta. `CFBundleVersion` debe ser un entero positivo y monótono para esta política: si la aplicación utiliza un valor con puntos, debe acordarse una política de versiones antes de integrarla; no se convierte silenciosamente.

La configuración se fija en la aplicación de distribución, nunca en un encabezado HTTP, orden del usuario ni respuesta booleana de un cliente. La biblioteca no ofrece flags `allowRoot`, `allowDebugger` o `ignoreUnknown`. Para probar el protocolo en CPU se usan fixtures de la política; no hay un bypass de producción.

## Límites de confianza

- Root/jailbreak/depuración son señales heurísticas y eludibles. Un resultado sin hallazgos no demuestra ausencia de manipulación, malware, Frida ni autenticidad del hardware.
- El certificado consultado por una aplicación comprometida tampoco constituye atestación remota. No hay hash maestro embebido que prometa resolverlo. La firma de instalación y las actualizaciones dependen del SO y del canal de distribución.
- No se captura ni escanea memoria de otros procesos, se ejecutan shells, se inyecta código, se evade instrumentación o se hacen cambios en el teléfono.
- No se garantiza borrado de buffers administrados de Java/Swift. No se incorporan nuevas llaves o secretos en memoria como parte de la inspección.
- El guard cubre las llaves de autorización del Pool 02. No se afirma que cubra toda la aplicación, el puente documental del Pool 01, la web o el motor de control remoto.
- Una política de versión mínima local puede ser modificada junto a una app comprometida; control de versiones y revocación deben validarse también en la raíz de confianza remota pendiente.

## Verificación reproducible

```sh
python pool-03-integrity/tests/verify.py --android-jar "$ANDROID_HOME/platforms/android-35/android.jar"
python pool-02-biometrics/tests/verify.py --android-jar "$ANDROID_HOME/platforms/android-35/android.jar"
python BACKEND/deployment/tests/device_approval_check.py -v
# Mac con Xcode:
swift test --package-path pool-03-integrity/ios
swift test --package-path pool-02-biometrics/ios
```

Verificado localmente: 16 aserciones Java de política (identidad, versiones, firmantes, rotación, múltiples firmantes, errores, depuración y root), compilación de los guards y llaves Android contra SDK oficial API35 y 9 aserciones de interoperabilidad de las firmas. Las pruebas positivas son fixtures software, no un teléfono rooteado ni una APK de distribución validada. Se conserva CI macOS/Android para compilar y probar los paquetes; su ejecución remota no ha sido observada aquí.

## Criterios pendientes para activación

1. Definir identidades, certificados y versiones reales de cada aplicación; firmar builds de distribución y probar actualizaciones/rotación.
2. Validar rechazo de APK reempaquetada, firma ajena, debug, dispositivo rooteado/jailbreak y fallos de inspección en teléfonos de pruebas autorizados. Medir falsos positivos y accesibilidad.
3. Comprobar cancelación, cambio de entorno durante el prompt y que el bloqueo no destruya llaves ni fondos.
4. Completar atestación remota y UI del Pool 02. Ni el guard ni un booleano enviado por móvil pueden activar la confianza del servidor.
5. Integrar la política en el resto de superficies nativas que manejen información sensible y revisar recuperación sin bypass.

Esto inicia el Pool 03; no declara terminados los Pools 01/02 ni seguridad absoluta, bloqueo de ingeniería inversa o protección mediante blockchain.
