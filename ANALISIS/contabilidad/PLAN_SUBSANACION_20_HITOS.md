# Plan autónomo de subsanación · 20 hitos

Verificados localmente: **4/20** · En ejecución: **16** · Pendientes: **0**. Este conteo no equivale al porcentaje global ni a aceptación productiva.

Estos 20 paquetes ordenan la ejecución de las mismas 24 tareas contables. No sustituyen el denominador global de 72 hitos ni añaden porcentaje por documentar un plan.

**Modo de trabajo:** implementar una corrección concreta, ejecutar pruebas, conservar evidencia y continuar con el siguiente paquete habilitado. Un bloqueo externo deja registrado el requisito y permite avanzar en paquetes independientes. La automatización de pruebas no se presenta como implementación automática de código.

Los cambios locales reversibles ya están autorizados. Las aprobaciones de movimientos financieros, publicación y cuentas reales conservan sus reglas existentes. El 100 % requiere evidencias de los criterios completos, no solo archivos o simulaciones.

| Hito | Frente | Estado | Dependencias |
|---|---|---|---|
| H01 | Privacidad y aislamiento de facturas legadas | VERIFICADO_LOCAL | Ninguna |
| H02 | Recuperación de resultados corporativos inciertos | VERIFICADO_LOCAL | H01 |
| H03 | Paginación e historial de fuentes y cuentas | VERIFICADO_LOCAL | H02 |
| H04 | Cortes y snapshots financieros coherentes | VERIFICADO_LOCAL | H01 |
| H05 | Conciliación de legados, apertura y FX | EN_EJECUCION | H04 |
| H06 | Políticas tributarias versionadas y conciliación | EN_EJECUCION | H04 |
| H07 | Documento UBL y representación del cliente | EN_EJECUCION | H06 |
| H08 | Firma fiscal y custodia soberana | EN_EJECUCION | H07 |
| H09 | Transporte DIAN y validación de acuses | EN_EJECUCION | H08 |
| H10 | Carga cifrada y almacenamiento BYOS | EN_EJECUCION | H01 |
| H11 | Recuperación y rotación de claves/documentos | EN_EJECUCION | H10 |
| H12 | Guardas operativas y SG-SST | EN_EJECUCION | H01 |
| H13 | Nómina, provisiones y costos por servicio | EN_EJECUCION | H05, H12 |
| H14 | Extractos y conciliación bancaria segura | EN_EJECUCION | H05 |
| H15 | Ratios turísticos y calibración financiera | EN_EJECUCION | H04, H13 |
| H16 | Carbono, impacto y reportes ESG | EN_EJECUCION | H04 |
| H17 | Asistente contable en ambos sistemas | EN_EJECUCION | H04 |
| H18 | Orquestación financiera con autorizaciones | EN_EJECUCION | H14, H17 |
| H19 | Captura offline cifrada y sincronización | EN_EJECUCION | H11, H12 |
| H20 | Rendimiento, seguridad, recuperación y cierre | EN_EJECUCION | H01, H02, H03, H04, H05, H06, H07, H08, H09, H10, H11, H12, H13, H14, H15, H16, H17, H18, H19 |

## H01 · Privacidad y aislamiento de facturas legadas

**Hallazgo:** El viewset legado consultaba todas las facturas y serializaba XML en claro; el receptor de señales usaba un atributo de estado incompatible.

**Corrección:** Restringir cabecera y operación a la empresa verificada, exigir dueño/sesión y respuestas privadas, retirar XML/URL del listado y conservar operaciones sin aceptar facturas ficticias.

**Resultado local actual:** API legado restringido a dueño/empresa vinculada y relación factura/operación coherente; XML/URL retirados de los metadatos y altas operativas conservadas sin emisión DIAN ficticia. Pruebas locales de implementación49 y regresión posterior.

**Cierre local verificable:** Pruebas HTTP/ORM de dueño, empresa ajena, relación inconsistente, vínculo revocado, anonimato y documentos ausentes; alta operativa sin emisión ficticia.

**Matriz original:** ACC-005, ACC-007, ACC-008, ACC-024.

**Requisitos externos:** Ninguno para la corrección local descrita.

**Evidencia:** ANALISIS/contabilidad/evidencias/implementacion-49.json, BACKEND/deployment/tests/accounting_legacy_invoice_check.py

## H02 · Recuperación de resultados corporativos inciertos

**Hallazgo:** Un timeout posterior al despacho puede ocultar una escritura ya confirmada; falta recuperar el detalle de la revisión desde la consola.

**Corrección:** Añadir consulta por revisión persistida y estado/journal al puente, más reanudación segura de la interfaz.

