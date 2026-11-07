# Pool 04 · Red y vistas sensibles

Estado: pendiente. Pool 01 no hace conexiones de red.

Antes de configurar pinning hacen falta dominios definitivos, SPKI de producción y
llave de respaldo, rotación y pruebas de caducidad/cambio. Mantener validación TLS
normal; nunca usar trust-all, HTTP de producción ni pins ficticios. Las acciones
financieras deben vincular origen y resumen firmado a sus autorizaciones.

Android permite FLAG_SECURE en vistas críticas. iOS puede ocultar contenido en el
selector de aplicaciones y ante captura/grabación detectada, pero sus APIs públicas
no garantizan bloquear todas las capturas de pantalla. Tampoco se puede impedir
una fotografía externa. Probar accesibilidad y restauración al volver al primer plano.

Ofuscación/R8 es una capa de reducción de exposición, no cifrado ni prueba de
integridad. Se configura en la aplicación host y se prueba en release firmado;
no se activa a ciegas sobre dependencias o APIs requeridas por el puente nativo.
