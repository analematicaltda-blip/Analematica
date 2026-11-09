# Implementación 60 · Borrador UBL local y validación estructural de referencia

**Avance global: 58,33 % (42/72).** Se acredita el incremento funcional y su verificación de ACC-009, antes vacíos; no aceptación completa. H07 pasa a ejecución: **4 paquetes verificados localmente, 11 en ejecución y 5 pendientes**, con aceptación completa0/24. No se declara completado el conjunto de20 hitos.

## Funcionalidad disponible en ambos paneles

El titular verifica la empresa y prepara un borrador UBL local con identificador declarado, UUID genérico de documento, fecha, emisor, comprador y línea de servicio. El generador compartido produce XML UBL, representación legible de importes e identidades y huella del contrato. La interfaz presenta una línea; el motor admite hasta50.

Todo se construye en memoria del cliente. No se envía XML ni texto claro a la API, no se descarga un documento sin cifrar y no se persiste el resultado en localStorage/IndexedDB. Cambiar campos invalida el resultado; perder identidad u ocultar/cerrar el panel lo retira. El panel mantiene azul, azul claro y texto blanco y se probó en móvil.

La salida está marcada **BORRADOR SIN FIRMA NI VALIDEZ FISCAL**. El UUID es un identificador genérico: no se genera ni simula CUFE. No se solicita numeración oficial, no se firma, no se emite, no se crea una solicitud fiscal ni se registra un asiento. Los bloqueos de envío DIAN existentes permanecen activos.

## Contrato y aritmética

El contrato exige empresa/UUID, identificador de borrador, fecha civil1900–2099, COP, identificaciones y nombres declarados y1–50 líneas con IDs únicos. Cantidad entera1–99999, precio unitario no negativo con hasta9 dígitos enteros y exactamente2 decimales, tasa entera0–10000 puntos básicos y clasificación gravada/exenta/excluida explícita. Exenta/excluida exige tasa0. Son declaraciones del usuario, no reglas tributarias calificadas.

Los importes usan BigInt en centavos, incluido el impuesto por línea con redondeo half-up. Se suman líneas ya redondeadas y se agrupan subtotales por categoría/tasa. No se utiliza float para cálculos monetarios ni porcentajes serializados. El contrato se copia antes de esperar operaciones asíncronas y su huella vincula empresa, identidades, líneas y cantidades.

Los nodos XML y HTML se construyen con APIs DOM y textContent; los textos no se interpretan como markup. Se rechazan campos inesperados, UUID/fecha incompatibles, cantidades fraccionarias, precios float/no finitos y tasas contradictorias. La identificación declarada no verifica existencia, NIT/dígito de verificación ni representación legal.

## Validación XSD y procedencia

Se conserva una copia mínima de14 esquemas con sus licencias/avisos y hashes, de revisiones fijadas de `phax/ph-ubl` y `phax/ph-xsds`. El header de la referencia dice **OASIS UBL2.1 CS1, 2013-06-16**. No se presenta como distribución aprobada por DIAN ni como anexo vigente.

Las dependencias CCTS/XMLDSIG/XAdES se cargan mediante un catálogo local de pruebas, pues algunos recursos del espejo importan solo por namespace. Los archivos copiados no se modificaron. El validador de desarrollo usa lxml6.0.2, sin red, DTD ni resolución de entidades externas; verifica los hashes y prueba que un documento vacío se rechaza. La presencia de esquemas de firma no implica firma implementada.

Cuatro documentos sintéticos generados por Chromium pasan el XSD de referencia: gravado, categorías mixtas, redondeo en medio centavo y valores que exceden la precisión entera segura de Number. **El navegador no ejecuta XSD**: valida el contrato y construye el documento. Los flags `xsd_validated_in_browser`, `dian_profile_validated`, `signed` y `fiscal_accepted` permanecen false.

Evidencia y capturas: [implementacion-60.json](evidencias/implementacion-60.json).

## Pendientes de H07/H08/H09

- Incorporar y cualificar el anexo/reglas DIAN vigentes, resolución/rango, prefijo, software, identidad/NIT/DV, direcciones y campos requeridos por tipo de documento. Los perfiles actuales son explícitamente locales y no fiscales.
- Integrar reserva/CRM y política tributaria revisadas con el contrato, documento y solicitud fiscal persistente; revisar notas crédito/débito, anticipos, retenciones, cargos/descuentos, divisas y cantidades fraccionarias.
- Completar representación requerida/PDF-A3 y el flujo de cifrado/custodia soberana antes de persistir documentos. La vista HTML actual no es PDF fiscal ni archivo de producción.
- Implementar firma XAdES y custodia cliente con cadena/política verificadas, transporte de habilitación y validación auténtica de acuses. Ninguna prueba local sustituye credenciales/certificados legítimos o aceptación de proveedor.
- Revisar accesibilidad, dispositivos reales, datos autorizados y aceptación profesional. No cerrar aceptación completa de ACC-009 usando solo los XSD de referencia.

No se hicieron commits, push, cambios en main, despliegues, pagos ni envíos DIAN/bancarios. Solo se consultaron repositorios públicos de esquemas; no se transmitieron documentos del cliente.

## Verificación final ejecutada

- **437 pruebas Python aprobadas**, con fuentes estables y regresión de las dos APIs contables de prueba.
- **359 comprobaciones Chromium aprobadas**: 50 ERP, 27 corporativas, 52 apertura/políticas, 28 nómina, 32 conciliación, 32 hoteleras, 32 ambientales, 44 offline/restauración, 24 criptográficas, 14 UBL/estructura y 24 UBL en ambos paneles.
- **4 documentos generados válidos contra el XSD de referencia**; 14 archivos XSD verificados por hash y caso sin contenido obligatorio rechazado. No se acredita perfil DIAN.
- TypeScript estricto de cuatro componentes sin errores; pip check sin dependencias rotas. No es un build Next completo.
- Suite `/tmp/sgacd-ubl-60-final`, hashes y coincidencia de fuentes actuales comprobados. Los 48 escenarios PostgreSQL de la entrega57 son evidencia histórica; no se repitieron en este incremento cliente sin nuevo esquema/escritura backend.
- Siete pruebas del porcentaje y documento canónico de pendientes de billetera comprobados. No hay aceptación física, profesional ni productiva.