**Resultado local actual:** Estado/revisión/historial recuperables con actor/empresa verificados; respuesta perdida tras commit recupera el mismo asiento, sin restaurar aprobaciones.

**Cierre local verificable:** Cortar respuesta después del commit, recuperar el mismo asiento y demostrar que el reintento no duplica; vínculo revocado deniega.

**Matriz original:** ACC-003, ACC-005, ACC-008.

**Requisitos externos:** Ninguno para la corrección local descrita.

**Evidencia:** ANALISIS/contabilidad/evidencias/implementacion-50.json

## H03 · Paginación e historial de fuentes y cuentas

**Hallazgo:** La selección de reconocimiento solo carga las primeras reservas y rechaza catálogos mayores de 500; falta reanudar revisiones.

**Corrección:** Implementar búsqueda y cursores estables por empresa, detalle de revisión y estados claros en ambos paneles.

**Resultado local actual:** Cursores y búsqueda acotada de cuentas, paginación de reservas e historial; navegación real con más de500 cuentas y20 reservas en ambos paneles.

**Cierre local verificable:** Recorrer más de 20 reservas y 500 cuentas sin omisiones/duplicados ni cruce empresarial; recuperar revisión vigente.

**Matriz original:** ACC-005, ACC-008, ACC-016.

**Requisitos externos:** Ninguno para la corrección local descrita.

**Evidencia:** ANALISIS/contabilidad/evidencias/implementacion-50.json

## H04 · Cortes y snapshots financieros coherentes

**Hallazgo:** Los reportes históricos no equivalen a un snapshot original de publicación; faltan garantías de corte consistente y diagnóstico de empresas inactivas.

**Corrección:** Consolidar lecturas bajo snapshot/primary explícitos y registrar metadatos del corte con errores accionables.

**Resultado local actual:** Reportes principales bajo bloqueo compartido de empresa/primary, rechazo de empresa inactiva/moneda histórica incompatible y referencia estable al último asiento; carrera PostgreSQL verificada.

**Cierre local verificable:** Posteo concurrente no mezcla cortes; moneda, fecha, integridad y origen verificables; empresa inactiva rechazada.

**Matriz original:** ACC-004, ACC-006, ACC-016.

**Requisitos externos:** Ninguno para la corrección local descrita.

**Evidencia:** ANALISIS/contabilidad/evidencias/implementacion-50.json

## H05 · Conciliación de legados, apertura y FX

**Hallazgo:** Saldos iniciales y valoraciones legadas requieren conciliación; faltan aperturas aprobadas y fuentes FX cualificadas.

**Corrección:** Crear propuestas trazables de conciliación/apertura con simulación y confirmaciones, preservando originales; reforzar política FX.

**Resultado local actual:** Apertura COP de primeros libros desde saldos originales balanceados, dos confirmaciones del mismo titular y prueba de origen persistida. También vincula un asiento existente exactamente coincidente, incluso en período cerrado, sin duplicarlo ni cambiar su hash. Reintento, fuente modificada, contrapartida y carreras verificadas en fixtures; pendientes legados no coincidentes, lotes mayores de100 cuentas, migraciones/valoraciones FX y soportes legítimos revisados.

**Cierre local verificable:** Descuadres/FX ausente bloquean; propuesta y asiento aprobado coinciden; repetición no duplica y contrapartida conserva historia.

**Matriz original:** ACC-001, ACC-004, ACC-006, ACC-015.

**Requisitos externos:** Saldos/documentos legítimos y revisión contable profesional; Fuente FX autorizada y vigencia para aceptación real

**Evidencia:** BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/opening_balances.py, BACKEND/deployment/tests/accounting_opening_check.py, ANALISIS/contabilidad/evidencias/implementacion-51.json

## H06 · Políticas tributarias versionadas y conciliación

**Hallazgo:** La conciliación interna existe; no hay aceptación de reglas normativas, retenciones ni cruce fiscal oficial.

**Corrección:** Modelar políticas revisadas por vigencia/empresa, trazabilidad de IVA y retenciones y discrepancias sin correcciones automáticas.

