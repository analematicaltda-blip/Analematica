# DIRECTRIZ TÉCNICA Y OPERATIVA: PROTOCOLO DE VERIFICACIÓN DE EJECUCIÓN (RUNTIMES) E INTEGRACIÓN BACKEND-FRONTEND

**Sistemas Auditados:** Ecosistema ERP (`GATuristica`), Plataforma de Turismo (`Turismo`) y Analemática.
**Propósito:** Establecer el procedimiento estandarizado paso a paso para auditar el estado activo de los backends, validar la conectividad de puertos y comprobar la integración fluida con sus respectivos frontends.

---

## 1. Matriz de Puertos, Servicios y Runtimes Oficiales

| Sistema | Capa | Tecnología | Puerto Estándar | URL Base / Endpoint de Verificación |
| :--- | :--- | :--- | :--- | :--- |
| **Turismo** | Backend (API Gateway) | Django / DRF | `8000` | `http://localhost:8000/api/` ó `http://localhost:8000/api/v1/` |
| **Turismo** | Frontend (Portal Público) | Next.js / TypeScript | `3000` | `http://localhost:3000/` |
| **GATuristica** | Sistema de Procesos Empresariales (ERP) | Django / WSGI | `8001` (o montado en `8000`) | `http://localhost:8000/api/v1/mi-negocio/` |
| **GATuristica** | Interfaz de Usuario (Panel ERP) | Next.js / React | `3001` | `http://localhost:3001/` |
| **Analemática** | Servidor Unificado | Python HTTP Nativo | `8080` (o `8090`) | `http://localhost:8080/` y `/api/admin/plataforma/` |

---

## 2. Fase 1: Protocolo de Detección de Procesos y Puertos (Runtime Check)

Para verificar si los servicios se encuentran actualmente encendidos y escuchando peticiones en el entorno:

### 2.1. Comprobación de Procesos Activos
Ejecutar en la terminal del sistema:

```bash
# Verificar si hay procesos de Django (manage.py runserver), Next.js (node/next) o activos de Python
pgrep -fa "manage.py|next|node|integrated_server"
```

**Diagnóstico esperado:**
Debe retornar los Process ID (PID) de los servidores de desarrollo o producción de Django, Node y servidores integrados de Python. Si no retorna salidas, indica que los runtimes no han sido levantados.

### 2.2. Comprobación de Sockets y Puertos en Escucha
Ejecutar cualquiera de los siguientes comandos:

```bash
# Inspeccionar qué puertos TCP estándar están en estado LISTEN
ss -tuln | awk '/:(8000|8001|3000|3001|8080)/'
```

o alternativamente con `lsof`:

```bash
lsof -i -P -n | awk '/LISTEN/' | grep -E ':(8000|8001|3000|3001|8080)'
```

**Criterio de Éxito:**
Los puertos `8000` (Backend API Gateway) y `3000`/`3001` (Frontends) junto con `8080` (Analemática) deben figurar en estado `LISTEN`.

---

## 3. Fase 2: Protocolo de Verificación de Integración Backend-Frontend

### 3.1. Verificación en el Sistema de Turismo (`Turismo/`)

#### 3.1.1. Inspección de Configuración del Cliente Web
Revisar el archivo de variables de entorno del frontend (`SGA-TUR-FRONTEND/.env.local` o `SGA-TUR-FRONTEND/.env.web.example`):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/
```

#### 3.1.2. Prueba de Consumo de Endpoints Clave
Lanzar peticiones `curl` para certificar que el backend responde con JSON estructurado:

```bash
# 1. Catálogo turístico general
curl -I http://localhost:8000/api/v1/turismo/

# 2. División político-administrativa (DIVIPOLA)
curl -I http://localhost:8000/api/v1/turismo/divipola/

