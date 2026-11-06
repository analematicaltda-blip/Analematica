# Pruebas locales de los cuatro backends

El entorno es local. No se contrató un servidor ni se publicó producción.
En Windows se recomienda Docker Desktop con WSL2 e integración con la distribución
Linux donde se clone el repositorio. Se necesitan Python 3.12 y Docker Compose v2.
Reserva al menos 20 GB libres para imágenes y compilaciones; las dependencias IA son
voluminosas. Los comandos siguientes se ejecutan desde la raíz del repositorio.

| Carpeta | Servicio Compose | Puerto local predeterminado | Configuración privada |
| --- | --- | --- | --- |
| `BACKEND/SGA-CD-BACKEND` | `sgacd` | 8000 | `.runtime/sgacd.env` |
| `BACKEND/ANALEMATICA-BACKEND` | `analematica` | 8001 | `.runtime/analematica.env` |
| `BACKEND/SGA-ERP-TUR-BAKEND` | `erp-tur` | 8002 | `.runtime/erp-tur.env` |
| `BACKEND/SGA-TUR-BAKEND` | `turismo` | 8003 | `.runtime/turismo.env` |

Cada proceso escucha en el puerto 8000 de su contenedor. Los puertos del equipo se
pueden cambiar con `SGACD_PORT`, `ANALEMATICA_PORT`, `ERP_TUR_PORT` y `TURISMO_PORT`.
La dirección predeterminada es **127.0.0.1**. PostgreSQL y Redis no publican puertos.
Este archivo Compose es una alternativa al Compose histórico de la raíz; no es un
override de aquella demo. Usa un nombre de proyecto propio para separar volúmenes.

## Preparar el entorno

```bash
python -m pip install -r BACKEND/deployment/requirements-tools.txt
python BACKEND/deployment/init_local.py
docker compose -f BACKEND/deployment/compose.yaml config --quiet
```

El generador crea claves aleatorias distintas por servicio, incluyendo RSA para los
dos Django. Guarda exclusivamente archivos privados en `.runtime/`, ignorados por
Git; no imprime claves ni sobrescribe configuraciones existentes. En Unix usa 0600.
En Windows mantén esta carpeta dentro del perfil privado del usuario y revisa sus ACL.
No borres/regeneres claves si ya hay datos cifrados o sesiones que deban conservarse.

Construye secuencialmente para reducir el consumo de disco:

```bash
docker compose -f BACKEND/deployment/compose.yaml build sgacd
docker compose -f BACKEND/deployment/compose.yaml build analematica
docker compose -f BACKEND/deployment/compose.yaml build erp-tur
```

ERP y Turismo usan la misma imagen Django, con variables, proceso, base PostgreSQL y
volumen propios. Comparten código porque el proyecto original tiene dependencias
cruzadas. Redis usa bases lógicas distintas para sus colas. No se arrancan Celery,
servicios de pago, envíos a Meta ni proveedores IA durante la preparación.
Si una red corporativa requiere una CA, el Dockerfile admite el secreto BuildKit
`proxy_ca`; consérvalo fuera del repositorio y mantén la verificación TLS activada.

## Inicializar SGA-CD en una base nueva

```bash
docker compose -f BACKEND/deployment/compose.yaml up -d --wait sgacd-db
docker compose -f BACKEND/deployment/compose.yaml run --rm --no-deps sgacd python /srv/entrypoint.py --init-db
docker compose -f BACKEND/deployment/compose.yaml up -d --wait sgacd analematica
```

`--init-db` crea las tablas declaradas en la base elegida sin borrar tablas. Úsalo
solo para una base nueva de pruebas; no sustituye migraciones de producción. Los
arranques normales no alteran esquemas (`SGACD_INIT_SCHEMA=0`, `DJANGO_MIGRATE=0`).
No se crea un usuario/contraseña por defecto. La consola corporativa mantiene su
vinculación explícita al dueño y devuelve 401 a una sesión sin autorización.

El servicio Analemática publica API, no archivos de frontend: delega `/api/*` al
SGA-CD de la red interna, conservando su autorización, errores y datos. El frontend
continúa en `FRONTEND/ANALEMATICA-FRONTEND`. `integrated_server.py` se conserva por compatibilidad
con el código importado; no es el entry point de Compose ni sustituye el login seguro.
La IA opcional sin credencial devuelve 503 cuando se solicita; no bloquea el arranque
de toda la API. No se incluyen claves de proveedor en código o imágenes.

## Estado real de los servicios turísticos

**ERP y Turismo todavía no completan el arranque.** Se corrigieron sus bindings de
paquetes, el registro del namespace de prestadores, las claves JWT por entorno y la
lista de dependencias. La comprobación de modelos Django ya pasa, pero el chequeo
completo falla en `gestion_contable/compras/urls.py`: importa `ProveedorViewSet`,
`FacturaCompraViewSet` y `GenerarPagoMasivoProveedoresView`, cuyo código está comentado
en `views.py`. No se activaron operaciones financieras incompletas para ocultar el error.
Puede haber otros bloqueos tras resolver este primero; los archivos heredados también
conservan las incidencias sintácticas inventariadas en la importación APP.

Para reproducir el bloqueo sin arrancar ni migrar bases:

```bash
docker compose -f BACKEND/deployment/compose.yaml run --rm --no-deps erp-tur
docker compose -f BACKEND/deployment/compose.yaml run --rm --no-deps turismo
```

Una vez corregidas las vistas, revisados los checks y preparadas las migraciones de
bases nuevas, el arranque conjunto es:

```bash
docker compose -f BACKEND/deployment/compose.yaml up -d --wait
```

Ese comando **no pasa actualmente para los cuatro servicios**. El entry point falla
ante errores de Django y el healthcheck no los declara sanos. No habilites migraciones
ni apuntes las variables a una base real sin revisar previamente los cambios de esquema.

## Comprobar y detener

```bash
docker compose -f BACKEND/deployment/compose.yaml ps
docker compose -f BACKEND/deployment/compose.yaml logs --tail 80 sgacd analematica
docker compose -f BACKEND/deployment/compose.yaml stop
```

SGA-CD y Analemática exponen `/healthz`; comprueban su base y dependencia interna,
respectivamente. `stop` conserva los datos. Evita `down -v` si deben mantenerse.

Se validaron construcción desde fuente de SGA-CD, imagen/gateway Analemática,
PostgreSQL aislado, HTTP de salud y rechazo de sesión sin autorización en el servidor
de pruebas del agente, usando puertos 28000 y 28001 para no interferir con las demos.
No se instaló Docker ni se inició un servicio en el portátil del usuario.
Pruebas: 32 de regresión de workspace, seis del conector/configuración local y dos
sobre la ausencia de proveedor IA. El estado de los contenedores turísticos es un
bloqueo funcional documentado, no una validación exitosa del sistema completo.
