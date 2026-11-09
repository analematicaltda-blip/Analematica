# Implementación 59 · Copias cifradas y restauración de borradores

**Avance global: 55,56 % (40/72), sin nuevos créditos.** Amplía ACC-022, acreditada en la entrega58. H19 sigue en ejecución: 4 paquetes verificados localmente, 10 en ejecución, 6 pendientes y aceptación completa0/24. No se declara completado el conjunto de20 hitos.

## Recuperación implementada

Ambos paneles permiten exportar una copia JSON cifrada del borrador local y restaurarla cuando falta su registro en IndexedDB. La exportación exige desbloquear el borrador con la contraseña correcta. El archivo contiene exclusivamente el sobre cifrado y sus metadatos; no incluye contraseña, clave derivada, campos en texto claro ni autorizaciones.

Restaurar exige empresa verificada, UUID del borrador y contraseña correspondiente a esa copia. Se valida esquema exacto, tamaño, contexto, autenticación AES-GCM y forma del contenido antes de escribir. Una contraseña incorrecta o una copia de otra empresa no crea registros. Se conserva la versión del archivo.

Si ya existe exactamente el mismo registro, la restauración recupera el mismo resultado. Si existe otro contenido o versión local, se rechaza sin sobrescribirlo. Así una copia antigua no reemplaza silenciosamente el borrador activo después de su rotación. Las escrituras conservan la comparación transaccional para conflictos concurrentes.

El contenido restaurado se presenta como borrador editable y retira las revisiones y casillas de autorización. No se sube automáticamente ni registra hechos contables. La medición online sigue requiriendo las dos confirmaciones y controles de pertenencia/duplicados del backend.

## Operación

1. Verificar la empresa mientras haya conexión y conservar el UUID del borrador.
2. Guardar el borrador cifrado y exportar su copia indicando la contraseña local.
3. Ante pérdida del registro local, cargar el panel, verificar la misma empresa e indicar el UUID que aparece en el nombre de la copia.
4. Seleccionar el JSON e introducir la contraseña que correspondía a esa copia. Restaurar no requiere red una vez verificada la sesión activa.
5. Revisar el borrador recuperado; al reconectar, autorizar de nuevo los pasos online.

Cambiar la contraseña del registro activo no modifica copias exportadas antes del cambio: esas copias siguen dependiendo de su contraseña anterior. Debe exportarse una nueva copia si se quiere respaldar la nueva versión. No existe recuperación de contraseña por servidor, revocación de archivos ya copiados ni backup de KEK fiscales.

## Evidencia funcional

La prueba de ambos paneles descarga un archivo real, verifica que no contiene el marcador privado ni la contraseña, elimina el almacén sintético de prueba y restaura desde ese archivo con la red deshabilitada. Comprueba igualdad de campos, conservación de versión, autorizaciones desmarcadas y posterior registro online con dos confirmaciones. No se borraron datos reales del cliente.

La prueba criptográfica verifica adicionalmente exportación autenticada, contraseña incorrecta sin escritura, restauración idempotente, rechazo entre empresas y rechazo de una copia antigua sobre una versión activa diferente.

Resultados y capturas en [evidencia59](evidencias/implementacion-59.json). El módulo usa WebCrypto/IndexedDB del navegador: no acredita custodia hardware, SQLite nativo ni pruebas físicas.

## Límites que permanecen

- La copia debe conservarse fuera del almacén que se pretende recuperar. La prueba no cualifica medios físicos, cifrado de disco, retención institucional, pérdida de dispositivo ni procedimientos de producción.
- Sigue pendiente el catálogo/listado de borradores, borrado por retención, arranque completo offline, captura de más dominios y sincronización ampliada. Actualmente se usa UUID conocido y sesión previamente verificada.
- Una copia válida de un borrador no es un evento financiero autorizado, una factura fiscal validada ni un mecanismo de recuperación de documentos/KEK soberanos. H10/H11 conservan sus requisitos propios.
- Los metadatos empresa/UUID/versión del archivo son visibles. La contraseña y el contenido descifrado pueden existir en memoria de JavaScript; no se promete borrado forense ni protección frente a scripts comprometidos del mismo origen.
- El servicio no detecta pérdida deliberada del almacén seguida de restauración de una copia vieja. La copia sigue siendo un borrador y las verificaciones online son obligatorias antes de registrar una medición; no se usa para retroceder el ledger.

No se hicieron commits, push, cambios en main, despliegues, pagos ni llamadas a proveedores, DIAN o bancos reales.

## Verificación final ejecutada

- **437 pruebas Python aprobadas**, con fuentes estables y las dos APIs contables reales de prueba.
- **321 comprobaciones Chromium aprobadas**: 50 ERP, 27 corporativas, 52 apertura/políticas, 28 nómina, 32 conciliación, 32 hoteleras, 32 ambientales, 44 offline/respaldo en ambos paneles y 24 criptográficas/IndexedDB.
- TypeScript estricto de cuatro componentes sin errores; no equivale a build Next completo.
- Suite final `/tmp/sgacd-offline-59-final`, hashes verificados y fuentes actuales coincidentes. Los 48 escenarios PostgreSQL de la entrega57 no se repitieron en esta ampliación de cliente sin nuevo esquema o escritura backend.
- Siete pruebas del cálculo de avance y documento canónico de pendientes de billetera comprobados. Sin aceptación física ni productiva.
