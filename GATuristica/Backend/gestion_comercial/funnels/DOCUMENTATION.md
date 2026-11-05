# Documentación del Módulo: Arquitecto de Embudos (`funnels`)

## 1. Diagrama de Modelos de Datos

```plaintext
+----------------+      +------------------+      +--------------------+
|     Tenant     |      |      Funnel      |      | FunnelPublication  |
|(infrastructure)|      |------------------|      |--------------------|
+----------------+      |- id (PK)         |      |- id (PK)           |
        |               |- tenant (FK)     |      |- funnel (FK)       |
        |               |- name            |      |- version (FK)      |
        |               |- status          |      |- public_url_slug   |
        +---------------+-- created_at     |      |- published_at      |
                        |-- updated_at     |      |- is_active         |
                        +------------------+      +--------------------+
                                |
                                |
          +---------------------+---------------------+
          |                                           |
+------------------+      +-----------------+      +-----------------+
|  FunnelVersion   |      |   LeadCapture   |      |   FunnelEvent   |
|------------------|      |-----------------|      |-----------------|
|- id (PK)         |      |- id (PK)        |      |- id (PK)        |
|- funnel (FK)     |      |- funnel (FK)    |      |- funnel (FK)    |
|- version_number  |      |- version (FK)   |      |- version (FK)   |
|- schema_json     |      |- page (FK)      |      |- event_type     |
|- created_at      |      |- form_data      |      |- metadata_json  |
|- is_active       |      |- captured_at    |      |- created_at     |
+------------------+      +-----------------+      +-----------------+
          |
          |
+------------------+
|    FunnelPage    |
|------------------|
|- id (PK)         |
|- funnel_version(FK)|
|- page_type       |
|- page_schema_json|
|- order_index     |
+------------------+
```

## 2. Documentación de Endpoints de la API

### Autenticación
Todos los endpoints, excepto los públicos (`/public/...`), requieren autenticación por Token JWT (`Authorization: Bearer <token>`).

### Gestión de Embudos (`/api/funnels/`)

- **`POST /api/funnels/`**: Crea un nuevo embudo.
  - **Request Body**: `{"name": "Mi Nuevo Embudo"}`
  - **Response (201)**: Objeto `Funnel` completo, incluyendo una `latest_version` inicial.

- **`GET /api/funnels/`**: Lista todos los embudos del tenant.
- **`GET /api/funnels/{id}/`**: Obtiene los detalles de un embudo específico.

### Gestión de Versiones

- **`POST /api/funnels/{id}/versions/`**: Crea una nueva versión para un embudo.
  - **Request Body**:
    ```json
    {
        "schema_json": { ... },
        "pages": [
            {"page_type": "landing", "page_schema_json": { ... }},
            ...
        ]
    }
    ```
  - **Response (201)**: Objeto `FunnelVersion` creado.

### Publicación

- **`POST /api/funnels/{id}/publish/`**: Publica una versión específica de un embudo.
  - **Request Body**: `{"version_id": <id_de_la_version>}`
  - **Response (200)**: `{"status": "...", "public_url": "/f/..."}`

### Endpoints Públicos (Sin Autenticación)

- **`GET /api/funnels/public/{slug}/`**: Obtiene el `schema_json` de una versión de embudo publicada para ser renderizada.
- **`POST /api/funnels/public/{slug}/leads/`**: Captura los datos de un formulario de un embudo público.
  - **Request Body**: `{"page_id": <id>, "form_data": { ... }}`
- **`POST /api/funnels/public/events/`**: Registra un evento de conversión (ej. `page_view`).
  - **Request Body**: `{"funnel_id": <id>, "version_id": <id>, "event_type": "...", "metadata": { ... }}`

## 3. Flujo de Trabajo Completo

1.  **Creación**: Un usuario crea un nuevo embudo a través de `POST /api/funnels/`. El backend crea el `Funnel` y una `FunnelVersion` inicial (v1).
2.  **Edición y Versionado**: El frontend trabaja con el `schema_json` del embudo. Cuando el usuario guarda su progreso, el frontend llama a `POST /api/funnels/{id}/versions/` con el nuevo `schema_json` y la estructura de páginas. El backend crea una nueva `FunnelVersion` (v2, v3, etc.).
3.  **Publicación**: El usuario decide publicar una versión específica (ej. v3). El frontend llama a `POST /api/funnels/{id}/publish/` con `version_id=3`. El backend crea un `FunnelPublication`, genera un `slug` único y lo activa.
4.  **Visualización Pública**: Un visitante accede a la URL pública. El frontend (o un renderizador) usa `GET /api/funnels/public/{slug}/` para obtener el `schema_json` de la v3 y renderiza la página.
5.  **Captura de Leads**: El visitante rellena un formulario. El frontend envía los datos a `POST /api/funnels/public/{slug}/leads/`. El backend lo guarda en `LeadCapture`.
6.  **Registro de Eventos**: A medida que el visitante navega, el frontend envía eventos a `POST /api/funnels/public/events/`, que son registrados por el backend.
