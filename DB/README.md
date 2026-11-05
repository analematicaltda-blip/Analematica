# Bases de datos del repositorio

- `SGA-CD-DB.git/`: modelos y migraciones de SGA-CD.
- `DB-SG -OP-TUR/`: anterior carpeta `db`, importada de APP.

El nombre `DB-SG -OP-TUR` contiene un espacio; citarlo en comandos de terminal.

Esta reorganización conserva los contenidos y no fusiona esquemas ni ejecuta
SQL, migraciones o modificaciones sobre los datos. Los volúmenes de PostgreSQL
y las bases locales de Flet no se han movido.

Se actualizaron la búsqueda de modelos del backend y sus pruebas, la comprobación
CI, la URL SQLite del entorno y el ejemplo, y las rutas de Alembic. Los scripts
`deploy.py` y `80_testing/sql_syntax_validation.py` de DB-SG -OP-TUR resuelven sus
archivos respecto a su propia ubicación para admitir el nuevo directorio.

Verificación: 174 archivos locales conservados; solo tres archivos internos de
configuración/rutas cambiaron. Las llamadas a psql y sqlfluff se simularon con
archivos temporales; no se ejecutaron contra bases de datos reales.
