# Implementación 47 · Aplicación revisada de anticipos a reservas

Avance global: **38,89 % (28/72 hitos)**. Se amplía el flujo funcional de reconocimiento existente; no se duplican hitos ya acreditados ni se declara aceptación productiva.

## Cambio funcional

Antes se rechazaba cualquier reserva cuyo deposit_paid fuese distinto de cero. Ahora el propietario puede vincular explícitamente un recibo previamente contabilizado, su cuenta de pasivo y la huella del soporte de conciliación. La revisión queda persistida, exige la primera confirmación y muestra saldo por cobrar y anticipo. Una segunda confirmación registra el reconocimiento mediante el motor compartido.

Ejemplo comprobado: servicio de 100 COP, recibo anterior de 40 COP. El reconocimiento debita cartera por 60 y pasivo de anticipos por 40, y acredita ingreso por 100. Si el desglose fiscal revisado contiene impuesto, el crédito se distribuye entre ingreso e impuesto. No se vuelve a debitar efectivo. Un anticipo total omite la línea de cartera en cero. La contrapartida revierte el reconocimiento y conserva el recibo original: no equivale a devolver dinero.

## Controles

- Propietario, empresa y vínculo vigentes; periodo abierto y servicio declarado como prestado.
- Recibo completo simple de dos líneas, contabilizado con hash v2 verificable, COP, anterior o igual a la fecha económica, sin contrapartida; cuentas activas de la empresa y su catálogo.
- Importe del recibo igual al anticipo declarado, positivo y no superior al precio. Pasivo separado de las cuentas de ingreso, cartera e impuesto; saldo contable suficiente antes de su primera aplicación.
- Huella del soporte y cliente/reserva ligados a la revisión. La correspondencia comercial es una declaración del propietario, **no una verificación bancaria independiente**.
- Reclamo determinista por recibo: no se reutiliza en otra reserva. Reintentos conservan el asiento; si falta la evidencia de aplicación se bloquea y no se reconstruye historia.
- Bloqueo de empresa y transacción compartidos con el ledger. Asiento, reclamo y prueba de origen se confirman juntos; una falla revierte el reconocimiento sin borrar el recibo anterior.
- Cambiar anticipo, fuente, revisión, identidad o estado del recibo antes de contabilizar invalida el proceso.

## Interfaz e integración

El formulario ERP conserva estructura, azul metalizado, azul claro y texto blanco. Añade asiento previo, pasivo y soporte; editar cualquiera descarta la aprobación local. La previsualización muestra cartera neta y aplicación de anticipo. La API acepta ese objeto opcional únicamente en la revisión, no en la confirmación final. Analemática consume los reportes del mismo ledger a través del puente corporativo previamente implementado; no se añadió escritura corporativa.

## Límites y producción

Solo un recibo completo por reserva, sin división entre reservas, acumulación de recibos, divisas ni reembolsos. El saldo global del pasivo no sustituye una conciliación individual bancaria. La asociación cliente/recibo requiere revisión humana con soporte legítimo. Los eventos de revisión/reclamo no están protegidos frente a un operador privilegiado de base de datos. Revertir o ajustar posteriormente el recibo por otros canales requiere conciliación; falta un control transversal que impida esa operación mientras tenga aplicaciones vigentes. No habilitar este alcance productivo hasta completar esos controles, validación profesional, roles, carga, respaldo/restauración y pruebas con datos autorizados. No hay emisión DIAN ni pagos.

La evidencia de esta entrega se registra en `evidencias/implementacion-47.json`. Las pruebas usan bases e identidades desechables; no certifican entornos de clientes.

## Verificación registrada

244 pruebas Python aprobadas, incluidas 29 de reconocimiento (9 nuevas). PostgreSQL verificó la aplicación concurrente con un único asiento/reclamo, además de las regresiones, integridad y restauración. Los hashes de fuentes se mantuvieron estables durante la corrida final. El navegador aprobó 42 comprobaciones de regresión del panel; la nueva asignación de anticipo se comprobó por ORM/PG, no mediante un recorrido específico de esos campos en navegador. TypeScript estricto del componente sin errores; no sustituye la compilación Next completa.
