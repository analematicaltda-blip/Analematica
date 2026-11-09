# Implementación 49 · Plan autónomo de 20 hitos y primera subsanación

Se creó el plan ejecutable por el agente en `PLAN_SUBSANACION_20_HITOS.md`, con registro canónico `plan-subsanacion-20.json`. Contiene exactamente 20 paquetes, dependencias anteriores al propio paquete, hallazgo, corrección, criterio de aceptación y requisito externo. Su cobertura mantiene las 24 tareas originales; el porcentaje global conserva la base de 72 hitos. Crear el plan o reforzar un hito existente no suma puntos artificiales: el avance global permanece en **41,67 %**.

## H01 · Facturas legadas aisladas por empresa

El listado previo usaba FacturaElectronica.objects.all y su serializador incluía xml_content y pdf_url. Ahora requiere autenticación ERP/JWT, recarga al usuario activo y resuelve la empresa a través del vínculo revisado del propietario. Tanto tenant_id de la factura como el Tenant de la operación relacionada deben coincidir con esa empresa; relaciones inconsistentes y registros legados sin clasificación quedan fuera de la consulta. No se adivina que un UUID de prestador equivale al UUID contable.

El listado/detalle conserva metadatos históricos pero no entrega XML ni enlaces de documentos. El campo fiscal_acceptance_verified=False distingue el estado legado de un acuse auténtico: no se reescribe la historia ni se supone que un estado guardado como aceptada esté verificado. Los endpoints PDF/envío mantienen el bloqueo explícito de DIAN; un identificador de factura ajena devuelve 404 antes de la ruta PDF. Todas las respuestas comprobadas son privadas/no-store.

También se corrigió un atributo incompatible en la señal comercial: la entidad actual utiliza status, mientras la señal leía estado. Las altas DRAFT/CONFIRMED se conservan sin excepción por ese atributo ni factura ficticia; el bloqueo de DIAN se registra sin generar documentos o enviar correos.

## Verificación y alcance

Siete pruebas nuevas ejecutan el modelo legado real, operaciones reales del ORM y el viewset/serializador DRF en tablas desechables. Verifican lista propia, factura ajena, relación inconsistente, anonimato, revocación, ausencia de XML/URL, estado legado no certificado, PDF/envío bloqueados y conservación de altas operativas. Se ejecuta además la regresión contable completa, incluida escritura corporativa real entre backends de prueba.

No se migraron ni borraron documentos de clientes. La retirada del texto claro del API no cifra ni sanea el contenido ya guardado en la BD: inventario, custodia y migración soberana quedan en H05/H10/H11. H01 es verificación local de esta corrección, no aceptación productiva de toda la tarea contable.

La evidencia final se guarda en `evidencias/implementacion-49.json`. Sin commits, push, merge ni despliegue.

**Resultado final:** H01 verificado localmente; siete pruebas nuevas y **269 pruebas de regresión contable aprobadas**. Fuentes estables durante la corrida; producción y migración de datos no acreditadas. Los 19 paquetes restantes conservan su estado pendiente y sus criterios explícitos.
