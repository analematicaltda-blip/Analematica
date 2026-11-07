# Pool 02: autorizaciones vinculadas al dispositivo

Estado: primera implementación comprobada del protocolo; no activada para producción.

Se incorporan credenciales por solicitante, retos de revisión y ejecución con caducidad de dos minutos, firma P-256/SHA-256 y consumo único. Ambas etapas requieren el mismo administrador y dispositivo verificado. La firma vincula servicio, importe, moneda, origen, destino e intención. Revocar un dispositivo invalida sus retos pendientes. El consumo y la modificación financiera comparten transacción, conservando la reversión ante fallos y la idempotencia.

El servidor exige pruebas de dispositivo por defecto. El alta está deshabilitada por defecto y permanece PENDING sin un verificador real de atestación configurado. No se acepta un booleano enviado por el cliente como evidencia biométrica. No se habilitan pagos externos.

Android incluye llave de firma propia en Keystore con autenticación biométrica por operación y solicitud de atestación. iOS incluye firma Secure Enclave con biometryCurrentSet y contexto nuevo por operación. Estas fuentes no constituyen validación remota del hardware: faltan adaptador de atestación, identidad de aplicación, pruebas físicas y conexión del panel móvil autenticado. En iOS no se presenta la llave local como si acreditara atestación remota. No se implementa una prueba de vida de cámara ni se afirma que la biometría nativa la sustituya.

## Evidencia local

- 13 pruebas específicas del protocolo: firmas, etapas, revocación, vencimiento, aislamiento y rechazos.
- 99 ejecuciones adicionales de regresión y bases migradas, más 2 de configuración local: 114 ejecuciones correctas en total. Las llaves de las pruebas del servidor son software y los dispositivos verificados son fixtures, no atestaciones reales.
- 9 aserciones Java y verificación cruzada del mensaje escrito por Django, firma JCE y validación Python. Fuentes Android compiladas contra API 35; no se ejercitó hardware.
- Migración nueva aplicada a las dos bases locales nuevas después de copias privadas. No se alteró el grafo histórico bloqueado.
- Se incorpora CI Android/Apple; su ejecución remota y compilación Swift no fueron observadas en esta sesión.

## Pendientes de aceptación

1. Implementar y validar la cadena de confianza y política de atestación real por plataforma.
2. Compilar las aplicaciones y conectar el flujo nativo a la sesión y perfil financiero autenticados, mostrando importe y destino antes de cada aprobación.
3. Probar cancelación, cambio de biometría, dispositivo revocado, restauración y concurrencia PostgreSQL en dispositivos reales.
4. Auditar recuperación, rotación y operación antes de habilitar transferencias.

Pool 01 conserva su implementación y paquete; faltan su activación en la aplicación y pruebas físicas. Pool 02 no se declara terminado ni ofrece protección absoluta o blockchain.
