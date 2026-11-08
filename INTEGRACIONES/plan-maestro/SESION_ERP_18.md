# Sesión ERP y recorrido HTTPS de cotizaciones

## Implementación

El ERP incorpora sesión web con contraseña real de Django, almacenamiento de
sesión en servidor y cookie HttpOnly. El componente de cotizaciones usa esa
sesión en vez del contrato antiguo de tokens; no guarda JWT ni contraseñas en
localStorage. Los clientes JWT existentes del dominio siguen siendo compatibles.

Se agregan estado, login y logout bajo /api/v1/erp-session/. El login exige CSRF
incluso antes de autenticar, limita intentos y no confía en X-Forwarded-For para
reiniciar la cuota. Django rota el identificador de sesión y el secreto CSRF al
entrar. La sesión dura quince minutos. Cookies separadas por servicio, SameSite
Strict, HttpOnly y ámbito /api/. En HTTPS se verificó Secure para ambas cookies.
Las respuestas de sesión y cotización llevan no-store.

No se crean cuentas, roles, empresas ni saldos al iniciar sesión. La autoridad
empresarial se sigue comprobando mediante VerifiedCompanyLink. Una cuenta con
MFA no puede entrar con contraseña sola por esta ruta; si enrola MFA después,
esta autenticación deja de aceptarla. El desafío MFA y SSO siguen pendientes.

Si falla la red durante logout, se limpian los datos de la pantalla y se muestra
que falta confirmar el cierre en el servidor, con botón para reintentarlo.
No se presenta una respuesta de red fallida como cierre de sesión confirmado.

## Gateway y entrada

El preparador crea /erp/cotizaciones en el proyecto Next ensamblado, reutilizando
el componente existente sin el layout heredado de dashboard. No sustituye el
acceso de los demás módulos. El proyecto completo y sus providers heredados
requieren todavía validación de build y recorrido propio.

SGACD_ENABLE_ERP_API=1 abre solo sesión y cotizaciones en el gateway. La
configuración mantiene bloqueadas las demás rutas, elimina Authorization de
Basic/Bearer hacia ese acceso de sesión y conserva el Host con puerto para CSRF.
ERP_WEB_SESSION_ENABLED=1 habilita el backend. Ambos son opt-in; no se activaron
servicios de trabajo ni producción. CSRF_TRUSTED_ORIGINS debe contener el origen
HTTPS exacto. SGACD_FRESH_LOCAL_HTTPS=1 activa cookies Secure al usar el perfil
fresh-local detrás de HTTPS; su valor predeterminado conserva HTTP de loopback.

## Evidencia real del recorrido local

Se ejecutó el componente React con Django WSGI y middleware completo, contraseña
real y cookies. Se repitió a través de Nginx HTTPS en Docker, con red temporal y
puerto publicado solo en 127.0.0.1. El backend de prueba escuchó en la IP privada
del entorno, porque el puente Docker estaba en otro namespace. Solo se eliminaron
el contenedor y la red creados para esta prueba.

Las cuentas y claves se generaron exclusivamente para la prueba, en memoria y
archivos privados fuera de Git; no son credenciales de clientes ni de producción.
El navegador acepta el certificado autofirmado únicamente en ese contexto local
y bloquea solicitudes externas. No se declara validación de un certificado de
producción ni despliegue del sistema completo.

- 10 pruebas de sesión: contraseña, CSRF, origen, cookies, rotación, MFA, logout,
  límite de intentos e imposibilidad de reiniciar la cuota con un encabezado.
- 27 pruebas de identidad/cotización y 14 de arranque ERP/Turismo.
- 5 pruebas de configuración y aislamiento del despliegue frontend.
- Total:56 ejecuciones Python aprobadas.
- 15 comprobaciones de navegador: entrada real, contraseña incorrecta, CSRF,
  cookies HttpOnly, ausencia de token local, guardado, idempotencia, recarga,
  retiro, fallo/reintento de logout, limpieza de datos, anónimo, móvil,
  paleta azul/blanco y ausencia de solicitudes externas.
- Nginx HTTPS también rechazó las rutas financieras todavía no habilitadas.

Ver erp-session-evidence-18.json y evidencias/sesion-erp-https-movil.png.
La compilación TypeScript del componente se comprobó; no equivale al build
completo de Next ni a certificación de pagos, reservas, SOC o dispositivos.

## Pendientes que siguen abiertos

MFA completo, SSO entre los almacenes de identidad, recuperación de cuentas,
revisión externa, capacidad y concurrencia productivas, build completo y recorridos
del ERP heredado, disponibilidad/impuestos/pagos, SOC y equipos reales.
El plan maestro continúa parcial. Los cambios permanecen sin commit/publicación.
