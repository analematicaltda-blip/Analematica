# Baseline fresh-local-v1

Migraciones generadas desde los modelos registrados actualmente en Django 5.2.12.
Se incluyen únicamente mediante `fresh_local_settings`; las migraciones heredadas
de cada aplicación se conservan sin alteración. Las dependencias auth/allauth y
otros paquetes externos conservan sus migraciones distribuidas.

Este baseline es para bases SQLite NUEVAS, privadas, de desarrollo. No es una
migración de datos históricos ni un reemplazo del historial productivo. No debe
seleccionarse para una base antigua, PostgreSQL de producción o una base de otro
servicio. El inicializador rehúsa directorios existentes y no usa `--fake`.

La segunda migración de prestadores y mi_negocio recoge modelos operacionales
que antes solo se registraban al importar URLs. Ahora AppConfig.ready los registra
antes de autodetectar migraciones. Las migraciones se versionan; no se regeneran
durante el arranque ni al crear una instalación nueva.

Verificar siempre `makemigrations --check --dry-run`, `/readyz`, claves foráneas y
restauración antes de utilizar nuevos cambios de esquema.
