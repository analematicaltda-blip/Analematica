# Implementación 58 · Borradores cifrados offline y reanudación supervisada

**Avance global: 55,56 % (40/72).** Se acredita el incremento funcional y la verificación de ACC-022, que estaban vacíos. No se acredita aceptación completa: 0/24 tareas. H19 pasa a ejecución y el plan conserva **4 paquetes verificados localmente, 10 en ejecución y 6 pendientes**. Los 20 hitos no están completados.

## Flujo disponible

ERP y Analemática incorporan «Borradores cifrados sin conexión» en sus paneles contables existentes. El titular verifica su empresa con la sesión online antes de desconectarse, prepara una actividad ambiental y guarda un borrador local. El identificador debe conservarse junto con una contraseña local larga y exclusiva; no existe recuperación mediante el servidor.

El formulario permite guardar, recuperar y cambiar esa contraseña sin llamadas de red. Recuperar devuelve los campos editables y elimina revisiones, resultados y autorizaciones de la interfaz. Al reconectar, el usuario debe revisar y confirmar nuevamente mediante el flujo online existente; la API vuelve a comprobar empresa, titular, fuentes y duplicados. No hay sincronización ni registro automático al volver la conexión.

La cola local se limita a un borrador ambiental individual por identificador. No guarda asientos, solicitudes de pago, tokens, revisiones ni confirmaciones. No generaliza aún captura offline a nómina, reservas o documentación fiscal, ni constituye una aplicación nativa offline completa.

## Cifrado y almacenamiento

El módulo compartido `accounting-offline.js` usa WebCrypto: PBKDF2-HMAC-SHA-256 con 600.000 iteraciones, salt aleatoria de 16 bytes por versión y clave AES-256-GCM no exportable. Cada cifrado usa IV aleatoria de 12 bytes. El contexto autenticado incluye empresa, borrador, versión, esquema, KDF y tipo de borrador.

IndexedDB conserva únicamente metadatos de contexto/versión, salt, IV y ciphertext. No almacena contraseña ni clave derivada. Empresa y UUID del borrador permanecen visibles como metadatos: no se afirma anonimato del almacén. Las cantidades y los factores se cifran antes de escribir. La contraseña se retira del campo al comenzar cada operación; ocultar/cerrar el panel o perder la identidad retira campos y bloquea los controles locales.

El límite es 8 KiB de contenido, una actividad/factor, contraseña de al menos 16 caracteres y hasta 1024 bytes UTF-8, con versiones acotadas. La longitud mínima no demuestra entropía: se requiere una frase exclusiva y no predecible. No hay envío a modelos, proveedores o servidores.

El navegador debe ofrecer contexto seguro HTTPS/localhost, WebCrypto e IndexedDB. Esta implementación no usa Secure Enclave, Android Keystore ni atestación física. JavaScript conserva strings y objetos que no pueden borrarse forensemente por contrato; limpiar campos y buffers propios no garantiza eliminación de copias del motor o del sistema operativo. Un script comprometido del mismo origen puede observar el borrador desbloqueado.

## Conflictos y rotación

Guardar una versión existente exige desbloquear la anterior; una contraseña incorrecta no sobrescribe el original. Después del cifrado, una transacción IndexedDB compara la versión y el registro previo antes de sustituirlo. Dos pestañas compitiendo por la misma versión producen un guardado y un conflicto: la segunda debe recuperar antes de editar. No se fusionan cantidades ni autorizaciones mediante CRDT.

Cambiar contraseña exige la anterior, descifra y vuelve a cifrar localmente con salt/IV nuevas y una versión superior. La copia activa deja de abrirse con la contraseña anterior. Esto no revoca copias antiguas del ciphertext ni proporciona recuperación de contraseña perdida o backup de llaves fiscales.

## Pruebas de navegador

Las dos interfaces se probaron con red deshabilitada durante guardado, recuperación y cambio de contraseña. Las pruebas verifican contenido cifrado, contraseña ausente del almacenamiento/campos, rechazo de contraseña incorrecta, ausencia de peticiones de red, autorizaciones sin restaurar y posterior registro online con dos confirmaciones. El ledger permanece cuadrado y sin cambios por el borrador/medición ambiental.

El módulo se probó adicionalmente en Chromium con recarga, dos pestañas, manipulación de ciphertext/IV/salt/versión/KDF/contexto, copia a otra empresa, campos de autorización rechazados, tamaño máximo, contraseña incorrecta sin sobrescritura y cambio de contraseña con recuperación exacta del contenido. Son datos sintéticos, sin cualificación física de dispositivos.

Evidencia consolidada y capturas: [implementacion-58.json](evidencias/implementacion-58.json).

## Pendientes de H19

- Instalación/arranque completamente offline y política de caché de la aplicación; actualmente requiere cargar y verificar la sesión antes de desconectarse. Tras ocultación/pérdida de identidad se requiere verificar de nuevo online.
- Captura móvil/escritorio nativa con SQLite cifrado, custodia hardware y validación en Android/iOS/equipos reales.
- Sincronización de más tipos de borrador, conflictos de dominio, revisión de revocaciones al reconectar y recuperación ante pérdida/evicción/cuota del navegador.
- Catálogo y exportación/importación de borradores cifrados, backup/restauración y política de retención/borrado. Actualmente la recuperación requiere UUID conocido y contraseña correcta en el mismo almacén del navegador.
- Evaluación de KDF/entropía/latencia en dispositivos objetivo, CSP y dependencias del origen. IndexedDB no equivale a custodia hardware ni WORM.
- No atribuir a la rotación local del borrador recuperación de KEK/documentos fiscales; H11 mantiene sus requisitos propios.

No se realizaron commits, push, cambios en main, despliegues, pagos, envío a servicios externos ni solicitudes DIAN/bancarias reales. Los restantes hitos conservan desarrollo local y cualificaciones externas pendientes.

## Verificación final ejecutada

- **437 pruebas Python aprobadas**, regresión contable de ambos backends con fuentes estables.
- **303 comprobaciones Chromium aprobadas**: 50 ERP, 27 corporativas, 52 apertura/políticas, 28 nómina, 32 conciliación, 32 hoteleras, 32 ambientales, 32 offline en ambos paneles y 18 de cifrado/IndexedDB.
- TypeScript estricto de cuatro componentes sin errores; sintaxis de los dos módulos JavaScript verificada. No se acredita build Next completo.
- Suite `/tmp/sgacd-offline-58-final` con verificación de hashes y coincidencia de fuentes actuales. Los 48 escenarios PostgreSQL de la entrega57 son evidencia histórica: no se repitieron aquí, pues esta entrega no añade esquema ni escritura backend.
- Registro de avance, siete pruebas de cálculo de porcentaje y documento canónico de pendientes de billetera comprobados. No se acredita seguridad física ni producción con estos datos sintéticos.
