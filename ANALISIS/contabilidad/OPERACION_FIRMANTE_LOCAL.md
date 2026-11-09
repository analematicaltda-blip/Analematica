# Firmante fiscal local · laboratorio

El código está en `DESKTOP/fiscal-signer`. Instalar sus dependencias en un entorno Python aislado mediante `pip install -r DESKTOP/fiscal-signer/requirements.txt`. Ejecutar únicamente en el equipo del cliente, sin registrar este comando en agent-desktop, Open Duet ni una ruta del ERP.

```bash
python DESKTOP/fiscal-signer/sign_local.py \
  --input paquete-cifrado.json --profile perfil-laboratorio.json \
  --key llave-laboratorio-pkcs8.pem --leaf certificado-laboratorio.pem \
  --root raiz-laboratorio.pem --policy politica-local.txt \
  --output paquete-firmado-cifrado.json
```

El paquete de entrada utiliza `sgacd-fiscal-package-v1`, producido por el SDK fiscal del navegador. El perfil JSON exige exactamente los campos `mode`, `company_id`, `document_id`, `supplier_nit`, `source_sha256`, `leaf_sha256`, `root_sha256`, `certificate_subject_serial`, `policy_id` y `policy_sha256`. Todos son cadenas. `mode` debe ser `LABORATORY_ONLY`; `policy_id` comienza por `urn:sgacd:lab-policy:`. Los UUID de empresa/documento, NIT y serial deben corresponder al borrador revisado y al certificado de prueba. Los SHA256 son hexadecimales de 64 caracteres, calculados sobre los bytes originales correspondientes; no introducir hashes arbitrarios.

La cadena admitida tiene exclusivamente una hoja RSA y una raíz RSA autofirmada, ambas con OU `SGACD LABORATORY ONLY`. La raíz es CA con path length cero; la hoja tiene uso de firma digital, no de CA, y EKU code signing. Se comprueban firmas, vigencia, extensiones críticas soportadas y huellas fijadas por el perfil. El certificado raíz no se incrusta como segunda hoja en KeyInfo: se valida externamente contra la huella aprobada. Un certificado real no se vuelve apto por cambiar el perfil: el firmante restringe explícitamente el uso a laboratorio.

La llave debe ser PKCS8 cifrado; perfil y llave requieren permisos privados (por ejemplo, 0600 en Linux). No se admiten archivos simbólicos ni archivos excesivos. El comando pide la contraseña del paquete y de la llave sin eco en terminal, y exige dos entradas distintas: `REVISADO <12 primeros caracteres del digest>` y `FIRMAR LAB <UUID del documento>`. No son autorizaciones financieras ni un mecanismo de aprobación remota resistente a suplantación. La biblioteca es importable para pruebas; no se ofrece como agente que pueda aprobarse a sí mismo.

El documento original se autentica y descifra en memoria. Solo se admiten borradores UBL Invoice marcados `SGACD-STRUCTURAL-DRAFT` / `LOCAL-UNSIGNED-DRAFT`. La firma XAdES usa RSA-SHA256 y referencias locales; se verifican la política y la correspondencia canónica con el documento revisado. El resultado se cifra con DEK e IV nuevos, incrementa la revisión y enlaza el digest del paquete anterior. La creación exclusiva 0600 impide sobrescribir el archivo de entrada u otro archivo existente. No se persiste XML ni llave en claro por este comando; el archivo PKCS8 original pertenece al cliente.

## Límites y pendientes productivos

Este perfil NO es firma fiscal DIAN cualificada. No hay validación oficial de identidad, PKIX completo, revocación OCSP/CRL, sello de tiempo confiable, certificado legítimo, HSM ni aceptación del anexo DIAN. `fiscal_accepted`, `dian_profile_validated`, `hardware_custody_verified`, `trusted_timestamp_verified` y `ledger_written` permanecen falsos. No existe envío de facturas, acceso bancario ni llamadas de red en el firmante.

Python/OpenSSL manejan objetos privados temporalmente en memoria; no se garantiza borrado forense, protección frente a un host comprometido ni aislamiento de hardware. Las dos revisiones locales no sustituyen las autorizaciones de negocio existentes. Faltan custodia y recuperación reales, dispositivos/HSM, revisión profesional de certificados/política, pruebas con identidades autorizadas y conectores fiscales cualificados. H08 permanece EN_EJECUCION; H18 no queda resuelto.