**Resultado local actual:** Políticas COP declaradas por el titular, versionadas y con vigencias no solapadas; cotización exacta por componente, categorías y nota crédito simulada. Implementación68 conecta versiones persistidas a revisión de reserva y reconocimiento explícito del ledger en ambos backends, revalidando fuente y evidencia. La cotización sola no crea documentos ni asientos. El flujo ligado es acotado a COP, un único código de impuesto positivo y fecha tributaria igual a contable; retenciones positivas y múltiples impuestos se rechazan. Pendientes posteo por componente, IVA descontable/retenciones, interfaz/recuperación completas, reglas normativas, contraste oficial y aceptación profesional/productiva. Implementación70 incorpora una ruta separada de hechos comerciales revisados con compra/venta, IVA descontable/generado, retenciones por componente y contrapartida canónica. Se verificó por API y puente HTTP; no relaja las restricciones de reservas ni completa fuentes nativas, conciliación unificada, devoluciones parciales, interfaz o aceptación tributaria. Implementación71 conecta conciliación integrada a ambos paneles y valida fuentes/sumas en lote; añade benchmark local reproducible,detecta547.209ms y reduce máximo a134.922ms en100 documentos sintéticos secuenciales. No acredita SLA productiva ni precisión IA. Implementación72: compras nativas operables en ambos paneles, catálogo con gastos y reserva de fuente/huella contra bypass, recuperación/contrapartida con dos confirmaciones; sin histórico, pagos, emisión o aceptación profesional completos.

**Cierre local verificable:** Casos con políticas sucesivas, exención, retención, devolución y contrapartida; cálculo exacto y explicación por componente.

**Matriz original:** ACC-014.

**Requisitos externos:** Normativa aplicable y revisión tributaria profesional; Datos/acuse oficial para contraste real

**Evidencia:** BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/tax_policies.py, BACKEND/deployment/tests/accounting_tax_policy_check.py, ANALISIS/contabilidad/evidencias/implementacion-51.json, ANALISIS/contabilidad/IMPLEMENTACION_68.md, ANALISIS/contabilidad/evidencias/implementacion-68.json, BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/commercial_tax_posting.py, BACKEND/deployment/tests/accounting_commercial_tax_check.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_commercial_tax.py, ANALISIS/contabilidad/IMPLEMENTACION_70.md, ANALISIS/contabilidad/evidencias/implementacion-70.json, ANALISIS/contabilidad/IMPLEMENTACION_71.md, ANALISIS/contabilidad/evidencias/implementacion-71.json, BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/tax_register.py, BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/tax_register_snapshot.py, BACKEND/SGA-CD-BACKEND/app/services/tax_register_contract.py, BACKEND/deployment/tests/accounting_tax_register_check.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_tax_register_contract.py, BACKEND/deployment/benchmark_accounting.py, BACKEND/deployment/accounting_benchmark_metrics.py, BACKEND/deployment/tests/accounting_benchmark_check.py, ANALISIS/contabilidad/IMPLEMENTACION_72.md, ANALISIS/contabilidad/evidencias/implementacion-72.json, BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/source_bindings.py, BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/compras/native_purchase.py, FRONTEND/ANALEMATICA-FRONTEND/js/native-purchases.js, FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-contable/indicadores-ledger/NativePurchases.tsx, BACKEND/deployment/tests/accounting_native_purchase_check.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_native_purchase.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_native_purchase_contract.py, FRONTEND/deployment/tests/native_purchases_browser.cjs

## H07 · Documento UBL y representación del cliente

**Hallazgo:** Los generadores legados eran incompletos y fabricaban CUFE; ahora están bloqueados.

**Corrección:** Implementar generación local del cliente, contratos completos y validación XSD/reglas; enlazar documento a solicitud sin centralizar el texto claro.

**Resultado local actual:** Borrador UBL COP local en ambos paneles, XML/representación en memoria, aritmética BigInt y contrato acotado; cuatro documentos sintéticos pasan XSD de referencia UBL2.1 CS1 con dependencias/procedencia conservadas. No valida XSD en navegador, perfil DIAN, firma, CUFE ni aceptación fiscal. Pendientes anexo vigente, integración CRM/política/solicitud, representación fiscal/PDF-A3, cifrado/custodia, campos tributarios/documentales completos y cualificación profesional. Implementación72: compras nativas operables en ambos paneles, catálogo con gastos y reserva de fuente/huella contra bypass, recuperación/contrapartida con dos confirmaciones; sin histórico, pagos, emisión o aceptación profesional completos.

**Cierre local verificable:** Identidad, numeración, líneas, impuestos y totales coinciden; documento inválido y datos faltantes bloquean; XML bien escapado.

**Matriz original:** ACC-008, ACC-009.

**Requisitos externos:** Anexo DIAN vigente, identidad/resolución y clasificación revisadas; Homologación de documentos y representación requerida

