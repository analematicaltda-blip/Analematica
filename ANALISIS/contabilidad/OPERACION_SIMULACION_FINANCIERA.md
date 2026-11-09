# Orquestación financiera · ensayo persistente

Código canónico: `BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/financial_orchestration.py`. Usa el Outbox existente dentro de transacciones Django, sin crear un segundo ledger ni tablas nuevas. Requiere empresa activa, administrador personal activo y vínculo titular/empresa vigente, comprobados nuevamente en cada operación. Los usuarios marcados como agentes no pueden confirmar. No modifica permisos del motor agent-desktop/Open Duet.

## Contrato y recorrido

La intención exige exactamente: `schema=sgacd-financial-rehearsal-v1`, `company_id`, `request_id`, `purpose`, `amount`, `currency`, `beneficiary_ref` y `source_evidence_digest`. Los identificadores son UUID canónicos; `purpose` admite SUPPLIER_PAYMENT o PAYROLL_BATCH; `amount` es cadena decimal positiva con dos decimales y máximo12 enteros; `currency` debe ser COP. Beneficiario y evidencia son referencias, no números de cuenta, credenciales ni documentos claros. Una referencia NO acredita que exista una cuenta bancaria válida ni que el soporte sea legítimo.

En ERP, bajo el router contable existente, las rutas POST son:

1. `preparar-simulacion-financiera/`: `{intent, confirmed:true}`. Persiste la intención y devuelve `request_id`, `plan_digest`, `expires_at`. Preparar NO cuenta como las dos confirmaciones.
2. `confirmar-simulacion-financiera/`: `{request_id, plan_digest, step:1, confirmed:true}`.
3. La misma ruta con `step:2`, desde el mismo titular. Repetir step1 devuelve su confirmación anterior y nunca crea step2.
4. `simular-orden-financiera/`: `{request_id, plan_digest, confirmed:true, impact_confirmation:"SIMULAR <importe> COP A <beneficiary_ref>"}`. Exige las dos confirmaciones y revisión exacta del impacto.
5. `cancelar-simulacion-financiera/`: `{request_id, plan_digest, confirmed:true}`. Conserva evidencia y bloquea nuevas confirmaciones/simulaciones del request cancelado.

Analemática expone el mismo recorrido a través del puente corporativo autenticado, con operaciones `prepare_financial_rehearsal`, `confirm_financial_rehearsal`, `simulate_financial_rehearsal` y `cancel_financial_rehearsal` en su ruta contable de comandos. Conserva origen fijo, sesión del titular, protección CSRF y revalidación de vínculo. Verifica empresa, digest, solicitud, estado y los indicadores de ausencia de ejecución del resultado.

La vigencia local es cinco minutos desde preparación. Una solicitud nueva obtiene revisiones nuevas; cambiar importe, destino, moneda, evidencia o actor impide reutilizar las aprobaciones. El request es idempotente para contenido idéntico. Tras persistir una simulación, el reintento recupera el mismo resultado incluso después del vencimiento, siempre que la identidad/vínculo sigan válidos y se revise el mismo impacto. No renueva aprobaciones, no genera otra simulación ni convierte el resultado en autorización de pago. Las operaciones se serializan con el bloqueo contable de empresa; aún debe cualificarse la carrera específica en PostgreSQL y bajo fallos de infraestructura.

## Límites

Solo existe SIMULATED_ONLY: `payment_executed=false`, `bank_destination_verified=false`, `source_independently_verified=false`, `network_called=false`, `desktop_job_created=false`, `ledger_written=false` y `usable_as_payment_authorization=false`. `network_called` describe el núcleo de ensayo, no el HTTP interno usado por el puente corporativo.

No hay trabajador bancario ni RPA financiero, no se transmiten órdenes al motor de escritorio y no se acepta una predicción o ubicación como autorización. Las confirmaciones HTTP autenticadas no acreditan presencia humana, biometría, firma de hardware ni inmunidad frente al robo de sesión. El marcado de agente impide cuentas declaradas como tales; no identifica mágicamente a un programa que usa una sesión robada.

No hay formulario web nuevo: las rutas están disponibles para integrar posteriormente los controles visuales conservando la identidad azul/azul claro/blanco. Faltan verificación legítima de beneficiario y soporte, integración supervisada con el motor limitado, cuentas/proveedor, recuperación operacional y recibos, evaluación de seguridad independiente, pruebas de concurrencia PostgreSQL y aceptación profesional. H18 permanece EN_EJECUCION.
