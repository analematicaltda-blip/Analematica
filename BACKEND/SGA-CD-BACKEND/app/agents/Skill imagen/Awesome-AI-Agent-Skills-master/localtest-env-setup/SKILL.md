---
name: localtest-env-setup
description: Use when setting up a local test environment for cloned or migrated web apps, especially localtest.me routing, static serving, HTTPS/CORS simulation, and repeatable localhost diagnostics.
---

# Skill: Localtest Environment Setup

## Propósito
Configurar rápidamente entornos de prueba locales (sandbox) que emulan dominios de producción utilizando el servicio DNS comodín (wildcard DNS) `localtest.me` combinado con un servidor local de enrutamiento interceptor en Python o Node.js, sin necesidad de tocar el archivo `hosts` del sistema.

## Cuándo usar
- Al probar clones de sitios web que utilizan validaciones estrictas de nombre de dominio (`location.hostname === 'midominio.com'`).
- Cuando necesitas rutear subdominios como `api.localtest.me` o aislar cookies y CORS en entornos "reales".
- Para levantar un servidor SPA (Single Page Application) que emule respuestas API, sirva estáticos y rutee todo a `index.html`.

## Implementación

### 1. El Servicio `localtest.me`
El dominio `localtest.me` y todos sus subdominios (ej. `midominio.localtest.me`) siempre resuelven a `127.0.0.1`. Esto te permite usar nombres amigables al instante:
```bash
http://proyecto.localtest.me:8081
```

### 2. Estructura del Proyecto
- `api_mock/`: Carpeta con archivos `.json` que simulan respuestas del backend.
- `assets/`: Carpeta raíz con estáticos interceptados.
- `server.py`: Servidor de enrutamiento interceptor.

### 3. Servidor de Intercepción y SPA (Python)
Crea un `server.py` que sirva archivos estáticos nativamente, pero intercepte llamadas API y URLs amigables de la SPA:

```python
import http.server, socketserver, urllib.parse, os

PORT = 8081

class SPAInterceptor(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # Interceptar Mock API
        if parsed.path.startswith("/api/mock"):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open("api_mock/data.json", "rb") as f:
                self.wfile.write(f.read())
            return
            
        # SPA Routing: Enviar todo lo que no sea un archivo estático al index.html
        if not "." in parsed.path.split("/")[-1]:
            self.path = "/index.html"
            
        super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), SPAInterceptor) as httpd:
        print(f"Servidor en: http://mi-clon.localtest.me:{PORT}")
        httpd.serve_forever()
```

### 4. Lanzador (.bat)
Si estás en Windows, automatiza el arranque para no tener que abrir terminales manualmente:
```bat
@echo off
title Servidor de Entorno Local
echo Iniciando servidor en puerto 8081...
start http://mi-clon.localtest.me:8081
python server.py
pause
```

## Beneficios
- Evita lidiar con certificados SSL rotos si configuras un reverse proxy proxy (como ngrok o localtunnel) encima.
- Emula rutas de producción 1:1, crucial para el éxito del routing nativo en el framework frontend.