**Evidencia:** FRONTEND/ANALEMATICA-FRONTEND/js/accounting-ubl-draft.js, FRONTEND/deployment/tests/ubl_draft_browser.cjs, FRONTEND/deployment/tests/ubl_panel_browser.cjs, FRONTEND/deployment/tests/validate_ubl_reference.py, FRONTEND/shared/accounting/vendor/ubl21-reference/PROVENANCE.json, ANALISIS/contabilidad/IMPLEMENTACION_60.md, ANALISIS/contabilidad/evidencias/implementacion-60.json, ANALISIS/contabilidad/IMPLEMENTACION_72.md, ANALISIS/contabilidad/evidencias/implementacion-72.json, BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/source_bindings.py, BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/compras/native_purchase.py, FRONTEND/ANALEMATICA-FRONTEND/js/native-purchases.js, FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-contable/indicadores-ledger/NativePurchases.tsx, BACKEND/deployment/tests/accounting_native_purchase_check.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_native_purchase.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_native_purchase_contract.py, FRONTEND/deployment/tests/native_purchases_browser.cjs

## H08 · Firma fiscal y custodia soberana

**Hallazgo:** Faltan firma XAdES cualificada, recuperación y certificado bajo custodia del cliente.

**Corrección:** Integrar firmante local restringido, validación de cadena/política y pruebas con claves efímeras; mantener bloqueo productivo hasta cualificación.

**Resultado local actual:** Firmante XAdES restringido a laboratorio en equipo del cliente: entrada/salida cifradas, certificado/política fijados, doble revisión local y verificación criptográfica. No es firma DIAN cualificada ni custodia hardware; aceptación y recuperación reales pendientes.

**Cierre local verificable:** Cambiar documento, certificado, firma o política invalida; claves privadas no aparecen en servidor/logs; recuperación probada.

**Matriz original:** ACC-009, ACC-010.

**Requisitos externos:** Certificado legítimo del cliente y política de firma vigente; Validación de custodia/dispositivos/HSM que correspondan

**Evidencia:** ANALISIS/contabilidad/IMPLEMENTACION_63.md, ANALISIS/contabilidad/evidencias/implementacion-63.json, DESKTOP/fiscal-signer/local_signer.py, BACKEND/deployment/tests/accounting_local_signer_check.py

## H09 · Transporte DIAN y validación de acuses

**Hallazgo:** No existe transporte verificado; configuración local no acredita aceptación.

**Corrección:** Construir adaptador de habilitación con destinos fijos, resultado incierto, reintentos y verificación auténtica de ApplicationResponse.

**Resultado local actual:** Verificador criptográfico ApplicationResponse y diario SQLite solo de laboratorio en el host del cliente. Firma/identidad verificadas, estados de prueba separados, reintentos inciertos con identidad estable, concurrencia y recuperación idempotente. Sin transporte DIAN, numeración oficial ni acuse auténtico; pendientes SOAP/WS-Security, perfil/códigos/confianza oficiales y habilitación legítima.

**Cierre local verificable:** Aceptado/rechazado/pendiente distintos; acuse ajeno o alterado rechazado; timeout no consume nueva numeración ni duplica.

**Matriz original:** ACC-009, ACC-014.

**Requisitos externos:** Proveedor o acceso DIAN de habilitación autorizado; Credenciales, test set, red aprobada y acuses legítimos

**Evidencia:** ANALISIS/contabilidad/IMPLEMENTACION_66.md, ANALISIS/contabilidad/evidencias/implementacion-66.json, DESKTOP/fiscal-signer/receipt_validation.py, DESKTOP/fiscal-signer/receipt_journal.py, BACKEND/deployment/tests/accounting_dian_receipt_check.py

## H10 · Carga cifrada y almacenamiento BYOS

**Hallazgo:** Existe SDK y adaptador PG aislado; falta recorrido de carga autenticado, OAuth y operación de destinos del cliente.

**Corrección:** Conectar cliente cifrador a destinos permitidos con permisos mínimos, idempotencia y verificación de identidad/procedencia.

**Resultado local actual:** API independiente del cliente y PostgreSQL explícito con paquetes versionados, cadena de versiones, reintento, rol mínimo y guardas. Cliente directo HTTPS, token BYOS distinto del JWT, sin cookies/redirecciones y rechazo de campos en claro antes de enviar. Ruta de navegador/API/PostgreSQL y restore aislados; controles compartidos cerrados sin perfil aprobado. Pendientes propiedad/TLS/credenciales/perfiles reales, ambos paneles provisionados, operación/retención/commit incierto y cualificación independiente.

**Cierre local verificable:** Recorrido cifrar/subir/leer/descifrar y revocar acceso; caída no duplica; servidor del ERP no conserva documento claro.

**Matriz original:** ACC-010, ACC-011.

