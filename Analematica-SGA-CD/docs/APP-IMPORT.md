# Importación de APP a SGA-CD

Origen: `analematicaltda-blip/APP`, commit `122723afde24b5c8d04b64dce55fbd83fddea1ab`.
La consola existente, sus pruebas y configuración de Meta se conservan en
`Analematica-SGA-CD`. La nueva carpeta `Analematica` procede de APP.

Carpetas importadas: `Analematica`, `GATuristica`, `Turismo`, `db`, `llm`,
`skills-contabilidad` y `Conta-Skills`. Se conservaron los nombres del origen.
Los 3710 archivos copiados coinciden byte a byte con la instantánea de origen.
Dos claves privadas JWT se mantienen solo en la copia local, con permisos 0600,
y quedan excluidas de la entrega Git: `GATuristica/Backend/keys/jwt-private.pem`
y `Turismo/Backend/keys/jwt-private.pem`. Deben generarse claves nuevas al desplegar.
No se regeneraron claves ni se cambiaron las bases de datos durante esta copia.

Las pruebas existentes del despliegue y preparación de la consola SGA-CD pasan
con la nueva ruta. El análisis sintáctico detecta 12 problemas preexistentes en
archivos Python de APP, detallados en `APP-IMPORT.json`. Se conservaron para no
mezclar una copia de repositorios con una reparación funcional no solicitada.
No se afirma que los sistemas importados estén listos para arrancar o producción.
No se ejecutaron sus servicios, migraciones, instaladores ni hooks.

Los contenedores existentes siguen usando sus versiones publicadas. Para futuras
actualizaciones de la consola SGA-CD, la ruta del instalador es:

```bash
python3 Analematica-SGA-CD/deployment/start.py
```

Esta importación no sustituye automáticamente el frontend desplegado por el de
APP y no modifica main. La rama de entrega conserva además los cambios probados
de Meta de `codex/analematica-node`.
