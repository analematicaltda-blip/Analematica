# Implementación 26 · Validación estructural de sobres fiscales

**Avance: 30,56 % (22/72 hitos).** Se amplía ACC-010, ya puntuado; no se acredita almacenamiento BYOS, custodia o recuperación.

## Contrato de recepción

API ERP: `POST /api/v1/mi-negocio/contable/contabilidad/cuentas/validar-sobre-fiscal/?provider_id=<UUID>`.

Reutiliza titularidad, usuario activo y vínculo a Tenant verificado. Acepta exclusivamente el sobre v1 del SDK compartido, con empresa/documento canónicos, algoritmo, IV, llave envuelta y ciphertext. No acepta campos extra como plaintext, XML, PDF, KEK o llaves privadas. La empresa se contrasta con el vínculo autorizado; nunca se equipara el UUID del prestador al Tenant.

Valida esquema, codificación base64url canónica y longitudes. El preview acepta hasta 1 MiB de documento más el tag, inferior al máximo de 16 MiB de la primitiva cliente. Un parser JSON exclusivo de esta ruta lee como máximo 1.500.001 bytes y rechaza por encima de 1.500.000 antes de construir el JSON completo. No se aumentaron límites globales. La infraestructura aún debe definir sus límites de ingreso/concurrencia y revisar middleware/proxy.

La respuesta contiene digest determinista del sobre y metadatos mínimos. Siempre indica `STRUCTURAL_VALIDATION_ONLY`, autenticidad de ciphertext no verificada, documento fiscal no validado, `stored=false`, almacenamiento no habilitado y ausencia de asiento. No descifra, no recibe KEK, no guarda documentos y no activa BYOS.

Sin la llave, el servidor no puede demostrar que unos bytes opacos son un cifrado auténtico o un XML/PDF fiscal válido. Un sobre de forma correcta puede contener bytes arbitrarios; no se emite una certificación criptográfica ni fiscal. Rechazar campos de texto claro tampoco evita que un cliente malicioso envíe texto codificado como si fuera ciphertext. No se ha acreditado conocimiento cero de todos los caminos de carga o logs/APM existentes.

## Verificación

- 127 métodos Python aprobados, incluidos contrato estructural, campos prohibidos, alcance empresarial, digest estable ante orden de claves, codificación/tamaños y límite real de lectura del parser.
- 28 comprobaciones integradas de Chromium → sesión/CSRF Django → ORM aislado. Un sobre generado realmente por WebCrypto llega al validador; se rechazan campos extra, empresa ajena y petición sobredimensionada. La respuesta de tamaño confirma que se usó el parser específico, no solo el validador posterior.
- No se crean asientos o registros de documentos. Los bytes y llaves son sintéticos.

Evidencia: `evidencias/implementacion-26.json`. El perfil contable y workflow incluyen las pruebas nuevas. No hay cambios de esquema o algoritmos concurrentes; no se repitió PostgreSQL.

## Pendientes

Integración de formularios reales, firma/procedencia del cliente según modelo de amenaza, versionamiento/antirrollback, custodia/backup/recuperación de KEK, empaquetado XML/PDF y conectores BYOS/OAuth con revocación y fallo. Esta ruta no cambia los uploaders existentes ni autoriza producción. Siguen pendientes la consola corporativa Analemática y demás pools. Sin cambios de datos del usuario, commit o push.
