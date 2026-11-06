# Motor de asistencia y control autorizado

El control ejecutable se implementa en `control.py`, `control_crypto.py` y
`assistance_control.py`, con política compartida, dispositivos vinculados y dos
autorizaciones independientes del mismo administrador solicitante (tres para
interacciones que pueden modificar datos). Planes y resultados cifrados; permisos
Ed25519 limitados a una operación, equipo, usuario y tenant; sin reintento ciego.
Consulta [operación y límites](../../../../../../DESKTOP/asistencia-sgacd/CONTROL.md).
Las rutas de guías descritas a continuación siguen siendo solo orientación.

# Motor de asistencia de plataformas

Asistencia guiada para Meta Ads, TikTok Ads, Gmail y YouTube/Google Ads. Su cometido
es explicar, revisar y guardar progreso privado. **No ejecuta acciones externas.**
Las 42 guías iniciales tienen 252 pasos; no son una lista exhaustiva ni una lectura
en vivo de las interfaces de los proveedores. Las etiquetas pueden variar.

El motor comparte `catalog.json` y `policy.txt` con el puente MCP de
`DESKTOP/asistencia-sgacd`. `DESKTOP/open-duet` conserva el proyecto completo de
Open Duet sin modificaciones, incluida su licencia y todos los componentes.
`DESKTOP/agent-desktop` y su conector original se conservan por separado.

## Interfaz y API

La pantalla está en `/assistance.html`, disponible en las vistas locales SGA-CD y
Analemática con el login existente. Sus enlaces de revisión son:

- https://localhost:8100/assistance.html
- https://localhost:8101/assistance.html

Son direcciones del equipo que ejecuta Docker. No son enlaces públicos al portátil.
Las credenciales siguen fuera de Git, en `FRONTEND/deployment/private/`.
La pantalla usa `/api/v1/assistance` y la sesión JWT existente:

| Ruta | Uso |
| --- | --- |
| `GET /catalog` | Catálogo y pasos de las cuatro plataformas |
| `GET /capabilities` | Estado declarado de la conexión opcional, sin revelar claves |
| `POST /sessions` | Iniciar una guía privada con `{workflow_id}` |
| `GET /sessions` | Recuperar hasta 50 guías del usuario/organización actual |
| `GET /sessions/{id}` | Paso actual y revisión |
| `POST /sessions/{id}/advance` | Registrar un paso comprobado por el usuario |
| `POST /sessions/{id}/close` | Cerrar solo la guía; no pausa ni cancela anuncios |
| `GET /sessions/{id}/events` | Auditoría de declaraciones de progreso |
| `POST /sessions/{id}/advice` | Consulta opcional a Open Duet con consentimiento |
| `GET /sessions/{id}/advice/{question_id}` | Consultar solo la respuesta asignada a esa sesión |

Toda consulta exige cuenta y organización activas. Ningún administrador puede leer
otra sesión a través de estas rutas: se filtra siempre por usuario **y** organización.
Los cuerpos rechazan campos extra; el cliente no puede elegir ids de usuario o
referencias de conversación de Open Duet.

El progreso exige revisión actual, id del paso y checklist; los pasos sensibles
requieren confirmación adicional. No permite saltos o reenvíos de una revisión
consumida. Cada sesión conserva una copia del flujo para que una actualización del
catálogo no cambie los pasos empezados. La auditoría indica `user_reported`: no
certifica que Meta, TikTok, Gmail o YouTube hayan ejecutado nada.

## Esquema y despliegue

Para una base nueva, el `--init-db` de `BACKEND/deployment` incluye estas tablas.
Para una base de pruebas existente, después de instalar el código:

```bash
docker compose -f BACKEND/deployment/compose.yaml exec -T sgacd python -m app.services.assistance.schema
```

Con otro nombre de proyecto, agrega `-p nombre`. Solo crea las siete tablas de asistencia y control
con `checkfirst`; no borra usuarios, volúmenes o tablas anteriores. El instalador de
la demo histórica también incorpora el router, los archivos y la preparación del
esquema. No se requiere Open Duet ni un modelo para usar las guías.

