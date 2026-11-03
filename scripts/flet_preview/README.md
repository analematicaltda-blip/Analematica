# Demo web y vistas Flet en Codespaces

Desde la raíz de SGA-CD, con la demo existente en `~/sgacd-demo`:

```sh
python3 scripts/update_demo_web.py
python3 scripts/setup_flet_previews.py
docker compose -f "$HOME/sgacd-demo/compose.json" build flet-desktop
docker compose -f "$HOME/sgacd-demo/compose.json" up -d --wait flet-desktop flet-mobile
```

Puertos privados: web 8080, escritorio Flet 8501 y móvil Flet 8502.
Los dos últimos son previsualizaciones web, no paquetes nativos instalados.
Se probaron imagen, healthchecks, sesiones WebSocket reales, controles
adaptables y paleta azul. El navegador del entorno de pruebas no pudo cargar
CanvasKit de gstatic; la revisión gráfica de Flet debe completarse en navegador
con acceso a esa CDN. La web sí se verificó con Chromium en cinco tamaños.

Las vistas Flet conservan su login SQLite heredado: todavía no se conectó a
las credenciales del backend. Tampoco se validaron sincronización ni todas sus
rutas. No son clientes completos de producción. No se descargan modelos LLM.

El actualizador web verifica hashes y conflictos antes de escribir, conserva
`js/config.js` y guarda respaldos fechados. El preparador de Flet conserva la
configuración Compose anterior y se detiene si esos servicios ya existen.
No ejecutar `docker compose down -v`: eliminaría volúmenes de datos.
