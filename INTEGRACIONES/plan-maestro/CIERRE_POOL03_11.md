# Pool03: ampliación y entrega del código de integridad

Estado: código de este corte integrado y comprobado localmente; cualificación real de distribución/dispositivos pendiente. No constituye cierre de producción del Pool03.

## Cambios entregados

- Se cerró la brecha del núcleo documental Pool01: exige un guard al crear llaves, cifrar y descifrar. iOS lo exige también al leer/escribir sobres. La aprobación sigue exigiéndolo en Pool02.
- El puente Flet nativo exige configuración del host fuera del canal Python, verifica integridad antes de operar y antes de comunicar éxito. No hay argumento para relajar la política. El código de bloqueo es visible, sin datos internos.
- Se incorporan los guards al paquete móvil por copia verificable de fuentes canónicas. Wheel 0.2.0 construido; se verifican doce recursos y las cuatro fuentes de integridad incluidas.
- Comprobación local de APK firmado mediante apksigner/aapt: esquema moderno, firmantes aprobados, identidad, versión y rechazo de debug/testOnly.
- Comprobación de .app en macOS mediante codesign con raíz Apple explícita, equipo, identidad, versión, plataforma y entitlements. Una firma autofirmada o ad hoc no satisface la política.
- Verificación sobre copia privada sin modificar/instalar el original; política explícita, límites y bloqueo ante herramienta ausente o error. No se generan certificados ficticios de distribución.
- Se documentan configuración, reacción a bloqueos y recuperación sin borrado destructivo ni bypass.

## Pruebas observadas

38 pruebas Python: 14 de la política de distribución (respuestas sintéticas de herramientas), 11 del contrato Flet y 13 del protocolo del servidor. 257 aserciones Java: 232 criptográficas, 16 de integridad y 9 de mensajes/autorizaciones. Interoperabilidad Django/JCE/Python comprobada; fuentes Android de los tres pools compiladas con API35. Wheel construido sin bytecode Python.

No se observaron compilación Swift/Flutter, una firma real de distribución validada ni teléfonos físicos. No se ejecutaron pagos ni operaciones sobre dispositivos del usuario. Los tests no acreditan hardware ni un release real.

## Lo que impide declarar terminado el Pool03 completo

1. Certificados e identidades de distribución reales de cada aplicación, versionados en su configuración segura.
2. Ejecutar la herramienta contra releases reales y compilar iOS/Flutter en sus toolchains.
3. Pruebas físicas de root/jailbreak/depuración/reempaquetado, falsos positivos, accesibilidad, cancelación y cambios de entorno.
4. Atestación remota y UI del Pool02, más recuperación revisada: dependencias previas aún no cualificadas.

No se inventan esas evidencias ni se marca producción habilitada. Comandos concretos y política: `../../pool-03-integrity/release/README.md`. El Pool04 no forma parte de este corte.
