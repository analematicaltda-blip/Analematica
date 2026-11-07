# Pool04 · Red, origen y pantallas sensibles

Estado: **implementado e integrado en las fuentes nativas; no activación productiva ni instalación en teléfonos**. No se han fijado dominios/pines de producción ni cambiado configuraciones financieras para habilitar pagos. Los límites previos de los Pools01–03 continúan.

## Conectado al código existente

- Android aplica FLAG_SECURE, oculta overlays mediante API31 y filtra toques oscurecidos antes de las operaciones de documentos y del prompt de autorizaciones. El puente documental lo exige antes de operar. Se conservan los flags hasta terminar la Activity, evitando que una operación concurrente desproteja otra. Los permisos necesarios se declaran en los manifests de bibliotecas.
- iOS instala coberturas de privacidad ante pérdida de actividad, desactivación de escena y captura/grabación detectada. Las operaciones nativas exigen una ventana activa sin captura antes de acceder o entregar información sensible. Se usa UIKit público, sin trucos con campos de contraseña.
- El wheel Flet0.3.0 incluye siete fuentes nuevas de protección, además de los núcleos anteriores: 19 recursos canónicos verificados byte a byte. No se añaden bytes/documentos/llaves al transporte Flet ni métodos para ignorar controles.
- Los paquetes Swift de integridad y protección están en subdirectorios con identidad única (`ios/SGAIntegrity`, `ios/SGAProtection`) para evitar colisiones entre dependencias locales llamadas `ios`. CI y dependencias se actualizan; no se afirma compilación Apple observada.

## Cliente HTTPS dedicado

Android `PinnedHttpsClient` y Apple `PinnedHTTPSClient` exigen:

1. HTTPS y origen exacto configurado; puerto443 o su omisión. Se rechazan credenciales en URL, fragmentos, sufijos engañosos y autoridades ambiguas. No se abren URLs externas ni se siguen redirecciones, incluso al mismo origen.
2. Validación TLS normal del sistema, hostname y pin SPKI/SHA-256 **dentro del handshake**, antes de enviar HTTP. Un pin correcto no convierte en válido un certificado autofirmado, una CA no confiable o un hostname incorrecto.
3. Dos a cuatro pines distintos (activo y respaldo) con fecha de caducidad de política obligatoria. No hay dominio/pin por defecto ni trust-all. La caducidad local depende del reloj del dispositivo y no sustituye el vencimiento de retos en el servidor.
4. Solicitudes GET/POST JSON acotadas (64KiB de cuerpo y 1MiB de respuesta), timeouts, no-store y rechazo de respuestas no2xx. La biblioteca no registra tokens ni cuerpos. Apple usa sesión efímera sin cookies/credenciales persistentes; Android rechaza la petición si hay un CookieHandler o Authenticator global; no altera esos gestores de todo el proceso para eludir la restricción. Revisar el host antes de conectarlo.

Los adaptadores de perfil leen recursos nativos del host, no parámetros del canal Flet ni encabezados del usuario. El cliente es una biblioteca explícita: **no intercepta ni protege automáticamente todas las conexiones existentes de la app, navegador o terceros**. El puente documental no necesita red y no comienza a hacer conexiones por esta incorporación. Falta conectar el cliente a la sesión financiera nativa final y probarla; no se presenta como un backend ya enlazado.

Las fuentes Apple requieren Xcode15+ (compilador Swift5.9+, modo de lenguaje Swift5). La UI se inspecciona en MainActor; no bloquear el hilo principal esperando una operación síncrona que deba volver a ese hilo.

Apple reconstruye SPKI correctamente para RSA/PKCS#1 y EC P-256/X9.62 antes de calcular el pin. Otras curvas/tipos se rechazan hasta incorporar y probar sus codificaciones. No se confunde la representación cruda de SecKey con SubjectPublicKeyInfo. Se agregan vectores públicos independientes para CI Apple.

## Configuración de host antes de conectar

