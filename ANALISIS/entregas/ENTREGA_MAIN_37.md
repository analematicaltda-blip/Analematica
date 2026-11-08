# Entrega consolidada autorizada a main

Fecha: 2026-11-08. Base remota comprobada antes de preparar la entrega: `9c62fea62807b3f78f85f4cb3664722dfd9d34aa`. El usuario autorizó explícitamente commit y actualización automática de main en esta entrega; no necesita unir parches manualmente.

## Contenido y organización

Se reúnen los avances acumulados de los cortes16–36: identidad/recuperación, cotizaciones/cupos, aislamiento, componentes web, control autorizado, contenido, herramientas de validación y respaldos, con sus pruebas/documentación. Se conservan cambios previos de terceros y evidencia histórica.

Los dos documentos consolidados de producción se movieron de la raíz a `ANALISIS/produccion`; se actualizaron enlaces, generador canónico e instrucciones. Los análisis contables nuevos, directriz, decisiones y matriz están en `ANALISIS/contabilidad`. Los informes previos ya organizados en `INTEGRACIONES` permanecen allí junto a sus herramientas. La raíz conserva archivos de entrada y configuración, no informes de análisis sueltos.

Se incluye el inicio del nuevo plan contable: corrección del alta UUID, validación de débitos/créditos, empresa/cuentas/periodo y guardas ORM. No se reemplazó el motor compartido ni se activó contabilidad autónoma. Matriz24 tareas;2 implementadas en alcance acotado,22 pendientes de desarrollo y validación. Ver sus criterios y hallazgos, sin interpretar esos2 cierres como dos pools completos.

## Verificación

- Perfiles `core + backup + browser`:18 grupos aprobados,237 pruebas Python, fuentes seleccionadas estables y hashes verificados. Navegador con fixtures, no cuentas reales.
- Fundación contable:9 pruebas ORM nuevas sobre SQLite aislado; no certifican posteo completo ni concurrencia PostgreSQL del ledger.
- Registro generado de billetera coherente con su JSON canónico; no se cerraron pendientes físicos/productivos por estas pruebas.
- Revisión de candidatos de entrega: sin claves privadas, tokens detectados por patrones ni rutas de datos/runtime. Esa comprobación acotada no sustituye una auditoría de seguridad integral.
- Cachés Python y artefactos generados no se incluyen en el commit; archivos históricos ya versionados no se borran como parte de esta entrega.

## Publicación y límites

La entrega se realiza con un commit consolidado y push normal de avance a main, sin force push ni reescritura de historia. Antes del push se vuelve a comprobar el remoto; si cambió, se integra conservando ambos avances. El identificador definitivo se obtiene del historial Git y se confirma contra `refs/heads/main`; no se introduce un hash autorreferencial en este documento.

Esto entrega código, no una liberación productiva: ambos builds ERP/Turismo continúan fallando por dependencias/contratos ausentes; hardware, proveedores, migraciones/recuperación integral y demás pendientes siguen abiertos. No se ejecutaron pagos, DIAN, bancos, campañas, BYOS real ni cambios sobre bases del usuario. Los workflows añadidos podrán ejecutarse al publicarse; no se afirma que hayan pasado remotamente.

Nuevos commits futuros continúan sujetos a la preferencia del usuario de entregas finales, no commits por cada modificación.
