# Implementación75 · Horas extra y recargos contabilizados

Se amplió el motor existente de nómina: además del salario base, ahora calcula y contabiliza horas extra y recargos declarados por trabajador. Conserva dos confirmaciones, reglas versionadas y un único asiento canónico. El detalle de liquidación y los costos por operación incluyen los suplementos, en ERP y Analemática.

## Resultados concretos

| Concepto del caso sintético | COP |
| --- | ---: |
| Salario base por días declarados | 500,00 |
| Hora extra:120 minutos, divisor200, factor12500 puntos básicos | 12,50 |
| Recargo:60 minutos, divisor200, factor3500 puntos básicos | 1,75 |
| Devengado | 514,25 |
| Deducción declarada sobre devengado | 20,57 |
| Neto por pagar | 493,68 |
| Aporte patronal declarado | 61,71 |
| Provisión declarada | 41,14 |
| Costo contabilizado | 617,10 |

**Estas tasas y divisores son datos de prueba, no valores legales recomendados.** En el recorrido de dos operaciones y capacidad con respaldo parcial,308,55 permanecen sin asignar; no se atribuye artificialmente todo el costo.

## Bloqueos subsanados

1. El salario base era el único devengado admitido: nuevo cálculo exacto de minutos, factor y divisor horario, sin coma flotante.
2. No existía base explícita para contribuciones con suplementos: cada componente debe declarar `BASE` o `GROSS`; falta de base bloquea.
3. La proyección mostraba cero en horas extra/recargos: se persisten y cotejan contra la revisión; alterar un detalle invalida la recuperación.
4. Los costos operativos solo tomaban salario base: ahora toman devengado completo, más aportes y provisiones revisados.
5. Dos planillas podían volver a causar salario base del mismo trabajador en períodos superpuestos: revisión y posteo lo bloquean. Incluso dos borradores revisados antes del primer posteo se vuelven a verificar al confirmar. El reintento de la planilla original recupera el mismo asiento.
6. Faltaban controles de captura: formulario compartido con activación explícita, divisor, factores, base de componentes, minutos y huella por trabajador. Editar invalida las autorizaciones. No se alteró la navegación ni la identidad visual.

## Verificación

**776 pruebas Python aprobadas en44 suites, sin omisiones**, incluidas71 del puente corporativo. Fuentes actuales estables y hashes de registros comprobados.16 pruebas nuevas ORM cubren redondeo, detalle, costo, reglas inválidas, evidencia, duplicados, período, contrato alterado, dos confirmaciones y planillas superpuestas. Un recorrido HTTP corporativo nuevo y68 comprobaciones Chromium entre suplementos y regresión de nómina base. Tipos estrictos de componentes seleccionados aprobados.

[Evidencias y registros](evidencias/implementacion-75.json) · [ERP](evidencias/implementacion-75-erp.png) · [Analemática](evidencias/implementacion-75-corporate.png).

## Límites que impiden cerrar R10

El propietario declara minutos y reglas respaldados: el sistema no determina automáticamente qué minuto es nocturno, dominical, festivo o extra. Falta enlazar individualmente los minutos a jornadas y reglas legales vigentes revisadas. Las novedades heredadas, ausencias e incapacidades siguen bloqueando el modo acotado para evitar omitirlas. Faltan viáticos, otras deducciones, nómina electrónica y cualificación productiva. Una segunda nómina de ajuste requiere su propio flujo revisado; no se reutiliza esta ruta de salario base.

**63,89% (46/72), aceptación completa0/24.** Se amplía ACC-013 ya acreditada, sin duplicar porcentaje. No se declara la subsanación de los20 hitos ni cumplimiento oficial por pruebas sintéticas. Sin commits, push, pagos, despliegue ni transmisión DIAN.
