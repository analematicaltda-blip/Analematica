# Implementación63 · Firma XAdES local de laboratorio

**Avance global: 58,33 % (42/72), sin créditos duplicados.** H08 pasa de pendiente a ejecución: 4 hitos verificados localmente, 14 en ejecución y 2 pendientes. No se declaran subsanados los20 hitos ni habilitación productiva. ACC-009 ya tenía incremento y verificación acreditados; ampliar sus capacidades no suma nuevamente esos hitos.

## Cambio funcional

Se implementó un firmante real XAdES RSA-SHA256 en `DESKTOP/fiscal-signer`, ejecutado exclusivamente en el host del cliente. Recibe el paquete cifrado del navegador, comprueba HMAC y AES-GCM, exige coincidencia con los bytes originales revisados, valida la cadena y política restringidas de laboratorio y firma el borrador UBL. El resultado se vuelve a cifrar con DEK/IV nuevos, revisión incrementada y vínculo al digest anterior. No modifica el original ni escribe XML o llave descifrados al disco mediante el comando.

Se valida la firma generada y el contenido firmado contra la fuente revisada, además de verificar independientemente el valor RSA con cryptography. Referencias externas, entidades XML, firmas duplicadas o reubicadas, documentos alterados, llave incompatible, certificados vencidos, raíz equivocada, política distinta y extensiones críticas no soportadas se rechazan.

La CLI usa contraseñas sin eco y dos confirmaciones separadas antes de cargar la llave privada PKCS8 cifrada. Requiere terminal interactiva y archivos privados; crea la salida exclusivamente con0600 y nunca sobrescribe un archivo existente. La prueba positiva usa una terminal real de laboratorio para comprobar este recorrido, no solo llamadas directas a la biblioteca.

## Interoperabilidad verificada

El navegador Chromium abre el paquete firmado por Python mediante el SDK existente: autentica HMAC, recupera exactamente los bytes firmados, preserva una única firma y la revisión2, sin aceptar fiscalmente, cargar archivos ni escribir al ledger. El XML firmado también se valida contra el esquema UBL de referencia. Son datos/certificados efímeros de prueba, no identidades ni facturas reales.

## Límites obligatorios

Solo se admite `LABORATORY_ONLY`, política URN local y certificados con OU explícita de laboratorio. Se comprueba una cadena restringida raíz/hoja RSA fijada por huellas, no PKIX completo ni revocación/OCSP/CRL/TSA. La clave permanece temporalmente en memoria Python/OpenSSL: no se acredita Secure Enclave, HSM ni borrado forense.

Las dos confirmaciones locales no son un broker de autorizaciones remotas ni permisos financieros. La biblioteca es importable para pruebas; no se conecta al motor de control ni habilita autoaprobaciones. H18 sigue pendiente.

`fiscal_accepted`, `dian_profile_validated`, `hardware_custody_verified`, `trusted_timestamp_verified` y `ledger_written` permanecen falsos. No hay solicitudes DIAN, llamadas bancarias, pagos, despliegue externo, cambios en main ni commits.

La [guía operativa](OPERACION_FIRMANTE_LOCAL.md) especifica entradas, ejecución, restricciones y requisitos de cualificación. Faltan certificado legítimo, política/anexo DIAN vigentes, custodia y recuperación reales, pruebas profesionales y recepción de acuses auténticos para cerrar H08/H09.

## Verificación final

- **476 pruebas Python aprobadas, sin omisiones**, en32 suites contables, incluidas24 del nuevo firmante y33 del puente corporativo. Fuentes estables y hashes de evidencia comprobados contra el árbol actual.
- Las24 pruebas incluyen6 comprobaciones reales del SDK en Chromium, un documento firmado válido contra el XSD UBL de referencia, verificación RSA independiente y ejecución positiva de la CLI en terminal sin eco de contraseñas. Estas comprobaciones están incluidas en la suite; no se suman otra vez al total Python.
- Dependencias compatibles (`pip check`), siete pruebas del cálculo de avance, registros/documentos canónicos y `git diff --check` aprobados.
- PostgreSQL52 y navegador424 de la entrega62 se conservan como evidencia histórica; no se presentan como reejecutados en esta entrega centrada en firma. No se acredita aceptación de producción.
