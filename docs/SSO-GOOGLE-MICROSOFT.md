# Acceso con Google y Microsoft

Estado: implementación preparada y probada con identidades simuladas. No está
activada: el propietario todavía no ha registrado las aplicaciones OAuth ni
configurado credenciales reales. No existe una prueba de acceso real a proveedores.

La web y los servidores de vista previa Flet utilizan un broker en el backend.
El acceso requiere tanto la identidad Google/Microsoft como la contraseña de la
cuenta SGA-CD autorizada: no es acceso sin contraseña. Esta comprobación adicional
evita que una solicitud abierta en otro dispositivo entregue una sesión por sí sola.
Escribe la contraseña de SGA-CD antes de pulsar el botón del proveedor.
Los secretos permanecen en el servidor. Se solicitan solo openid, email y profile;
esto no concede acceso a Gmail, Drive ni al correo de Microsoft. La integración
Google Workspace anterior se mantiene separada y no se reutiliza para este login.
Microsoft se limita a cuentas personales (Outlook, Hotmail, Live); cuentas laborales
Entra requieren otra configuración y política de emisores.

## Registrar las aplicaciones

1. En https://console.cloud.google.com/apis/credentials configura la pantalla de
   consentimiento de Google, agrega tus usuarios de prueba y crea un cliente OAuth
   de tipo **Aplicación web**. Registra la URL de retorno que imprime el preparador.
2. En https://entra.microsoft.com registra una aplicación que permita **cuentas
   personales de Microsoft**. Agrega una plataforma **Web** con la URL de retorno
   de Microsoft. Crea una credencial de cliente en Certificados y secretos.
3. Conserva los IDs y secretos en `~/sgacd-demo/sso.env`, fuera del repositorio.
   No pegues los secretos en el chat. Las URLs de retorno deben coincidir exactamente.

Para el Codespace actual, el preparador detecta el dominio y usa el puerto web 8080:

```sh
python3 scripts/setup_sso.py
```

Si no reconoce Codespaces:

```sh
python3 scripts/setup_sso.py --public-origin https://TU-DIRECCION-REENVIADA-8080.app.github.dev
```

Imprime estas dos rutas sobre ese origen:

- `/api/v1/sso/google/callback`
- `/api/v1/sso/microsoft/callback`

Los proveedores deben poder completar la redirección en tu navegador autenticado.
Conserva privados los puertos; Codespaces es una demo temporal, no alojamiento
permanente. Cambiar el nombre del Codespace o el dominio requiere actualizar las
URLs registradas y `SSO_PUBLIC_ORIGIN`.

## Autorizar cuentas existentes

Completa en el archivo privado:

```dotenv
SSO_PUBLIC_ORIGIN=https://TU-DIRECCION-REENVIADA-8080.app.github.dev
SSO_GOOGLE_CLIENT_ID=
SSO_GOOGLE_CLIENT_SECRET=
SSO_MICROSOFT_CLIENT_ID=
SSO_MICROSOFT_CLIENT_SECRET=
SSO_ACCOUNTS_JSON={"google":{"tu-cuenta@gmail.com":"usuario_sga"},"microsoft":{"tu-cuenta@outlook.com":"otro_usuario_sga"}}
```

Cada usuario SGA-CD debe existir, estar activo y tener exactamente ese correo.
La correspondencia se configura expresamente: el login no crea usuarios ni asigna
roles por dominio, no altera cuentas existentes y no autoriza administradores
por el mero hecho de tener una cuenta de Google o Microsoft.

Para construir el backend ampliado e iniciar solo backend y vistas Flet:

```sh
python3 scripts/setup_sso.py --start
python3 scripts/update_demo_web.py
```

El preparador respalda Compose, conserva las credenciales existentes, crea una
imagen derivada de la imagen actual del backend y monta el estado temporal de
acceso en el volumen `/state`. No borra volúmenes. Los proveedores sin credenciales
permanecen deshabilitados; la contraseña local sigue disponible.

## Alcance y comprobación

Se validan firma RS256, audiencia, emisor, caducidad, nonce, PKCE S256, state,
cookie HttpOnly/Secure y comprobante de consumo de un solo uso. No se guardan
tokens del proveedor ni JWT de SGA-CD en la base temporal de solicitudes y no se
incluyen en direcciones URL. Los permisos salen de la cuenta local autorizada.

El estado temporal SQLite compartido corresponde a una demo en un solo servidor;
no es una solución distribuida entre varios servidores independientes.

En Flet, la sesión central se muestra en una pantalla de cuenta verificada.
Los módulos conservan su SQLite para trabajar sin internet y sincronizar
posteriormente con el servidor. La autenticación central no sustituye esa base
ni transfiere IDs sin una correspondencia de usuarios válida. Esta entrega no
modifica ni certifica la sincronización existente. Tampoco empaqueta aplicaciones
nativas.

Pruebas:

- `tests/sso/test_broker.py`: firmas e identidades inválidas, emisor/audiencia,
  correo verificado, PKCE/cookie/state, expiración y consumo único.
- `tests/sso/test_routes.py`: cookies seguras, proveedores deshabilitados, emisión
  de JWT con los roles existentes y rechazo de comprobantes incorrectos/repetidos.
  Se ejecuta dentro de la imagen de backend con `/tmp/sso_routes.py` preparado.
- `tests/frontend/oauth.cjs`: botones deshabilitados y sesión de navegador simulada.

La prueba con cuentas reales queda pendiente del registro y la configuración de
las aplicaciones por su propietario. No se afirma una auditoría de seguridad ni
que todos los módulos de negocio estén preparados para producción.
