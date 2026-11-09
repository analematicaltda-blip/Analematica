# Implementación 19 · Ensayo de respaldo y restauración del ledger PostgreSQL

**Avance: 27,78 % (20/72 hitos).** Se refuerza ACC-024, ya puntuado por incremento y pruebas. No se acredita recuperación productiva integral.

## Ensayo reproducible

La suite PostgreSQL crea un ledger sintético en una base desechable, ejecuta los contratos existentes y genera un respaldo `pg_dump` en formato custom. El archivo se crea con permisos 0600 dentro de un directorio privado. Se restaura con `pg_restore --exit-on-error` en otra base nueva; no sobrescribe la fuente. Ambas bases y el archivo se eliminan al terminar, incluso ante error.

Compara origen, restauración y origen tras el ensayo mediante un digest determinista que incluye todas las filas de tablas creadas por el fixture, valores/estado de secuencias, columnas y tipos/defaults, restricciones e índices, incluidas secuencias IDENTITY, funciones contables y definición/estado de triggers. No publica filas, credenciales o archivos de respaldo en la evidencia; solo digests y conteos.

Verifica la cadena e invariantes del ledger para todas las empresas del fixture con asientos contabilizados. Comprueba que los controles SQL estén activos y que una modificación de cabecera contabilizada sea rechazada en la restauración. El recibo, outbox, auditoría, proyecciones y políticas quedan incluidos al comparar todas las tablas del fixture. Se exige igualdad de digest y que la fuente permanezca sin cambios.

La comprobación está integrada en la suite PostgreSQL existente; se ejecuta mediante el perfil local `--profile accounting --profile postgres`. El helper nuevo es un verificador exclusivo de fixtures, no un comando de restauración autorizado para bases productivas.

## Compatibilidad de la comparación

PostgreSQL puede reescribir el CHECK de estados de entrega desde un cast de array completo a casts por elemento. Se normaliza exclusivamente esa transformación conocida, conservando el conjunto exacto de estados y rechazando expresiones o dominios inesperados. Se añadieron pruebas unitarias y comprobaciones reales de aceptación de los cinco estados y rechazo de uno inválido. Las demás restricciones se comparan sin descartar diferencias.

## Límites de alcance

El ensayo usa `--no-owner --no-acl` y una cuenta de fixture: no valida recuperación de propietarios, permisos productivos ni credenciales externas. No restaura llaves maestras, archivos de bóveda, documentos BYOS, almacenamiento adjunto o información externa al fixture. No acredita RPO/RTO, disponibilidad regional, backup continuo, retención cifrada o recuperación ante ransomware. El digest no es una firma independiente ni valida la corrección económica de datos reales.

Faltan un procedimiento operativo y simulacro con infraestructura/roles reales, respaldo y recuperación de llaves bajo custodia del cliente, restauración de medios/documentos, pruebas independientes y medición de tiempos. Continúan el grafo de migraciones histórico y los demás pendientes del plan. No se cambia el runtime productivo, la base del usuario ni el diseño.

## Evidencia

Resultados finales en `evidencias/implementacion-19.json`: 109 métodos Python y 16 escenarios contables PostgreSQL aprobados. Se recuperaron 24 tablas, 197 filas, 9 secuencias, 195 columnas, 85 restricciones, 97 índices, 3 funciones contables y 6 triggers del fixture; se verificó la integridad de 16 empresas con asientos contabilizados. Origen y restauración coincidieron y la fuente quedó sin cambios. Sin commit ni push.
