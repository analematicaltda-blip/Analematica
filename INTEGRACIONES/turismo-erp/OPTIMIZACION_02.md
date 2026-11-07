# Segunda entrega · permisos institucionales y reseñas de clientes

## Cambios y alcance

**Atractivos institucionales.** Se elimina la escritura pública y se emplea un permiso compartido con `CanManageAtractivos`. La autorización requiere usuario activo, rol institucional coherente, GovernmentProfile activo y Profile del mismo organismo. Nivel de gobierno y tipo de entidad deben coincidir. El municipio debe pertenecer al departamento del perfil. Tener un rol o enviar un encabezado no concede acceso a otra jurisdicción.

Los permisos funcionales estándar `api.add_atractivoturistico`, `api.change_atractivoturistico`, `api.delete_atractivoturistico` y `api.view_atractivoturistico` son adicionales al ámbito. No se asignan automáticamente. El superusuario activo conserva su capacidad global explícita; un usuario con el texto de rol ADMIN no obtiene por ello ese bypass.

Las consultas públicas muestran solo publicados. Un funcionario con permiso de consulta puede ver borradores dentro de su ámbito; para escribir se usa siempre el queryset de su entidad/territorio. Crear fija autor e institución desde el servidor, valida territorio y coordenadas. El permiso `api.publish_atractivoturistico` es independiente para publicar, retirar publicación, modificar o eliminar un registro ya publicado. Su registro/asignación administrativa es prerrequisito; esta entrega no agrega grants a personas ni aplica migraciones. La prueba lo aprovisiona explícitamente en la base temporal.

El detalle público no revela el login del funcionario. La URL de detalle `/api/v1/atractivos/<id>/` usa el ID entero real del modelo; la declaración UUID anterior no correspondía a su esquema. Se conserva también el router general.

**Rutas turísticas e historia.** Se mantiene lectura pública de registros publicados. Sus escrituras quedan no disponibles (405): la historia no tiene jurisdicción institucional y las rutas aún no cuentan con un contrato de propiedad/aprobación suficiente. No se inventó un propietario ni una autorización universal para habilitarlas. La edición administrativa se incorporará después del diseño de ámbito/migración correspondiente.

**Reseñas del cliente.** La API de gestión permite al cliente autenticado administrar únicamente sus propias reseñas. Autor e indicador `is_verified_purchase` son de solo lectura para él y se fijan en servidor. Las altas nuevas son no verificadas: no se afirma una compra que no se comprobó. Se rechazan rating fuera de 1–5, duplicados y cambio del servicio al que pertenece una reseña. La unicidad se protege también mediante transacción/constraint; una carrera no devuelve una confirmación falsa. No se concede al propietario del prestador permiso para modificar lo escrito por sus clientes.

La consulta pública/moderación de reseñas y el enlace a una compra real siguen pendientes. Este cambio es del marketplace compartido con el ecosistema empresarial; no equivale a haber completado todo el portal ERP.

## Pruebas

`BACKEND/deployment/tests/domain_security_check.py`: 18 ensayos HTTP/ORM correctos con modelos reales sobre SQLite en memoria. Incluyen contenido publicado/borrador, escrituras anónimas, municipio ajeno, actualización propia, creación con territorio ligado al servidor, manipulación de institución/publicación, coordenadas y permisos, rutas/historia solo lectura, reseña ajena, autor/verificación protegidos, duplicados, oficina inactiva, rol/nivel contradictorio, publicación autorizada, detalle sin login, ámbito departamental y el recorrido de URL/middleware completo con lectura pública y escritura protegida.

Los usuarios se siembran explícitamente con bulk_create para no aprovisionar billeteras o compañías: registro de usuario y wallet no están bajo prueba. El esquema temporal se construye con schema_editor exclusivamente para estos fixtures, no con migraciones falsas; no demuestra que el grafo de migraciones de producción sea válido.

Repetición:

```bash
PYTHONDONTWRITEBYTECODE=1 python BACKEND/deployment/tests/domain_security_check.py -v
CHECK_SERVICE=erp-tur PYTHONDONTWRITEBYTECODE=1 python BACKEND/deployment/tests/tourism_runtime_check.py -v
CHECK_SERVICE=turismo PYTHONDONTWRITEBYTECODE=1 python BACKEND/deployment/tests/tourism_runtime_check.py -v
```

Los checks y las siete regresiones de cada backend permanecen correctos. No se ejecutaron pagos, reservas reales, RNT/DIAN, API externas, migraciones ni cambios de datos existentes. El nodo de migración ausente sigue bloqueando la cualificación sobre una base real.

## Siguiente trabajo

Completar autorización territorial de los otros directorios, formalizar escritura/aprobación de rutas/historia y preparar migraciones sobre copia restaurada. En ERP, separar carrito de suscripción de catálogo/reserva turística y ensayar disponibilidad/cotización antes de checkout. Registro institucional, verificación RNT y promoción contractual siguen separados; ningún permiso de publicación aquí verifica RNT ni habilita pauta por pago.
