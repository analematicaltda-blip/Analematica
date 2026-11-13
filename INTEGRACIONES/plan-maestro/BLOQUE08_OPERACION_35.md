# Bloque 8 — Calidad y operación

Estado: herramienta de verificación, instalación aislada, evidencias y procedimiento de reversión implementados. El plan maestro sigue en curso y producción permanece deshabilitada. Los builds web y la cualificación de hardware siguen siendo bloqueos reales.

## Implementación

- `BACKEND/INTEGRACIONES/operacion/verify_local.py`: una entrada para perfiles core, instalación nueva, navegador, dispositivos, PostgreSQL y builds web estrictos. No instala dependencias automáticamente, despliega ni modifica Git.
- Procesos independientes, límites de tiempo, registros privados de hasta 8 MiB, cancelación que termina el hijo y detiene grupos siguientes. Un comando que no descubre pruebas unittest no puede aprobar el grupo.
- Estados explícitos `PASSED`, `PASSED_WITH_SKIPS`, `FAILED`, `BLOCKED`, `TIMEOUT` y `CANCELLED`. Las omisiones impiden un resultado agregado completo; no se convierten en pruebas aprobadas.
- Informes JSON con versiones, tiempos, grupos y huellas; inventario de fuentes seleccionadas al principio y al final. Si cambia el código seleccionado durante la batería, no se declara completa.
- Verificación de hashes de registros/informe/inventario para detectar cambios accidentales. Son hashes locales, no una firma del autor ni una atestación de imágenes.
- Perfil fresh que instala ERP y Turismo en directorios y bases SQLite nuevos con migraciones locales; no reutiliza bases del usuario. Revisa HTTP, esquema, migraciones repetibles, relaciones, respaldos y procesos acotados existentes.
- Nuevo ensayo que restaura el modelo real `ContentDraft`, conservando texto cifrado, revisión y claves originales en otra base, sin cambiar el origen. Complementa el ensayo PostgreSQL existente de MFA/sesiones; no sustituye un respaldo completo productivo.
- Se excluye `/.runtime/` del Git de la raíz para evitar incorporar registros privados o credenciales temporales.
- Workflow manual `Local operation evidence` con permisos de lectura, sin credenciales Git persistidas ni despliegue; conserva solo resumen/hashes. No se ejecutó remotamente.
- Manual de preparación, diagnóstico y reversión compatible con esquema y claves; no incluye borrado de volúmenes, migraciones inversas ciegas ni sustitución automática de bases.

## Uso

```bash
python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile core --output /tmp/sgacd-core-nuevo
python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile fresh --output /tmp/sgacd-fresh-nuevo
python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile browser --profile devices --profile postgres --output /tmp/sgacd-integracion-nueva
python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile web-build --web-dependencies /ruta/node_modules --output /tmp/sgacd-build-nuevo
python BACKEND/INTEGRACIONES/operacion/verify_local.py --verify /tmp/sgacd-core-nuevo
```

Salida 0 significa únicamente que los perfiles seleccionados pasaron sin omisiones y con fuentes estables. Salida 2 conserva cualquier fallo, omisión, bloqueo, cancelación o cambio de fuentes. `production_ready=false` no se eleva por aprobar una batería.

Los resultados privados se guardan en una carpeta nueva, fuera del repositorio o bajo `.runtime` ignorado. No publicar sus bases, claves o registros crudos. El inventario abarca los directorios declarados, incluidos archivos nuevos dentro de ellos; no certifica todo el repositorio ni dependencias transitorias. No se exportan variables de entorno ni secretos al informe.

## Límites de aceptación productiva

1. Resolver `@sarita/shared-ui` y demás contratos/fuentes ausentes y completar ambos builds sin desactivar verificaciones.
2. Cualificar Android/iOS y escritorio físicos y distribución firmada; los contratos móviles simulados no acreditan hardware ni cuentas reales.
3. Verificar migraciones y restauraciones del esquema integral sobre infraestructura real, incluyendo claves y retención; medir RPO/RTO y carga. Los ensayos de esta entrega utilizan datos sintéticos aislados.
4. Fijar y reconstruir imágenes/dependencias productivas, escanear vulnerabilidades y firmar artefactos. `pip check` comprueba coherencia, no ausencia de vulnerabilidades; los requisitos actuales aún tienen rangos.
5. Cerrar los pendientes funcionales, identidad/SSO, proveedores, observabilidad y datos de los bloques anteriores. Que no exista la sesión ERP en Turismo no se soluciona exponiéndola sin diseño de permisos.

Manual completo: `INTEGRACIONES/operacion/README.md`. Se conserva la identidad visual; esta entrega no modifica pantallas. No hubo commit, push, merge, despliegue ni modificaciones de datos productivos.

## Resultado final observado

Batería final: `core + fresh + browser + devices + postgres + web-build` en `/tmp/sgacd-quality-final-35`.

| Resultado | Evidencia |
| --- | --- |
| Grupos seleccionados | 23: **20 PASSED**, **2 PASSED_WITH_SKIPS**, **1 FAILED** |
| Pruebas Python | 236 ejecutadas: 235 aprobadas, 1 omitida |
| Pruebas Node | 13 ejecutadas: 12 aprobadas, 1 omitida |
| Instalación nueva ERP | Esquema listo; 11 pruebas aprobadas |
| Instalación nueva Turismo | Esquema listo; 10 pruebas aprobadas y 1 omitida porque no expone la sesión ERP |
| Restauración editorial SQLite | Modelo real, revisión y descifrado conservados; base de origen intacta |
| PostgreSQL | 21 escenarios concurrentes; restauración de 28 tablas/108 filas con datos y relaciones coincidentes, 22 materiales MFA y 6 sesiones recuperados con claves originales |
| Chromium | Panel/taller en 1440, 390 y 320 píxeles con fixtures API |
| Builds estrictos | ERP y Turismo **FAILED**; continúa ausente `@sarita/shared-ui` |
| Inventario de fuentes | 2522 archivos seleccionados, sin cambios durante la batería |
| Integridad de evidencias | Hashes de registros, informe e inventario verificados |

El proceso devolvió **2**, coherente con omisiones y fallos; no es una aprobación de release. La prueba nativa de escritorio está omitida y los adaptadores Android/iOS usan transportes simulados. Las pruebas frescas de billetera usan llaves y datos de fixture; su registro canónico de producción fue actualizado sin cerrar pendientes.

`operation-evidence-35.json` y `evidencias/operacion-35/` conservan los resultados resumidos, incluido el informe de ambos builds. Los registros privados originales y el inventario detallado permanecen en la ruta temporal indicada; no se copiaron claves, bases ni registros crudos al repositorio. El paquete público resumido no contiene todos los archivos necesarios para `--verify` del paquete privado completo.
