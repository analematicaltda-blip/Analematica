# Plan maestro de integración · ejecución y límites

Alcance aprobado: Analemática, SGA-ERP-TUR y SGA-TUR; trabajo local sin reescritura general. Este registro distingue infraestructura comprobada de procesos de negocio no certificados. El alcance institucional/ERP recibido después se documenta en `../turismo-erp/DOCUMENTO_MAESTRO.md` y no convierte automáticamente sus requisitos en funciones implementadas.

| Frente | Avance de esta fase | Cierre pendiente |
|---|---|---|
| Arquitectura e inventario | Inventario reproducible de fuentes, rutas, modelos y páginas; matriz funcional y dependencias. | Completar trazas runtime, bases migradas y recorridos por rol. |
| Backends/datos | Ambos registros Django pasan checks; compras/proyectos/presupuesto/reportes quedan explícitamente no disponibles. Se preservan fuentes y bases existentes. | Reconciliar modelos/migraciones y realizar procesos reales; no activar pagos de ejemplo. |
| Identidad | Encabezados de proveedor exigen principal autenticado y propiedad; limpieza del contexto en excepciones; JWT de dominio no equivale al JWT central. | Delegaciones de empleados, jurisdicción institucional y SSO con contratos revisados. |
| Experiencia | Se inventarían páginas/layouts y recorridos candidatos; continúan paneles de control/recursos ya incorporados. | Responsive y E2E institucional primero; ERP desde el cliente después. |
| Motor asistente | Se conserva protocolo de dos autorizaciones del mismo solicitante y tercera de impacto. Se evita dependencia obligatoria de SDK IA al arrancar. | Android/iOS físicos, cuentas de prueba y proveedor vivo. |
| Seguridad/observabilidad | Se evita selección de proveedor por simple encabezado; deception con respuestas ficticias es opt-in en la configuración local. Hallazgo público de escritura institucional documentado. | Corregir y demostrar jurisdicción, desplegar AiSOC y conectar fuentes reales. |
| IA/contenido | ERP sin proveedor responde 503 y no fabrica contenido Dummy. Descubrimiento de 102 opciones conserva condiciones no verificadas. | Calidad/coste/privacidad medidos y adaptadores reales autorizados. |
| Calidad/operación | Pruebas Django aisladas, regresiones centrales y CI reproducible; inventario de cambios y estado de migraciones. | Restauración de copias, pruebas de carga, binarios móviles y preparación productiva. |

No se declara terminado el plan completo ni producción apta: faltan pruebas físicas, procesos de negocio, migraciones, conectores y revisión de permisos. El siguiente orden sigue siendo auditoría institucional → recorridos de cliente ERP → desarrollo incremental por criterio de aceptación.

## Cambios técnicos de esta fase

- Las rutas de compras importaban vistas totalmente comentadas con cuentas bancarias de ejemplo. Se conserva esa fuente, pero la API exige autenticación y devuelve 503 con `module_not_enabled`, sin consultar ni escribir datos financieros.
- Proyectos, presupuesto y reportes importaban modelos ausentes o comentados. Sus rutas pendientes devuelven 503 explícito; no se inventan alias contables ni se ocultan como módulos listos.
- Se registran los modelos de embudo existentes durante `AppConfig.ready`, evitando que una relación Lead dependa del orden de importación de URLs. No se migran tablas.
- Los SDK Gemini, semántica y voz se cargan cuando corresponde, sin impedir el arranque por ausencia de una integración opcional. El router de reescritura ERP devuelve 503 cuando no hay proveedor y no utiliza DummyProvider como respuesta real.
- Se agregan límites de tiempo a solicitudes Ollama y se conservan credenciales fuera de Git.
- Las rutas históricas conservan sus direcciones HTTP pero usan namespaces diferentes, sin ambigüedad con los canónicos.
- Se ajustan los campos requeridos por allauth y se excluyen directorios estáticos que no existen, sin silenciar checks de Django.
- El endpoint de salud no necesita resolver una entidad territorial por hostname. Su 200 solo comprueba conectividad de base, no esquemas ni procesos turísticos.
- La selección por `X-Tenant-ID`/`X-Company-ID` ya no concede acceso por sí sola. La propiedad del proveedor debe coincidir con el principal autenticado. Un perfil ajeno no se acepta; el contexto se restaura incluso con una excepción. El ID de proveedor NO se transforma automáticamente en ID core ERP; delegaciones y relaciones de empresas quedan pendientes de validación.

## Repetir verificaciones

En un entorno aislado Python 3.12, instalar las dependencias de turismo y las dependencias de pruebas FastAPI. Ejecutar desde la raíz:

```bash
CHECK_SERVICE=erp-tur python BACKEND/deployment/tests/tourism_runtime_check.py -v
CHECK_SERVICE=turismo python BACKEND/deployment/tests/tourism_runtime_check.py -v
PYTHONPATH=BACKEND/SGA-CD-BACKEND python -m unittest discover -s BACKEND/SGA-CD-BACKEND/tests -p 'test_assistance*.py' -v
PYTHONPATH=BACKEND/SGA-CD-BACKEND python -m unittest discover -s BACKEND/SGA-CD-BACKEND/tests -p test_resources.py -v
python INTEGRACIONES/turismo-erp/inventory.py --output /tmp/inventario-tecnico.json
```

Las pruebas Django generan claves temporales y usan SQLite en memoria. No deben apuntar a producción. No ejecutan migraciones, pagos, campañas ni proveedores. No se arrancaron Docker ni servidores en el portátil del usuario. Un chequeo Django exitoso no elimina los errores sintácticos de módulos que no se cargan en ese recorrido.

La validación desde un clon limpio detectó que el gateway API corporativo referenciado por Docker no estaba versionado. Se agrega su implementación restringida y pruebas de credenciales/cookies para que el código requerido acompañe al despliegue. La base de migraciones turística conserva su bloqueo explícito.

## Cortes posteriores de ejecución

- `../turismo-erp/OPTIMIZACION_02.md`: jurisdicción de atractivos y reseñas.
- `../turismo-erp/OPTIMIZACION_03.md`: aislamiento empresarial y bloqueo de RNT/pagos ficticios.
- `CIERRE_TECNICO_04.md`: reparación CRM y preparación de esquema.
- `BASES_LOCALES_05.md`: instalaciones nuevas sin respaldo histórico y copias privadas recuperadas.
- `BILLETERA_06.md`: transferencias internas con dos solicitudes de autorización, límites e idempotencia; pagos externos pendientes.

El tablero y las evidencias por corte distinguen código comprobado de pendientes. Las bases nuevas no requieren reparar la historia antigua para seguir desarrollando. Su correcta instalación no cierra reservas, contabilidad, conectores oficiales ni cualificación productiva.
