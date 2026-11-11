## Nota para Futuros Agentes

Este proyecto tiene una configuración de entorno particular que afecta a cómo se resuelven las importaciones de Python.

**El Problema:**
El repositorio `BACKEND/SGA-CD-BACKEND` depende de `SGA-CD-DB.git`, que debería ser un paquete instalable. Sin embargo, en el entorno de ejecución actual, ni `pip install -e` ni la configuración de la variable `PYTHONPATH` funcionan como se esperaba. Esto causa un `ModuleNotFoundError` al intentar importar módulos de la base de datos (ej. `from models...` o `from sga_cd_db.models...`).

**La Solución (Workaround):**
Para hacer que la aplicación funcione en este entorno, las sentencias de importación dentro de `BACKEND/SGA-CD-BACKEND/app/` han sido modificadas para usar una mezcla de importaciones relativas y absolutas que son relativas al directorio `app/`.

*   En el directorio `app/crud/`, se usan importaciones relativas como `from ..models import ...`.
*   En el directorio `app/api/`, se usan importaciones absolutas como `from app.models import ...`.

**Advertencia:**
Esta no es una solución ideal y se considera deuda técnica. Si el entorno de ejecución se corrige en el futuro para que `PYTHONPATH` funcione correctamente, estas importaciones deberían revertirse a su forma más simple y estándar (ej. `from models import ...` en todo el proyecto, asumiendo que `SGA-CD-DB.git` está en `PYTHONPATH`).

No reviertas estas importaciones a menos que hayas confirmado que el entorno de `PYTHONPATH` ha sido reparado.

## Herramientas de escritorio locales

La copia de agent-desktop está en `DESKTOP/agent-desktop`; el conector y su
procedencia están en `DESKTOP/agent-desktop-sgacd`. El runner local es
`node DESKTOP/agent-desktop-sgacd/run.mjs`. Antes de usar acciones, consulta
`skills get desktop`, `skills get platform` y `status` del runtime instalado.
El proceso opera su propio host: Codespaces no proporciona acceso al portátil.
La configuración MCP del proyecto no conecta automáticamente esta sesión de chat.

## Organización de la billetera

Requisito permanente del usuario: cualquier persona de Colombia puede registrarse
y usar su billetera personal, sin pertenecer al ERP, SGA-CD ni al sector turístico.
TURISTA/EMPLEADO son etiquetas históricas, no requisitos de elegibilidad. El vínculo
con una reserva y el consentimiento se exigen para recibir ese reembolso concreto,
no para el acceso general a la billetera.

Las fuentes canónicas están en WALLET-BACKEND, WALLET-FRONTEND, WALLET-MOVIL
y WALLET-DESKTOP. Conservar los imports apps.wallet, la etiqueta Django wallet
y las migraciones existentes mediante adaptadores de compatibilidad. No mover
bases, secretos o llaves junto con el código.

Actualizar ANALISIS/produccion/PENDIENTES-PRODUCCION-BILLETERA.md mediante el registro canónico
production_pending.json y WALLET-BACKEND/tools/update_pending_doc.py en cada
entrega que cambie evidencia o deje un bloqueo nuevo. No cerrar pruebas físicas,
identidad, proveedores o releases usando evidencia sintética.

Los agentes funcionales nuevos deben apoyarse en el contrato Open Duet +
agent-desktop mediante el conector limitado y el control de autorizaciones
existente. No autoaprobar, exponer secretos a modelos ni crear bypasses de shell.
El modo offline prepara borradores/apuntes, no liquida dinero; las dos revisiones
locales no son autorizaciones financieras ni permisos de control.

## Preferencia del usuario sobre entregas y Git

No crear commits parciales durante el desarrollo. No hacer push, merge ni
reescribir historia como parte de las verificaciones. El usuario ha indicado
que los commits y la actualización del repositorio se harán únicamente al
terminar el trabajo final y cuando lo indique. Conservar avances en la rama y
archivos actuales; documentar diferencias frente a main sin obligar a aplicar
parches parciales. Consultar INTEGRACIONES/plan-maestro/VERIFICACION_MAIN.md.

## Umbral vigente para la siguiente entrega Git

El usuario indicó que el siguiente commit consolidado ("Summit") se realizará
cuando el avance verificable sea estrictamente superior al 70 %. No hacer
commits parciales ni push antes de ese umbral. Conservar código y evidencias
locales y no aumentar porcentajes para habilitar una entrega.

El2026-11-11 el usuario autorizó expresamente una excepción para un único commit
consolidado y la integración de los avances actuales en main, aunque el indicador
siga en66,67%. Esta excepción no autoriza commits parciales posteriores.

El cierre secuencial deACC-003 acredita51/72=70,83% y cumple el umbral
para la siguiente entrega consolidada del acumulado local. Esta entrega consume
esa condición; no autoriza commits parciales automáticos posteriores.

## Identidad visual obligatoria

