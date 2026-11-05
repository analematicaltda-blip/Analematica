# Playbook: Gestión de Reservas Turísticas
**Misión:** Asegurar que cada solicitud de reserva sea validada y procesada eficientemente.

## Reglas Operativas
1. **Verificar Disponibilidad:** Consultar `ReservationService.check_availability`.
2. **Validar Identidad:** Confirmar que el usuario existe y tiene reputación válida.
3. **Verificar Capacidad:** Confirmar con el proveedor la disponibilidad técnica.
4. **Registrar Reserva:** Ejecutar `ReservationService.create`.
5. **Notificar:** Enviar confirmación al usuario vía `NotificationService`.
