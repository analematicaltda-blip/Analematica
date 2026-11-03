# Nodos Flet móvil y escritorio

Con la demo existente en `~/sgacd-demo`, ejecuta desde el repositorio:

```sh
python3 scripts/start_flet_nodes.py
```

El comando prepara los dos servicios, construye una imagen compartida, los
arranca y comprueba HTTP y una sesión WebSocket real con la vista inicial.
Se puede repetir. Conserva los servicios existentes y los volúmenes de datos;
si los nodos tienen otra configuración, se detiene antes de sustituirla.
La primera preparación guarda un respaldo de compose.json.

| Nodo | Fuente montada en lectura | Puerto privado |
| --- | --- | --- |
| Escritorio | SGA-CD-APP.git | 8501 |
| Móvil | SGA-CD-APK.git | 8502 |

En Codespaces, abre **Puertos**, agrega 8501 y 8502 si no aparecen y conserva
la visibilidad **Private**. Abre la dirección reenviada de cada fila. El comando
también imprime las direcciones cuando reconoce las variables de Codespaces.
No cambies la visibilidad a pública.

Estos son servidores de vista previa web de las aplicaciones Flet, no
instaladores Android/iOS/Windows/macOS/Linux. El login SQLite heredado sigue
independiente del backend. El acceso central Google/Microsoft tiene su pantalla
de cuenta verificada; requiere configurar los proveedores según
[la guía SSO](../../docs/SSO-GOOGLE-MICROSOFT.md). Los módulos locales todavía no
se unificaron con la API.
No se descargan modelos LLM al arrancar. La comprobación de sesión no sustituye
la revisión visual ni valida todos los módulos. CanvasKit y recursos externos
pueden requerir acceso desde el navegador.

Diagnóstico:

```sh
docker compose -f "$HOME/sgacd-demo/compose.json" ps flet-desktop flet-mobile
docker compose -f "$HOME/sgacd-demo/compose.json" logs --tail 60 flet-desktop flet-mobile
```

Para detener solo estos nodos sin borrar datos:

```sh
docker compose -f "$HOME/sgacd-demo/compose.json" stop flet-desktop flet-mobile
```

Para otra demo, usa `--demo-dir /ruta/demo`. En un entorno con CA de proxy,
`--proxy-ca /ruta/ca.pem` pasa la CA como secreto de construcción sin desactivar
TLS. No ejecutar `down -v`, pues elimina volúmenes.

La actualización de la web es independiente: `python3 scripts/update_demo_web.py`.
