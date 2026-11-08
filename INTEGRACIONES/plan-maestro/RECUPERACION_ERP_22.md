# Acceso ERP con código de recuperación — corte 22

Se implementó el acceso con códigos previamente emitidos por allauth. Esto no
completa la recuperación integral ni el plan maestro.

## Cambio funcional

Después de comprobar contraseña, el desafío ofrece usar TOTP o un código de
recuperación guardado previamente. Cada código válido se consume atómicamente
bajo bloqueo del usuario y los factores antes de establecer la sesión. Se
mantienen TOTP, roles y permisos; no se elimina ningún factor. La sesión nueva
registra la versión posterior al consumo; otras sesiones con la versión anterior
requieren reautenticación. Los códigos nunca se devuelven en la respuesta.

La nueva ruta POST /api/v1/erp-session/recovery/ conserva CSRF, vínculo con el
navegador, desafío de dos minutos, cinco intentos y bloqueo persistente compartido
con TOTP. Se rechazan códigos repetidos, desafíos vencidos, formatos legados sin
cifrar y políticas débiles. Solo se admiten semillas cifradas y configuración de
8 a 32 dígitos, entre 1 y 100 códigos. WebAuthn no se degrada a este mecanismo.

ERP_RECOVERY_CODES_ENABLED está apagado por defecto y exige habilitación
explícita además del acceso web ERP. No se habilitaron cuentas reales ni se
emitieron códigos para clientes. El gateway permite únicamente la ruta revisada.
La interfaz mantiene azul metalizado, azul claro y texto blanco; los códigos
se limpian al enviar y no se almacenan en localStorage.

## Verificación

- 43 pruebas de sesión, MFA, activación, limpieza y recuperación aprobadas,
  incluidas seis nuevas de recuperación.
- 27 regresiones de identidad y cotizaciones aprobadas.
- Cinco pruebas de configuración y límites del gateway aprobadas.
- 22 comprobaciones HTTPS con React, Django WSGI y Nginx reales, incluidos
  ingreso por recuperación, rechazo de reutilización y posterior prueba TOTP.
- TypeScript estricto y empaquetado comprobados por el recorrido web.
- git diff --check correcto. Sin migraciones nuevas.

Todos los usuarios y secretos de prueba son sintéticos, en entorno aislado.
No se verifica recepción de correos, teléfonos ni una aplicación autenticadora
real. Esta prueba no acredita concurrencia PostgreSQL de los códigos de
recuperación; requiere validación específica antes de producción.

## Pendientes y siguiente trabajo

1. Emisión y rotación desde interfaz con reautenticación y prueba TOTP fresca;
   no mostrar de nuevo ni regenerar códigos con una sesión sin nueva prueba.
2. Recuperación con pérdida de ambos factores mediante identidad verificada y
   procedimiento auditable, sin bypass por parte de empleados.
3. Recuperación de contraseña por correo previamente verificado, con proveedor,
   dominio y envío reales revisados; conservar MFA después del restablecimiento.
4. Prueba concurrente PostgreSQL de consumo, auditoría y notificaciones de uso.
5. Identidad compartida entre productos y restantes módulos del plan maestro.

No se cambian las dos autorizaciones del motor ni las firmas de la billetera.
No se creó commit, no se hizo push y no se desplegó a producción.