Replicar la identidad de SGA-CD en Analemática, ERP, Turismo y billetera: azul
metalizado, acentos azul claro y texto blanco. Referencia FRONTEND/IDENTIDAD-VISUAL.md.
Conservar estructura, navegación y componentes existentes. No introducir otra
paleta primaria, fondos blancos con texto oscuro ni reconstruir layouts como
parte de una mejora funcional. Verificar contraste, foco y vista móvil.

## Organización de análisis

Los análisis y pendientes consolidados nuevos van en ANALISIS/; no crear informes
en la raíz. Conservar informes históricos de integración en sus carpetas actuales.
La directriz contable y matriz de pools están en ANALISIS/contabilidad/.

## Seguimiento del motor contable

En cada entrega contable informar el porcentaje calculado de implementación y
optimización según ANALISIS/contabilidad/PROGRESO.md. La base estable es la matriz
de 24 tareas y 72 hitos: incremento funcional, verificación y aceptación completa.
Actualizar el registro de evidencias y regenerar con
`python ANALISIS/contabilidad/tools/update_progress.py`; comprobar con `--check`.
No aumentar el porcentaje por añadir documentación, duplicar evidencia o repetir
pruebas de un hito ya acreditado. La presencia de un archivo no demuestra por sí
sola un proceso operativo. No acreditar aceptación completa, ambos sistemas,
proveedores o producción usando únicamente pruebas sintéticas. Conservar la base
anterior al cambiar alcance o ponderaciones; no inventar porcentajes ad hoc.

## Seguimiento consolidado autorizado

El usuario exige un solo archivo de novedades/hallazgos/pendientes: actualizar
ANALISIS/contabilidad/CIERRE_20_HITOS.md. No crear nuevos informes por análisis o
entrega (IMPLEMENTACION_NN.md, cierres nuevos, etc.). Conservar documentos históricos
y enlaces existentes; mantener las matrices/registros automáticos canónicos.
La actualización de main solicitada el2026-11-09 es una entrega consolidada
explícitamente autorizada; después se conserva la preferencia de no commits parciales.

## Ejecución secuencial de las24 tareas contables

Directriz expresa vigente del usuario: enumerarACC-001 aACC-024 y cerrar cada
tarea al100% antes de iniciar la siguiente. Única tarea activa: la primera que
no tenga aceptación integral acreditada en progress-registry.json. No alternar
frentes ni ampliar otras tareas mientras esa tarea siga abierta. Si un requisito
externo impide el cierre, registrar el bloqueo y solicitar únicamente la
evidencia necesaria; no saltar a otra tarea ni declarar100% local como cierre
integral. Mantener alcance/criterios originales y separar implementado/probado,
desarrollo pendiente y requisitos externos. La secuencia y su seguimiento viven
en ANALISIS/contabilidad/CIERRE_20_HITOS.md; no crear otro plan narrativo.


## Ejércitos propios de los ERP

Directriz expresa del usuario: SGA-CD es referencia estructural, no dependencia
operativa. Los ejércitos contables propios viven en
`BACKEND/ANALEMATICA-BACKEND/gestion_contable/contabilidad/agent_army` y
`BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/contabilidad/agent_army`.
Comparten primitivas del ledger existente, conservando namespaces de misiones,
configuración, estado mayor y APIs propios. No importar agentes/servicios de
SGA-CD ni exigir que ese backend esté encendido.

Jarvi es el General operativo; Neko es el General conversacional; SOUP es el
General optimizador de procesos de los agentes. La cadena interna es Coronel,
Capitán, Teniente, Sargento y Soldado. El agente de voz fluida es una función
separada cuyo nombre/proveedor no fue identificado; no confundirlo con Neko.
La transcripción no constituye una aprobación financiera.

Turismo Nacional es institucional, no un ERP: no añadirle esta estructura
contable ni habilitar acceso empresarial por jurisdicción o rol institucional.
La integración inicial usa consultas/diagnósticos permitidos y auditoría; las
acciones financieras conservan sus flujos de revisión, consentimientos y firmas.
SOUP mide y propone: no entrenar/promover candidatos ni activar cambios sin
validación. Los motores locales tienen configuración propia por backend,
asignación explícita a administrador/empresa y están deshabilitados por defecto.

## Liderazgo central de Analemática · directriz 2026-11-11

El usuario autoriza una entrega consolidada y renombrar el repositorio GitHub a
Analematica. Analemática es el sistema líder. Las fuentes completas OpenJarvis,
N.E.K.O y Soup pertenecen a BACKEND/ANALEMATICA-BACKEND/agents, junto con los
contratos canónicos y legacy_command_staff.py. SGA-CD conserva únicamente sus
adaptadores de compatibilidad y sus divisiones propias. Los adaptadores ERP
conservan su política empresarial, autenticación y namespaces; el núcleo común
y el comportamiento de los generales pertenecen al backend de Analemática.
La centralización de fuentes no habilita servicios ni comparte credenciales.
No convertir Turismo Nacional en ERP. No cambiar porcentajes por este traslado.
