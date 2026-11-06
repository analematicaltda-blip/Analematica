# Cuatro vistas web locales

Esta configuración permite revisar las cuatro interfaces en el equipo donde se
inicia Docker. No las publica en Internet ni las instala en el portátil desde
la sesión del agente. En Windows usa Docker Desktop y ejecuta los comandos dentro
de WSL2; así las dependencias Node nativas coinciden con los contenedores Linux.
Se necesitan Node 24, Python 3.12 y los backends locales de `BACKEND/deployment`.

| Sistema | Enlace local | Estado comprobado |
| --- | --- | --- |
| SGA-CD | https://localhost:8100/login.html | Vista, login real y sesión protegida |
| Analemática | https://localhost:8101/login.html | Vista, login real y sesión del dueño |
| ERP turístico | https://localhost:8102/ | Vista de revisión; operaciones backend pendientes |
| Turismo | https://localhost:8103/dashboard/login | Pantalla de acceso; login backend pendiente |

**`localhost` significa el equipo que ejecuta Docker.** Los enlaces del servidor
de validación del agente no son URLs públicas accesibles desde otro computador.
Al ejecutar estos comandos en tu equipo, los mismos enlaces abren allí las vistas.
El certificado es autofirmado para `localhost` y `127.0.0.1`, con vigencia de 30 días;
no reemplaza un certificado de dominio verificado para producción.

## Arranque

Primero prepara/inicia `sgacd` y `analematica` siguiendo `BACKEND/deployment/README.md`.
Después, desde la raíz:

```bash
python -m pip install -r FRONTEND/deployment/requirements-tools.txt
npm ci --prefix FRONTEND/deployment --ignore-scripts
python FRONTEND/deployment/prepare.py
docker compose -f FRONTEND/deployment/compose.yaml up -d
```

La red externa predeterminada es `sgacd-backends_default`. Si elegiste otro nombre
de proyecto backend, configura `BACKEND_NETWORK` con su red real. En la validación
se usó `sgacd-backends-local_default`. Los contenedores usan UID/GID 1000, habitual
para el primer usuario de WSL2; ajusta `user` en Compose si tu UID/GID difiere.
No montes carpetas privadas del equipo para corregir permisos.

Para crear un dueño **solo en la base nueva local**:

```bash
python BACKEND/deployment/create_local_owner.py
```

El helper rechaza otros destinos de base y conserva dueños/contraseñas existentes.
Con un nombre de proyecto personalizado usa `--project nombre-del-proyecto`.

## Credenciales

Se guardan fuera de Git, con permisos privados:

- `private/ACCESOS-LOCALES.md`: cuatro usuarios/contraseñas distintos para la capa
  de acceso HTTPS a las vistas. El navegador los solicita antes de mostrar HTML.
- `private/LOGIN-APLICACIONES.md`: login real del dueño local, compartido por
  SGA-CD y Analemática porque usan la misma cuenta y autorización backend.

ERP y Turismo **no tienen credenciales internas funcionales validadas**. La clave
que permite ver su interfaz no inicia una sesión ERP. Sus `/api/` responden 503
hasta reparar y conectar el backend real; no se usan usuarios ni sesiones simulados.
No subas `private/`, certificados privados, `.runtime/` ni archivos `.env` a Git.
El preparador conserva claves existentes y no imprime contraseñas.

## Qué se publica

SGA-CD y Analemática sirven copias de recursos públicos permitidos, no sus carpetas
completas. Analemática mantiene los controles de autorización de la API SGA-CD;
no se activa el servidor importado con autenticación de demostración.

Los fuentes turísticos originales no incluían un manifiesto npm ni un proyecto
independiente para el fragmento ERP. El preparador crea dos proyectos de revisión
usando los recursos compartidos de Turismo y superpone los archivos ERP en su ruta
real de dashboard. Los originales siguen separados y la copia generada es descartable.
El manifiesto y lockfile de dependencias están en esta carpeta.

Estas dos vistas usan **Next en modo desarrollo**, detrás del acceso HTTPS local.
Los mocks MSW están desactivados por defecto. Se corrigieron las declaraciones
repetidas del hook ERP y un icono inválido; los importes y plazos simulados de su
pantalla inicial se sustituyeron por datos no disponibles. La vista ERP indica que
sus operaciones no están conectadas. No se validaron todas las rutas del proyecto.

## Controles y límites de seguridad

- Solo se publican puertos en `127.0.0.1`; Node, Redis y PostgreSQL no se exponen.
- HTTPS TLS 1.2/1.3; claves de acceso largas aleatorias y hashes bcrypt separados.
- Intentos y solicitudes limitados; las claves Basic no se reenvían a las API.
- Sesiones backend verificadas; visitar `/admin.html` no concede permisos.
- Contenedores sin privilegios adicionales, sin capabilities y con filesystem
  de imagen de solo lectura; los backends están en una red separada.
- CSP, bloqueo de iframes, `nosniff`, permisos del navegador limitados, directorios
  ocultos denegados y logs sin Authorization ni parámetros de URL.
- No hay claves privadas de IA en las variables públicas de navegador.

**No es una garantía contra ataques ni una aprobación de producción.** Persisten
código heredado por revisar, tokens del frontend en localStorage y dos servidores
Next de desarrollo; su CSP requiere `unsafe-eval`. Antes de exponerlos harán falta
reparar Turismo/ERP, compilaciones de producción verificadas, revisar autorización
por rol/tenant, XSS/CSRF, ciclo de sesiones, recuperación de credenciales, MFA,
copias/restauración, TLS de dominio y actualización de dependencias. No se anuncia
un sistema completo funcional mientras esos puntos sigan pendientes.

## Validación y parada

Se comprobaron HTTPS con confianza/pinning al certificado local, 401 sin acceso,
200 autenticado de las cuatro vistas, pantallas reales con Chromium, login y sesión
real en las dos aplicaciones operativas. La auditoría npm de dependencias de
producción informó cero vulnerabilidades conocidas al validar esta entrega;
esto no detecta todas las vulnerabilidades ni sustituye una revisión del código.

```bash
python -m unittest discover -s FRONTEND/deployment/tests -v
docker compose -f FRONTEND/deployment/compose.yaml ps
docker compose -f FRONTEND/deployment/compose.yaml stop
```

`prepare.py` vuelve a copiar los recursos de revisión; detén antes las vistas si
estás navegando para evitar una recarga intermedia. Las claves se conservan.
