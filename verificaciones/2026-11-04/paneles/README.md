# Verificación: paneles integrados por rol

Entorno de validación local, separado del Codespace privado del usuario.

- 13 pruebas backend/actualizador: Básico denegado, Full vigente, delegación y revocación, aislamiento de empresa/plataforma, rechazo de fechas futuras y estados inválidos, cuotas atómicas, devolución ante fallos, canal cifrado propio, publicación privada idempotente, protección de rutas antiguas, registro persistente y preservación de servicios/estado offline.
- 10 pruebas Nodo 6: generación con proveedor simulado, FFmpeg real, secretos no reflejados, configuración persistente con permisos 0600, canal por empresa, autenticación y publicación privada con transporte simulado.
- 48 combinaciones de navegador: 12 roles × 1440, 768, 390 y 320 px. Verificación de acordeón, cajón móvil cerrado/foco, ausencia de desbordamiento, control de plan/rol y uso del JWT de SGA en lugar del token del trabajador.
- Recorrido real nginx → backend PostgreSQL → Nodo 6: un miembro delegado generó un MP4 1080×1920, descargó con JWT y perdió el acceso tras revocar su permiso.
- Navegador contra los servicios reales: panel de empresa generó y reprodujo un MP4 1080×1920. Capturas adjuntas de escritorio, móvil y estudio.
- Actualizador ejecutado repetidamente sin pérdida de configuración web, usuarios o datos. Solo se recrearon backend y nodo 6; nginx recargado.
- Sin solicitudes de publicación a YouTube ni envíos sociales reales. Las llamadas Gemini/YouTube de pruebas unitarias usan transporte simulado. No se afirma validación externa de cuentas no autorizadas.

Reproducir pruebas locales:

```bash
python -m unittest discover -s BACKEND/tests/workspace -v
NODE6_OUTPUT=/tmp/sgacd-node6-tests python -m unittest discover -s BACKEND/tests/node6 -v
python FRONTEND/tests/publisher.py
node FRONTEND/tests/service-worker.cjs
SGA_WEB_URL=http://127.0.0.1:18090 PLAYWRIGHT_MODULE=/ruta/node_modules/playwright GSAP_DIST=/ruta/node_modules/gsap/dist node FRONTEND/tests/workspace.cjs
```

El backend conserva avisos previos de modelos dinámicos SQLAlchemy y configuraciones Pydantic antiguas; no impidieron las pruebas. No se modificaron para ampliar el alcance de esta entrega.
