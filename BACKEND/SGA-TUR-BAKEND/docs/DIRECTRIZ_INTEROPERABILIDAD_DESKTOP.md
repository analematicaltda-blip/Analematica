# DIRECTRIZ DE INTEROPERABILIDAD TOTAL — BACKEND ↔ DESKTOP APP

## 1. Puente de Hardware Local (Hardware Bridge)
- **Tecnología:** Electron Inter-Process Communication (IPC).
- **Alcance:** Integración con impresoras térmicas, escáneres USB y periféricos POS.
- **Seguridad:** Aislamiento vía `contextBridge` para evitar inyecciones en el proceso renderer.

## 2. Gestión de Sesión Empresarial
- **Persistencia:** Implementación de `DesktopStorageProvider` en el Shared SDK.
- **Ciclo de Vida:** Tokens de larga duración con rotación automática gestionada por el backend.
- **Sincronización:** Carga de perfiles de usuario y permisos RBAC en tiempo real.

## 3. Procesamiento Híbrido (Edge Computing)
- **Renderizado Local:** Generación de reportes PDF/Excel pesados en el cliente para liberar CPU del servidor.
- **Validación Backend:** El servidor valida la integridad de los reportes generados localmente mediante firmas SHA-256.

## 4. Comunicación Bidireccional
- **Canal:** WebSockets persistentes (WSS).
- **Mando y Control:** Recepción de directivas de Agentes IA para ejecución de tareas automáticas en la estación de trabajo.
- **Monitoreo:** Reporte de salud del hardware local (ej: "Sin papel en impresora") al Super Admin.

## 5. Seguridad de Instalación
- **Identidad:** Autorización de `Device-ID` único por terminal.
- **Firma:** Requerimiento de ejecutables firmados para acceso a la API de producción.
- **Túnel:** Encriptación TLS 1.3 obligatoria para todo el tráfico de datos.
