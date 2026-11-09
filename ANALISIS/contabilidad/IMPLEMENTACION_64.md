# Implementación64 · Ensayo financiero persistente en ERP y Analemática

**Avance: 61,11 % (44/72), antes58,33 % (42/72).** Se acreditan por primera vez el incremento funcional y su verificación de ACC-021. No se acredita aceptación completa: permanece0/24. El plan de20 paquetes queda en4 verificados localmente,15 en ejecución y1 pendiente. No se declara 100%.

## Implementación

El núcleo contable incorpora un ensayo financiero persistente sobre el Outbox existente, sin tablas nuevas, sin crear un ledger paralelo y sin emitir dinero. Comprueba titular personal activo, empresa activa y vínculo empresarial vigente en cada paso; las cuentas marcadas como agentes se rechazan. La preparación no sustituye las dos confirmaciones separadas del mismo solicitante. La ejecución de ensayo exige además una frase que incluye importe exacto y referencia de destino.

La intención se fija por digest con esquema estricto, UUID de solicitud/empresa/beneficiario, propósito, COP, importe decimal exacto y digest de soporte revisado. Cambiar contenido, actor o referencia invalida su reutilización. Las revisiones vencen en cinco minutos. La cancelación conserva evidencia y bloquea continuar. Reintentar recupera el mismo resultado persistido; recuperar un resultado antiguo no renueva permisos ni produce una orden nueva.

Se incorporaron cuatro rutas ERP y cuatro comandos de puente corporativo de Analemática. Conservan sesión, CSRF, origen fijo y comprobaciones de identidad. El puente verifica empresa, intención, digest, solicitud, estado y todos los indicadores que deben permanecer falsos. No se añadieron formularios ni se cambió la identidad visual.

## Verificación y límites

Se probaron18 casos del núcleo/API y3 recorridos reales HTTP Analemática→ERP con almacenes desechables y autenticación de prueba. Cubren ambas revisiones, impacto incorrecto, destino/importe cambiados, vencimiento, cancelación, agente, otro revisor, vínculo revocado, contrato estricto, fallo de escritura y reintento; se compara que el ledger conserva sus cifras.

Los estados son exclusivamente SIMULATED_ONLY. `payment_executed`, `bank_destination_verified`, `source_independently_verified`, `desktop_job_created`, `ledger_written` y `usable_as_payment_authorization` son falsos. No hay proveedor bancario, verificación de cuenta/soporte, trabajador de dispersión ni conexión al ejecutor de escritorio. Las confirmaciones HTTP no acreditan biometría o presencia humana frente a una sesión comprometida.

La [guía operativa](OPERACION_SIMULACION_FINANCIERA.md) documenta contratos, rutas, vigencia y límites. H18 queda EN_EJECUCION, no cerrado. El hito H09 requiere todavía transporte DIAN y validación auténtica de acuses. Los demás paquetes abiertos conservan sus criterios de cierre en el [plan de20 hitos](PLAN_SUBSANACION_20_HITOS.md).

No se ejecutaron pagos, cuentas reales, envíos DIAN, despliegues externos, commits, push ni actualización de main.

## Regresión final ejecutada

- **497 pruebas Python aprobadas en33 suites, sin omisiones**, incluidas18 del nuevo núcleo/API y36 del puente corporativo (3 nuevas). La suma incluye las24 del firmante local de laboratorio.
- Hashes de evidencia y manifiesto de fuentes estables comprobados contra el árbol actual; `pip check` sin dependencias rotas.
- Siete pruebas del cálculo de avance y verificaciones canónicas del plan20/pendientes de billetera aprobadas; `git diff --check` limpio.
- No se repitieron las52 pruebas PostgreSQL ni las424 comprobaciones de navegador de la entrega62; se conservan como evidencia histórica. Este corte no modifica interfaces web, esquemas SQL, firma fiscal ni transporte DIAN.
