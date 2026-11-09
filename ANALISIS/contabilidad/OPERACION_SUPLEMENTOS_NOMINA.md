# Operación de suplementos de nómina declarados

La ruta existente `review_payroll` admite la ampliación opcional; `post_payroll` y recuperación conservan sus contratos. Ambas versiones usan las mismas reglas y el mismo ledger.

## Contrato

Si `policy.earning_rules` está presente, incluye de1 a8 reglas con `code`, `kind` (`OVERTIME` o `SURCHARGE`), `rate_bps` entero positivo y `hour_divisor` entero positivo. El factor es el que se paga sobre la hora salarial; no se añade automáticamente100%. Para recargo se declara únicamente el factor adicional cuando ese sea el criterio revisado. No hay tasas legales por defecto.

Cada componente de deducción, aportes o provisión debe añadir `basis: BASE|GROSS`. Cada trabajador debe añadir `earnings`, arreglo de0 a8 objetos con `code`, `minutes` enteros positivos y `evidence_digest`. Una regla puede aparecer una sola vez por trabajador. Lista vacía significa ausencia explícita de suplementos; minutos cero no se envían. La suma de minutos declarados se limita a la duración física del período; no sustituye validación individual de jornadas ni detecta solapamientos por horario.

La fórmula, en centavos, es `salario_contractual × minutos × factor_bps / (divisor_horario ×60 ×10000)`, con redondeo half-up por componente. `GROSS` usa salario base más suplementos; `BASE` usa únicamente salario base. El devengado y el detalle de horas extra/recargos se conservan en la instantánea y se cotejan al recuperar. Una versión de política ya declarada no puede cambiar de tasas, divisor o bases.

El formulario compartido permite activar **Incluir horas extra y recargos declarados**; exige revisar los parámetros con el responsable laboral. Para el modo de captura actual se declaran ambos factores; un trabajador sin minutos en una categoría declara cero en el campo correspondiente. La política es común y los minutos/huellas son individuales. No se genera ni transmite nómina electrónica y no se dispersa dinero.

Sin `earning_rules`, la política y trabajadores mantienen exactamente el contrato histórico de nómina base. Las novedades existentes no compatibles siguen bloqueando; no son ignoradas ni transformadas en suplementos automáticamente.
