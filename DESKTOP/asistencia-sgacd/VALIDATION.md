# Validación de esta entrega

Entorno Linux, Python 3.12, Node 24 y Chromium instalado. Datos de protocolo aislados; pruebas de interfaz con el login real del entorno local de validación. Fecha: 2026-11-06.

| Comprobación | Resultado |
|---|---|
| Backend de asistencia y control | 27 pruebas correctas: privacidad usuario/tenant, catálogo, Open Duet simulado/contrato real, dos etapas del solicitante, tercera confirmación, caducidad, repetición, dominios/paquetes permitidos, revocación y resultado no presentado como éxito del proveedor. |
| Ejecutor Node | 11 correctas, una opcional de diagnóstico nativo omitida. Firma Ed25519, permisos alterados/vencidos, identidad, hilos MCP limitados, perfiles de planificación, Appium simulado Android/iOS y navegador real. |
| Chromium real, página sintética | Rechaza contenido de destinatario cambiado, consume referencias, exige login manual en campos protegidos, rechaza sustitución de archivo y carga los bytes cuyo hash se aprobó. |
| Panel web real | Ambas vistas HTTPS locales, SGA-CD y Analemática, a 1440/390/320 px: login, vinculación, revisión y ejecución autorizadas por separado, cancelación, revocación, sin desbordamiento ni errores JS. Sin ejecutor conectado a esas órdenes. |
| Open Duet original | 7 tests upstream correctos. Los 1.172 archivos coinciden con los hashes/modos de procedencia. |
| Regresiones | 32 workspace, 6 despliegue backend, 4 seguridad de vistas, 2 despliegue corporativo correctas. |
| Entradas web/Flet | Cuatro TSX modificados transpilan; ambos accesos Flet validan origen HTTPS, rechazan credenciales en URL y no abren el panel para un rol local no administrativo. No son builds completos de apps. |

No se probaron dispositivos Android/iPhone físicos, simuladores completos, Xcode/firma Apple, permisos USB reales, sesiones reales de proveedores, publicaciones, mensajes, campañas, gasto publicitario ni un proveedor de IA vivo. Open Duet completo no se arrancó: su backend upstream requiere Python 3.14+. Las pruebas Appium son respuestas W3C controladas, no una cualificación física.

Se inicializaron tablas/claves nuevas únicamente en el backend local de validación, conservando su base y credenciales. No se desplegó producción. Los backends turísticos conservan sus limitaciones documentadas; un enlace al control compartido no resuelve esas limitaciones.

Repetir localmente:

```bash
npm ci --prefix DESKTOP/asistencia-sgacd --ignore-scripts
node DESKTOP/asistencia-sgacd/verify-source.mjs
node --test DESKTOP/asistencia-sgacd/tests/*.test.mjs
PYTHONPATH=BACKEND/SGA-CD-BACKEND python -m unittest discover -s BACKEND/SGA-CD-BACKEND/tests -p 'test_assistance*.py' -v
```

Las pruebas de interfaz `tests/control.cjs` leen credenciales y certificado desde rutas privadas indicadas por variables; nunca imprimen esos valores. No deben ejecutarse contra producción. Para completar la cualificación, seguir la lista física y de cuentas en [CONTROL.md](CONTROL.md), en cada host y dispositivo expresamente autorizado.
