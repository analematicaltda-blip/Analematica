# Implementación61 · Recuperación y rotación local de documentos cifrados

**Avance global: 58,33 % (42/72), sin nuevos créditos.** Amplía la protección cliente de ACC-010, ya acreditada. H11 pasa de pendiente a ejecución: **4 paquetes verificados localmente, 12 en ejecución y 4 pendientes**; aceptación completa0/24. No se declara completado el plan de20 hitos.

## Flujo operativo en ambos paneles

Después de preparar el borrador UBL, el titular puede cifrarlo y preparar un archivo descargable, recuperar ese archivo en memoria o rotar su protección. La contraseña se introduce localmente, no se almacena ni se envía a servidores. El archivo descargado solo contiene ciphertext, llave de datos envuelta, contexto, descriptor de derivación, autenticador y huellas.

La recuperación exige contraseña, empresa y UUID del documento correctos. La interfaz muestra el texto mediante textContent, sin ejecutar XML/HTML ni validar fiscalmente su contenido. Una contraseña incorrecta o manipulación del paquete se rechaza y conserva el paquete activo anterior. Editar las fuentes o perder identidad retira la vista y el paquete activo; los campos de contraseña se vacían al iniciar cada operación.

La rotación verifica el paquete original antes de crear la nueva versión. Conserva el ciphertext y la IV del documento, vuelve a envolver la misma DEK con una nueva KEK y registra el digest de la versión anterior. La descarga usa otro nombre de versión y el código no elimina archivos anteriores. Cancelar una descarga no garantiza que exista una copia externa: la custodia sigue siendo responsabilidad explícita del cliente.

## Recuperación desde un archivo conservado

1. Verificar la empresa en el panel.
2. Copiar el UUID de `sgacd-document-<UUID>-v<N>.json` al campo «UUID del documento borrador».
3. Elegir ese archivo, introducir su contraseña y recuperar en memoria.
4. Para rotar, indicar contraseña actual y nueva; conservar la descarga de la nueva versión junto con el historial autorizado.

«Paquete activo» identifica el archivo cargado en esta vista, no una declaración de que sea la última versión global. Recuperar un archivo antiguo es una consulta local legítima y no retrocede ningún asiento ni estado fiscal del servidor.

## Cifrado y autenticación del paquete

Se reutiliza el SDK canónico `FRONTEND/shared/accounting/fiscalEnvelope.ts`: AES-256-GCM con DEK aleatoria por creación de documento y AAD de empresa/documento; AES-256-KW para envolver la DEK. El archivo `fiscal-envelope-runtime.js` es una compilación reproducible de ese SDK, no una implementación criptográfica alternativa.

La opción portátil actual deriva la KEK en el navegador mediante PBKDF2-HMAC-SHA-256, 600.000 iteraciones y salt aleatoria de16 bytes. Una clave HMAC no exportable usa una derivación separada por dominio (`salt || UTF8('fiscal-package-auth')`). HMAC-SHA-256 autentica esquema, revisión, parent digest, descriptor y sobre completo; un digest SHA-256 canónico identifica el paquete autenticado.

El descriptor admite únicamente el algoritmo/iteraciones fijos. Se comprueban campos exactos, codificación canónica, UUID, contexto, versión y límites antes de recuperar contenido. El documento se limita a1 MiB y la importación a1.500.000 bytes; la contraseña tiene un mínimo de16 caracteres y máximo de1024 bytes UTF-8. La longitud no demuestra entropía: hace falta una frase larga, exclusiva y no predecible.

La KEK y clave HMAC se derivan como CryptoKey no exportables. Esto no es Secure Enclave/Keystore, ni impide a un script comprometido del mismo origen capturar la contraseña o el contenido desbloqueado. Se limpian buffers propios, pero strings/objetos JavaScript y copias internas no tienen borrado forense garantizado.

## Qué prueba y qué no prueba una versión

