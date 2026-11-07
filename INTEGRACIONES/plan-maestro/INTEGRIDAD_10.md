# Pool 03: control local de integridad

Estado: iniciado; primera biblioteca local integrada en las autorizaciones nativas del Pool 02. No activación productiva.

Android comprueba paquete, versión mínima, certificados actuales de firma, flags de desarrollo, depurador y señales conocidas de root. iOS comprueba identidad y versión de bundle, desarrollo, simulador, señal de depurador y rutas conocidas de jailbreak; la firma de instalación queda a cargo de iOS y no se afirma validar un equipo de firma mediante metadatos del bundle.

Las llaves del Pool 02 exigen un guard explícito. Se impide crear la llave o entregar una firma ante riesgos o errores de inspección, con revisión antes y después de la interacción biométrica. No hay borrado automático de llaves, cambios financieros, llamadas a proveedores ni confianza concedida al servidor mediante booleanos.

## Comprobado

- 16 aserciones Java de política, incluyendo rotación y rechazo de firmantes desconocidos, identidad ajena, versión antigua, depuración, root y fallos de inspección.
- Compilación de fuentes de integridad y aprobación Android contra el SDK oficial API35.
- 9 aserciones de mensajes y verificación cruzada de firma P-256 entre Django/JCE/Python.
- 13 pruebas de servidor del Pool 02 correctas tras integrar el guard.
- CI Android/Apple actualizado; ejecución remota y compilación Swift no observadas en esta sesión.

## Límites y pendientes

Los positivos de las pruebas son fixtures CPU; no acreditan un teléfono seguro o una firma de distribución. No existen certificados de release aportados ni teléfonos conectados, Xcode o Swift en este entorno. Faltan builds firmadas, rotación real, prueba de APK reempaquetada, dispositivos de pruebas con root/jailbreak, falsos positivos, accesibilidad e integración en las pantallas finales.

La inspección local es eludible y complementaria. Pool 02 conserva pendiente su atestación remota y activación móvil. El guard no cubre aún todas las operaciones del Pool 01 ni la web. No se incorporan técnicas evasivas, destrucción de llaves o afirmaciones de protección absoluta mediante blockchain.

Configuración, comandos y criterios de aceptación: `../../pool-03-integrity/README.md`.
