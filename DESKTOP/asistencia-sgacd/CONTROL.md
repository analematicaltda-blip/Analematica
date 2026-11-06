# Control autorizado desde web, escritorio y móvil

Estado: protocolo y adaptadores implementados; pruebas aisladas de backend, Chromium y Appium simulado. No se ha cualificado un Android/iPhone físico ni operado una cuenta real de Meta, TikTok, Gmail o YouTube. El sistema no garantiza compatibilidad con todas las pantallas o futuras modificaciones de esas plataformas.

El panel responsive `/control.html` usa el inicio de sesión central SGA-CD y los roles administrativos activos. Está publicado junto a los paneles web de Analemática y SGA-CD. Las aplicaciones Flet de escritorio y móvil incluyen un acceso al mismo panel HTTPS: configura `SGACD_CONTROL_ORIGIN=https://tu-panel`. No se transfieren JWT, contraseñas ni permisos del login offline en una URL. El backend vuelve a autenticar y autorizar cada solicitud. Los frontends Turismo y ERP incluyen un enlace configurable mediante `NEXT_PUBLIC_SGACD_CONTROL_ORIGIN` (origen HTTPS sin rutas); no se han reemplazado sus sistemas de autenticación ni generado nuevos binarios móviles.

## Autorizar y ejecutar

1. El administrador crea un código de vinculación en el panel; vence en cinco minutos y solo puede usarse una vez.
2. El operador lo introduce en el ejecutor del host que controla el dispositivo. Vincular no ejecuta ni cuenta como autorización.
3. El administrador prepara una operación con equipo, plataforma, cuenta, argumentos y propósito exactos. La cuenta es el perfil dedicado `principal` de cada plataforma; el operador debe verificar visualmente su identidad. No se afirma identificar cuentas comerciales automáticamente.
4. Primera autorización: revisar el plan y escribir la frase de revisión.
5. Segunda autorización: escribir una frase nueva y autorizar ejecución. Debe aprobar el mismo administrador solicitante; el agente y otros administradores no pueden sustituirlo. Para click, texto, tecla, carga, tap o swipe hay una tercera confirmación de impacto.
6. El dispositivo reclama una sola vez el permiso Ed25519, válido durante un máximo de 30 segundos para iniciar. Verifica firma, identidad, etapas, alcance y hash antes de despachar una interacción. No son 30 segundos de sesión libre.
7. Un resultado indica entrega de interacción, no éxito verificado en la plataforma. Los fallos inciertos no se reintentan. Revisa el proveedor antes de emitir otra orden.

No hay aprobaciones globales, por lote ni realizadas por IA. Cada interacción nueva necesita autorizaciones nuevas. Cambiar el plan crea otra orden. Las referencias de elementos vencen en 120 segundos; cambiar el contenido observado impide su utilización. Animaciones/contenido dinámico pueden invalidar observaciones y requieren repetir la revisión. Detener/revocar impide nuevas reclamaciones, pero no puede retirar una interacción ya despachada. Ctrl+C detiene el ejecutor local.

## Instalar el ejecutor

Node 22+, Chrome local para escritorio. En la raíz:

```bash
npm ci --prefix DESKTOP/asistencia-sgacd --ignore-scripts
node DESKTOP/asistencia-sgacd/device.mjs doctor --kind desktop
node DESKTOP/asistencia-sgacd/device.mjs pair --kind desktop --backend https://tu-panel --name Mi-PC
node DESKTOP/asistencia-sgacd/device.mjs run --kind desktop --allow-control
```

Para un certificado de desarrollo confiado explícitamente, añade `--ca /ruta/certificado.crt` al vincular. No desactives TLS. Las claves de dispositivo y perfiles se guardan en `.runtime` privada, ignorada por Git. El proceso hace conexiones HTTPS salientes, no abre un puerto remoto. No expongas Appium a Internet. Los archivos que se pueden cargar deben estar en `.runtime/device-ID/shared`; la orden `files_list` permite revisar nombre, tamaño y SHA-256. La carga tiene un máximo de 64 MiB y utiliza los mismos bytes cuyo hash fue aprobado. No se permite explorar el resto del disco ni usar enlaces simbólicos.

