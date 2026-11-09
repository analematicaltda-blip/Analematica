# Implementación 28 · Recuperación del destino documental PostgreSQL

**Avance: 33,33 % (24/72 hitos).** Se refuerzan ACC-011 y ACC-024, ya puntuados. No se concede crédito adicional ni aceptación completa.

## Incremento operativo verificado

El perfil PostgreSQL ahora ejecuta un ciclo real `pg_dump` → archivo temporal privado → `pg_restore` en una base documental nueva, separada tanto del origen cliente como del ledger. La recuperación no llama al bootstrap del almacén: debe conservar por sí misma las tablas, la vinculación empresarial y los triggers.

El ensayo verifica los dos documentos sintéticos completos a través del adaptador y compara un digest ordenado de sus UUID, empresa, digest de sobre, bytes cifrados y fecha de creación, además de la vinculación y versión de esquema. Comprueba nuevamente el origen para detectar cambios. Una operación DELETE en la base restaurada debe fallar por el control de inmutabilidad; después vuelve a verificar sus documentos. El manifiesto está acotado a esta fixture de dos documentos, no es un exportador masivo productivo.

El archivo tiene permisos 0600, tamaño máximo de fixture de 8 MiB y se elimina al terminar; también se eliminan las bases temporales. El contenido documental permanece cifrado. El dump contiene metadatos de PostgreSQL y los identificadores de empresa/documentos; no se afirma cifrado integral del archivo. No incluye KEK del cliente. La fixture usa llaves sintéticas en memoria, que no acreditan recuperación de llaves de usuarios.

## Resultado

- Siete suites contables aprobadas: 127 métodos Python.
- Perfil PostgreSQL aprobado: 20 escenarios contables, con la recuperación documental incorporada al escenario BYOS, además de la restauración existente del ledger.
- Dos sobres recuperados idénticos; vinculación intacta, fuente sin cambios y borrado rechazado tras restaurar.
- Evidencia y fuente estables: `evidencias/implementacion-28.json`.

## Pendientes de aceptación

Roles y ACL no se restauran en este ensayo (`--no-owner --no-acl`). Deben revisarse y reprovisionarse en un despliegue real. Faltan custodia/cifrado integral y retención de respaldos, restauración con rol operativo, recuperación independiente de KEK, punto de recuperación y RPO/RTO medidos, versiones reales, gran volumen y fallos durante copia/restauración. El digest no es una firma ni una protección frente a un administrador malicioso.

BYOS continúa sin conectar formularios o endpoints de producción; el preview sigue sin almacenar. No se usaron datos reales ni se hicieron commit, push o despliegue. La consola corporativa de Analemática, otros proveedores BYOS y los demás criterios de la matriz siguen pendientes.
