# Tercer corte: protección de empresas y reservas

Los perfiles empresariales, incluidas cuentas bancarias, y los servicios permitían acceso sin filtro de propietario. Ahora consultas y escrituras se limitan al dueño del prestador; solo un superusuario activo conserva acceso global. `is_staff` no concede acceso entre empresas. El servidor asigna propietario al alta y exige un rol empresarial. Se impiden transferencias de perfiles/servicios y precios negativos.

Clientes y propietarios pueden consultar sus reservas, sin metadatos internos. Las reservas quedan de solo lectura: faltan contratos de tarifas, unidades/cupos, concurrencia, idempotencia y cancelaciones. Antes el solicitante podía enviar cliente, precio y estado arbitrarios. El borrado de prestadores, perfiles y servicios se deshabilita para proteger reservas ante cascadas; falta definir una política completa de archivo.

La integración RNT simulaba validación por longitud del número y permitía obtener un propietario sin comprobar credenciales. Se conserva su interfaz pero validación, sincronización y acceso responden 503 hasta contar con una integración oficial comprobada. Las altas no fabrican validaciones ni puntuaciones; cambiar el número retira la verificación previa. Las marcas históricas requieren auditoría: no se modificaron masivamente datos existentes. También falta vincular la futura verificación a la identidad legal completa y su versión.

El servicio financiero confirmaba reservas al emitir una solicitud, sin evidencia de pago. Sus entradas de pago, transacción y saldo ahora responden 503 sin eventos ni confirmaciones. Permanece el cálculo decimal de comisión. No se conectó un proveedor ni se efectuaron cobros.

El carrito existente es de planes de suscripción ERP, no de servicios turísticos. Estas correcciones de dominio afectan al backend institucional que contiene esos modelos; el ERP conserva sus módulos y se verificó su arranque por separado.

## Pruebas

- `python BACKEND/deployment/tests/provider_security_check.py -v`: 12 correctas; HTTP/ORM, aislamiento, RNT, reservas y ausencia de eventos financieros.
- `python BACKEND/deployment/tests/domain_security_check.py -v`: 18 correctas; jurisdicción y reseñas.
- `CHECK_SERVICE=erp-tur python BACKEND/deployment/tests/tourism_runtime_check.py -v`: 7 correctas, check Django sin incidencias.
- `CHECK_SERVICE=turismo python BACKEND/deployment/tests/tourism_runtime_check.py -v`: 7 correctas, check Django sin incidencias.

Total: 44 pruebas correctas. Nueva suite incluida en CI. Se usó PYTHONDONTWRITEBYTECODE=1, SQLite en memoria, usuarios sintéticos y claves temporales. No se aplicaron migraciones ni cambios a bases de clientes. No se probó navegador en este corte. Los scripts históricos que esperan pagos simulados no son evidencia de liquidación.

## Pendiente

Resolver el grafo de migraciones documentado con copia/restauración verificada antes de repararlo. Definir moneda, unidades, tarifas, inventario por fecha, bloqueo concurrente, reservas idempotentes y cancelaciones; conectar un proveedor con notificación autenticada y conciliación; verificar el portal de cliente completo. RNT oficial, publicación comercial consentida y registro institucional permanecen separados.

Este corte no declara completos reservas, disponibilidad, DIAN, RNT ni despliegue productivo.
