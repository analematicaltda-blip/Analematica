# Acuses y reintentos · laboratorio local del cliente

Implementación H09 en `DESKTOP/fiscal-signer/receipt_validation.py`, `receipt_journal.py` y `verify_receipt_local.py`. Reutiliza las dependencias fijadas del firmante local. No es un transporte DIAN ni una ruta del backend del proveedor.

## Verificación criptográfica

El verificador exige un ApplicationResponse UBL completo firmado con XMLDSig RSA-SHA256 y una sola referencia al documento raíz. Comprueba la cadena restringida raíz/hoja de laboratorio, huellas fijadas, vigencia y serial declarado del certificado. La firma se valida antes de extraer la semántica del contenido firmado.

El perfil público exige exactamente: `mode`, `company_id`, `document_id`, `invoice_number`, `invoice_fingerprint`, `sender_id`, `recipient_id`, `environment`, `leaf_sha256`, `root_sha256`, `certificate_subject_serial`. Todos son cadenas. Los identificadores empresa/documento son UUID canónicos; las huellas de certificado son SHA256 y la referencia documental es una cadena hexadecimal de96 caracteres. Esa referencia se compara como dato explícito; el módulo no calcula ni certifica CUFE.

Solo admite `mode=LABORATORY_ONLY`, `environment=HABILITACION-LAB`, CustomizationID SGACD-LAB-RECEIPT y ProfileID LABORATORY-ONLY, con certificados de OU SGACD LABORATORY ONLY. Los únicos códigos admitidos son LAB_ACCEPTED, LAB_REJECTED y LAB_PENDING: **son códigos propios de pruebas, no códigos oficiales DIAN**. No habilitar documentos reales cambiando el perfil.

Se rechazan referencias externas, DTD/entidades, firmas ausentes, duplicadas o desplazadas, contenido alterado, identidades ambiguas y coincidencias incorrectas de emisor, destinatario, entorno, número o huella documental. No se recibe un booleano `signature_valid` ni un callback del solicitante como sustituto de la verificación.

La CLI abre un paquete cifrado del cliente compatible con el SDK existente, pide la contraseña sin eco en una terminal interactiva y muestra únicamente el resumen:

```bash
python DESKTOP/fiscal-signer/verify_receipt_local.py \
  --input acuse-cifrado.json --profile perfil-acuse-laboratorio.json \
  --leaf certificado-laboratorio.pem --root raiz-laboratorio.pem
```

El paquete se autentica/descifra en memoria bajo el contexto empresa/documento. Perfil y paquete deben ser archivos privados; no se escriben el XML descifrado, certificados privados ni contraseña en un servidor. Esta CLI no solicita una clave privada. La ruta positiva de verificación criptográfica se prueba en biblioteca; la CLI tiene prueba de rechazo de entrada no interactiva. No se acredita una sesión física de usuario con esta prueba.

## Diario recuperable

`ReceiptJournal.initialize(path_absoluto)` crea exclusivamente una base SQLite local nueva en un directorio privado0700, con archivo0600. No sobrescribe una base existente ni inicializa/“repara” automáticamente una ruta al abrirla. Operaciones posteriores verifican versión y definición exacta de las cuatro guardas SQL append-only.

La preparación fija una sola identidad por empresa/documento: hash del perfil y hash declarado de los bytes firmados. Cambiar perfil o hash no permite reusar esa identidad. `begin_attempt` crea un identificador de intento local; `mark_uncertain` registra un resultado incierto informado por el llamador. Un reintento conserva la identidad original. Dos comienzos simultáneos no obtienen dos intentos activos. Un token de intento anterior se rechaza.

`apply_receipt` vuelve a verificar internamente firma e identidad y solo registra hashes, revisión y estado de laboratorio. Pendiente puede avanzar a aceptación/rechazo de laboratorio; un resultado terminal distinto se bloquea para investigación. El mismo acuse se recupera idempotentemente después de reabrir el archivo. No persiste XML, números de factura, NIT, referencia CUFE, contraseñas o llaves privadas. Conserva UUID de empresa/documento y metadatos/hash: el archivo **no es SQLCipher ni almacenamiento cifrado completo**.

El diario usa transacciones BEGIN IMMEDIATE y sincronización FULL. Las pruebas incluyen reintento, concurrencia local SQLite y rollback por fallo de escritura. Los eventos enlazan hashes y se limita la historia a256 eventos por documento; el límite bloquea en lugar de truncar silenciosamente. Las guardas y hashes no son WORM ni protegen frente a quien pueda reemplazar/coherentemente reescribir todo el archivo o eliminar su tramo final con privilegios.

## Estados y límites

PREPARED_LAB, IN_FLIGHT_LAB y UNCERTAIN_LAB describen el ensayo local, no una transmisión observada. PENDING_LAB_ONLY, ACCEPTED_LAB_ONLY y REJECTED_LAB_ONLY son resultados criptográficamente comprobados de un emisor de laboratorio fijado por el perfil. No son recepción, validación previa ni rechazo emitidos por DIAN.

`fiscal_accepted`, `dian_origin_verified`, `dian_profile_validated`, `usable_as_fiscal_acceptance`, `network_called`, `number_allocated` y `ledger_written` siguen falsos. El hash de documento es declarado por el llamador: el diario no lee ni comprueba bytes de la factura (`signed_document_bytes_verified=false`). No reserva numeración oficial ni prueba un timeout de red; únicamente conserva la identidad local durante la reproducción controlada de esos escenarios.

Faltan el anexo vigente, certificados/política oficiales, revocación/PKIX/TSA que correspondan, cliente SOAP/WS-Security cualificado, endpoints fijos aprobados, mapeo oficial de estados, identidad/resolución/credenciales/test set legítimos, numeración transaccional e integración con el flujo comercial, pruebas de habilitación y acuses auténticos. La frontera productiva `block_unverified_submission` permanece bloqueada.
