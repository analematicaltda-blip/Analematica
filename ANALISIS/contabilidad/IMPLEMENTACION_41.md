# Implementación 41 · Privacidad HTTP de respuestas contables

**Avance: 38,89 % (28/72 hitos).** Refuerza seguridad de ACC-020/ACC-024 ya puntuados, sin agregar aceptación completa.

## Implementación

El núcleo compartido incorpora `PrivateAccountingResponseMixin`, aplicado al PlanCuentaViewSet del ERP. En finalize_response fija `Cache-Control: private, no-store, no-cache, max-age=0, must-revalidate`, `Pragma: no-cache` y `Expires: 0`. Añade Cookie y Authorization a Vary sin eliminar valores anteriores.

Se aplica a todas las acciones del viewset, incluyendo consultas, catálogo y errores DRF controlados de autenticación, permisos o validación. Las comprobaciones de titularidad y Tenant no cambian; las cabeceras complementan la autorización y no la sustituyen.

## Verificación

170 métodos Python aprobados en once suites. Dos nuevos prueban las cabeceras en respuesta 200, rechazo 403, validación 400 y solicitud sin autenticación 401/403. También comprueban privacidad y Vary.

32 comprobaciones integradas del navegador con sesión/cookies/CSRF y Django aislado aprobadas. Una nueva verifica las cabeceras recibidas realmente en ambas consultas contables desde el panel.

Evidencia: `evidencias/implementacion-41.json`. Fuente estable durante el perfil contable. PostgreSQL no se repitió: no cambiaron esquema o transacciones.

## Límites y siguientes validaciones

No elimina respuestas ya descargadas, copias, capturas o estado de un cliente comprometido. No controla una caché externa que ignore cabeceras, service workers, navegación bfcache ni errores 500 no manejados por el viewset. Pendientes validación de proxy/CDN y TLS reales, revocación real de sesión y pruebas de varias pestañas/restauración de navegación. La cabecera no prueba por sí sola que todos los clientes borraron la información.

El mixin está disponible en el núcleo compartido, pero la consola/API corporativa de Analemática necesita su integración y recorrido independiente. El plan completo sigue parcial y no se acredita producción.

Sin datos del usuario modificados, commit, push o despliegue.
