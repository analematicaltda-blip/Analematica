# Monitor y acceso federado preparado

El título de la captura es Monitor en Vivo, no el del panel territorial. Se
conserva su sección. El espacio vacío se reprodujo con GSAP 3.12.5 y ScrollTrigger
reales: el código anterior dejaba las cuatro tarjetas con opacidad cero porque
la animación global de feature-card esperaba al bloque Módulos, situado después.
La animación ahora se limita a las tarjetas del bloque correspondiente y planes
tiene su propio disparador. El caso anterior falla y la corrección pasa; también
se comprobó el monitor vacío sin reserva de altura. Las cifras no se parten en
varias líneas en los cinco tamaños probados.

Se añade un broker para Google y Microsoft personales, con PKCE S256, estado,
nonce, cookie Secure/HttpOnly, comprobante temporal de consumo único, firma RS256,
emisor y audiencia. Solo autoriza correos vinculados explícitamente a usuarios
existentes activos cuyo correo coincida, y exige además la contraseña de SGA-CD.
Esta entrega no proporciona login sin contraseña ni crea usuarios o roles.
No se persisten JWT ni tokens de proveedor en el almacén temporal privado.

La web consulta disponibilidad y mantiene deshabilitados los proveedores sin
configuración. Los clientes Flet usan el broker y muestran la cuenta verificada;
no pasan IDs centrales a los módulos SQLite heredados. La sincronización de esos
módulos sigue pendiente. Las traducciones Flet se cargan por ruta de archivo,
independientemente del directorio de trabajo del contenedor.

El preparador conserva los archivos privados existentes, respalda Compose y crea
una imagen derivada del backend que añade el router sin sustituir sus ajustes.
Se probó construcción de imagen e importación de rutas mediante OpenAPI. La
repetición conserva Compose y el archivo privado tiene permisos 0600.

Pruebas locales completadas:
- GSAP/ScrollTrigger reales: fallo anterior reproducido y corrección confirmada.
- Landing: orden, menú, afiliados, video, ajustes simulados y cifras en cinco anchos.
- Broker: cinco pruebas, con firmas RSA reales generadas para el test, rechazo de
  identidad/nonce/audiencia/emisor/caducidad, correo no autorizado y solicitudes
  repetidas o rechazadas por la comprobación de cuenta.
- Rutas: cookies seguras, proveedores deshabilitados, JWT con rol profesor y
  aislamiento por inquilino, comprobante incorrecto y consumo repetido.
- Clientes Flet: recepción simulada de sesión central en ambos clientes sin tocar
  SQLite, construcción de vista de cuenta y sesiones WebSocket reales de login.
- Web OAuth: proveedores deshabilitados y respuesta autorizada simulada.
- Publicación y service worker: pruebas existentes pasan.

No hay aplicaciones OAuth registradas: el usuario confirmó que todavía no existen.
No se configuraron secretos reales ni se probó inicio de sesión externo. No se
accedió al terminal del Codespace del usuario. No se afirma producción completa,
una auditoría de seguridad ni resultados de Actions remoto. Instrucciones de
registro y configuración: docs/SSO-GOOGLE-MICROSOFT.md.
