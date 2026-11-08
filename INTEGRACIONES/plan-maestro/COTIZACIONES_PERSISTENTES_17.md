# Implementación: cotizaciones persistentes e interfaz ERP

## Comportamiento implementado

- Guardar un borrador con precios de servidor, empresa verificada y cliente propio.
- Repetir la solicitud con la misma clave sin duplicar el registro ni cambiar sus precios.
- Rechazar la reutilización de la clave con otro contenido (409).
- Listar borradores paginados, consultar detalle y retirar conservando el historial.
- Revalidar autoridad empresarial en cada acceso; sin acceso global para otros usuarios.
- Detectar cambios del snapshot por su checksum y mostrar caducidad sin reactivar el borrador.
- Impedir el borrado de clientes con cotizaciones vinculadas.
- Seleccionar empresas, clientes y productos reales desde la pantalla del ERP.
- Adaptar la interfaz al renderer empresarial real, incluidos los metadatos de paginación.

Los borradores son propuestas no vinculantes: no reservan cupos o inventario,
no calculan impuestos, no generan deuda, no facturan y no cobran. Los precios
se conservan como snapshot; el checksum detecta cambios accidentales respecto
al valor registrado, no sustituye una firma externa contra un administrador de DB.

## Fuentes y rutas

- Modelo: apps/turismo/models/quotation.py, registrado como turismo.QuotationDraft.
- Persistencia: gestion_comercial/quote_drafts.py; interfaz HTTP: quote_views.py.
- Migración nueva: fresh_migrations/turismo/0003_quotationdraft.py.
- Pantalla: FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-comercial/cotizaciones/page.tsx.
- Página en el proyecto ensamblado: /dashboard/prestador/mi-negocio/gestion-comercial/cotizaciones.
- Enlace añadido a gestión comercial; corregido el import faltante de useMiNegocioApi.

Bajo /api/v1/mi-negocio/comercial/:

| Método | Ruta | Resultado |
|---|---|---|
| GET | quotation-options/ | Empresas propias verificadas |
| GET | quotation-options/?provider_id=... | Clientes y productos de esa empresa; búsquedas acotadas |
| POST | quotation-drafts/ | Alta idempotente; 201 nueva o 200 repetición |
| GET | quotation-drafts/?provider_id=... | Listado paginado privado |
| GET | quotation-drafts/{id}/ | Snapshot y estado |
| POST | quotation-drafts/{id}/withdraw/ | Retiro con digest; no borra |

No hay endpoint para editar los importes guardados, aceptar cobros ni eliminar
el historial. Para otra propuesta se genera una solicitud nueva explícita.

## Evidencia y límites

27 pruebas de identidad/cotización, 6 regresiones CRM y 10 comprobaciones por
cada base migrada (53 ejecuciones Python). La prueba de navegador compila con
TypeScript estricto y usa el componente React real más vistas/ORM Django reales.
La identidad es sintética y el servidor de esa prueba solo escucha en loopback:
no certifica login, middleware completo ni gateway productivo.

El flujo HTTP también se probó con APIClient sobre las bases migradas, incluidas
las respuestas normalizadas por el renderer real. Los datos sintéticos de esos
checks se revierten al terminar. Solo se aplicó la migración en bases privadas
bajo /tmp creadas para pruebas; no se tocaron las bases del proyecto ni producción.

La configuración frontend/deployment sigue rechazando /api de ERP/Turismo con
503 por defecto. Por tanto, la pantalla está implementada pero no se declara
habilitada para usuarios reales: falta integrar y validar autenticación/gateway.
No se certifica el build completo del frontend heredado a partir del test aislado.

## Repetir el navegador

Instalar esbuild0.25.11, React/ReactDOM19.2.0, TypeScript5.9.3 y tipos React19.2.2
solo en un directorio de pruebas; no reemplazar dependencias del producto.
Configurar QUOTE_UI_DEPS hacia su node_modules y QUOTE_PYTHON hacia el Python
con dependencias backend. Ejecutar FRONTEND/deployment/tests/quotation_browser.cjs.
PLAYWRIGHT_MODULE admite el módulo instalado y CHROMIUM_PATH el Chromium local;
con CHROMIUM_PATH=playwright se usa el navegador instalado por Playwright en CI.

El harness quotation_server.py y quotation_auth_fixture.ts son exclusivos de
pruebas: no se copian al código de autenticación ni se despliegan como servidor.

## Pendientes de este módulo

Autenticación/gateway ERP, build completo, recorrido con identidad real,
concurrencia PostgreSQL, aceptación/persistencia de propuestas comerciales,
impuestos y disponibilidad, notificaciones y futuras integraciones de cobro.
Nada de esto se marca terminado por guardar un borrador.

Los cambios quedan sin commit ni publicación, según el acuerdo vigente.

Captura de la prueba móvil: [cotizaciones-movil.png](evidencias/cotizaciones-movil.png).
El recorrido final incluye limpieza de borradores en pantalla al cerrar sesión.
