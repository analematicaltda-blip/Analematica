# Implementación74 · Nómina y costos operables desde ambos paneles

Se conectó el flujo de costos de operación con Analemática y con las interfaces de ambos sistemas. Ya permite consultar jornadas, declarar capacidad y centros, revisar el reparto, dar una segunda autorización, registrarlo y recuperar su historial. Todo se apoya en la nómina contabilizada del libro compartido; no se genera otro gasto ni pago.

## Cambios verificables

- Cinco comandos corporativos fijos conservan la sesión ERP, CSRF, vínculo empresarial vigente y exclusividad del propietario. No se reciben servidores ni empresas alternativos del cliente.
- Contrato específico rechaza empresa/nómina ajenas, importes ambiguos, reparto que no concilia, procedencia inesperada, totales completos sin cobertura y supuestas autorizaciones financieras.
- Formulario compartido mantiene azul metalizado, azul claro y blanco. No incluye jornada legal predeterminada ni inventa centros. La capacidad sin respaldo permanece sin asignar.
- Dos confirmaciones separadas; editar descarta revisión y autorizaciones. La recuperación muestra vigencia, revisiones y costo sin asignar sin recuperar aprobaciones.
- Cierre de sesión/cambio de identidad descartan los datos locales privados. La selección empresarial del ERP desmonta el panel y cancela las solicitudes pendientes.
- Fixtures y sus datos sintéticos solo se instalan en los servidores desechables de prueba bajo indicadores explícitos; no se agregan datos durante el arranque normal.

## Verificación

**759 pruebas Python aprobadas en43 suites, sin omisiones**, incluidas70 del puente corporativo. Manifiesto estable actual y hashes de registros comprobados.12 pruebas nuevas: dos recorridos HTTP reales Analemática→ERP y diez de contrato.40 comprobaciones de navegador entre los dos paneles, incluyendo regresión de contabilización de nómina y el flujo nuevo; tipos estrictos de los componentes seleccionados aprobados. No sustituyen build completa, validación física ni aceptación normativa.

[Registro de evidencia](evidencias/implementacion-74.json) · [ERP móvil](evidencias/implementacion-74-erp.png) · [Analemática móvil](evidencias/implementacion-74-corporate.png).

## Pendientes y avance

R10 sigue en ejecución: la nómina base y su distribución ya son operables, pero faltan reglas revisadas de novedades, recargos, viáticos y deducciones completas; nómina electrónica, concurrencia/volumen productivo PostgreSQL y evidencia laboral legítima. R18 continúa parcial por los demás recorridos pendientes. Esta entrega no completa los20 hitos.

**63,89% (46/72), aceptación completa0/24.** Son ampliaciones de hitos ya acreditados, sin crédito duplicado. No se realizaron commits, push, pagos ni envíos DIAN.
