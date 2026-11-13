# Comprobación de distribución y configuración del host

Esta herramienta es local: no firma, instala, publica ni modifica la aplicación original. Verifica una copia privada estable y vincula los resultados a su `artifact_tree_sha256` (hash de rutas, tamaños y hashes de contenido; no equivale a `sha256sum` del APK). Devuelve código 1 ante errores de herramienta, identidad, firma, versión o formato. Los límites son 512 MiB y 20.000 entradas sin enlaces simbólicos. Solo admite APK o directorio `.app`, no IPA/AAB.

## Android

Instalar los Build Tools oficiales del SDK (apksigner y aapt). Crear fuera de Git una política con exactamente estos campos:

- `platform`: `android`.
- `application_id`: paquete real de distribución.
- `minimum_version`: entero positivo de versionCode.
- `signer_sha256`: lista de uno a cuatro SHA-256 hexadecimales en minúsculas de certificados previamente aprobados. Usar el certificado de Play App Signing cuando corresponda, no el certificado de subida. No derivar la lista automáticamente del APK que se está evaluando.

```sh
python MOVILES/WALLET-MOVIL/native/pool-03-integrity/release/verify_release.py \
  --artifact /ruta/privada/aplicacion.apk \
  --policy /ruta/privada/politica-android.json \
  --apksigner "$ANDROID_HOME/build-tools/35.0.0/apksigner" \
  --aapt "$ANDROID_HOME/build-tools/35.0.0/aapt"
```

Se ejecuta verificación criptográfica de apksigner con esquema v2 o superior, se comprueban todos los certificados firmantes actuales, paquete y versión, y se rechazan debuggable/testOnly. No basta con leer un certificado del ZIP o calcular un hash embebido.

El host del puente Flet 0.2.0 declara estas entradas dentro de `<application>` en AndroidManifest.xml, apuntando a recursos string de distribución:

```xml
<meta-data android:name="co.analematica.integrity.package" android:value="@string/sgacd_integrity_package" />
<meta-data android:name="co.analematica.integrity.signers" android:value="@string/sgacd_integrity_signers" />
<meta-data android:name="co.analematica.integrity.minimumVersion" android:value="@string/sgacd_integrity_minimum_version" />
```

Los tres recursos son strings: paquete esperado, pines separados por comas sin espacios y versión mínima decimal. No se incorporan valores inventados en este repositorio. Falta de configuración, debug o testOnly bloquean el puente. La configuración no cruza Flet/Python y no puede relajarse mediante `skip_integrity`.

## iOS

Ejecutar en macOS con Xcode sobre un `.app` **para dispositivo**, firmado para distribución. Política privada con exactamente:

- `platform`: `ios`.
- `application_id`: Bundle ID real.
- `minimum_version`: entero positivo de CFBundleVersion.
- `team_id`: identificador Apple de diez caracteres alfanuméricos en mayúsculas.

```sh
python MOVILES/WALLET-MOVIL/native/pool-03-integrity/release/verify_release.py \
  --artifact /ruta/privada/Aplicacion.app \
  --policy /ruta/privada/politica-ios.json
```

La herramienta exige verificación estricta de codesign con requisito explícito `anchor apple generic`, Team ID y Bundle ID. Una firma ad hoc o un certificado autofirmado que solo declare el mismo equipo no cumplen esa raíz de confianza. Además comprueba entitlements de identidad, rechaza `get-task-allow` y simuladores. No sustituye validación de provisioning, distribución de Apple, revocación, atestación remota ni pruebas físicas.

El Info.plist del host incluye un diccionario `SGACDIntegrity` con strings `ExpectedBundle` y `MinimumVersion`, fijados por distribución. Se leen en el cliente nativo; no por el canal de métodos. La aplicación de firmas en ejecución sigue dependiendo de iOS: los metadatos locales por sí solos no prueban una firma.

## Respuesta y alcance

Una comprobación correcta indica `artifact_verified: true`, pero **siempre** `physical_device_verified: false` y `production_authorized: false`. El paquete firmado no acredita el estado del teléfono. La autorización financiera continúa requiriendo el protocolo y la atestación real del Pool02.

Los 14 tests de esta herramienta utilizan respuestas sintéticas de las utilidades para cubrir la política y sus rechazos. No se presentan como una validación criptográfica de un release real ni como un dispositivo seguro.

## Bloqueo y recuperación

Ante bloqueo, cancelar la operación, conservar llaves/documentos y mostrar un mensaje sin datos sensibles. Reinstalar o actualizar desde el canal oficial y solicitar revisión del soporte desde otro equipo confiable. No activar flags para ignorar root, depuración, firmas o errores de inspección. No revocar automáticamente todos los dispositivos ni destruir fondos por una señal heurística.

Si la escritura cifrada terminó antes de un bloqueo o cancelación, no asumir que fue revertida: consultar el listado desde un entorno validado antes de reintentar. La recuperación criptográfica/financiera y pruebas de accesibilidad son criterios de aceptación separados; estas instrucciones no habilitan un bypass.
