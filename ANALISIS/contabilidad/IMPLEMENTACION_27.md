# Implementación 27 · Destino PostgreSQL soberano explícito

**Avance: 33,33 % (24/72 hitos).** ACC-011 acredita un incremento funcional y su verificación; permanece PARCIAL. Ninguna tarea acredita todavía aceptación completa.

## Implementación

El núcleo compartido incorpora `CustomerPostgresStore`: recibe una conexión PostgreSQL explícita a una base del cliente. Rechaza bases que contienen el ledger y verifica una vinculación empresarial única. No infiere credenciales ni reutiliza automáticamente la conexión predeterminada.

Una inicialización separada crea tablas y controles contra UPDATE, DELETE y TRUNCATE. Lectura/escritura comprueban la presencia y configuración de esos controles; su pérdida bloquea el acceso, sin reparación automática. El rol de escritura necesita SELECT/INSERT; el bootstrap exige otro rol. La comprobación estructural de triggers no atesta su cuerpo ni resiste a un propietario de base malicioso.

Cada UUID representa una versión inmutable: repetir exactamente el mismo sobre es idempotente; otros bytes bajo ese UUID generan conflicto. Dos primeras escrituras concurrentes iguales crean una sola fila. Se verifica digest, contexto y límite de tamaño al recuperar. Las escrituras exigen conexión dedicada en autocommit, fuera de una transacción del ledger; no se promete atomicidad distribuida entre ambos destinos.

El adaptador acepta únicamente el contrato de sobre opaco y no recibe KEK o documentos descifrados. Valida estructura, no autenticidad criptográfica ni validez fiscal: un cliente malicioso puede enviar bytes arbitrarios con forma válida. La propiedad real del destino sigue sin verificarse independientemente.

## Evidencia

- 127 métodos Python contables aprobados en siete suites.
- 20 escenarios contables PostgreSQL aprobados, incluyendo restauración del ledger y el nuevo destino cliente separado.
- Documento sintético cifrado realmente con AES-GCM, DEK envuelta y descifrado posterior correcto; ninguna llave se guarda en el adaptador.
- Rechazo de otra empresa, destino del proveedor, sobrescritura, borrado con rol restringido, mutaciones SQL y acceso tras retirar un trigger. Dos conexiones concurrentes producen una inserción y un replay.
- Fuente estable durante la verificación. Evidencia: `evidencias/implementacion-27.json`.

## Límites y siguientes pasos

No se ha activado carga desde formularios, endpoints, dispositivos o cuentas reales. El preview existente mantiene `stored=false`. El rewrap del SDK no sobrescribe versiones: requiere diseñar versionamiento y referencias actuales; un documento nuevo necesita contexto y cifrado cliente adecuados. No hay antirrollback global.

Pendientes: custodia y recuperación real de KEK, autenticación y autorización del cliente, propiedad del destino, revisión de roles/esquemas/funciones privilegiadas, revocación y caída de red, respaldo/restauración de esta base del cliente, retención y disponibilidad. Drive, OneDrive y S3/OAuth siguen pendientes. La restauración comprobada en esta entrega corresponde al ledger, no al almacén documental cliente. No se certifica conocimiento cero de uploaders existentes o del ERP completo.

El módulo compartido conserva los motores existentes; la integración corporativa completa de Analemática sigue pendiente. Sin cambios de datos del usuario, commit, push o despliegue.
