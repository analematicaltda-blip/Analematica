# Bloque 2 — disponibilidad y retenciones de cupos

Primera implementación de disponibilidad por intervalo y retenciones temporales.
El bloque completo sigue abierto: no se habilitan reservas confirmadas ni pagos.

## Entregado

Nueva AvailabilityHold y migración fresh-local turismo.0007_availabilityhold.
Cada retención tiene prestador, servicio, solicitante, intervalo, cantidad,
clave de idempotencia, digest, vencimiento y liberación. Caduca en diez minutos.
No descuenta dinero, no genera factura y no crea Reservation confirmada.

Las rutas privadas del ERP son:

- POST /api/v1/mi-negocio/comercial/service-availability/
- POST /api/v1/mi-negocio/comercial/capacity-holds/
- POST /api/v1/mi-negocio/comercial/capacity-holds/{id}/release/

Exigen autenticación JWT o sesión ERP con CSRF y vínculo empresarial revisado
vigente del titular. ERP_CAPACITY_HOLDS_ENABLED=1 habilita explícitamente estas
rutas; permanece apagado por defecto. El gateway admite solamente las rutas
revisadas. La respuesta no se almacena en caché. No hay interfaz web nueva en
este corte; el diseño existente no se modifica.

## Contrato

Disponibilidad: provider_id, service_id, start_at, end_at y quantity entero.
Creación añade idempotency_key UUID. Las fechas requieren zona explícita,
intervalo positivo de hasta365 días y comienzo futuro para nuevas operaciones.
No se admiten campos adicionales como precio, impuesto o indicador de pago.
Cantidad entre1 y10000. La capacidad usa unidades del servicio, no se interpreta
automáticamente como camas, habitaciones, huéspedes o vehículos.

Los intervalos son semiabiertos: el final de uno puede coincidir con el inicio
de otro. Se calcula el pico de ocupación simultánea, no la suma de retenciones
disjuntas. Creación y liberación bloquean la fila del servicio en SQL. El acceso
se revalida aun al repetir solicitudes. Una clave repetida devuelve el mismo
registro sin renovar su plazo; contenido diferente devuelve409. Una carrera
de claves iguales entre servicios diferentes también se controla con unicidad
SQL y conflicto409, sin duplicar registros.

Retenciones vencidas o liberadas dejan de consumir cupos. Las filas se conservan
para trazabilidad; falta política operativa de retención. Cualquier reserva
histórica activa que se cruce bloquea el intervalo como requiere conciliación:
no se adivina la cantidad consumida de metadata heredada. Más de10000 retenciones
coincidentes exige revisión en vez de certificar disponibilidad con datos truncados.
La lectura es orientativa; únicamente crear la retención comprueba capacidad
bajo bloqueo. Otros escritores heredados deben adaptarse a ese bloqueo antes
de garantizar capacidad de extremo a extremo en producción.

## Verificación

-14 pruebas de dominio/API aprobadas: capacidad, medio abierto, pico simultáneo,
vencimiento, liberación, idempotencia, revocación y acceso ajeno, servicio cruzado,
conciliación histórica, fechas/campos inválidos y habilitación explícita.
-27 regresiones de identidad/cotizaciones y5 del gateway aprobadas.
-3 carreras PostgreSQL entre procesos: último cupo (una aceptación), mismo payload
(dos respuestas y una sola retención), misma clave entre servicios (una aceptación
más409). No se excedió capacidad en esos escenarios.
-Se conservaron13 escenarios anteriores de MFA/HTTP y el ensayo de restauración.
-Migración aplicada y deriva comprobada en dos bases temporales, no de clientes.
-git diff --check correcto. Casos sintéticos; no pagos ni llamadas a proveedores.

## Qué falta para cerrar el bloque 2

1. Interfaz web de calendario/retenciones y flujos del cliente, con pruebas reales
   de sesión, permisos, vencimiento y recuperación ante fallo de red.
2. Política por tipo de servicio: recursos, horarios, temporadas, bloqueos de
   mantenimiento, unidades y conciliación de reservas antiguas.
3. Convertir retención en reserva confirmada mediante transición idempotente,
   cancelaciones, auditoría y políticas comerciales, sin doble liberación.
4. Enlazar Product/CRM del cotizador con TourismService sin asumir igualdad de IDs;
   congelar tarifas y condiciones aceptadas.
5. Perfil tributario, clasificación y cálculo revisados; no inventar IVA ni
   interpretar ausencia de configuración como exención.
6. Proveedor de pagos en sandbox, verificación de webhook/firma, conciliación,
   reversión y comprobantes; aprobación para operar cuentas reales/productivo.
7. Carga y carreras HTTP de disponibilidad, permisos de administración de cupos,
   respaldo integral, integración operativa y supervisión.

La prueba nueva solo garantiza el contrato nuevo; no certifica todos los
escritores de reservas existentes. Ningún bloqueo fiscal o de pagos fue retirado.
Sin commit, push ni publicación. Ver capacity-evidence-29.json.
