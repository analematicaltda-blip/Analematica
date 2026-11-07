# Instalación local sin respaldo histórico

El usuario indicó que no dispone de respaldos. Se inspeccionaron los archivos visibles e ignorados por Git, sin extraer registros privados. Se encontraron cinco bases auxiliares: contabilidad Analemática, billetera y entregas de cada backend turístico. No son una base completa de gestión institucional o empresarial.

Se conservaron los originales y se crearon cinco copias privadas en `BACKEND/deployment/.runtime/recovered-backups/`. Se usó la API de backup SQLite y se comprobó integridad y restauración aislada con esquema y conteos iguales. No se publican esas copias, claves ni filas en Git. Es una copia de datos; conservar además las claves originales de cifrado. No se atribuye procedencia productiva a estos archivos.

## Alternativa implementada

`fresh-local-v1` permite continuar el desarrollo con bases NUEVAS SQLite. Versiona un baseline propio separado del historial antiguo. Se incluyen migraciones de 102 aplicaciones del proyecto, conservando las migraciones de paquetes externos. Django aplica 163 migraciones y crea 584 tablas por base. Las bases ERP y Turismo tienen directorios y claves independientes.

Se corrigió el descubrimiento de modelos operacionales, campañas y eventos: antes dependía de cargar URLs concretas. Se registran durante AppConfig.ready y se verifica ausencia de diferencias con `makemigrations --check --dry-run`. Se detectaron y corrigieron dos instalaciones iniciales incompletas; la verificación de preparación impidió anunciarlas listas. Una nueva instalación final desde cero quedó verificada después de esas correcciones.

El inicializador rehúsa directorios existentes, usa permisos privados y no ejecuta `--fake`. No toma una base anterior ni elimina su historial. El perfil local usa canales y caché en memoria y correo local para no depender de Redis o correo externo durante pruebas. No sustituye el despliegue Compose/PostgreSQL. No ofrece persistencia/distribución de canales en memoria.

## Comprobaciones

- Dos bases independientes: `/readyz` 200, todas las tablas/columnas requeridas presentes, ninguna migración pendiente y cero violaciones de claves foráneas.
- Migración repetida sin duplicar historia, modelo sin divergencia y copia/restauración privada verificada.
- HTTP completo del CRM en ambas bases: alta 201, consulta/edición 200, consulta y escritura desde otra empresa 404. Los datos sintéticos se revierten con transacción, incluso si falla una prueba; no se conservan como información real.
- 80 ejecuciones correctas: 64 de regresión anterior, 14 sobre bases migradas (7 por servicio) y 2 de respaldo/WAL/no sobrescritura. La repetición adicional de instalación limpia confirma el baseline final. CI reproduce ambas instalaciones desde cero.

Evidencia de conteos e integridad: `fresh-local-evidence.json`. Los comandos para crear y administrar estas instalaciones están en `BACKEND/deployment/README.md`.

## Límites

Esto elimina la necesidad de conseguir un respaldo inexistente para continuar pruebas NUEVAS. No recupera datos ausentes ni reconcilia la historia heredada. Los modelos y módulos incompletos no se convierten en procesos terminados porque sus tablas existan. Permanecen pendientes reservas/disponibilidad/pagos, contabilidad completa, RNT/DIAN y proveedores oficiales, contratos/consentimiento, despliegue y móviles físicos. El plan maestro continúa en ejecución.