**Requisitos externos:** Almacenamiento/credenciales propiedad del cliente; Consentimientos OAuth y revisión de permisos reales

**Evidencia:** BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/customer_package_store.py, BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/customer_package_api.py, BACKEND/deployment/tests/customer_package_contract.py, BACKEND/deployment/tests/accounting_customer_package_check.py, FRONTEND/ANALEMATICA-FRONTEND/js/accounting-customer-store.js, FRONTEND/deployment/tests/customer_store_browser.cjs, ANALISIS/contabilidad/IMPLEMENTACION_62.md, ANALISIS/contabilidad/evidencias/implementacion-62.json

## H11 · Recuperación y rotación de claves/documentos

**Hallazgo:** Faltan custodia, recuperación, control de versiones y cualificación de medios de respaldo del cliente.

**Corrección:** Implementar recuperación/rotación sin entregar KEK al proveedor; versionar referencias y probar restauración consistente.

**Resultado local actual:** Paquete cifrado cliente con recuperación local, HMAC de metadatos, revisión/parent digest y rewrap de DEK con KEK nueva, integrado en ambos paneles. Contraseña/empresa/documento erróneos y manipulación rechazados; descargas sin red ni aceptación fiscal. Pendientes custodia/medios/hardware, política de recuperación, referencias/publicación soberana, conflictos de ramas/última versión y cualificación física. No revoca archivos antiguos ni recupera contraseñas perdidas.

**Cierre local verificable:** Rotación conserva autenticidad, revocación impide acceso y respaldo restaura documento más referencias sin exportar llaves privadas.

**Matriz original:** ACC-010, ACC-011, ACC-024.

**Requisitos externos:** Medios y política de recuperación del cliente; Validación física de custodia cuando aplique

**Evidencia:** FRONTEND/ANALEMATICA-FRONTEND/js/accounting-fiscal-package.js, FRONTEND/deployment/build_fiscal_runtime.cjs, FRONTEND/deployment/tests/fiscal_package_browser.cjs, FRONTEND/deployment/tests/fiscal_package_panels_browser.cjs, ANALISIS/contabilidad/IMPLEMENTACION_61.md, ANALISIS/contabilidad/evidencias/implementacion-61.json

## H12 · Guardas operativas y SG-SST

**Hallazgo:** No hay incremento acreditado de aptitud/EPP/fatiga; geolocalización no demuestra aptitud. Hallazgo adicional: SSTService usa un denominador fijo de10 trabajadores; faltan guardas efectivas de despacho/fatiga y revisión del alcance de acceso médico.

**Corrección:** Auditar módulos existentes e integrar guardas explícitas por actividad/rol y evidencias mínimas, con acceso médico restringido.

**Resultado local actual:** Implementación69 añade datos persistentes de autorización profesional cifrada, EPP, jornadas/descanso y revocaciones; permisos clínicos explícitos; despacho positivo de orden genérica con política provisionada y dos confirmaciones del titular; cierre hacia VALIDACION con jornada registrada, sin costo/nómina. Pendientes datos/habilitación profesional y política laboral legítimos, evidencia física/off-platform, procesos especializados, interfaces, migración histórica, PostgreSQL/concurrencia y custodia cualificada. No habilita producción ni actuación física.

**Cierre local verificable:** Aptitud vencida, EPP faltante o exceso de jornada impiden despacho; correcciones quedan auditadas y datos médicos segregados.

**Matriz original:** ACC-005, ACC-012.

**Requisitos externos:** Reglas SG-SST y validación profesional de riesgos/aptitud

**Evidencia:** BACKEND/deployment/tests/accounting_sst_check.py, BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/sg_sst/access.py, ANALISIS/contabilidad/evidencias/implementacion-52.json, ANALISIS/contabilidad/IMPLEMENTACION_67.md, ANALISIS/contabilidad/evidencias/implementacion-67.json, BACKEND/deployment/tests/accounting_dispatch_guard_check.py, BACKEND/deployment/tests/accounting_worker_safety_check.py, ANALISIS/contabilidad/IMPLEMENTACION_69.md, ANALISIS/contabilidad/evidencias/implementacion-69.json, BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/dispatch_authorization.py, BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/sg_sst/worker_data.py, BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/sg_sst/worker_data_service.py, BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/sg_sst/worker_data_views.py, BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/sg_sst/worker_data_guards.py, BACKEND/deployment/worker_dispatch_policy.py

## H13 · Nómina, provisiones y costos por servicio

