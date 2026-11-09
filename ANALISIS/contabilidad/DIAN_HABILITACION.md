# Ruta de habilitación DIAN · controles pendientes

La frontera actual **no envía** y **no aprueba** facturas. Se retiraron respuestas de aprobación, firmas-hash y CUFE simulados de facturacion/dian_service.py y gestion_comercial/dian_services.py. Los puntos de entrada se conservan para que los consumidores reciban un bloqueo explícito. Los registros históricos marcados como aceptados por esas rutas requieren auditoría con acuses auténticos; no se recalifican automáticamente.

## Disponible localmente

1. Revisiones persistidas de fuente/desglose y solicitud idempotente, separadas de reconocimiento de ingreso y pago.
2. Diagnóstico privado de configuración pública por empresa, mediante `ACCOUNTING_DIAN_PUBLIC_PROFILES` en settings. Solo metadatos: company_id, supplier_nit, resolution_number, prefix, range_start, range_end, next_number, valid_from, valid_until, environment=HABILITACION, software_id, test_set_id. No poner PIN, clave privada, contraseña de certificado ni token en este objeto ni en Git.
3. Detección de resolución vencida, rango agotado, identificadores incompletos, entorno prematuro y contexto ajeno. El diagnóstico no consulta registros oficiales ni verifica la titularidad legal.
4. Conciliación interna del pasivo tributario con las fuentes y contrapartidas contabilizadas.

## Dependencias para una emisión válida

- Identidad jurídica y tributaria, responsabilidades, resolución y rango oficialmente autorizados; clasificación turística/IVA/retenciones revisada por profesional competente.
- Definir proveedor tecnológico o integración directa, ambiente de habilitación y test set legítimo. No se inventan credenciales ni se usa producción para pruebas.
- Perfil UBL y reglas vigentes del anexo DIAN; validación XSD/Schematron y casos de factura, nota y contingencia aplicables. El hash fiscal debe corresponder a la fórmula normativa completa y sus datos oficiales.
- Firma XAdES-EPES y certificado vigente bajo custodia del cliente, cadena de confianza, política, revocación y reloj. Un hash de XML no firma nada. El modelo legado que almacena P12/password del lado servidor requiere migración de custodia revisada antes de reutilizarse; no se copian sus secretos a este diagnóstico.
- Transporte SOAP/WS-Security con endpoints fijos del entorno aprobado, control de tiempos, seguimiento de recepción/procesamiento, reintentos ante resultado incierto y numeración bajo bloqueo. No consumir un nuevo consecutivo por repetir una transmisión incierta.
- Validación criptográfica y semántica del ApplicationResponse/acuse, coincidencia documento/emisor/ambiente/CUFE y origen; rechazo, pendiente y aceptado son estados distintos.
- Cliente/agente soberano para generar/firmar/cifrar el documento y depositarlo en BYOS. No persistir XML/PDF en claro ni llaves privadas en logs/BD del proveedor. Resolver recuperación y disponibilidad legal del documento.
- Pruebas de habilitación y revisión profesional, respuesta rechazada/timeout/duplicado, restauración y carga. Publicar evidencia redactada sin certificados privados o secretos.

El entorno actual no tiene secretos DIAN configurados. La política de red observada permite gestores de paquetes, no acredita acceso a los servicios DIAN. No se realizaron intentos de transmisión ni se solicitaron secretos por chat.
