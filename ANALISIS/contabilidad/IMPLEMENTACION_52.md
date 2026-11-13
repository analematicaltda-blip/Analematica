# Implementación 52 · Privacidad y consistencia SG-SST

**Avance global: 47,22 % (34/72), desde 44,44 % (32/72). Nuevo incremento funcional ACC-012, de alcance parcial.** Se subsanan accesos entre empresas y el cálculo ficticio de accidentalidad. No se certifica aptitud ni se habilita despacho turístico. H12 y H13 continúan en ejecución. Hay 4 paquetes verificados localmente, 7 en ejecución y 9 pendientes; aceptación completa 0/24. No están cerrados los 20 paquetes.

## Aislamiento y datos clínicos

Los endpoints SST exigen titular activo, proveedor propio seleccionado y vínculo TourismProvider/Tenant vigente. No se usa perfil_prestador como prueba de propiedad ni se concede acceso por ser superadministrador. Las actividades quedan filtradas por empresa del plan y los cambios de plan se validan contra ese mismo ámbito. Se conserva crear/actualizar/eliminar tareas propias. Las respuestas incluyen private/no-store y Vary Cookie/Authorization, también ante rechazo.

Los registros de salud requieren adicionalmente un permiso Django explícito por acción (view/add/change/delete_saludocupacional), directo o de grupo. No se usa el bypass has_perm de superusuario. Revocar ese permiso se verifica de nuevo; cambiar el empleado hacia otra empresa se rechaza. No se otorgan permisos automáticamente. Este control no acredita título clínico ni consentimiento o custodia legal: siguen pendientes aprovisionamiento clínico, segregación profesional y almacenamiento/cifrado de históricos.

La propiedad de cada registro se obtiene del servidor; un provider contradictorio en el contenido se rechaza. Los rangos de probabilidad/consecuencia del riesgo se limitan a 1–4. Las escrituras vuelven a verificar empresa/vínculo con bloqueo y transacción, sin convertir esta revisión en una garantía de privacidad ante administrador de base de datos.

## Indicadores sin fuentes inventadas

Se elimina el denominador fijo de 10 trabajadores. El dashboard calcula observaciones del mes y año actuales, excluyendo registros futuros y otras empresas, con trabajadores ACTIVO de nómina como dotación observada. Sin trabajadores devuelve desconocido, no una tasa cero. No reconstruye meses anteriores con la dotación actual ni persiste una meta legal inventada. Los indicadores históricos legados se conservan pero se cuentan como no verificados en lugar de presentarlos como KPI certificados.

El cociente observado no equivale a tasa normativa de accidentalidad: falta población expuesta histórica. Cumplimiento de plan solo se calcula si existe un único plan activo del año y actividades. Los cálculos no escriben en nómina, ledger ni documentos fiscales.

## Auxiliares SST internos

Registrar incidente y suspender un proceso requieren ahora actor personal activo y proveedor explícito propio/vinculado. Los IDs del contexto no se adivinan. Se elimina el archivo ficticio en empresa 1 y se indica archive_created=false; una gravedad grave no se presenta como contención automática aplicada.

La suspensión queda acotada al proceso de esa empresa, no modifica estados finalizados ni añade el motivo sensible a la descripción. Auditoría contiene IDs y huella del motivo, no texto médico. Suspensión/auditoría son atómicas: si falla la auditoría, no cambia el proceso. Repetir una suspensión conserva un solo efecto. Es una corrección del auxiliar interno existente, no un nuevo flujo de control remoto ni un sistema completo de despacho autorizado.

## Límites y trabajo pendiente

Faltan comprobación profesional de aptitud vigente, evidencias EPP por trabajador/actividad y cálculo de fatiga/jornada; guardas transversales que impidan iniciar/reanudar una operación por cualquier ruta; registro/aprobaciones y pruebas de campo. El bloqueo interno aislado no evita por sí solo modificaciones desde otros servicios o SQL. Continúan pendientes pantalla clínica, permisos delegados cualificados, retención/consentimiento y protección de datos históricos. No se modificaron registros reales.

## H13 · Corrección de respuestas y accesos de nómina

La auditoría comprobó tasas/base2024/2025, ausencias sin período, un símbolo Ausencia no importado y una ruta que creaba un borrador contable y marcaba CONTABILIZADA sin posteo comprobado. Se retira esa ejecución incompleta: liquidar_periodo y contabilizar_nomina devuelven503 estable antes de consultar/modificar datos. No se ejecuta una liquidación obsoleta ni se entrega éxito contable ficticio, tampoco desde el auxiliar de agentes existente.

Las acciones HTTP verifican primero la planilla mediante un queryset acotado a empresa propia/vinculada: un UUID ajeno devuelve404 y un vínculo revocado deniega. Crear y corregir borradores propios permanece operativo. No se pueden enviar estado PAGADA/CONTABILIZADA ni referencias de asiento/orden de pago; tampoco editar o eliminar planillas con estado o efectos previos. Fechas invertidas y empresa contradictoria se rechazan; respuestas privadas/no-store. Los estados históricos se conservan y el serializador los identifica como NOT_VERIFIED, sin asumir que estén respaldados por un posteo.

Esto subsana accesos de esas rutas y el falso éxito; **no implementa la nómina completa y no recibe crédito ACC-013**. Siguen pendientes motor laboral vigente, novedades por turno/período, revisión y doble aprobación, mapeo de cuentas, causación/provisiones canónicas, reconciliación de estados históricos y documentos laborales oficiales. Los demás endpoints/auxiliares laborales requieren auditoría de sus relaciones, permisos y diagnósticos; no se declara todo el módulo aislado por este cambio.

La evidencia final de regresión y recuentos se conserva en [implementacion-52.json](evidencias/implementacion-52.json). Ningún resultado sintético acredita producción ni aceptación completa.

## Resultados reproducibles

- **330 pruebas Python aprobadas**, incluidas 14 nuevas SST y 8 de límites de planillas. Sin omisiones.
- **37 escenarios contables PostgreSQL aprobados** y restauración local. No son cualificación concurrente PostgreSQL de los nuevos auxiliares SST.
- **135 comprobaciones Chromium aprobadas** tras estos cambios: 53 ERP, 30 Analemática y 52 de aperturas/políticas. No se modificó la identidad visual.
- Controles de progreso/plan, pendientes de billetera y git diff --check aprobados.
- Perfil final con fuentes estables en `/tmp/sgacd-remediation-52-final`; reporte/log hashes conservados en evidencia52. Los ensayos intermedios con fuentes cambiantes no se presentan como cierre de regresión.

Para repetir: ejecutar `BACKEND/INTEGRACIONES/operacion/verify_local.py --profile accounting --profile postgres --output <directorio_nuevo>` con el Python del entorno de integración. Las pruebas usan bases aisladas y no deben apuntar a bases de clientes.

No se crearon commits ni se actualizó main. El 47,22 % corresponde a 34 de 72 hitos de la base original, no al porcentaje de paquetes cerrados ni a una aceptación productiva.