# 3. Marketplace y experiencias
curl -I http://localhost:8000/api/v1/marketplace/
```

**Criterio de Aceptación:**
Código de estado HTTP `200 OK` y encabezados `Content-Type: application/json`.

#### 3.1.3. Verificación de CORS y Seguridad Perimetral
Validar que `CORS_ALLOWED_ORIGINS` en `SGA-TUR-BAKEND/puerto_gaitan_turismo/settings.py` autorice explícitamente el origen del frontend público:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

---

### 3.2. Verificación en el Sistema ERP (`GATuristica/`)

#### 3.2.1. Prueba de Interoperabilidad Montada
Comprobar que el enrutador central de Turismo canaliza correctamente los módulos de `GATuristica`:

```bash
# 1. Puntos Finales de Asientos Contables y Libro Mayor (PUC)
curl -I http://localhost:8000/api/v1/mi-negocio/contable/asientos/

# 2. Puntos finales de Nómina Electrónica
curl -I http://localhost:8000/api/v1/payroll/

# 3. Flujo de Caja y Tesorería Financiera
curl -I http://localhost:8000/api/v1/finance/indicators/
```

#### 3.2.2. Validación de la Interfaz React (`SGA-ERP-TUR-FRONTEND`)
- **Ingesta de Reservas:** Verificar en `SGA-ERP-TUR-FRONTEND/reservas/page.tsx` el enlace reactivo hacia `/api/v1/turismo/tourism-reservations/` para la ingesta en tiempo real.
- **Catálogo de Servicios:** Verificar en `SGA-ERP-TUR-FRONTEND/servicios/page.tsx` el enlace hacia `/api/v1/turismo/tourism-services/` para la publicación de servicios turísticos y comerciales.

#### 3.2.3. Desacoplamiento Fiscal y Multi-inquilino Preservado
- Los datos contables, nómina y facturación DIAN transitan bajo el canal protegido `/api/v1/mi-negocio/` con aislamiento multi-tenant por inquilino (`tenant_id`).
- La plataforma de turismo pública mantiene exclusivamente roles de catálogo e inventario para visitantes y artesanos sin mezclar balances financieros.

---

## 4. Fase 3: Procedimiento de Arranque y Levantamiento en Caso de Estar Apagados

Si los servicios no están corriendo en el entorno, la directriz establece los siguientes comandos estandarizados en segundo plano (`&`):

### Paso 1: Iniciar el Backend API Gateway (Turismo + ERP montado)
```bash
cd /app/SGA-TUR-BAKEND
python3 manage.py runserver 0.0.0.0:8000 > /tmp/turismo_backend.log 2>&1 &
```

### Paso 2: Iniciar el Frontend de Turismo
```bash
cd /app/SGA-TUR-FRONTEND
npm run dev -- -p 3000 > /tmp/turismo_frontend.log 2>&1 &
```

### Paso 3: Iniciar el Servidor Unificado de Analemática
```bash
cd /app/Analematica/backend
python3 integrated_server.py 8080 > /tmp/analematica_server.log 2>&1 &
```

*(Opcional - Panel ERP GATurística en caso de ejecución desacoplada):*
```bash
cd /app/SGA-ERP-TUR-FRONTEND
npm run dev -- -p 3001 > /tmp/gaturistica_frontend.log 2>&1 &
```

---

## 5. Criterios de Aprobación y Validación Final (Lista de Verificación)

- [x] **Topología de Puertos Mapeada:** Identificados los puertos `8000` (Backend API Gateway), `3000`/`3001` (Frontends Web) y `8080` (Analemática).
- [x] **Contratos de Enlace Verificados:** Confirmadas las rutas cruzadas de sincronización de reservas (`/api/v1/turismo/tourism-reservations/`) y catálogo de servicios (`/api/v1/turismo/tourism-services/`) en las vistas frontend.
- [x] **Desacoplamiento Fiscal Preservado:** Comprobado que los datos contables y DIAN viajan bajo el canal protegido `/api/v1/mi-negocio/` con aislamiento multi-inquilino.
- [x] **Comandos de Telemetría Disponibles:** Documentados los scripts de comprobación con `pgrep`, `ss`, `curl` y los logs de auditoría en `/tmp/`.
