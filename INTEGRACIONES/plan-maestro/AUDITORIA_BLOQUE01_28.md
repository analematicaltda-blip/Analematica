# Bloque 1: inventario, auditoría y priorización

La entrega verificable está en [auditoria-bloque01/README.md](auditoria-bloque01/README.md).
Se amplió el inventario anterior: ahora incluye todas las fuentes propias de
Analemática auditables, su frontend estático y la dependencia central, además
de ERP y Turismo; antes el alcance corporativo solo cubría deployment.

Se entregan arquitectura observada,161 requisitos con evidencia/estado,
diez hallazgos priorizados, fuentes con hash, relaciones declaradas, candidatos
a duplicación y diez suites con152 pruebas aprobadas. La consulta AST no carga
ni ejecuta los módulos inspeccionados. No se eliminaron duplicados ni se
cambiaron funciones de negocio, bases de clientes, diseños o migraciones.

Tres archivos propios no compilan; el cuarto aviso pertenece a un fixture
JavaScript intencional. La matriz tiene153 requisitos NO VERIFICADA,7 PARCIAL
y1 DEFECTUOSA de fuente. Estas categorías no se extrapolan a todo un sistema.
No hay evidencia suficiente para cerrar la auditoría funcional integral ni
para afirmar que los153 requisitos estén ausentes. Están identificados los
siguientes casos, riesgos, responsables y dependencias para verificarlos.

Se mantiene abierta la validación integral del bloque1. La primera etapa de
inventario/diagnóstico/priorización queda entregada para revisión. Sin commit,
push ni despliegue. La prueba de restauración iniciada previamente se conservó
como anexo independiente de alcance mínimo, sin cerrar producción.