Android: `AndroidPinnedProfile.fromApplication(context)` lee tres valores string de metadata: `co.analematica.network.host`, `co.analematica.network.pins` y `co.analematica.network.validUntil`. Usar recursos `@string/...` propios de distribución. Host sin esquema; pines `sha256/BASE64` separados por comas, sin espacios; caducidad Unix decimal. La ausencia, caducidad o formato inválido impide crear el cliente.

iOS: `PinnedHTTPSClient.fromApplication()` lee un diccionario Info.plist `SGACDNetwork` de strings `Host`, `Pins`, `ValidUntil` con el mismo significado. No se rellenan con certificados de prueba ni se obtienen automáticamente del servidor que se evalúa.

Obtener SPKI de certificados aprobados fuera del canal de conexión que se está verificando. Mantener un pin de respaldo real, rotar mediante actualizaciones firmadas antes de caducar y probar recuperación. No pinnear Meta/TikTok/Google a ciegas: esta política corresponde a los servidores propios del sistema, no a certificados cambiantes de terceros.

## Pantallas y límites

Android FLAG_SECURE se aplica en una Activity nativa real y normalmente impide capturas/grabaciones por el SO. No impide una cámara externa ni acredita un dispositivo sin comprometer. iOS **no ofrece una API pública que impida todas las capturas individuales**; se oculta al detectar grabación/inactividad y se bloquean operaciones mientras exista ese estado. Las fuentes están integradas, pero ese comportamiento no fue validado físicamente. Probar overlays permitidos, accesibilidad, multitarea y cambios de configuración para detectar falsos positivos.

No se borra ninguna llave ni saldo por grabación o pérdida de foco. Una escritura cifrada puede haber terminado antes de un bloqueo; revisar su estado desde un entorno validado antes de repetirla. Los flags Android permanecen en la Activity y pueden afectar todas sus pantallas: esa es la política conservadora actual, no un restablecimiento automático.

## R8/ofuscación

La ofuscación se configura en la aplicación host de distribución, no habilitando minify sobre un AAR sin conocer su consumidor. En `buildTypes.release`, utilizar `isMinifyEnabled=true`, `isShrinkResources=true` y `proguard-android-optimize.txt` con reglas propias. Conservar el registrador/plugin Flutter y las APIs requeridas por las dependencias, probar un release firmado y guardar los mapas fuera de Git. **No se ha activado ni verificado R8 en la aplicación principal** y no se presenta como cifrado o control de acceso.

## Verificaciones observadas

- 26 aserciones Java de políticas: origen, vencimiento, pines activo/respaldo, entradas malformadas, límites y rechazo de token con CRLF antes de abrir conexión.
- Cinco escenarios TLS reales en loopback con CA/llaves efímeras: PKI+pin válidos aceptados; pin incorrecto, CA no confiable con pin coincidente, hostname incorrecto con pin coincidente y redirección rechazados. No llegaron solicitudes HTTP en los fallos TLS; no hubo llamadas externas ni certificados de producción.
- Fuentes Android compiladas contra SDK35. Regresión de 232 aserciones criptográficas Pool01, 9 de autorizaciones, 11 pruebas Flet y 13 del servidor. Wheel0.3.0 construido y recursos comprobados.
- Pruebas Swift de política/SPKI/pantallas no soportadas y CI agregadas; compilación Apple/Flutter y pruebas de dispositivos no observadas en este entorno.

```sh
python WALLET-MOVIL/native/pool-04-anti-phishing/tests/verify.py --android-jar "$ANDROID_HOME/platforms/android-35/android.jar"
# Linux con permiso para abrir loopback443, puerto libre y cryptography:
python WALLET-MOVIL/native/pool-04-anti-phishing/tests/local_tls.py
# Mac con Xcode:
swift test --package-path WALLET-MOVIL/native/pool-04-anti-phishing/ios/SGAProtection
```

## Pendientes para activación de producción

Dominios y pines reales; integrar el cliente con autenticación financiera final; compilación y firma de apps; pruebas de rotación/caducidad/MitM en dispositivos autorizados; pantallas físicas Android/iOS, accesibilidad y R8 release; completar atestación del Pool02. No se habilitan transferencias o confianza de hardware para omitir estos requisitos.
