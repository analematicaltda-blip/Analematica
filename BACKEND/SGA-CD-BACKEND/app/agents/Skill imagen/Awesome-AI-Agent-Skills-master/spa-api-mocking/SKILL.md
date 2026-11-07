---
name: spa-api-mocking
description: Use when a cloned, migrated, or locally tested SPA needs safe local API mocks, backend shadowing, fixture responses, or route interception to run without the original production backend.
---

# Skill: SPA API Mocking (Backend Shadowing)

## Propósito
Interceptar y mockear llamadas a la API (fetch/XHR) de una Single Page Application (SPA) en un entorno local, eliminando dependencias de servidores externos y evitando bloqueos por CORS durante procesos de clonación profunda, ingeniería inversa o pruebas offline.

## Cuándo usar
- Cuando estás clonando un sitio web que depende de un backend para renderizar contenido (ej. listas de productos, perfiles).
- Cuando el frontend crashea o se queda en blanco por peticiones 404/403 hacia un dominio original.
- Para habilitar un entorno de desarrollo 100% offline.

## Implementación
1. **Identificar Endpoints:** Analiza las peticiones de red (usando `puppeteer` o inspeccionando el código) para encontrar las rutas de la API (ej. `/security/feedpducts`).
2. **Descargar Mocks:** Copia la respuesta JSON del servidor real usando tu navegador o `curl` y guárdalos en una carpeta local (ej. `api_mock/`).
3. **Servidor Interceptor:** Configura un `http.server` en Python o Node.js que:
   - Sirva los archivos estáticos (`index.html`, `js`, `css`).
   - Intercepte las rutas de la API específicas usando condicionales (`if path.startswith(...)`).
   - Devuelva los archivos JSON locales adjuntando los headers correctos, específicamente `Access-Control-Allow-Origin: *` y `Content-type: application/json`.
4. **Enrutamiento SPA:** Si es una SPA (React, Vue, JS Vainilla), todas las rutas no reconocidas o rutas principales (ej. `/login`, `/productos`) deben redirigirse a servir el `index.html`.

## Ejemplo de Servidor en Python
```python
import http.server, socketserver, urllib.parse, os

class SPAMockHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # Interceptar API
        if parsed.path.startswith("/api/productos"):
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open("api_mock/productos.json", "rb") as f:
                self.wfile.write(f.read())
            return
            
        # Enrutamiento SPA
        if parsed.path in ["/", "/productos", "/login"]:
            self.path = "/index.html"
            
        super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", 8081), SPAMockHandler) as httpd:
        httpd.serve_forever()
```

