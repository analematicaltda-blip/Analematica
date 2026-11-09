# Implementación66 · Inicio de H09: acuses firmados y reintentos de laboratorio

**Avance global:61,11 % (44/72), sin créditos duplicados.** H09 pasa de pendiente a EN_EJECUCION. Quedan4 paquetes verificados localmente y16 en ejecución; no hay paquetes sin iniciar, pero no están los20 subsanados. Aceptación completa0/24 y producción no habilitada.

## Implementación ejecutada

Se añadió un verificador local de ApplicationResponse con firma XML real RSA-SHA256 y cadena/hoja de laboratorio fijadas explícitamente. Extrae identidad y estado solo del documento verificado. Rechaza firmas alteradas, duplicadas o reubicadas, referencias externas, entidades, emisor/destinatario/documento/entorno ajenos y códigos no admitidos. Se conservan separados pendiente, aceptación y rechazo **exclusivamente de laboratorio**, sin homologarlos a estados oficiales DIAN.

Se añadió un diario SQLite local del cliente, con inicialización exclusiva, permisos privados, guardas SQL de actualización/borrado y hashes encadenados. Un documento conserva su misma identidad de perfil/bytes declarados durante reintentos inciertos. Se serializa el comienzo concurrente, se rechazan tokens anteriores y se recupera el mismo acuse idempotentemente. Un resultado terminal conflictivo se bloquea. Un fallo de preparación revierte intención y eventos. Solo almacena metadatos/hashes; no XML, números fiscales, NIT ni llaves.

La CLI abre un paquete cifrado del cliente para verificarlo localmente, sin solicitar llaves privadas ni escribir documentos descifrados en el servidor. No es un emisor ni una integración fiscal habilitada. [Operación y contratos](OPERACION_ACUSES_LABORATORIO.md).

## Por qué los otros15 no están cerrados

Se revisaron contra sus faltantes actuales y se separaron los desarrollos pendientes de la evidencia externa. Hay código por completar —despacho SG-SST, novedades de nómina, representación fiscal, interfaces, sincronización nativa y otros— además de certificados, datos y aceptación profesional. La [matriz de cierre por paquete](CIERRE_20_HITOS.md) identifica ambos grupos; no atribuye todos los bloqueos al entorno.

## Límites

No se implementó ni ejecutó un transporte SOAP/WS-Security a DIAN. No se asignó numeración oficial. El diario reproduce escenarios locales: `IN_FLIGHT_LAB` no prueba que se transmitiera nada y `UNCERTAIN_LAB` no acredita un timeout real. Los hashes de factura se declaran; el diario no compara los bytes originales. Las credenciales/política/anexo/endpoints/test set y acuses legítimos siguen pendientes.

`fiscal_accepted`, `dian_origin_verified`, `dian_profile_validated`, `usable_as_fiscal_acceptance`, `number_allocated`, `network_called` y `ledger_written` permanecen falsos. Las guardas y hashes internos no son WORM ni protección frente al reemplazo privilegiado del archivo. No se acredita PKIX completo, revocación, TSA, hardware ni custodia cualificada.

No se modificaron la frontera fiscal de producción ni los paneles web. No se hicieron commits, push, cambios en main, envíos DIAN, pagos, despliegues ni acciones sobre cuentas reales.

## Verificación final ejecutada

- **538 pruebas Python aprobadas en35 suites, sin omisiones**, incluidas24 nuevas de verificación de acuse/diario y38 del puente corporativo.
- Firmas XML criptográficas y cadena de laboratorio verificadas; documento/identidades/entorno ajenos, alteraciones y referencias externas rechazados. No se habilitaron códigos oficiales ni confianza DIAN.
- Concurrencia real entre conexiones SQLite de ensayo: una preparación nueva y un único comienzo activo; rollback, reapertura/reintento y guardas exactas comprobados. No es una prueba de transmisión ni numeración oficial.
- Fuentes estables, hashes de evidencia y coincidencia con el árbol actual comprobados; `pip check`, siete pruebas del avance, plan20, pendientes de billetera y `git diff --check` aprobados.
- No se reejecutó la suite Chromium44 de la entrega65 ni PostgreSQL52. Esta entrega añade componentes de escritorio, sin cambios de interfaz ni servidor fiscal. No se acredita CLI física positiva, hardware, datos reales o aceptación productiva.