Android requiere SDK/Java, un dispositivo explícito y depuración USB autorizada personalmente. El host puede ser Linux, Windows o Mac. Instala Appium y su driver en el host, verifica sus diagnósticos y luego:

```bash
npx appium@3.9.0 driver install uiautomator2@8.7.3
npx appium@3.9.0 --address 127.0.0.1 --port 4723
# En otra terminal, selecciona el UDID que autorizaste:
node DESKTOP/asistencia-sgacd/device.mjs pair --kind android --backend https://tu-panel --udid TU-UDID
node DESKTOP/asistencia-sgacd/device.mjs run --kind android --allow-control
```

iOS requiere un Mac con Xcode, dispositivo confiado, permisos de desarrollo y WebDriverAgent firmado conforme a Apple. Prepara y verifica WDA primero; no se evita el bloqueo, la confianza del dispositivo ni la firma. Appium puede controlar un iPhone físico desde ese Mac; el administrador puede autorizar desde otro dispositivo mediante el panel.

```bash
npx appium@3.9.0 driver install xcuitest@12.22.8
npx appium@3.9.0 --address 127.0.0.1 --port 4723
node DESKTOP/asistencia-sgacd/device.mjs pair --kind ios --backend https://tu-panel --udid TU-UDID --xcode-team TU-TEAM
node DESKTOP/asistencia-sgacd/device.mjs run --kind ios --allow-control
```

No uses `--relaxed-security` ni habilites ejecución de shell de Appium. El ejecutor solo emite los comandos W3C y gestos locales codificados en `mobile-driver.mjs`, con paquetes/bundles oficiales permitidos. El navegador móvil depende además del driver compatible de Chrome/Safari. Las aplicaciones oficiales deben estar instaladas y las sesiones iniciadas manualmente.

## Backend, claves y aislamiento

La inicialización explícita de la base de Compose (`--init-db`) prepara siete tablas adicionales con `checkfirst`, sin borrar datos, y claves Ed25519/Fernet en `/state/assistance-control-keys`. En otros despliegues ejecuta explícitamente:

```bash
python -m app.services.assistance.schema
python -m app.services.assistance.control_crypto
```

Conserva el volumen privado `/state`: perder la clave de datos hace ilegibles los planes anteriores; cambiar la clave de firma requiere revincular dispositivos. Respalda y protege esas claves fuera de Git. Se cifran planes, textos, desafíos y resultados en la base de datos. El dispositivo almacena solo su credencial, no un JWT administrativo. El operador del host y el administrador del servidor son parte de la frontera de confianza.

La política común está en `BACKEND/SGA-CD-BACKEND/app/services/assistance/control_policy.json`. Solo se abren orígenes oficiales HTTPS y aplicaciones permitidas. Contraseñas, CAPTCHA, códigos de verificación, recuperación y permisos del sistema se atienden personalmente. No hay bypass, shell remoto genérico ni herramientas de aprobación para el modelo. Google Ads gestiona los anuncios asociados a Gmail y YouTube.

El catálogo de 42 guías/252 pasos y Open Duet planifican/orientan. El MCP limitado no ejecuta acciones: la antigua observación por variables de entorno fue deshabilitada para que no eluda las autorizaciones. `agent-desktop` aporta diagnóstico nativo; Playwright controla el navegador dedicado y Appium las aplicaciones móviles. No se entrega a Open Duet acceso directo irrestricto a esos ejecutores. Copiar código no conecta el portátil, las cuentas o los servidores privados de proveedores.

## Verificación pendiente antes de uso real

Validar en cada host Android/iOS físico: UDID y permisos, app instalada/versionada, bloqueo manual, identidad de cuenta, lectura de elementos, rechazo de pantalla cambiada, dos/tres confirmaciones, entrega única, revocación y pérdida de conexión. Una prueba de protocolo simulada no sustituye esto. Tampoco se han firmado/distribuido nuevos APK/IPA ni certificado seguridad de producción; ninguna aplicación puede garantizar inmunidad absoluta frente a ataques.
