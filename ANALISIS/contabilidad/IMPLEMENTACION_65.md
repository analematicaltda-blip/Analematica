# Implementación65 · Corrección ambiental sin borrar ni duplicar observaciones

**Avance global: 61,11 % (44/72), sin créditos nuevos.** Se amplía ACC-018, cuyo incremento y verificación ya estaban acreditados. El plan conserva4 paquetes verificados localmente,15 en ejecución y1 pendiente. No se declara subsanación total ni producción habilitada.

## Corrección implementada

El registro ambiental permitía confirmar observaciones y bloquear duplicados por identificador, pero no corregir una observación registrada. Se añadió una cadena de correcciones con revisión de cabecera y dos confirmaciones del mismo titular. Mantiene las observaciones, factores y reclamaciones originales. La estimación vigente reemplaza a la anterior en la consulta, sin volver a contar actividades ni generar pasivos o créditos de carbono.

Las cantidades y versiones nuevas de factores se recalculan mediante el mismo motor decimal. No se permite cambiar la identidad, fecha económica o unidad de las actividades originales. Los factores existentes no se sobrescriben. Una revisión competidora que quedó obsoleta se rechaza; repetir una corrección ya registrada devuelve el mismo resultado. Un fallo de escritura revierte los factores nuevos y el registro de esa transacción.

Se añadieron tres rutas ERP y los comandos/fuente equivalentes en el puente corporativo de Analemática. La recuperación del panel común muestra el total corregido y su revisión, deja constancia del original y no restaura autorizaciones ni reutiliza el soporte antiguo para la corrección. Se conserva azul, azul claro y texto blanco.

## Evidencia funcional

- 15 pruebas nuevas del núcleo y API verifican original preservado, sustitución del total, factor versionado, segunda confirmación, reintentos, rama obsoleta, encadenamiento, modificaciones inconsistentes, fallo transaccional, empresa/usuario ajenos, agente y vínculo revocado.
- 2 pruebas nuevas recorren HTTP corporativo autenticado hacia ERP, incluyendo consulta de original/efectivo y rechazo de corrección obsoleta.
- La suite Chromium de registros ambientales verifica22 comprobaciones por sistema:44 en total. Incluye corrección preparada por API, recuperación del total vigente en el panel, procedencia visible, soporte anterior vacío, revisión sin autorizaciones y limpieza por pérdida de identidad. No se presenta la preparación por API como un formulario visual nuevo.

## Límites y pendientes

La cadena interna no es WORM ni protección frente a reescritura privilegiada completa/eliminación del tramo final; se comprueban inconsistencias detectables con los registros conservados. Las fuentes y soportes siguen siendo declarados. No hay certificación ESG, crédito, compensación, pasivo, pago ni asiento generado.

Faltan formularios de corrección, búsqueda/cortes/exportación, incertidumbre, duplicados semánticos, integración con operación real, factores y revisión profesional y cualificación operacional/PostgreSQL específica. H16 sigue EN_EJECUCION. H09 continúa pendiente de transporte y acuses DIAN auténticos; su bloqueo no se sustituye por una aceptación simulada.

[Guía operativa y contratos](OPERACION_CORRECCIONES_AMBIENTALES.md). [Evidencia65](evidencias/implementacion-65.json).

No se hicieron commits, push, cambios en main, migraciones sobre datos reales, pagos, publicaciones externas ni llamadas DIAN.

## Regresión final

- **514 pruebas Python aprobadas, sin omisiones, en34 suites**, incluidas15 de correcciones y38 del puente corporativo (2 nuevas).
- **44 comprobaciones Chromium aprobadas**,22 por panel. Capturas de datos sintéticos: [ERP](evidencias/implementacion-65-erp.png) y [Analemática](evidencias/implementacion-65-corporate.png). Se inspeccionó la captura ERP y se comprobó el total vigente, origen conservado y texto blanco sobre azul.
- La expectativa inicial del navegador asumía un original distinto de cero; el fixture existente registra explícitamente cero. Se corrigió esa expectativa y se repitió la suite completa de ambos paneles, incluidas limpieza del total corregido al perder identidad y autorizaciones desmarcadas.
- Fuentes estables, hashes de evidencia y coincidencia con el árbol actual comprobados. Dependencias compatibles, sintaxis JavaScript y siete pruebas del porcentaje verificadas. Plan20/pendientes de billetera sincronizados y `git diff --check` limpio.
- No se reejecutaron las52 pruebas PostgreSQL ni el conjunto histórico completo de424 comprobaciones de navegador. Este corte ejecuta la suite focal de44 comprobaciones; no acredita concurrencia específica PostgreSQL ni cierre de producción.
