# Cuarto corte de ejecución del plan maestro

## Cambios comprobados

1. ERP CRM: reparación de campos inexistentes en el serializador y filtro empresarial. Las rutas comercial y operacional comparten aislamiento por propietario. Alta con empresa e identificador público asignados por servidor, consulta/edición propia, rechazo de escritura y lectura ajenas. Correo duplicado por empresa devuelve 400 en vez de error SQL. Si hay varias empresas se exige selección explícita; no se elige arbitrariamente.
2. ERP/Turismo: endpoint `/readyz` independiente de salud. Comprueba historia, migraciones pendientes, existencia de tablas y columnas; responde 503 sin revelar detalles internos. Nunca aplica migraciones. Un esquema válido no certifica procesos financieros ni integraciones.
3. Auditoría reproducible de fuentes de migraciones sin SQL: 140 nodos, 17 referencias al nodo ausente `prestadores.0001_full_reset`, 17 aplicaciones con modelos concretos sin migraciones. Detalle en `migration-sources.json`. No se eliminaron dependencias ni se fabricó una migración vacía.
4. CI incorpora preparación de esquema en ambas configuraciones y CRUD CRM.

## Evidencia y alcance

64 ejecuciones correctas: 18 jurisdicción/reseñas, 12 empresas/reservas, 7 bootstrap ERP, 7 bootstrap Turismo, 8 preparación ERP, 8 preparación Turismo y 4 CRM. SQLite aislado, claves temporales, sin modificar bases de clientes. Las 4 CRM prueban vistas/serializadores/modelos reales mediante APIRequestFactory; no son un recorrido del navegador. La suite de preparación combina HTTP del grafo heredado real y fallos de esquema controlados. No se ejecutaron pagos, cuentas externas ni teléfonos físicos.

## Bloqueo que no se debe ocultar

No hay una copia restaurada y verificada de las bases de negocio para reconciliar la historia heredada con sus datos. Los modelos `ProviderProfile` ahora son proxies de TourismProvider, mientras las migraciones antiguas esperan entidades concretas bajo otra aplicación. Remover dependencias o crear tablas vacías no demuestra compatibilidad ni conserva las relaciones históricas.

Para cerrar ese frente se necesita un respaldo en el entorno privado con su procedencia/historial, restauración aislada, mapa de identidad y conteos/invariantes antes y después. Ninguna credencial debe ponerse en Git o en el chat. Mientras tanto, la preparación devuelve 503 de forma verificable.

El plan maestro completo permanece en ejecución: módulos contables ausentes, contratación/consentimiento, disponibilidad/reservas/pagos, RNT/DIAN oficiales, proveedores IA, SOC, móviles físicos y pruebas de producción no se sustituyen por estos checks. No se atribuyen a Analemática mejoras de negocio realizadas únicamente en ERP/Turismo.
