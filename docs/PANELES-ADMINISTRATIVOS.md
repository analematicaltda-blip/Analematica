# Paneles integrados de SGA-CD

El nodo 6 sigue siendo un servicio interno. El usuario entra en `app.html`, usa su sesión SGA-CD y abre CRM, Estudio multimedia, Publicaciones o Mensajería dentro de su panel. El navegador nunca recibe `NODE6_TOKEN` ni necesita abrir el puerto 8606.

## Planes y equipo

| Acceso | Operación institucional y personal | CRM, multimedia, publicaciones y mensajería social |
|---|---|---|
| Administrador general | Gestión de la plataforma | Espacio propio de la plataforma |
| Empresa Básico | Sí, según los roles existentes | No |
| Administrador de empresa Full vigente | Sí | Sí, en el espacio de su empresa |
| Equipo administrativo Full | Según su rol | Solo funciones delegadas explícitamente |
| Profesor, alumno y acudiente | Sus módulos existentes | No se convierten en administradores por abrir un enlace |

El registro de empresa crea y guarda al administrador inicial en Básico. Su usuario de acceso es el correo completo. El administrador da de alta al personal desde **Equipo y permisos → Alta y gestión de personal**, conservando la jerarquía existente. Después habilita CRM, multimedia, publicaciones y/o mensajería por persona en **Habilitar funciones al equipo**. Puede revocar cada permiso independientemente. La suspensión del usuario, de la empresa o el vencimiento de Full bloquean las funciones en el servidor.

Los roles administrativos delegables son jefe de área, profesional de área, técnico de área, coordinador, jefe de almacén, almacenista y jefe de escenarios. Ninguna delegación cambia el rol del usuario. No se permite delegar en otra empresa.

Se conservan las cuotas comerciales existentes. Cancelar la renovación mantiene el acceso durante el periodo ya pagado, según la política existente; una suscripción vencida, inconsistente, ausente o que todavía no empezó no habilita Full. Cambiar localStorage, el hash de la URL o un menú no modifica los permisos del servidor.

## Orden del panel

- Inicio por tareas, con identidad y organización verificadas en la base de datos.
- Menú con grupos plegados inicialmente, buscador y cajón móvil con cierre por Escape.
- Equipo y permisos separado de CRM y comunicación.
- Un módulo por pantalla. Los módulos anteriores se conservan en el menú y en **Operación y módulos**, incluido el resumen original.
- Paleta azul cielo, formularios redondeados y disposición adaptable.
- **Mi espacio → Direcciones de paneles** muestra enlaces con el dominio real de la sesión.

## Direcciones para revisión

Dominio del Codespace facilitado en la conversación. Si se recrea o cambia de nombre, utiliza el directorio dentro del panel. Son puertos privados de GitHub; primero debes acceder a GitHub y luego iniciar sesión en SGA-CD con una cuenta del rol correspondiente. Un enlace no permite suplantar a otro rol.

| Rol | Dirección |
|---|---|
| Administrador general | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/admin_general/inicio |
| Administrador de empresa | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/admin_empresa/inicio |
| Jefe de área | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/jefe_area/inicio |
| Profesional de área | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/profesional_area/inicio |
| Técnico de área | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/tecnico_area/inicio |
| Coordinador | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/coordinador/inicio |
| Jefe de almacén | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/jefe_almacen/inicio |
| Almacenista | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/almacenista/inicio |
| Jefe de escenarios | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/jefe_escenarios/inicio |
| Profesor / instructor | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/profesor/inicio |
| Alumno | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/alumno/inicio |
| Padre / acudiente | https://glowing-sniffle-p76j799v56q73rj5w-8080.app.github.dev/app.html#/padre_acudiente/inicio |

## Actualizar la demo existente

La rama `codex/integrated-role-workspaces` conserva los cambios recientes de `main` y los del nodo 6. Desde la terminal del Codespace:

```bash
bash -e <<'SH'
cd /workspaces/SGA-CD
git fetch origin codex/integrated-role-workspaces
git merge --ff-only FETCH_HEAD
python3 BACKEND/tools/integrate_workspace.py --start
SH
```

Si Git informa divergencia o cambios locales en conflicto, se detiene sin forzar ni descartar archivos. No uses reset, clean ni reemplaces las bases de datos para continuar.

El actualizador valida primero la web, crea respaldo privado de Compose y de los archivos de registro del backend, monta versiones adicionales de código en solo lectura, conecta backend con nodo 6, recrea únicamente esos dos servicios, crea cuatro tablas nuevas sin borrar las anteriores, actualiza la copia web conservando `js/config.js` y recarga nginx para resolver la dirección del backend recreado. No reconstruye ni reinicia Flet y no modifica sus bases locales ni su sincronización. Para preparar únicamente la configuración, omite `--start`. Mantén el puerto 8080 privado y recarga el navegador con Ctrl+Shift+R después de actualizar.

Los respaldos quedan en `~/sgacd-demo/workspace-backup-*`. Para revertir la configuración, copia su `compose.json` al lugar original y vuelve a levantar solo los servicios afectados. Conserva las tablas nuevas y volúmenes; no hace falta borrar datos.

## Estado real de proveedores

El administrador general puede configurar el proveedor Gemini desde el estudio; las credenciales permanecen en el servidor. Cada empresa Full configura su propio canal YouTube. Las credenciales del canal se cifran en la base de datos usando una clave derivada del secreto del servidor y nunca se devuelven al navegador. Cambiar ese secreto requiere volver a autorizar los canales.

Los reels actuales son MP4 verticales renderizados con FFmpeg; no son movimiento generado por Veo. Texto e imágenes dependen de la clave, modelos, conectividad y cuota reales de Gemini. No se ha demostrado inferencia remota con una cuenta autorizada en esta entrega. Las pruebas de YouTube se limitan a **privado**, requieren confirmación y clasificación infantil explícitas, impiden duplicados y nunca utilizan el canal global del dueño para una empresa cliente.

La pantalla de mensajería indica correctamente que WhatsApp, Instagram y Facebook requieren autorización y webhooks. No muestra conversaciones ficticias ni afirma contestar mensajes antes de configurar las cuentas. La integración de esta entrega es en los paneles web; los clientes Flet mantienen sus bases offline y su sincronización existentes.
