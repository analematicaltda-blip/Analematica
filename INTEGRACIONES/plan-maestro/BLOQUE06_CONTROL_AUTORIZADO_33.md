# Bloque 6 — Control autorizado de escritorio y móvil

Estado: refuerzo del protocolo implementado y verificado en local. La cualificación de dispositivos y cuentas reales continúa pendiente; el plan maestro no está al 100 %.

## Cambios entregados

- Se mantienen dos autorizaciones separadas del mismo administrador solicitante; las operaciones de impacto requieren una tercera. No hay aprobación por el agente.
- La política `sgacd-control-v2` exige comprobación online inmediatamente antes del despacho. El ejecutor comprueba firma, plan, dispositivo, administrador, empresa, alcance y vencimiento; la comprobación no amplía el permiso ni cuenta como autorización.
- Se vuelven a consultar permisos administrativos, estado del usuario/empresa y revocación del dispositivo. Los bloqueos SQL siguen el orden dispositivo → orden y evitan aprobaciones, reclamaciones y resultados duplicados concurrentes.
- Se rechazan permisos vencidos incluso en el instante exacto de caducidad. La cola excluye planes de políticas antiguas; el panel indica que requieren un plan nuevo.
- El diario local consume cada permiso antes del despacho. Sin comprobación online no se ejecuta; una entrega incierta no se reintenta automáticamente. Un resultado del dispositivo conserva `provider_success_verified=false`.
- CI incorpora los archivos del protocolo, ejecutor y pruebas en sus filtros. Se conserva la estructura y paleta del panel.

## Evidencia reproducible

| Verificación | Resultado |
| --- | --- |
| Python `test_assistance*.py` | 34 aprobadas |
| Node, con Chromium real sobre página de prueba | 12 aprobadas, 1 omitida, 0 fallos |
| PostgreSQL, sesiones SQLAlchemy independientes | 4 carreras aprobadas: aprobación, reclamación, resultado y revocación frente a reclamación |
| Suite PostgreSQL previa | 17 escenarios aprobados |
| Restauración aislada | 28 tablas, 108 filas, integridad y secretos de prueba recuperados; origen intacto |

En la carrera de revocación, una reclamación puede ocurrir antes de revocar; la comprobación posterior a la revocación debe rechazar el despacho. No se afirma atomicidad entre una transacción SQL y una interacción externa.

Comandos desde la raíz (Python con dependencias instaladas y Docker disponible para PostgreSQL):

```bash
PYTHONPATH=BACKEND/SGA-CD-BACKEND python -m unittest discover -s BACKEND/SGA-CD-BACKEND/tests -p 'test_assistance*.py' -v
node --test DESKTOP/asistencia-sgacd/tests/*.test.mjs
python BACKEND/deployment/tests/mfa_postgres_check.py
```

Los resultados y hashes de los registros locales están en `control-evidence-33.json`. Los registros originales permanecen en `/tmp/block6-release-python.log`, `/tmp/block6-companion-v2.log` y `/tmp/block6-pg-verified.log`; son temporales, no artefactos de producción. Las carreras usan bases efímeras y datos sintéticos.

## Activación y compatibilidad

Actualizar backend y ejecutor juntos antes de habilitar uso real. Un ejecutor anterior no puede aceptar permisos v2. Los planes anteriores se conservan como historial y deben recrearse y autorizarse nuevamente; no se reinterpretan ni aprueban automáticamente. No regenerar claves ni borrar credenciales durante esta actualización. No se requieren migraciones de esquema para estos cambios.

## Límites y pendientes

1. Validar el circuito completo en Android físico, iPhone con Mac/Xcode y hosts de escritorio; la prueba nativa de escritorio está omitida. Appium Android/iOS se probó con transportes simulados.
2. Verificar cuentas oficiales y flujos concretos de Meta, TikTok, Gmail/Google Ads y YouTube con autorización previa. Ninguna cuenta real fue operada en esta entrega.
3. Completar identidad central entre sistemas, autenticación reforzada y despliegue HTTPS real. Las pruebas HTTP usan identidad de prueba; dos etapas autenticadas no demuestran presencia física humana.
4. Validar desconexiones, observaciones cambiantes y revocación en cada dispositivo. El checkpoint reduce la ventana previa al despacho, pero no puede retirar una acción ya entregada ni asegurar parada instantánea de una operación externa en curso.
5. Cualificar distribución firmada, infraestructura, capacidad y protección del host. El protocolo no convierte un ejecutor comprometido en confiable.

Sin commit, push, despliegue ni cambios sobre datos de producción.
