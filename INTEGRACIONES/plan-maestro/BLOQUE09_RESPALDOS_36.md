# Bloque 9 — Respaldos cifrados y restauración

La referencia histórica del bloque9 en `auditoria-bloque01/README.md` corresponde a recuperación/restauración. Esta entrega continúa ese alcance dentro del frente F8, sin inventar un noveno frente del plan maestro.

## Implementado

- CLI reutilizable `BACKEND/deployment/encrypted_backup.py`: creación explícita de clave, backup SQLite, verificación y restauración hacia otra base.
- AES-256-GCM con clave independiente, nonce aleatorio y cabecera autenticada por servicio/versionado/hash. No se imprimen claves, datos ni rutas privadas en los resultados del CLI.
- Copia consistente incluyendo WAL, verificada en RAM; no se escribe una copia plana intermedia. La copia se vuelve autocontenida sin alterar el origen. Límite64MiB y copia limitada a60s.
- Destinos nuevos exclusivamente; rechaza sobrescritura, archivos auxiliares SQLite preexistentes, permisos inseguros de clave, alteración de archivo, servicio/clave incorrectos y relaciones inválidas. Un error de escritura elimina solo el archivo parcial que acaba de crear.
- Claves/archivos/bases restauradas0600. Se impide generarlos dentro del código versionable; permite rutas externas o directorios `.runtime` ignorados. No se regeneran claves existentes ni se modifica la conexión activa de ningún backend.
- Perfil `backup` integrado al verificador y workflow manual; ensayo `ContentDraft` actualizado para restaurar desde archivo cifrado con una clave de respaldo separada de las claves originales del aplicativo.
- Procedimiento y límites en `INTEGRACIONES/operacion/RESPALDOS.md`. Sin borrado automático por retención ni tareas programadas sobre datos reales.

La bandera `application_keys_included=false` indica que no se añadieron archivos externos de claves al respaldo. La base se copia completa, sin filtrar campos; las claves originales y configuración externas deben custodiarse aparte para descifrar los registros al recuperar el sistema.

## Evidencias

| Prueba | Resultado |
| --- | --- |
| Nuevas pruebas de respaldo | 14 aprobadas: cifrado, restauración, manipulación, permisos, claves/servicio erróneos, WAL, tamaño/plazo, errores de disco y no sobrescritura |
| Regresiones del verificador | 14 aprobadas |
| Compatibilidad de snapshots previos | 2 aprobadas |
| Restauración editorial | Modelo real ContentDraft en nueva base: texto cifrado recuperado, revisión conservada, relaciones válidas y origen intacto |
| PostgreSQL aislado | 21 escenarios concurrentes; restauración de28 tablas/108 filas idénticas y relaciones válidas,22 materiales MFA y6 sesiones recuperados con claves originales |
| Perfiles finales backup+postgres | 3 grupos PASSED; código0, fuentes seleccionadas estables y hashes verificados |

La evidencia original está en `/tmp/sgacd-backup-release-36`; resumen verificable de resultados en `backup-evidence-36.json` y `evidencias/respaldos-36/local-report.json`. Los registros privados, claves y bases de fixture no se copiaron al repositorio. El resumen público no contiene el paquete privado completo necesario para `--verify`.

```bash
python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile backup --profile postgres --output /tmp/sgacd-respaldos-nuevos
python BACKEND/INTEGRACIONES/operacion/verify_local.py --verify /tmp/sgacd-respaldos-nuevos
```

## Pendientes que no se cierran

CLI productivo de PostgreSQL y copias integrales de datos/adjuntos/configuración, custodia externa de claves, retención fuera del host, rotación, monitorización y RPO/RTO medidos. La restauración de contenido o MFA no acredita recuperación financiera integral de billetera ni llaves hardware. El registro canónico de billetera conserva esos pendientes abiertos.

Pasar estos perfiles no aprueba perfiles no seleccionados: ambos builds web siguen fallando y la cualificación física continúa pendiente. No se declara el plan al100% ni producción habilitada. Sin commit, push, despliegue o cambios de datos del usuario.