El autenticador detecta alteraciones por quien no conoce la contraseña y el parent digest enlaza las versiones generadas. No es firma fiscal, prueba de identidad legal, auditoría independiente, WORM ni consenso sobre la última versión. Dos custodios con una copia pueden crear ramas válidas; su conciliación/publicación soberana queda pendiente.

Rotar la KEK no revoca archivos exportados, contraseñas anteriores ni DEK ya conocidas. Una copia antigua continúa recuperándose con su contraseña original. Si la DEK o el contenido fueron comprometidos, se requiere una política de renovación/re-cifrado y respuesta a incidentes distinta de este rewrap.

No se almacena el paquete en la base central ni se conecta todavía el flujo de cliente con Drive/OneDrive/S3/PostgreSQL propios. H10 mantiene el trabajo de carga/identidad/permisos de destinos. Tampoco se recupera una contraseña perdida desde el servidor.

## Reproducción del runtime

Con esbuild0.25.11 disponible en `QUOTE_UI_DEPS`:

```sh
node FRONTEND/deployment/build_fiscal_runtime.cjs --check
```

Sin `--check` se reconstruye el activo desde el SDK TypeScript. Las pruebas también comprueban el SDK original y la equivalencia del activo, preservando el contrato criptográfico existente. No se agregaron dependencias criptográficas externas a la aplicación.

## Pruebas y límites pendientes

Las pruebas del paquete incluyen creación aleatoria, recuperación, contraseña incorrecta, empresa/documento ajenos, manipulación de metadatos/ciphertext, límites, preservación del original ante fallo y recuperación de una versión serializada. Node WebCrypto verifica de forma independiente el HMAC, deriva la KEK y abre el documento producido por Chromium.

Los dos paneles descargan y reabren archivos reales de prueba sin red, rotan a versión2, comprueban parent digest y conservación de ciphertext/IV y rechazan la contraseña antigua y una versión manipulada. Las identidades y documentos son sintéticos, sin pagos ni aceptación fiscal. Evidencia y capturas: [implementacion-61.json](evidencias/implementacion-61.json).

Pendientes: custodia hardware/HSM/KMS o proveedor cliente revisado; política de recuperación/escrow autorizada; publicación y referencias versionadas en almacenamiento soberano; conflictos de ramas/última versión; backups y medios reales; permisos, retención y pruebas físicas. La vista de recuperación soporta texto UTF-8; el SDK admite bytes, pero no se entrega aquí visor/representación fiscal de PDF u otros binarios.

Los campos `fiscal_accepted`, `uploaded` y `ledger_written` permanecen false en la recuperación. No se hicieron commits, push, cambios en main, despliegues, pagos ni envíos a proveedores/DIAN/bancos.

## Verificación final ejecutada

- **437 pruebas Python aprobadas**, regresión de ambos backends con fuentes estables.
- **412 comprobaciones Chromium aprobadas**: 50 ERP, 27 corporativas, 52 apertura/políticas, 28 nómina, 32 conciliación, 32 hoteleras, 32 ambientales, 44 offline/restauración, 24 criptográficas offline, 14 UBL/estructura, 24 UBL en paneles, 17 paquete/documento, 26 recuperación/rotación en paneles y 10 SDK original.
- Node verifica y descifra de forma independiente el paquete del navegador. Se conservan cuatro validaciones XSD de referencia UBL y las pruebas negativas del SDK; nada acredita perfil/firma DIAN.
- TypeScript estricto del SDK y cuatro componentes sin errores; runtime reproducible comprobado contra la fuente canónica. No se acredita build Next completo.
- Suite `/tmp/sgacd-package-61-final`, hashes y coincidencia de fuentes actuales comprobados. No se repitieron los 48 escenarios PostgreSQL históricos de la entrega57, al no añadir esquema/escritura backend.
- Siete pruebas del porcentaje y documento canónico de pendientes de billetera comprobados. Sin aceptación física, profesional ni productiva.