**Hallazgo:** No hay hito verificado del vínculo operativo con nómina/provisiones/costos. Auditoría adicional52: reglas salariales 2024/2025 fijas, ausencia contada sin período y símbolo Ausencia sin importar; contabilizar_nomina crea borrador y marca CONTABILIZADA sin posteo verificado; acciones liquidar/contabilizar no consultan primero el objeto acotado. Corregir antes de habilitar nómina.

**Corrección:** Integrar novedades revisadas y reglas por vigencia al ledger, con centros de costo, corrección e idempotencia.

**Resultado local actual:** Nuevo flujo explícito en ERP y Analemática: contrato/días/parámetros declarados y cuentas revisados, segunda confirmación y asiento canónico de base/deducciones/aportes/provisiones, sin pago. Recuperación de resultado, reintento único, fuente cambiada y duplicación de período rechazados. Alcance1–10 empleados, COP y modo base sin novedades/ausencias; reglas laborales/nómina oficial/dimensiones turísticas completas pendientes. Las rutas legadas incompletas permanecen en503.

**Cierre local verificable:** Turno repetido no duplica provisión; recargo/viático y contrapartida trazables; cifras exactas y permisos segregados.

**Matriz original:** ACC-003, ACC-012, ACC-013.

**Requisitos externos:** Reglas laborales revisadas y datos legítimos de personal; Habilitación de nómina electrónica para aceptación oficial

**Evidencia:** BACKEND/deployment/tests/accounting_payroll_boundary_check.py, ANALISIS/contabilidad/evidencias/implementacion-52.json, BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/nomina/reviewed_payroll.py, BACKEND/deployment/tests/accounting_payroll_check.py, FRONTEND/deployment/tests/payroll_browser.cjs, ANALISIS/contabilidad/evidencias/implementacion-53.json

## H14 · Extractos y conciliación bancaria segura

**Hallazgo:** La aplicación de anticipos es declarada por el propietario; no existe conciliación bancaria independiente acreditada.

**Corrección:** Importar extractos con huellas/duplicados, proponer correspondencias y exigir revisión antes de asientos o aplicaciones.

**Resultado local actual:** Confirmación persistente de1–30 correspondencias únicas y liberación append-only, cada una con dos pasos del mismo titular. Reservas de línea/referencia impiden duplicación bajo bloqueo de empresa; recuperación y revisión tras contrapartida, datos derivados sin CSV/IDs originales, API y panel compartidos. No autentica extractos, no concilia saldos completos ni escribe asientos/pagos; pendientes fuente bancaria legítima, FX, lotes parciales/ambiguos y garantías operativas/SQL independientes. Entrega76 añade resoluciones explícitas, metadatos parciales con diferencias, reservas de referencias pendientes y selección ambigua; no divide importes ni concilia saldos completos. Los nuevos registros requieren lectorv2. Entrega77 añade saldos de apertura/cierre y cobertura del libro para períodos declarados COP, con calificación separada e invalidación por cambios retroactivos. No autentica el extracto ni amplía los límites de volumen.

**Cierre local verificable:** Archivo repetido no duplica; recibo ajeno/divisa/importe incorrectos no concilian; diferencia y origen quedan visibles.

**Matriz original:** ACC-008, ACC-015.

**Requisitos externos:** Extractos autorizados; Accesos bancarios mínimos si se integra API; ninguna dispersión automática

**Evidencia:** ANALISIS/contabilidad/evidencias/implementacion-50.json, BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/bank_reconciliation.py, BACKEND/deployment/tests/accounting_bank_reconciliation_check.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_bank.py, FRONTEND/deployment/tests/bank_reconciliation_browser.cjs, ANALISIS/contabilidad/evidencias/implementacion-54.json, ANALISIS/contabilidad/evidencias/implementacion-76.json, ANALISIS/contabilidad/evidencias/implementacion-77.json

## H15 · Ratios turísticos y calibración financiera

**Hallazgo:** Faltan ratios con denominadores operativos reales, ventanas de evaluación completas y cualificación de series.

**Corrección:** Integrar ocupación/cupos/paquetes verificados y ampliar backtesting/sensibilidad en ambos paneles.

**Resultado local actual:** Observaciones diarias versionadas de habitaciones físicas existentes, doble confirmación, cuentas operativas/exclusiones explícitas y RevPAR/GOPPAR desde ledger contabilizado por fecha económica y conocimiento. Cero/missing/unclasificado no calculan; no se usa inventario actual para pasado. UI/API ERP y corporativas. Pendientes ocupación/ADR/cupos/paquetes, denominadores independientes, calibración de series, datos legítimos y validación profesional.

**Cierre local verificable:** RevPAR/GOPPAR/margen concilian con ledger; división cero es no calculable; ventanas no anticipan información futura.

