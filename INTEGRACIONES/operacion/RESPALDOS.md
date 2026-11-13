# Bloque 9 — Respaldos cifrados y restauración local

El bloque 9 se identifica en la referencia histórica de `INTEGRACIONES/plan-maestro/auditoria-bloque01/README.md` como continuidad/restauración. Esta entrega añade una herramienta reutilizable; los ensayos anteriores eran fixtures, no un servicio de copias para datos reales.

## Alcance

`BACKEND/deployment/encrypted_backup.py` crea archivos SQLite cifrados con **AES-256-GCM**, verifica su autenticación y restaura únicamente hacia destinos nuevos. Python 3.12, cryptography y SQLite con serialización/deserialización disponibles; validado en Linux. No es una herramienta de backup PostgreSQL productiva ni copia llaves hardware, archivos adjuntos o volúmenes.

- Instantánea consistente mediante la API backup de SQLite; incluye filas confirmadas que aún estén en WAL.
- La instantánea se verifica en RAM antes de cifrar; no crea un dump SQLite plano intermedio en disco. La cabecera WAL de la copia se normaliza al formato autocontenido, sin tocar la fuente.
- Clave independiente de 32 bytes; nonce aleatorio de 12 bytes por archivo. Versión, servicio, fecha, tamaño y hash del contenido quedan autenticados como AAD. No se incluyen rutas, nombres de usuarios ni claves en esa cabecera.
- El servicio es una etiqueta elegida por el operador, no una detección automática del origen. Verificar el servicio esperado evita restauraciones accidentales cruzadas; no reemplaza comprobar esquema, claves y permisos de la aplicación.
- Se rechazan alteraciones, clave/servicio erróneos, relaciones inválidas, destinos existentes y archivos auxiliares SQLite preexistentes al restaurar. No se sobrescriben claves ni se borra una base anterior.
- Claves, archivos cifrados y bases restauradas se crean con 0600. En POSIX se rechazan claves legibles por grupo/otros. Los archivos no se pueden generar dentro del código versionable: usar rutas externas o `.runtime` ignorado.
- Tamaño máximo de la base/instantánea: **64 MiB**; tiempo de copia SQLite limitado a 60 segundos. Es un flujo local acotado, no un respaldo por streaming para bases grandes. No se cambian estos límites ni se trunca contenido silenciosamente.
- El destino de restauración contiene la base **descifrada**, privada y solo después de autenticar/verificar íntegramente el archivo. Se requiere proteger el disco y sus accesos.

Las claves internas de aplicación (Fernet/MFA, firmas de control, claves hardware y configuración) **no se incluyen** en el archivo. Deben custodiarse por separado para que los registros cifrados puedan utilizarse después de restaurar. Regenerarlas no recupera datos anteriores. Perder la clave de respaldo también impide abrir el archivo.

## Uso por el operador local

Crear previamente directorios privados para claves y copias. Los siguientes comandos son ejemplos con rutas que deben existir; no se ejecutan automáticamente sobre una base del usuario.

```bash
python BACKEND/deployment/encrypted_backup.py keygen --key-file /ruta-privada/claves/respaldo.key
python BACKEND/deployment/encrypted_backup.py backup --source /ruta-privada/erp/application.sqlite3 --destination /ruta-privada/copias/erp-001.sgacdb --key-file /ruta-privada/claves/respaldo.key --service erp-tur
python BACKEND/deployment/encrypted_backup.py verify --archive /ruta-privada/copias/erp-001.sgacdb --key-file /ruta-privada/claves/respaldo.key --service erp-tur
python BACKEND/deployment/encrypted_backup.py restore --archive /ruta-privada/copias/erp-001.sgacdb --destination /ruta-privada/recuperacion/erp-001.sqlite3 --key-file /ruta-privada/claves/respaldo.key --service erp-tur
```

Etiquetas permitidas: `sgacd`, `analematica`, `erp-tur`, `turismo`. Salida 0 indica que la operación solicitada terminó; salida 1 indica rechazo/error; argumentos inválidos usan el código de argparse. La salida no muestra claves ni contenidos, ni modifica la conexión del backend. La creación exclusiva evita sobrescribir una copia que ya existía. No hay borrado por retención ni cron habilitado automáticamente.

Después de restaurar: conservar el origen y la copia intactos, configurar una instancia aislada del código compatible para la base nueva, suministrar **las claves originales** y comprobar esquema, identidad, permisos y procesos de negocio antes de decidir una conmutación. No iniciar servicios reales, proveedores, cobros o colas de control durante el ensayo.

## Validación integrada

```bash
python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile backup --profile postgres --output /tmp/sgacd-respaldo-evidencia-nueva
python BACKEND/INTEGRACIONES/operacion/verify_local.py --verify /tmp/sgacd-respaldo-evidencia-nueva
```

`backup` ejecuta pruebas negativas/positivas y el ensayo del modelo real `ContentDraft`: recuperar texto cifrado y versión revisada con las claves originales. `postgres` ejecuta los contratos existentes en un contenedor efímero, con origen intacto y restauración hacia otra base. El perfil por sí solo no se conecta a PostgreSQL del usuario.

El workflow manual `Local operation evidence` incorpora el perfil `backup`; no se ha disparado remotamente. El perfil `core` conserva su ensayo editorial, ahora con archivo cifrado, y las herramientas de snapshot anteriores siguen disponibles para compatibilidad.

## Pendientes

- Copias completas de PostgreSQL y de archivos/volúmenes del usuario, consistencia entre ambos y esquema integral, con credenciales gestionadas por el operador.
- Custodia externa de claves, rotación, copias fuera del equipo y almacenamiento con retención/inmutabilidad. Cifrar no impide que un atacante del mismo host elimine el archivo.
- Recuperación del sistema completo: datos, configuración, claves de aplicación, adjuntos, versiones y dispositivos. Las pruebas de MFA/control o contenido no certifican recuperación financiera integral de la billetera.
- Medir RPO/RTO reales, carga y monitorización periódica de copias; revisar permisos/ACL en Windows y cifrado de disco. No se habilitó producción ni se prometió pérdida de datos cero.
