# Bloque 3 — ámbito empresarial y sesiones ERP

Primera ampliación de controles compartidos para clientes y catálogo ERP.
El bloque integral de identidad/roles/jurisdicciones sigue abierto.

## Cambios implementados

company_scope.owned_provider unifica la selección de empresa para CRM y productos.
Exige titular personal activo, prestador activo y propiedad vigente. No infiere
propiedad por rol, superusuario, encabezado o ID del cuerpo. Si existen varias
empresas activas propias, exige selección explícita; si solo existe una, conserva
el comportamiento anterior. Consulta provider_id y los encabezados heredados
X-Tenant-ID/X-Company-ID, normaliza UUID y contrasta el contexto del middleware.
Selecciones contradictorias devuelven400; empresas ajenas/inactivas,403.
En estos encabezados heredados el identificador es TourismProvider, no core Tenant.
No se interpreta como vínculo financiero verificado.

El catálogo deja de depender de perfil_prestador e IsOwner, cuya comparación era
ambigua con múltiples empresas. Sus consultas filtran por empresa autorizada.
provider pasa a solo lectura y cualquier intento de trasladar productos a otra
empresa se rechaza, incluso cuando ambas pertenecen al mismo dueño. La política
de cancelación solo puede pertenecer al prestador seleccionado. El UUID público
se genera en el servidor. Se corrigió además la representación de Money como
importe decimal y se rechazan precios negativos.

CRM y catálogo usan explícitamente JWTAuthentication y ErpSessionAuthentication.
Una cookie Django genérica no basta: la sesión ERP debe tener marcador y versión
de factores válidos. Cambiar los factores invalida el acceso por esa cookie.
Las operaciones mediante cookies conservan la exigencia CSRF. Los clientes JWT
se conservan; no se cambian sus claves ni se crean cuentas compartidas.

GET /api/v1/mi-negocio/comercial/company-scopes/ devuelve hasta100 empresas
propias activas, con indicador truncated. No incluye documentos, cuentas bancarias
ni datos de terceros, responde no-store y declara que no concede SSO ni permisos
financieros. Está preparada la API; su selector visual está pendiente.

## Matriz aplicada en las rutas modificadas

| Principal | CRM/catálogo |
| --- | --- |
| Titular activo, una empresa activa | Su empresa |
| Titular activo, varias empresas | Solo la seleccionada explícitamente |
| Dueño de otra empresa | Sin acceso a registros ajenos |
| Empleado o rol administrativo sin propiedad | Sin acceso por herencia de rol |
| Superusuario que no es propietario | No recibe propiedad empresarial |
| Cuenta inactiva, agente o empresa inactiva | Acceso rechazado |
| Sesión Django sin flujo ERP o factores cambiados | Cookie rechazada |

No se añadieron delegaciones a empleados. La billetera conserva el control
exclusivo de titular/administrador empresarial autorizado por su propia política.
Estas rutas no conceden acceso a fondos ni reemplazan las autorizaciones del motor.
Los procesos financieros siguen requiriendo el vínculo revisado de identidad.

## Evidencia

-13 pruebas nuevas: múltiples empresas, lectura/escritura propia, rechazo ajeno,
traslado entre empresas propias, políticas cruzadas, contexto forjado, selectores
contradictorios, inactividad/agentes, superusuario, opciones privadas y precios.
Incluyen login real con contraseña/cookie, CSRF y rechazo de cookie tras cambiar
factores, así como rechazo de una sesión Django sin marcador ERP.
-6 regresiones CRM y27 de identidad/cotizaciones aprobadas. Se actualizaron dos
fixtures para parchear el proveedor de contexto común, manteniendo el mismo caso
negativo y la protección de borrado de clientes con historia comercial.
-14 regresiones de cupos,18 de jurisdicción institucional y5 del gateway aprobadas.
-Total83 pruebas de estos conjuntos. Casos aislados; algunas usan force_authenticate,
y el caso de cookie utiliza middleware y autenticación reales con APIClient.
-No hay migraciones nuevas ni modificaciones visuales. git diff --check correcto.

## Qué falta para cerrar el bloque 3

1. Selector visual de empresas y recorridos completos de cliente/catálogo.
2. Auditar y adaptar los demás endpoints empresariales al mismo contrato; este
   corte no cubre todas las rutas ni los procesos de otros módulos.
3. Delegaciones explícitas por empresa, función, vigencia y revocación; nunca
   heredar permisos financieros o de billetera por un rol de empleado.
4. Jurisdicción multinivel en eventos, artesanos, documentos, tareas, aprobación
   y exportación. Las18 pruebas conservan cobertura acotada de atractivos/reseñas,
   no acreditan todos los módulos institucionales.
5. Identidad central/SSO: contrato de emisor, audiencias, vinculación verificada,
   revocación y migración de cuentas. No igualar IDs ni copiar tokens entre
   SGA-CD y Django. Analemática mantiene su dependencia central y sus controles.
6. WebAuthn, recuperación integral, notificaciones y validación física/operativa.

No se habilitó producción, no se elevó el rol de usuarios, no se modificaron bases
de clientes. Sin commit ni push. Ver company-scope-evidence-30.json.