**Matriz original:** ACC-016, ACC-017.

**Requisitos externos:** Datos operativos reales y revisión de supuestos financieros

**Evidencia:** BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/contabilidad/tourism_metrics.py, BACKEND/deployment/tests/accounting_tourism_metrics_check.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_hotel.py, FRONTEND/deployment/tests/hotel_metrics_browser.cjs, ANALISIS/contabilidad/evidencias/implementacion-55.json

## H16 · Carbono, impacto y reportes ESG

**Hallazgo:** No existen hitos verificados de factores de emisión y reportes ESG; no se puede inferir pasivo financiero ambiental.

**Corrección:** Auditar módulos, registrar factores/unidades/versiones/evidencias y separar medición ambiental de obligación contable.

**Resultado local actual:** Estimación y registro persistente con doble confirmación, versiones explícitas e inmutables de factores, exclusión de actividades ya confirmadas y recuperación por revisión sin restaurar autorizaciones; ambos paneles/APIs. Sin asientos, pasivos ni créditos. Pendientes fuentes/soportes legítimos, identidad operativa y duplicados semánticos, búsqueda/cortes/exportación, incertidumbre y reconocimiento profesional. Correcciones append-only con revisión de cabecera, dos confirmaciones, factores inmutables y recuperación del total efectivo en ambos paneles (implementación65); sin borrar/reclamar actividades originales ni generar asientos.

**Cierre local verificable:** Cálculo reproducible, correcciones sin duplicar compensación y reporte con fuente/unidad; ninguna certificación ficticia.

**Matriz original:** ACC-018, ACC-019.

**Requisitos externos:** Factores y marcos aplicables revisados; Evidencia legítima de compensaciones/obligaciones

**Evidencia:** BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/environmental.py, BACKEND/deployment/tests/accounting_environmental_check.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_environmental.py, FRONTEND/deployment/tests/environmental_browser.cjs, ANALISIS/contabilidad/IMPLEMENTACION_56.md, ANALISIS/contabilidad/evidencias/implementacion-56.json, BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/contabilidad/environmental_records.py, BACKEND/deployment/tests/accounting_environmental_records_check.py, FRONTEND/deployment/tests/environmental_records_browser.cjs, ANALISIS/contabilidad/IMPLEMENTACION_57.md, ANALISIS/contabilidad/evidencias/implementacion-57.json, ANALISIS/contabilidad/IMPLEMENTACION_65.md, ANALISIS/contabilidad/evidencias/implementacion-65.json

## H17 · Asistente contable en ambos sistemas

**Hallazgo:** La consulta acotada ERP no cubre aún todo el recorrido corporativo ni un modelo abierto evaluado.

**Corrección:** Ampliar herramientas de consulta autorizadas y fuentes, primero deterministas; evaluar modelo privado con dataset.

**Resultado local actual:** Asistente corporativo de lectura conectado al ERP con fuentes trazables y rechazo de inyección. Falta comprensión abierta/modelo privado evaluado y dataset autorizado.

**Cierre local verificable:** Consultas explicables enlazan reportes; inyección y empresa ajena rechazadas; sin SQL libre ni escrituras desde el asistente.

**Matriz original:** ACC-005, ACC-020.

**Requisitos externos:** Dataset autorizado y evaluación de calidad/privacidad antes de modelo abierto

**Evidencia:** ANALISIS/contabilidad/evidencias/implementacion-50.json

## H18 · Orquestación financiera con autorizaciones

**Hallazgo:** No hay hito verificado de dispersión/RPA financiera; una predicción o ubicación no autoriza pagos.

**Corrección:** Integrar borradores de tareas al motor existente, dos autorizaciones del solicitante y confirmación de impacto ligada al payload.

**Resultado local actual:** Ensayo financiero persistente y acotado: titular/vínculo personal vigentes, dos confirmaciones separadas, importe/destino ligados al digest, revisión de impacto y un solo resultado recuperable. API ERP y puente corporativo HTTP comprobados; sin pagos/trabajador bancario/trabajos de escritorio. Pendientes UI, broker limitado, cuentas/recibos legítimos y cualificación operacional.

**Cierre local verificable:** Cambiar importe/destino invalida aprobaciones; reintento no duplica; prueba local sin ejecutar dinero real.

**Matriz original:** ACC-015, ACC-020, ACC-021.

**Requisitos externos:** Proveedor/cuenta y recibos verificados; Autorizaciones explícitas para pruebas reales de impacto