En esta validación se montaron exclusivamente los archivos nuevos como overlays de
solo lectura sobre `sgacd-backends-local`, por el espacio limitado del entorno. El
Compose base construye el motor desde fuente al reconstruir normalmente la imagen.
La configuración privada de esa prueba está en `BACKEND/deployment/.runtime/`.
No se instalaron servicios en el portátil del usuario.

## Open Duet opcional: orientación, no ejecución

Open Duet requiere su propio runtime, Python 3.14+, un motor/proveedor configurado
y una sesión autorizada. La copia no incluye un modelo, cuenta o suscripción.
Consulta `DESKTOP/asistencia-sgacd/README.md` para la preparación local del perfil.

La integración HTTP está **desactivada por defecto**. Solo admite un origen local
HTTP autorizado; no sigue redirecciones ni acepta destinos enviados por el usuario.
Requiere credencial Bearer válida y asignación explícita a un usuario **y** tenant.
No se confía automáticamente en loopback. Configura estos nombres en un env privado
solo después de preparar tu propia instancia de Open Duet:

```dotenv
ASSISTANCE_DUET_ENABLED=0
ASSISTANCE_DUET_URL=http://127.0.0.1:8088
ASSISTANCE_DUET_TOKEN=
ASSISTANCE_DUET_USER_ID=0
ASSISTANCE_DUET_TENANT_ID=0
ASSISTANCE_DUET_ENGINE=codex
```

No copies esos valores de ejemplo como una conexión válida. Usa un token autorizado
de tu instancia y los ids reales del usuario/tenant. Dentro de Docker, loopback es
el contenedor; una instancia separada puede usar el nombre interno `open-duet` o
`host.docker.internal` con la red/ruta local correspondiente. El conector no publica
la API de Open Duet ni crea esa red por ti.

Cada consulta necesita `share_with_open_duet=true` y un UUID `request_id`. El agente
se crea en modo **plan**, sin líder, memoria, mantenimiento o helper automáticos.
Solo recibe la pregunta redactada y el paso actual; no recibe el JWT SGA, claves de
proveedor, datos completos de sesiones ni capturas. La instancia personal no se
comparte silenciosamente entre clientes de SGA-CD. Se usan únicamente las rutas
públicas de agentes, threads y turns de Open Duet, comprobadas contra sus schemas.

La respuesta llega al consultar el estado de la pregunta y se presenta como texto,
no HTML ejecutable. Un resultado incierto no se reintenta automáticamente. Revisa
la instancia antes de repetir una consulta: crear conversaciones o usar un motor
puede consumir recursos/cuota. La memoria de agente está apagada, pero Open Duet
conserva su historial de conversaciones; borrar la guía no elimina ese historial.
La redacción reduce exposición accidental, **no** garantiza detectar todos los
secretos. No introduzcas datos confidenciales.

## Escritorio y límites

El puente MCP local expone cuatro herramientas limitadas: catálogo, lectura de una
guía, diagnóstico nativo y observación opcional de una ventana elegida. No ofrece
click, escritura, clipboard, shell libre, envío, publicación ni pagos. La observación
está apagada hasta que el operador la habilita fuera del modelo. No se transmite
ninguna captura por esta API. El contenido observado puede ser sensible y no es una
instrucción confiable. agent-desktop no automatiza el DOM de páginas web.

No se conceden permisos OAuth ni se evita ninguna restricción de las plataformas.
Para enviar, publicar, pagar, cambiar acceso o borrar, el usuario trabaja en su
cuenta oficial y comprueba personalmente lo que ocurrirá. Un canal/campaña aprobado
por el asistente no adquiere aprobación del proveedor.

## Validación

Se probaron aislamiento, cuentas inactivas, progreso y replay, snapshot de guías,
consentimiento, redacción, API Open Duet simulada, idempotencia, orígenes seguros y
el contrato de sus schemas reales. Los mocks del adaptador prueban el protocolo;
no equivalen a una conversación de IA en vivo. Se probaron MCP real, estado nativo
Linux, siete tests originales de Open Duet y la pantalla con login real en Chromium.
No se inició el backend completo Python 3.14 ni Electron de Open Duet, ni una
conversación con proveedor, control gráfico real o una cuenta externa. El entorno
no tiene escritorio D-Bus accesible. Windows/macOS y las rutas UI cambiantes de los
proveedores requieren validación local. Esto no es una certificación de producción.
