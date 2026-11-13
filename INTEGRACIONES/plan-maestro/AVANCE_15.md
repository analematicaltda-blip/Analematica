# Estado consolidado y continuación — 2026-11-07

El plan no está terminado. Las evidencias anteriores son cortes con alcance
limitado; su suma no certifica los tres productos de extremo a extremo.

| Frente | Comprobado en el repositorio | Falta para cerrar |
|---|---|---|
| F1 Arquitectura | Inventario y matrices institucional/ERP, procedencia de fuentes y mapa de módulos | Trazabilidad de cada pantalla a datos y flujo comprobado |
| F2 Backend/datos | Arranque Django de ambos sistemas, bases locales nuevas y CRM aislado | Reservas/disponibilidad concurrente, contratos contables, DIAN/RNT, migración histórica |
| F3 Identidad | Propiedad empresarial, jurisdicción y política personal/empresarial de billetera | SSO entre los tres productos y autoridad empresarial real |
| F4 Frontend | Centro compartido y panel público de billetera probado previamente | Recorridos autenticados completos y responsive en los tres productos |
| F5 Asistencia | Contrato de dos autorizaciones y confirmación de impacto; conectores y perfiles limitados | Ejecución supervisada con cuentas de prueba y dispositivos físicos |
| F6 Seguridad | Cifrado offline, controles nativos en fuentes, aislamiento y registro de pendientes | AiSOC con eventos reales, revisión externa y pruebas de hardware |
| F7 IA | Catálogo y rechazo explícito cuando no hay proveedor | Comparativa medida y contenido revisable con adaptador real |
| F8 Operación | CI, comprobaciones de esquema y utilidades de respaldo | Carga, PostgreSQL concurrente, releases firmadas y simulacro productivo |

## Cambio funcional de este corte

El recurso comercial de operaciones tenía filtros `estado`, `tipo_operacion`,
`fecha` y `perfil_ref_id` incompatibles con el modelo vigente. Su serializador
intentaba asignar `tenant` sin un contrato de identidad empresarial revisado.
El POS fabricaba una venta completada y una referencia `FAC-*` a partir del total
recibido. Esas entradas se conservan, autenticadas, con respuesta 503 explícita,
sin SQL ni emisión de factura. El CRM sigue habilitado y aislado por propietario.
Esto cierra una ruta insegura; no implementa ventas ni facturación.

Se añaden regresiones de rechazo, autenticación y ausencia de escrituras.
El workflow maestro ahora observa WALLET-BACKEND después de su traslado;
antes los cambios exclusivos de esa carpeta no activaban esas pruebas.

## Próximos paquetes verificables

| ID / prioridad | Responsable | Dependencia | Criterio de aceptación |
|---|---|---|---|
| NEXT-01 / crítica | Identidad y backend | Mapa TourismProvider ↔ empresa contable | Identificadores explícitos y verificados; rechazar empresa ajena, ambigua y revocada; nunca inferir equivalencia de UUID |
| NEXT-02 / alta | Backend comercial | NEXT-01 | Cotización/borrador con líneas y tarifas calculadas por servidor; idempotencia y aislamiento; no confirmar cobros sin recibo validado |
| NEXT-03 / alta | Frontend y QA | NEXT-01, CRM | Alta/consulta/edición de cliente en navegador por dos empresas; capturas y consola sin errores |
| NEXT-04 / alta | Identidad y frontend | Autoridad de administrador titular | Perfil personal opt-in y panel empresarial exclusivo; personal administrativo rechazado; WAL-019 |
| NEXT-05 / alta | Seguridad e infraestructura | Entorno AiSOC y contrato de evento sin secretos | Ingesta, detección sintética, trazabilidad y exportación; respuestas automáticas deshabilitadas |
| NEXT-06 / media | IA y automatización | Modelo local o proveedor habilitado | Guion → artefacto → revisión humana; medir coste, latencia y privacidad; sin publicación automática |
| NEXT-07 / alta | QA y operación | Hardware y releases | Android/iOS/escritorio reales, recuperación/revocación y respaldo restaurado; registrar resultados sin sustituirlos con mocks |

## Repetición local

`python BACKEND/INTEGRACIONES/plan-maestro/verify_local.py --output /tmp/informe-nuevo.json`
ejecuta suites fijas y aisladas con límite por proceso, conserva solo resultados
sin logs sensibles y falla si una suite no acredita pruebas. No migra bases,
no instala software, no despliega ni utiliza cuentas externas. Utilizar el Python
con las dependencias del proyecto. Un informe ya existente no se sobrescribe.

## Resultado de la comprobación actual

57 pruebas correctas: 18 jurisdicción/reseñas, 12 aislamiento de prestadores,
6 CRM/cierre comercial, 7 arranque ERP, 7 arranque Turismo y 7 acceso de billetera.
La petición inicial de test_platform.py no termina en este entorno; se registra
como TIMEOUT a los 180 segundos (foundation-evidence-15.json), no como aprobación ni como fallo funcional confirmado de Analemática.
No se realizaron pruebas nuevas de navegador, proveedores ni hardware en este corte.
