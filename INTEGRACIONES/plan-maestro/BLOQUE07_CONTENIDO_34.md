# Bloque 7 — IA y producción de contenido

Estado: primer flujo editorial implementado y probado localmente; evaluación de modelos reales y modalidades multimedia pendiente. No se declara el frente ni el plan maestro completos.

## Entrega

- Nuevo taller `/content.html`, enlazado desde el centro administrativo, recursos y guías. Conserva la estructura existente con azul metalizado, acentos azul claro y texto blanco; se copia expresamente a las vistas de Analemática y SGA-CD.
- API administrativa `/api/v1/assistance/content`: crear, consultar, editar, revisar y exportar borradores privados del solicitante en su organización. Los identificadores ajenos no revelan contenido.
- Tabla aditiva `assistance_content_drafts`: brief/texto cifrados con Fernet y claves existentes fuera de Git; procedencia y métricas separadas. La preparación explícita está en `app.services.assistance.schema`, sin borrados ni instalación sobre bases reales.
- Revisión humana ligada a versión y SHA-256. Editar exige revisión nueva; solicitudes sobre versiones anteriores se rechazan mediante actualización condicional SQL. Exportar no publica ni concede autorizaciones de control.
- Adaptador Ollama local optativo: consentimiento por operación, modelos permitidos por el operador, loopback, sin redirecciones ni herramientas. Límites de tiempo/tamaño/salida; errores visibles sin respuestas ficticias ni sustitución por APIs pagadas. Se filtran patrones conocidos de credenciales antes de enviar el brief; no es un detector exhaustivo de datos personales.
- Evaluador secuencial optativo para modelos locales: brief público sintético idéntico, latencia, longitud y hash de salida. No almacena textos/credenciales ni inventa calificaciones de calidad.
- CI incluye pruebas editoriales y recorrido de navegador. Sin cambios de permisos de billetera ni automatización de publicación.

## Pruebas realizadas

| Prueba | Resultado y alcance |
| --- | --- |
| Suite de asistencia | 43 aprobadas, incluidas 9 nuevas de contenido/proveedor |
| Catálogo administrativo | 3 aprobadas |
| Preparación y seguridad web | 8 aprobadas |
| Chromium, 1440/390/320 | Crear, revisar, exportar y editar; error de proveedor; texto blanco y ausencia de desbordamiento |
| Evaluador sin proveedor habilitado | Salida 1 y estado `unavailable`, sin generación ni métricas inventadas |

Las pruebas de API usan identidad y SQLite de fixture; las respuestas Ollama usan `MockTransport`. El navegador usa un contrato API sintético, separado de las pruebas de backend. No se afirma una prueba end-to-end con login y modelo reales. Los registros temporales y sus hashes se identifican en `content-evidence-34.json`.

Comandos desde la raíz:

```bash
PYTHONPATH=BACKEND/SGA-CD-BACKEND python -m unittest discover -s BACKEND/SGA-CD-BACKEND/tests -p 'test_assistance*.py' -v
PYTHONPATH=BACKEND/SGA-CD-BACKEND python -m unittest discover -s BACKEND/SGA-CD-BACKEND/tests -p test_platform.py -v
python -m unittest discover -s FRONTEND/deployment/tests -p 'test_*.py' -v
PLAYWRIGHT_MODULE="$PWD/DESKTOP/asistencia-sgacd/node_modules/playwright" node FRONTEND/ANALEMATICA-FRONTEND/tests/content.cjs
```

## Pendientes verificables

1. Instalar y habilitar un modelo real; medir calidad en español, exactitud, latencia, RAM, licencia y coste operativo antes de recomendarlo. Este entorno no dispone de Ollama/modelo ni credenciales de proveedor configurados.
2. Evaluar proveedores actuales de imágenes, vídeo, voz y transcripción. El catálogo gratuito existente es una referencia, no evidencia de disponibilidad o gratuidad vigente.
3. Verificar sesión real, permisos y enlaces desde ERP/Turismo, manteniendo aislamiento; SSO aún no implementado.
4. Probar carga/concurrencia PostgreSQL del taller, límites compartidos, respaldo/restauración de contenido y claves, retención y eliminación. Las pruebas del bloque 6 no certifican esta tabla nueva.
5. Mantener publicación separada: si después se integra con ejecutores, requerirá las dos autorizaciones del solicitante y tercera de impacto; la aprobación editorial no se reutiliza como permiso de ejecución.

Configuración, contratos, comparativa de alternativas y procedimiento de evaluación: `INTEGRACIONES/ia-contenido/README.md`.

No hubo commit, push, despliegue ni operaciones sobre cuentas reales.
