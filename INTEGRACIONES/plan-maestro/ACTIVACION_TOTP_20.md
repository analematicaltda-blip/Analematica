# Activación TOTP desde el ERP — corte 20

Se implementó la primera activación del segundo factor desde el espacio de
cotizaciones. El plan maestro sigue en curso; no se certifica producción.

## Comportamiento y límites

- Sesión ERP personal activa, CSRF y reingreso de contraseña obligatorios.
- La clave pendiente se cifra en SQL con el adaptador MFA existente. No se crea
  un autenticador hasta demostrar un código correcto; vence a los dos minutos
  y admite cinco intentos. La propuesta está vinculada a cuenta, sesión,
  contraseña y versión de factores.
- La activación guarda el contador usado y rota la sesión. No permite reemplazar
  factores registrados. Otra sesión no puede confirmar la propuesta.
- Cancelar es repetible, elimina el secreto pendiente y nunca elimina factores.
  Reiniciar invalida y elimina el secreto de la propuesta anterior de esa sesión.
- La interfaz ofrece configuración manual sin servicio QR externo. La clave se
  muestra enmascarada, vive en memoria y se oculta al abandonar la pestaña. Si
  falla la cancelación de red, oculta la clave y ofrece reintentar.
- Colores azul metalizado, celeste y texto blanco; vista móvil de 390 px comprobada.

Rutas POST: /api/v1/erp-session/enrollment/start/, confirm/ y cancel/.
El gateway limita la exposición a esas rutas. ERP_TOTP_ENROLLMENT_ENABLED=1 es
necesario además de ERP_WEB_SESSION_ENABLED=1. Ambos permanecen apagados por
defecto; no se habilitó ningún entorno de clientes.

Nueva migración fresh-local turismo.0005_erptotpenrollment, aplicada únicamente
en dos bases temporales de validación. No se modifican migraciones heredadas.

## Evidencia observada

- 34 pruebas de sesión/MFA y activación aprobadas (nueve de activación).
- 27 regresiones de identidad empresarial y cotizaciones aprobadas.
- Base ERP migrada: 11 pruebas aprobadas.
- Base Turismo migrada: 10 aprobadas y una omitida por no exponer sesiones ERP.
- HTTPS con React, Django y Nginx reales: 22 comprobaciones del recorrido de
  activación, incluida cancelación con fallo de red, prueba incorrecta,
  activación correcta e ingreso posterior con el factor recién creado.
- Regresión HTTPS de ingreso TOTP existente: 19 comprobaciones aprobadas.
- Configuración y límites del gateway: cinco pruebas aprobadas.
- TypeScript estricto y empaquetado del componente incluidos en la prueba web.

Se usaron cuentas y claves sintéticas. No se conservan claves de configuración
ni credenciales en la evidencia. Ver enrollment-evidence-20.json y
[evidencia móvil](evidencias/enrollment-erp.png).

## Pendientes para producción y continuación

1. Recuperación verificada, pérdida del autenticador y cambios de dispositivo;
   no existe un botón que retire la protección sin una nueva prueba.
2. Validación con aplicaciones autenticadoras y teléfonos físicos; lo observado
   genera códigos estándar en Node y los verifica en Python.
3. Política y tarea de purga de propuestas abandonadas: caducar impide activarlas,
   pero el cifrado de una propuesta abandonada permanece hasta cancelación,
   reinicio en la misma sesión o limpieza administrativa aún no implementada.
4. Custodia y rotación de FIELD_ENCRYPTION_KEY, auditoría independiente,
   concurrencia integral en PostgreSQL y pruebas de carga.
5. WebAuthn, identidad central de los tres productos, demás recorridos y build
   completo. Este corte prueba el espacio de cotizaciones, no todos los módulos.

Contraseña y TOTP acreditan identidad; siguen siendo necesarias las dos
aprobaciones separadas del administrador para el motor y las firmas vinculadas
a dispositivos de la billetera. No se habilitan operaciones financieras,
publicaciones ni control de equipos. Cambios locales sin commit ni push.