**Evidencia:** ANALISIS/contabilidad/IMPLEMENTACION_64.md, ANALISIS/contabilidad/evidencias/implementacion-64.json, BACKEND/deployment/tests/accounting_financial_orchestration_check.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_financial_rehearsal.py

## H19 · Captura offline cifrada y sincronización

**Hallazgo:** No hay aceptación de sincronización real en dispositivos; offline prepara datos y no liquida dinero.

**Corrección:** Integrar cola local cifrada, versiones, idempotencia y resolución de conflictos apropiada a cada campo.

**Resultado local actual:** Borrador ambiental individual cifrado en IndexedDB, recuperación/cambio de contraseña sin red, CAS entre pestañas y reanudación online con dos confirmaciones en ambos paneles. Exportación y restauración manual de copia cifrada con contraseña/contexto verificados, sin sobrescribir versiones diferentes ni restaurar autorizaciones. Pendientes arranque offline completo, más dominios, catálogo/retención/evicción, sincronización ampliada, SQLite/custodia nativa y dispositivos reales.

**Cierre local verificable:** Desconexión/reconexión no pierde ni duplica novedades; conflicto visible; aprobaciones vencidas no se reutilizan.

**Matriz original:** ACC-003, ACC-010, ACC-022.

**Requisitos externos:** Dispositivos Android/iOS/escritorio y pruebas físicas de custodia/sincronización

**Evidencia:** FRONTEND/ANALEMATICA-FRONTEND/js/accounting-offline.js, FRONTEND/deployment/tests/offline_drafts_crypto_browser.cjs, FRONTEND/deployment/tests/offline_drafts_browser.cjs, ANALISIS/contabilidad/IMPLEMENTACION_58.md, ANALISIS/contabilidad/evidencias/implementacion-58.json, ANALISIS/contabilidad/IMPLEMENTACION_59.md, ANALISIS/contabilidad/evidencias/implementacion-59.json

## H20 · Rendimiento, seguridad, recuperación y cierre

**Hallazgo:** No están acreditados 250 ms, precisión IA, roles productivos completos, RPO/RTO ni restauración soberana integral.

**Corrección:** Ejecutar regresión integrada, carga con métricas, revisión de privilegios y ensayo de restauración; consolidar entrega sin commits parciales.

**Resultado local actual:** Regresión Python/PostgreSQL/navegador y restore ejecutados. Faltan benchmark con hardware objetivo, precisión IA, roles y recuperación productivos y cierre de dependencias. Implementación71 conecta conciliación integrada a ambos paneles y valida fuentes/sumas en lote; añade benchmark local reproducible,detecta547.209ms y reduce máximo a134.922ms en100 documentos sintéticos secuenciales. No acredita SLA productiva ni precisión IA. Implementación72: compras nativas operables en ambos paneles, catálogo con gastos y reserva de fuente/huella contra bypass, recuperación/contrapartida con dos confirmaciones; sin histórico, pagos, emisión o aceptación profesional completos.

**Cierre local verificable:** Informe reproducible con percentiles/máximo, errores y límites; restore y permisos probados; criterios pendientes impiden declarar 100%.

**Matriz original:** ACC-001, ACC-002, ACC-003, ACC-007, ACC-023, ACC-024.

**Requisitos externos:** Infraestructura/hardware objetivo, roles/grants y llaves/medios reales; Aceptaciones profesionales/proveedor pendientes; aprobación final de publicación

**Evidencia:** ANALISIS/contabilidad/evidencias/implementacion-50.json, ANALISIS/contabilidad/IMPLEMENTACION_71.md, ANALISIS/contabilidad/evidencias/implementacion-71.json, BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/tax_register.py, BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/tax_register_snapshot.py, BACKEND/SGA-CD-BACKEND/app/services/tax_register_contract.py, BACKEND/deployment/tests/accounting_tax_register_check.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_tax_register_contract.py, BACKEND/deployment/benchmark_accounting.py, BACKEND/deployment/accounting_benchmark_metrics.py, BACKEND/deployment/tests/accounting_benchmark_check.py, ANALISIS/contabilidad/IMPLEMENTACION_72.md, ANALISIS/contabilidad/evidencias/implementacion-72.json, BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/source_bindings.py, BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/compras/native_purchase.py, FRONTEND/ANALEMATICA-FRONTEND/js/native-purchases.js, FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-contable/indicadores-ledger/NativePurchases.tsx, BACKEND/deployment/tests/accounting_native_purchase_check.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_native_purchase.py, BACKEND/SGA-CD-BACKEND/tests/test_corporate_ledger_native_purchase_contract.py, FRONTEND/deployment/tests/native_purchases_browser.cjs
