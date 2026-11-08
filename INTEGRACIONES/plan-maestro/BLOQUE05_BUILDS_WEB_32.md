# Bloque 5 — builds y recorridos web

Se implementaron herramientas reproducibles y correcciones de fuentes. Los
builds completos ERP/Turismo siguen FALLANDO; el bloque5 no está terminado.
No se habilita producción ni se ignoran errores para declarar un build válido.

## Cambios realizados

- Build aislado de fuentes completas mediante build_check.py. Usa el manifiesto
  y lockfile canónicos, exige TypeScript/tipos y genera logs e informe por sistema.
  Conserva fuentes originales y evidencia anterior. Solo usa proyectos generados.
- next_projects admite dependencias explícitas y selección de sistema. Turismo
  resuelve módulos ERP reutilizados en src/shared/erp, sin montarlos como rutas
  nuevas. Aliases relativos sirven tanto en host como en contenedor.
- Corrección de25 imports relativos del hook existente y otras referencias a
  Card, Modal y hooks. Se cerraron las etiquetas JSX inválidas en verificación
  y directorio de prestadores; el análisis sintáctico completo quedó sin errores.
- Contratos de Button/Badge compatibles con variantes y tamaños ya utilizados,
  con paleta azul metalizado/celeste y texto blanco. No se cambian layouts.
- Switch controlado accesible, con teclado y deshabilitación si no hay handler.
  La configuración financiera sin backend queda identificada y deshabilitada;
  no representa automatizaciones activas ni ejecuta reindexación.
- Export nombrado adicional del cliente HTTP existente, sin crear otra instancia.
- Dependencia oficial slick-carousel1.8.1 fijada en manifiesto/lockfile para los
  estilos ya importados por react-slick. No se cambió la versión de Next/React.
- Workflow manual Full web build audit, con checks estrictos y reporte. Un fallo
  real mantiene el job fallido; no usa continue-on-error ni publica sitios.

## Resultado verificado

| Comprobación | Resultado | Alcance |
| --- | --- | --- |
| Parser718 fuentes |0 errores sintácticos |11 JS corporativos,240 ERP,467 Turismo |
| Páginas sin export default |7 avisos |No equivalen a páginas implementadas |
| TypeScript estricto de Button/Badge/Switch |Correcto |Tres controles y dependencias de sus tipos |
| Preparación y gateway |8 pruebas aprobadas |No añade rutas ERP al portal institucional |
| Controles en Chromium |13 comprobaciones |Ratón, teclado, callbacks, disabled y colores |
| Cotizaciones ERP por HTTPS |19 comprobaciones |Sesión MFA y persistencia; datos sintéticos |
| Analemática |Renderizado1440/390/320 correcto |Manifest con API simulada; no login real del dueño |
| Build ERP Next16.4.5 |FAILED |No se resuelve @sarita/shared-ui |
| Build Turismo Next16.4.5 |FAILED |No se resuelve @sarita/shared-ui |

La comprobación semántica completa inicial encontró1224 diagnósticos en ERP
y1196 en Turismo, antes de las últimas correcciones de controles compartidos.
Comparten muchas fuentes y no se suman como2420 funciones distintas. No es un
recuento final tras esas correcciones; se conserva solo como línea base de
priorización, sin código fuente ni datos sensibles en el resumen. Importaciones,
exports, props, DTO y páginas incompletas requieren revisión por contrato.
El análisis sintáctico correcto no certifica tipos ni rutas operativas.

## Bloqueos concretos y siguiente orden

1. Recuperar el paquete real @sarita/shared-ui o establecer su contrato a partir
   de las fuentes autorizadas. La carpeta local components/shared-ui tiene otros
   exports y no satisface WebLayout/KpiCard/DataTable/AttractionCard/EventCalendar/
   InteractiveRouteMap usados por las pantallas. No se creó una biblioteca falsa.
2. Recuperar/revisar shared-sdk y contratos de clientes importados desde rutas
   monorepo ausentes. La consulta GitHub de solo lectura al APP original devolvió
   Forbidden. No acredita que las fuentes no existan en el origen; no pudieron
   recuperarse en esta sesión. No se modificó ningún repositorio remoto.
3. Resolver los demás módulos ausentes detectados: tipos de ventas, servicio de
   publicaciones, Footer y formulario de descargas, contrastando contratos antes
   de escribir implementaciones. Presencia de imports no prueba que funcionen.
4. Implementar las páginas vacías y corregir exports/props/DTO sin usar any global,
   stubs funcionales ni ignoreBuildErrors. Los siete avisos están en la evidencia.
5. Ejecutar ambos builds completos y recorridos con APIs reales de prueba. Los
   recorridos actuales acotados no equivalen a todas las páginas institucionales,
   empresariales o al panel completo de Analemática.
6. Validar login institucional, selector empresarial, documentos, reservas,
   permisos, estados de error y navegación móvil en cada dominio.

## Reproducir

```bash
npm ci --prefix FRONTEND/deployment --include=dev --ignore-scripts
node FRONTEND/deployment/check_sources.cjs --dependencies FRONTEND/deployment/node_modules --output /tmp/nuevo-syntax.json
node FRONTEND/deployment/check_components.cjs --dependencies FRONTEND/deployment/node_modules --output /tmp/nuevos-controles.json
python FRONTEND/deployment/build_check.py --dependencies FRONTEND/deployment/node_modules --output /tmp/nuevo-build-web
```

Usar destinos nuevos para conservar evidencia. En este entorno los subprocesos
Node del build requieren ejecución fuera del sandbox: dentro devolvían salida
vacía incluso con un comando trivial, por lo que esos intentos iniciales no se
clasifican como defectos de la aplicación. La evidencia final corresponde a la
ejecución efectiva, que sí informó los módulos faltantes.

La instalación se probó con npm ci y el lockfile actualizado. git diff --check
correcto. No hay credenciales nuevas, contratos comerciales activados, cambios
backend, commits, push ni despliegues. Ver web-build-evidence-32.json y logs en
evidencias/build-web-32/. El plan y el bloque5 continúan abiertos.
