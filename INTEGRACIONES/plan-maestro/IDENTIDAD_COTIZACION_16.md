# Vínculo empresarial y vista previa comercial

Este corte desarrolla NEXT-01 y una parte de NEXT-02. No declara terminado el
plan maestro, el SSO ni un sistema financiero operativo en producción.

## Identidad entre prestador y empresa contable

VerifiedCompanyLink relaciona dos identificadores distintos mediante claves
foráneas protegidas. Registra administrador titular, operador independiente,
huella de evidencia, NIT revisado, fecha, caducidad y revocación. Solo se admite
un vínculo por prestador y por empresa; no se reescriben vínculos anteriores.

La resolución revalida usuario activo, propietario actual, prestador activo,
empresa activa, NIT sin cambios y vigencia. Un permiso general de empleado o
superusuario no concede acceso a la billetera empresarial. El operador que
revisa no puede ser el administrador beneficiario. La revisión manual se apoya
en evidencia externa que el operador debe comprobar: un hash por sí solo no
certifica identidad legal ni consulta RNT/DIAN.

`review_company_link` exige operador autorizado e identificadores explícitos;
sin `--apply` únicamente valida. No hay alta pública del vínculo. No se crea
empresa, usuario, cuenta financiera, moneda, límites o saldo. La recuperación,
renovación y auditoría externa del procedimiento quedan pendientes.

La acción de solo lectura `tourism-providers/{id}/company-identity/` devuelve
el vínculo solo al titular autorizado, con no-store y sin documentos/NIT.
El adaptador TourismCompanyAdministrator puede utilizar ese registro para la
billetera ERP-TUR, pero continúa deshabilitado por defecto. El SGA-CD central
usa otro almacén de identidad: no se infiere equivalencia entre sus usuarios.

## Vista previa de cotización

La ruta comercial relativa `quotation-preview/` recibe prestador, cliente y
líneas con producto/cantidad. Comprueba el vínculo y calcula precios usando
Product.base_price, filtrado por prestador y estado activo. Rechaza precios del
cliente, productos ajenos, cantidades inválidas, duplicados y monedas diferentes.

Devuelve NON_BINDING_PREVIEW con subtotal, impuestos sin calcular y total pagable
vacío. No persiste venta, no reserva inventario, no cobra, no emite factura y no
confirma disponibilidad. El flujo de operaciones/POS previo sigue cerrado hasta
implementar líneas persistentes, impuestos, concurrencia y evidencia de pago.
No se usa el subtotal como deuda o comprobante fiscal.

## Datos y alcance de migración

Se añade turismo.0002_verifiedcompanylink al perfil fresh-local-v1. La historia
heredada no se altera. Solo se migraron bases nuevas privadas bajo /tmp creadas
para esta validación; no las bases de trabajo ni datos de clientes. La creación
inicial superó un límite de tiempo; la base temporal incompleta se conservó y
se completó su migración de forma explícita. No se ocultó como instalación
limpia exitosa en el primer intento.

El bloqueo de test_platform del corte anterior era reproducible dentro del
sandbox: fuera del aislamiento sus tres pruebas y las 27 de asistencia pasan.
Esto valida contratos locales, no conexión con equipos o cuentas reales.

## Pendientes siguientes

- Interfaz de cotización conectada, validación humana y persistencia de borradores.
- Impuestos colombianos, unidades/cupos y contratos de tarifa/disponibilidad.
- Identidad externa, alta pública y panel exclusivo del administrador empresarial.
- Recuperación y renovación auditada del vínculo, concurrencia PostgreSQL.
- SOC vivo, comparación de modelos, cuentas de prueba y equipos físicos.

Los cambios quedan en el directorio de trabajo sin commit ni publicación,
conforme a la preferencia del usuario.

## Evidencia final

111 ejecuciones aprobadas:17 identidad/cotización,15 billetera,13 protocolo
de dispositivo,12 prestadores,6 CRM,3 contrato central,27 asistencia y18
bases migradas (9 por servicio). Ambas bases de prueba tienen 588 tablas y167
migraciones, sin violaciones de claves foráneas. Ver company-identity-evidence-16.json.
La vigencia y autoridad externas siguen sin certificar; el adaptador sigue opt-in.
