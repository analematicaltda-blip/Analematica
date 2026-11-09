# Recuperación contable · procedimiento de validación

Estado: ensayo local reproducible; no es una autorización de restauración productiva.

## Ensayo automatizado disponible

Desde la raíz, con el entorno Python de integración y Docker local preparados:

```bash
python INTEGRACIONES/operacion/verify_local.py --profile accounting --profile postgres --output /tmp/contabilidad-recuperacion-resultado-nuevo
python INTEGRACIONES/operacion/verify_local.py --verify /tmp/contabilidad-recuperacion-resultado-nuevo
python ANALISIS/contabilidad/tools/update_progress.py --check
```

Usar un directorio nuevo. El contrato crea bases PostgreSQL desechables, genera un archivo privado, restaura en otra base y elimina archivo/bases al terminar. No seleccionar una base del cliente ni ejecutar el helper directamente sobre ella. La evidencia contiene digests y conteos, no el dump ni credenciales. Los hashes verifican consistencia local, no firma ni aprobación productiva.

La aprobación local exige: comparación de datos y estructura, secuencias IDENTITY, funciones/triggers, restricciones e índices; integridad del ledger de cada empresa contabilizada; protección SQL activa después de recuperar; fuente sin cambios. Una normalización específica admite solo la transformación de casts del CHECK de estados conocida y probada, sin omitir el dominio de valores permitido.

## Antes de cualquier recuperación real

Documentar en el registro de producción:

1. Base/empresa, punto de recuperación, propietario de la operación y respaldo de la situación previa. Destino separado; nunca sobrescribir la fuente como prueba.
2. Versiones de aplicación/DB, migraciones y compatibilidad. Inventariar documentos, archivos BYOS y llaves necesarias sin copiarlas a informes o logs.
3. Custodia, cifrado, integridad, retención y acceso al respaldo. El ensayo actual usa datos sintéticos y no resuelve custodia productiva.
4. Roles y ACL del destino. El fixture restaura sin propietarios/ACL y no cualifica los permisos de producción.
5. RPO/RTO acordados y tiempos medidos; procedimiento de reversión y responsables. No deducir estos objetivos del tiempo del test.
6. Verificación posterior: integridad monetaria y de cadena, recibos/outbox/proyecciones, documentos y llaves, controles SQL, readiness y flujos autenticados.
7. Ensayo independiente y autorización concreta antes del cambio real; conservar la evidencia del resultado y el punto de reversión.

El proveedor ERP no debe recibir las KEK del cliente para cerrar una prueba. Recuperar una base no acredita recuperar la bóveda de documentos ni permite saltarse autorizaciones de pagos o control remoto.

Referencia del ensayo: [implementación19](IMPLEMENTACION_19.md). Pendientes canónicos: `../produccion/PENDIENTES-PRODUCCION-ECOSISTEMA.md`.

## Recuperación documental PostgreSQL cliente · ensayo adicional

El mismo perfil `postgres` incluye ahora `customer_byos_recovery.py`, invocado únicamente desde la fixture BYOS. Exporta su base temporal a un dump privado y restaura en otra base vacía. Compara la vinculación y todos los sobres de la fixture, verifica controles sin reinicialización y comprueba que el origen no cambió. La fixture elimina bases/archivo; no usarla sobre un destino real.

Los documentos siguen cifrados pero el dump completo no está cifrado adicionalmente; contiene metadatos. No se exportan KEK. Las ACL y propietarios se omiten deliberadamente y requieren provisión/revisión separada. La prueba no cubre recuperación de llaves, volumen real, restauración con rol limitado ni RPO/RTO productivos. Referencia: [implementación28](IMPLEMENTACION_28.md).
