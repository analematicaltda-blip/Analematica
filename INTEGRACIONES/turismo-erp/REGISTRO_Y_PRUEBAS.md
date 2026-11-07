# Registro de modificaciones y pruebas de esta fase

## Modificaciones

Se realizaron ajustes de consolidación técnica autorizados por el plan maestro: límites explícitos para cuatro módulos contables incompletos, descubrimiento de modelos de embudo, carga opcional de SDK, ausencia de respuestas Dummy en reescritura ERP, límite de tiempo Ollama, namespaces compatibles, configuración allauth/estáticos, salud sin lookup territorial y selección de proveedor ligada a propiedad autenticada.

Los detalles están en `../plan-maestro/README.md` y en el diff de la rama. No se aplicaron migraciones, no se modificaron archivos de datos de clientes, no se ejecutaron pagos/asientos/publicaciones y no se usaron claves externas. No se eliminaron módulos heredados: la fuente comentada se conserva; los módulos pendientes responden 503 en lugar de bloquear la carga o simular éxito.

El centro `/platform.html` usa autenticación administrativa central y acceso de solo consulta. Comparte enlaces a control, guías y recursos. Declara las sesiones de dominio independientes y no afirma disponibilidad de servicios ni de procesos que no comprobó. No implementa SSO turístico ni una equivalencia de roles.

## Evidencia nueva

- Django ERP: **7 pruebas correctas**, con registro completo, `check` sin errores/advertencias, salud por HTTP de prueba, autenticación y 503 de módulos pendientes sin SQL, ausencia de proveedor IA, contexto de proveedor y rutas.
- Django Turismo: **7 pruebas correctas** con los mismos límites y preservación del alias legado/canónico.
- Centro administrativo FastAPI: **3 pruebas correctas** de autenticación, aislamiento de contexto y ausencia de rutas de escritura.
- Regresión del motor de asistencia/control: **27 pruebas correctas**.
- Recursos y exportación: **9 pruebas correctas**.
- Gateway/configuración: **12 pruebas correctas**, incluidas preservación de errores, no reenvío de credenciales Basic y aislamiento de cookies del pool.
- Publicación corporativa: **2 pruebas correctas**.

Estas pruebas usan SQLite en memoria y claves temporales. No constituyen un recorrido de reservas/pagos/instituciones con una base migrada ni una cualificación productiva.

El entorno se reinició durante el trabajo. Se recuperó la rama de seguridad ya publicada y se repitieron las pruebas en el entorno nuevo; no se reutilizaron como actuales los resultados del entorno perdido. Las vistas previas y credenciales privadas anteriores no estaban disponibles en el nuevo host. No se afirma haber actualizado los servidores del portátil ni haber repetido el login de aquellas vistas.

## Inventario y grafo

`inventory.py` inspecciona fuentes sin ejecutarlas. Los fragmentos de URL y páginas no se cuentan como funcionalidades terminadas. Hay errores sintácticos en código heredado fuera del recorrido cargado por Django; un fixture de pruebas intencionalmente inválido se debe distinguir de los defectos funcionales.

El grafo de migración se examinó sin conectar una base: **no es válido** por un nodo inexistente. Esto bloquea el cierre de integración de datos y producción aunque el check Django pase. No se realizaron reparaciones de historia de migración sin conocer y respaldar los datos.

## No verificado

Bases productivas/backups, RNT/MinCIT/DIAN reales, flujos institucionales por jurisdicción, reservas/pagos completos, contenido comercial consentido, navegadores y dispositivos de clientes, carga, modo offline y todos los agentes de dominio. H-001/H-002 siguen pendientes de desarrollo después de presentar el plan; no se encubren con pruebas de arranque.

Se detectó y versionó el gateway `deployment/api.py` que el Dockerfile ya exigía pero faltaba en la rama limpia. El gateway conserva autenticación y errores de la API central, evita servir fuentes internas y no transfiere cookies de otro usuario desde su pool HTTP. No se reconstruyó una imagen ni se anunció un servidor productivo por esta corrección.

La verificación de snapshots se ajusta al checkout declarado por AiSOC: sus tres scripts PowerShell se guardan como blobs LF y se extraen como CRLF por sus `.gitattributes`. Solo se normaliza esa conversión explícita para comparar el mismo SHA/blob; cualquier cambio de contenido sigue fallando. No se modifican los archivos upstream.

El nuevo centro pasó una prueba Chromium a 1440/390/320 px con un contrato API sintético y sin login vivo: navegación interna, mensajes de sesión y ausencia de desbordamiento/errores JS. El backend administrativo se prueba por separado con TestClient y SQLite. El motor Node pasó 11 pruebas, con una prueba opcional nativa omitida. Las copias upstream pasan el verificador con la conversión de checkout declarada.
