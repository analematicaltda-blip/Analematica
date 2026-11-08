# Estado y pendientes del ecosistema

Revisión documental: 2026-11-08. Alcance: Analemática, SGA-ERP-TUR y SGA-TUR, con servicios compartidos y billetera. **Plan maestro en curso; producción NO habilitada.** Los bloques entregados contienen implementaciones y pruebas acotadas; no implican cumplimiento integral de cada frente. No se dispone de evidencia para afirmar un porcentaje global de terminación.

El estado por frente se conserva en [tablero del plan](../../INTEGRACIONES/plan-maestro/tablero.json). Este documento reúne pendientes y criterios de cierre, sin sustituir las evidencias ni los registros canónicos de la billetera. Los responsables indicados son áreas propuestas, no personas formalmente asignadas.

## Falta desarrollar o comprobar en local

Estos pendientes no se resuelven simplemente trasladando el código a un servidor.

| ID | Prioridad | Pendiente | Área responsable | Criterio para cerrar |
| --- | --- | --- | --- | --- |
| LOC-01 | Crítica | Builds completos ERP/Turismo: falta `@sarita/shared-ui` y siguen contratos/fuentes incompletos | Frontend/arquitectura | Recuperar o implementar contratos reales, compilar ambos sin ignorar errores y verificar recorridos; conservar identidad azul metalizado/celeste/blanco |
| LOC-02 | Alta | Auditoría funcional integral institucional y ERP | Arquitectura/QA | Verificar requisitos con trazas y pruebas de extremo a extremo, después de inventariar rutas/modelos; no clasificar una función por tener botón o archivo |
| LOC-03 | Alta | Reservas definitivas, interfaz de disponibilidad, tarifas/impuestos y pagos | Backend/comercial | Probar confirmación, concurrencia, cancelación, reglas comerciales e idempotencia; no confirmar un cobro sin recibo real validado |
| LOC-04 | Alta | Identidad común, delegaciones empresariales, jurisdicción, SSO y recuperación completa/WebAuthn | Identidad/seguridad | Matriz y pruebas positivas/negativas por rol, empresa y territorio; no equiparar JWT o UUID de dominios diferentes |
| LOC-05 | Alta | Integración efectiva de telemetría con AiSOC | Seguridad/infraestructura | Recepción, detección de prueba y trazabilidad de eventos sin secretos; respuestas automáticas deshabilitadas |
| LOC-06 | Media | Evaluación de IA y contenido multimedia | IA/QA | Instalar/configurar modelo autorizado y medir calidad, privacidad, licencia, latencia y coste; probar imágenes/vídeo/voz/transcripción antes de habilitarlos |
| LOC-07 | Alta | Cobertura y operación reproducible | QA/infraestructura | Ampliar pruebas a procesos pendientes, resolver fallos, fijar dependencias/imágenes, revisar vulnerabilidades y límites compartidos; `pip check` no es un escaneo de seguridad |

## Requiere infraestructura, proveedores o equipos reales

La infraestructura puede ser de validación; no es necesario activar producción para comenzar estos ensayos. No se autoriza su activación por la mera existencia de este documento.

| ID | Prioridad | Validación pendiente | Área responsable | Evidencia necesaria |
| --- | --- | --- | --- | --- |
| REAL-01 | Crítica | Recuperación integral y continuidad | Operaciones/DBA | Restaurar esquema completo PostgreSQL, datos, adjuntos, configuración y claves hacia un entorno aislado; medir pérdida admisible de datos y tiempo de recuperación; verificar copias externas y retención |
| REAL-02 | Crítica | Seguridad e identidad de billetera | Seguridad/móvil | Cumplir los 19 pendientes canónicos con equipos, proveedores y revisión correspondiente; no cerrar usando fixtures |
| REAL-03 | Alta | Control nativo Android/iOS/escritorio | Móvil/escritorio/QA | Dispositivos físicos, Mac/Xcode para iOS, permisos, cuenta correcta, observaciones cambiantes, dos autorizaciones del solicitante y tercera de impacto, parada y desconexión |
| REAL-04 | Alta | Distribución e integridad | Release/seguridad | Compilaciones firmadas, instalación, actualización, revocación y recuperación en cada plataforma; verificar atestación, biometría, pines y protección de vistas críticas |
| REAL-05 | Alta | Correo y plataformas oficiales | Integraciones/QA | Correo de recuperación entregado y flujos supervisados con cuentas autorizadas de Meta/TikTok/Gmail/YouTube; comprobar permisos, recibos y resultados reales |
| REAL-06 | Alta | Seguridad operativa y carga | Infraestructura/seguridad | HTTPS, secretos y permisos SQL, aislamiento, sesiones, límites entre procesos, métricas/alertas, carga y revisión de dependencias; conservar el cierre seguro ante fallos |
| REAL-07 | Alta | Integraciones comerciales y fuentes oficiales | Producto/integraciones | Validar RNT, pasarelas/conciliación y obligaciones aplicables con fuentes/proveedores autorizados; separar registro institucional de publicación comercial |

## Evidencia existente y límites

- [Auditoría, bloque 1](../../INTEGRACIONES/plan-maestro/AUDITORIA_BLOQUE01_28.md): 161 requisitos inventariados; 153 no verificados, 7 parciales y 1 defecto de fuente en ese corte. No se ha acreditado después una auditoría integral que cierre esa matriz.
- [Operación, bloque 8](../../INTEGRACIONES/plan-maestro/BLOQUE08_OPERACION_35.md): 20 grupos aprobados, 2 con omisiones y 1 fallido. Ambos builds completos fallan. Las omisiones no cuentan como pruebas aprobadas.
- [Respaldos, bloque 9](../../INTEGRACIONES/plan-maestro/BLOQUE09_RESPALDOS_36.md): copias SQLite cifradas hasta64MiB, restauración editorial y contratos PostgreSQL aislados aprobados. No demuestra recuperación productiva del ecosistema ni recuperación financiera integral de la billetera.
- [Guía de operación y reversión](../../INTEGRACIONES/operacion/README.md) y [respaldos](../../INTEGRACIONES/operacion/RESPALDOS.md): procedimientos locales y límites, sin conmutación automática de datos reales.
- [Pendientes canónicos de billetera](PENDIENTES-PRODUCCION-BILLETERA.md): generado desde `WALLET-BACKEND/offline/src/sgacd_wallet_offline/production_pending.json`; producción permanece deshabilitada.

No se ejecutaron pruebas nuevas para crear esta consolidación: se revisaron los informes registrados y la coherencia del documento canónico de billetera. Las evidencias originales distinguen fixtures, modelos reales de datos, transportes simulados y dispositivos físicos pendientes.

## Regla de cierre y entrega

Cerrar cada pendiente con evidencia fechada, responsable identificado, criterio satisfecho y revisión de regresiones. Conservar las funciones existentes y sus datos. No activar cobros, publicación, control de equipos o producción por asumir que un módulo está terminado. No regenerar claves para intentar recuperar datos cifrados.

Los cambios de desarrollo siguen locales y sin publicación nueva en Git por esta revisión. Commits, push y actualización de main quedan sujetos a la instrucción explícita del usuario al terminar la entrega correspondiente.
