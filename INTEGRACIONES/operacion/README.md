# Calidad y operación local

Una entrada única ejecuta suites existentes en procesos separados y conserva evidencias. No instala dependencias, despliega, crea commits, cambia ramas ni selecciona bases del proyecto. Está pensada para Python 3.12 en Linux/WSL2; PostgreSQL usa Docker local y los navegadores requieren Node/Chromium.

## Preparación y uso

Usar un entorno virtual dedicado y las instrucciones de dependencias existentes en `BACKEND/deployment/README.md` y `FRONTEND/deployment/README.md`. La herramienta registra versiones instaladas y ejecuta `pip check`; esto comprueba coherencia de dependencias, no vulnerabilidades ni reproducibilidad binaria. Los requisitos Python aún contienen rangos y las imágenes Compose generales usan etiquetas: no se presenta un entorno productivo fijado por digest.

Desde la raíz del repositorio, con ese Python:

```bash
python INTEGRACIONES/operacion/verify_local.py --profile core --output /tmp/sgacd-core-nuevo
python INTEGRACIONES/operacion/verify_local.py --profile fresh --output /tmp/sgacd-instalacion-nueva
python INTEGRACIONES/operacion/verify_local.py --profile browser --profile devices --profile postgres --output /tmp/sgacd-integracion-nueva
python INTEGRACIONES/operacion/verify_local.py --profile web-build --web-dependencies /ruta/node_modules --output /tmp/sgacd-build-nuevo
python INTEGRACIONES/operacion/verify_local.py --verify /tmp/sgacd-core-nuevo
```

Se pueden repetir perfiles en una sola invocación; se deduplican. Sin `--profile` se ejecuta `core`. Usar una ruta nueva por ejecución; no se sobrescriben evidencias. Guardar los resultados fuera del repositorio o dentro de `.runtime` ignorado. Los directorios son privados y los archivos 0600 en Unix. No subir bases, claves ni registros crudos a Git.

| Perfil | Verificación | Requisitos adicionales |
| --- | --- | --- |
| `core` | Coherencia de paquetes, contratos de la herramienta, asistencia/contenido, catálogo, recursos, preparación web, permisos territoriales/empresa, identidad, cupos, sesiones, recuperación y restauraciones SQLite | Dependencias Python de validación |
| `accounting` | Fundación, posteo, identidad/API y consumidor contable local | Fixtures aislados; añadir `postgres` para concurrencia real |
| `backup` | Copia cifrada AES-256-GCM, rechazos y restauración editorial con claves originales | SQLite local estándar, hasta 64 MiB; ver `RESPALDOS.md` |
| `fresh` | Crea **dos bases nuevas** con migraciones locales y comprueba esquema, HTTP y respaldo | Dependencias Django; no usa directorios existentes |
| `browser` | Panel y taller en Chromium, fixtures API y vistas responsive | Playwright disponible; `PLAYWRIGHT_MODULE` opcional |
| `devices` | Protocolo, Chromium y adaptadores móviles simulados | Node y Playwright; prueba nativa puede quedar omitida |
| `postgres` | Concurrencia y restauración en contenedor efímero aislado | Docker local; imagen de prueba fijada por digest en el ensayo existente |
| `web-build` | Builds completos ERP y Turismo, sin desactivar comprobación estricta | Dependencias completas instaladas desde `FRONTEND/deployment/package-lock.json` |

No conectar Ollama, proveedores de pago ni cuentas reales para estos perfiles. El runner deshabilita las conexiones opcionales de asistencia/contenido y fija una base SQLite de fixture en el entorno del proceso. Las suites Django preparan sus propios datos aislados; PostgreSQL crea su propio contenedor. Los perfiles no son pruebas sobre una instalación productiva.

## Interpretación y evidencia

- Código de salida **0**: todos los grupos seleccionados pasaron, sin omisiones, y el inventario de fuentes seleccionado se mantuvo estable.
- Código **2**: al menos un grupo falló, no pudo arrancar, agotó el tiempo, omitió pruebas o cambió la fuente durante la ejecución.
- Un error de argumentos conserva el código de argparse; `--verify` devuelve **1** si hay evidencia incompleta o hashes distintos.
- `PASSED_WITH_SKIPS` conserva el número de omisiones. No significa validación de hardware. Cero pruebas descubiertas no aprueba una suite unittest.
- Los registros tienen un máximo de 8 MiB; excederlo marca fallo, en lugar de truncar silenciosamente una evidencia considerada aprobada. Las esperas tienen límite y se termina el grupo de procesos al agotar el plazo en POSIX. Ctrl+C registra `CANCELLED`, termina el hijo y detiene los siguientes grupos, conservando informe incompleto.
- `report.json` contiene resultados/tiempos/versiones; `source-manifest.json` identifica fuentes de los directorios declarados; `checksums.json` cubre los archivos de evidencia del primer nivel. Los datos temporales anidados de instalación/build no se presentan como respaldos verificados por ese manifiesto.

