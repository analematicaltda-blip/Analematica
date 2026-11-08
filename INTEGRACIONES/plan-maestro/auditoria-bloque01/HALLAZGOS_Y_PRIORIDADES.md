# Hallazgos y orden de trabajo del bloque 1

Los defectos de fuente son reproducibles por AST; su activación en runtime no se supone. Las brechas de cobertura no equivalen a vulnerabilidades confirmadas. Ninguna fuente se eliminó.

## B01-001 · ALTA · Analemática

Import incompleto y asignación sin expresión: no compila. No se acredita conexión a rutas activas.

Evidencia: `BACKEND/ANALEMATICA-BACKEND/services/gov_reports.py:4`.

Acción: Mapear consumidores y contrato de indicadores; implementar o aislar justificadamente después de revisar dependencias.

Aceptación: Compila, pruebas de indicadores con datos reales de prueba y autorización territorial.

Dependencia: No depende de equipos externos.

## B01-002 · ALTA · SGA-ERP-TUR

Archivo Python contiene marcado de herramienta y JSX después de urlpatterns.

Evidencia: `BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/archive/urls.py:8`.

Acción: Determinar ruta efectiva del módulo archivístico y separar contenido con pruebas.

Aceptación: Import de rutas correcto; acceso documental autorizado y rechazo entre empresas.

Dependencia: Auditar módulos documentales y sus modelos.

## B01-003 · ALTA · SGA-TUR

Bucle sin cuerpo ejecutable; no compila. Un retorno True tampoco acredita integridad contable.

Evidencia: `BACKEND/SGA-TUR-BAKEND/apps/enterprise_core/services/self_healing.py:68`.

Acción: Definir contrato de verificación sin reparar automáticamente datos financieros.

Aceptación: Detecta alteraciones de prueba y no certifica un ledger manipulado; cero modificaciones destructivas.

Dependencia: Revisar dependencia de JournalEntry y formatos de cadena.

## B01-004 · ALTA · ERP y Turismo

No se encuentra package.json en las raíces fuente auditadas; la preparación de preview es separada. Build integral no acreditado.

Evidencia: `FRONTEND/SGA-ERP-TUR-FRONTEND; FRONTEND/SGA-TUR-FRONTEND`.

Acción: Recuperar contrato de build y rutas de cada aplicación, antes de instalar versiones arbitrarias.

Aceptación: Build repetible con lockfile y navegación real, azul metalizado/celeste/blanco.

Dependencia: Determinar fuentes canónicas, aliases y dependencias.

## B01-005 · ALTA · Tres sistemas

144 grupos exactos de fuentes candidatas; no prueba que se puedan borrar.

Evidencia: `inventario.json:exact_duplicate_source_groups`.

Acción: Mapear imports, rutas y responsables; decidir fuentes canónicas sin reescritura general.

Aceptación: Ninguna función o ruta se pierde al consolidar; pruebas antes/después.

Dependencia: Mapa de dependencias y builds.

## B01-006 · CRITICA · ERP y Turismo

Los paquetes reubicados comparten namespaces y kernel; separar carpetas no independiza contratos de negocio.

Evidencia: `BACKEND/deployment/tourism_bindings.py`.

Acción: Auditar Tenant, usuario, proveedor y vínculo empresarial en todos los endpoints.

Aceptación: Pruebas negativas empresa A/B, actor no titular, cambio y revocación en cada módulo.

Dependencia: Bases temporales y contratos de identidad.

## B01-007 · CRITICA · ERP

POS/operaciones responden503 deliberadamente; los borradores no son venta ni factura.

Evidencia: `BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/views.py:10`.

Acción: Definir disponibilidad, aceptación, impuestos, idempotencia y conciliación antes de habilitar.

Aceptación: Venta y reversión verificadas sin duplicar cobros ni emitir comprobantes ficticios.

Dependencia: Reglas comerciales y proveedores fiscales/de pago autorizados.

## B01-008 · CRITICA · SGA-TUR

Permisos de atractivos/reseñas cubiertos; no todos los módulos institucionales.

Evidencia: `BACKEND/deployment/tests/domain_security_check.py`.

Acción: Extender matriz rol+nivel+entidad+jurisdicción+permiso a tareas, eventos, documentos y exportaciones.

Aceptación: Usuario municipal no accede ni escribe otro territorio; consolidación no concede edición.

Dependencia: Datos de prueba de entidades y delegaciones.

## B01-009 · ALTA · Tres sistemas

153 requisitos siguen sin evidencia funcional integral,7 tienen evidencia parcial y1 defecto de fuente clasificado.

Evidencia: `matriz-priorizada.json`.

Acción: Ejecutar casos de aceptación por flujo institucional y luego ERP desde el cliente.

Aceptación: Cada requisito tiene resultado, ruta, evidencia, riesgo y regresión.

Dependencia: Inventario y priorización entregados.

## B01-010 · BAJA · Dependencia central

El encabezado declara JavaScript ejecutado por Node pese a extensión.py. No es un defecto Python productivo.

Evidencia: `BACKEND/SGA-CD-BACKEND/app/open-generative-ai/tests/fixtures/fake-wan2gp/wgp.py:1`.

Acción: Conservar y distinguirlo en escáneres; no convertirlo a Python.

Aceptación: La prueba que lo usa sigue funcionando.

Dependencia: Revisión del consumidor Node antes de cualquier cambio.
