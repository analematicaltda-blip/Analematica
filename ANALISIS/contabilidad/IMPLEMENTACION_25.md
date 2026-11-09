# Implementación 25 · Primitiva compartida de sobre cifrado en cliente

**Avance: 30,56 % (22/72 hitos).** ACC-010 incorpora un incremento funcional y verificación automatizada; no acredita bóveda completa, custodia real o recuperación productiva. La base permanece en 24 tareas.

## Implementación

SDK TypeScript compartido en `FRONTEND/shared/accounting/fiscalEnvelope.ts`, independiente del backend y de los wrappers nativos de billetera. Cifra bytes de documento en el navegador con DEK aleatoria de 256 bits por operación, AES-256-GCM, IV aleatorio de 96 bits y tag de 128 bits. Envuelve la DEK con una KEK AES-KW-256 no extraíble suministrada por el cliente. El SDK no crea una política de custodia ni conserva la KEK.

AAD determinista vincula esquema/algoritmo, empresa, documento y propósito fiscal. La lectura valida campos exactos, UUID, esquema, codificación base64url canónica y límites: 1 byte a 16 MiB de documento. Rechaza cambios de contexto, IV, wrapped key o ciphertext, KEK incorrecta, campos adicionales y formatos incompatibles.

El sobre contiene identificadores, IV, DEK envuelta y ciphertext; no nombre de archivo, documento en texto claro ni KEK. La rutina no realiza peticiones ni persiste información. La identidad/permiso real de empresa debe provenir del flujo autenticado integrador; un UUID o la posesión del sobre no autorizan acceso por sí solos.

Incluye `rewrapDocument`: verifica primero la autenticidad del ciphertext, cambia la KEK envolvente y conserva ciphertext/IV. El descifrado normal obtiene una DEK no extraíble. La DEK temporal de cifrado/rewrap debe ser extraíble internamente para wrapKey, pero no se devuelve. Se limpian buffers privados donde es posible; JavaScript/WebCrypto no garantizan borrado de todas las copias de memoria ni uso de Secure Enclave/HSM.

## Modelo de amenaza y límites

El objetivo es reducir exposición de documentos persistidos y detectar modificación de sobres cuando se use un cliente confiable y una KEK protegida. No protege frente a JavaScript activo malicioso/XSS, dispositivo comprometido o entrega de cliente alterada que capture datos antes de cifrar. La KEK no extraíble del navegador no demuestra custodia en hardware.

Rewrap no revoca sobres antiguos: quien conserve un sobre anterior y su KEK anterior aún puede leerlo. No detecta por sí solo replay/rollback de un sobre válido; requiere control de versiones y evidencia confiable fuera del sobre. Sin la KEK o una recuperación externa válida, el SDK no puede recuperar el documento. Tamaño, identificadores y momento de acceso siguen siendo metadatos visibles.

No se conectó ni reemplazó ningún uploader existente. No se acredita que las cargas actuales del ERP sean de conocimiento cero, ni se creó almacenamiento Drive/OneDrive/S3, permisos OAuth o acceso de operadores. El empaquetado XML/PDF, integración de ambos frontends, KEK del cliente, backup/recuperación, rotación/revocación completa, versionamiento, CSP/entrega confiable y auditoría independiente siguen pendientes.

## Verificación

10 comprobaciones criptográficas con WebCrypto real de Chromium y 15 rechazos esperados. Incluye datos binarios en múltiples bloques, DEK/IV nuevos, roundtrip, tamper, AAD, límites, rewrap y descifrado independiente del sobre en Node/OpenSSL con clave de prueba conocida. No se subieron documentos ni se llamó un servicio externo. Llaves y bytes son sintéticos.

Tipado TypeScript estricto del SDK sin errores; 119 métodos contables de regresión aprobados. Se amplió el manifest de fuentes para incluir TypeScript y los frontends compartidos/ERP/Turismo, y se prepararon las comprobaciones criptográficas en el workflow (no ejecutado remotamente, sin publicación).

Evidencia: `evidencias/implementacion-25.json`. No hay migraciones ni cambios de datos del usuario. Sin commit ni push.