`--verify` comprueba hashes locales de registros, informe e inventario. No compara el código actual con una versión publicada, no autentica al autor ni sustituye firma de artefactos: quien puede reescribir todo el paquete puede recalcular hashes. El inventario es de fuentes seleccionadas, no una atestación completa de imágenes o de todo el repositorio. `production_ready` permanece `false` aunque un perfil pase.

El workflow manual `Local operation evidence` ejecuta un perfil por vez, sin credenciales Git persistidas ni permisos de escritura. Publica solo el resumen y hashes por siete días; los registros privados no se suben. Descargar solo ese resumen no permite verificar registros que no se incluyeron. El workflow `Full web build audit` mantiene la verificación completa de builds. Ninguno se ha disparado remotamente en esta entrega.

## Diagnóstico y arranque

1. Revisar `report.json` y el registro privado del primer grupo bloqueado/fallido. No ocultar errores ni activar mocks para conseguir una marca verde.
2. Runtime ausente: instalar las herramientas indicadas en el manual correspondiente; repetir hacia una carpeta nueva. No cambiar TLS ni permisos para forzar una conexión.
3. Base nueva de ERP/Turismo: usar `fresh_local.py` y su marcador por servicio; `/readyz` verifica esquema. Un `/healthz` correcto o un contenedor healthy no prueba procesos de negocio completos.
4. Compose: seguir la inicialización explícita en `BACKEND/deployment/README.md`, con proyecto local separado, puertos 127.0.0.1 y secretos privados existentes. No ejecutar inicialización de esquema sobre una base con datos por inferencia.
5. Build incompleto: conservar el registro y resolver el módulo/contrato ausente. No usar `ignoreBuildErrors`, reemplazar servicios por respuestas ficticias ni anunciar enlaces productivos.

## Reversión segura

Este procedimiento es manual y debe ensayarse para la instalación concreta antes de producción. La herramienta no conmuta servicios o bases del usuario automáticamente.

1. **Antes de cambiar una instalación**, identificar proyecto Compose, servicio, imagen exacta/digest, versión de código, esquema/migraciones, volúmenes, configuración y versiones de claves. Conservar el candidato anterior y una copia cifrada de datos; custodiar claves aparte. No guardar `.env`, tokens o claves en Git ni en informes compartidos.
2. Verificar restauración hacia una **base nueva aislada**, con las claves originales y el código compatible: integridad, relaciones, filas y descifrado. Los ensayos incluidos hacen esto con fixtures; no son copias de los datos reales del cliente.
3. Definir una ventana y detener nuevas escrituras/órdenes de control antes de cambiar. No reasignar una cola de permisos antiguos a un ejecutor incompatible; conservar el contrato v2 backend/ejecutor.
4. Si el cambio no alteró el esquema y la compatibilidad está comprobada, volver a la imagen/código anterior identificado sin reconstruir una etiqueta mutable y sin regenerar claves. Revisar sesión, permisos, `/readyz` y un recorrido funcional antes de reabrir escrituras.
5. Si hubo migraciones o datos incompatibles, **no ejecutar una migración inversa a ciegas**. Restaurar la copia verificada en otra base, aplicar el código compatible y validar antes de conmutar. Documentar y resolver escrituras posteriores al respaldo; no prometer pérdida de datos cero.
6. Registrar incidente, versión recuperada, intervalo de datos y pruebas. No usar `down -v`, borrar volúmenes, `git reset --hard` o eliminar carpetas para intentar recuperar un despliegue.

## Pendientes para producción

Builds web completos, migraciones integrales en PostgreSQL real, copias cifradas externas con custodia de claves, RPO/RTO medidos, carga, límites compartidos, escaneo de dependencias, imágenes reproducibles/firmadas, observabilidad/SOC, distribución móvil/escritorio firmada y equipos físicos. Se mantienen los pendientes de identidad, funcionalidades y proveedores de los bloques anteriores. Ningún ensayo de este directorio permite declarar el plan al 100 %.

El bloque 9 añade el perfil `backup` y el procedimiento `RESPALDOS.md`. El ensayo editorial ahora usa un archivo autenticado y cifrado, con clave de respaldo independiente.
