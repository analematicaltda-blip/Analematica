# Paneles institucionales por rol y plan

Los siguientes enlaces son una revisión de solo lectura para el dueño autenticado. No cambian la identidad de la sesión ni el plan contratado. Se puede seleccionar una entidad existente desde el encabezado. Los enlaces operativos reales usan `#/ROL/basico/inicio` o `#/ROL/full/inicio`; el servidor aplica siempre el plan real y el alcance del usuario.

| Rol | Básico | Full |
| --- | --- | --- |
| Administrador de empresa | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/admin_empresa/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/admin_empresa/full/inicio) |
| Jefe de área | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/jefe_area/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/jefe_area/full/inicio) |
| Coordinador | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/coordinador/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/coordinador/full/inicio) |
| Profesional de área | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/profesional_area/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/profesional_area/full/inicio) |
| Técnico de área | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/tecnico_area/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/tecnico_area/full/inicio) |
| Profesor / Instructor | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/profesor/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/profesor/full/inicio) |
| Jefe de almacén | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/jefe_almacen/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/jefe_almacen/full/inicio) |
| Almacenista | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/almacenista/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/almacenista/full/inicio) |
| Jefe de escenarios | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/jefe_escenarios/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/jefe_escenarios/full/inicio) |
| Alumno | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/alumno/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/alumno/full/inicio) |
| Madre, padre o acudiente | [Revisar Básico](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/padre_acudiente/basico/inicio) | [Revisar Full](https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/revision/padre_acudiente/full/inicio) |

## Derechos y contratos funcionales

El dueño tiene las funciones de plataforma sin suscripción Full ni cupos comerciales de empresa. Se mantienen los límites técnicos y los permisos exigidos por proveedores externos.

Básico conserva las funciones institucionales de cada contrato, sin CRM, creación multimedia, publicación ni bandeja de mensajes comerciales. Full habilita esos módulos para administrador de empresa, jefe de área, coordinador, profesional y técnico. Una restricción individual explícita prevalece hasta que el administrador restaure la herencia. Profesor, almacén, escenarios, alumnos y familias conservan sus funciones de rol, sin recibir automáticamente permisos de marketing.

Se preservan los módulos originales; la navegación organiza los accesos por contrato. La revisión del dueño muestra la estructura y no permite operaciones que escriban datos en nombre del rol revisado. Los contratos usados son funcionales, documentados en `ROLES_Y_PERMISOS.md`, las autorizaciones existentes y los requisitos del propietario; no se encontraron contratos laborales individuales.

El nombre guardado en los datos de empresa aparece centrado en la cabecera de sus paneles. El administrador configura las especialidades desde el catálogo oficial de 500 disciplinas deportivas y 500 modalidades culturales, sin borrar las ya adoptadas.

## Actualización en Codespaces

```bash
bash -e <<'SH'
cd /workspaces/SGA-CD
git fetch origin codex/company-role-bi-panels
git merge --ff-only FETCH_HEAD
python3 BAKEND/SGA-CD-BACKEND/scripts/update_panels.py --start
SH
```

El instalador prepara tablas adicionales, conserva datos y credenciales y actualiza los servicios existentes. Si hay cambios incompatibles locales, se detiene para no sobrescribirlos. No mueve ni modifica las bases SQLite offline de Flet. Cargar de nuevo con Ctrl+Shift+R. El servidor de Codespaces pertenece al usuario: la validación de desarrollo no lo actualiza remotamente.
