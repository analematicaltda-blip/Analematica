# Implementación 38 · Base de consulta contable en lenguaje natural acotado

**Avance: 38,89 % (28/72 hitos).** ACC-020 acredita incremento funcional y verificación de alcance parcial; no acredita aceptación completa.

## Implementación

El núcleo compartido incorpora un resolvedor determinista de preguntas españolas, sin LLM, SQL generado o ejecución de código. Reconoce seis variantes explícitas de dos intenciones: rentabilidad empresarial y estado de la cola comercial. Normaliza mayúsculas, acentos y espacios; cualquier otra instrucción se rechaza. No se presenta como comprensión general del lenguaje ni como un clasificador IA evaluado.

`answer_query` permite exclusivamente question/since/until. La rentabilidad requiere fechas ISO explícitas, ordenadas y hasta 366 días; la cola rechaza filtros de fecha no implementados. La pregunta admite hasta 240 caracteres. La empresa procede del contexto autorizado, nunca del cuerpo. No se envían preguntas ni datos a proveedores externos.

La ruta ERP `POST /api/v1/mi-negocio/contable/contabilidad/cuentas/consulta-contable/?provider_id=<UUID>` reutiliza la autenticación y vínculo empresarial del titular. Llama a `ReportsEngine.get_profitability` o `inspect_commercial_outbox`, identifica su fuente y devuelve read_only, generated_sql=false, external_model_used=false y financial_action_authorized=false. Una respuesta nunca autoriza pagos o automatización.

Ejemplos de cuerpo:

```json
{"question":"¿Cuál es la rentabilidad de mi empresa?","since":"2026-11-01","until":"2026-11-30"}
```

```json
{"question":"¿Cómo está la cola de facturación?"}
```

El helper interno no autentica por sí mismo: solo se debe usar desde un contexto autorizado. La cola conserva NOT_VERIFIED y consumidor fiscal pendiente; no se transforma PROCESSED en aceptación tributaria.

## Verificación

168 métodos Python aprobados en once suites. Seis nuevos prueban resolución/normalización, rechazo de SQL e instrucciones financieras, tamaño/tipos, fechas y campos/filtros desconocidos; dos pruebas ORM/API verifican consulta real al reporte, ausencia de asientos nuevos, empresa titular, rechazo de otro usuario/vínculo revocado y Tenant spoofing.

Evidencia: `evidencias/implementacion-38.json`, fuente estable. Runner y workflow incluyen la suite. No se ejecutó CI remoto. No se repitió PostgreSQL porque no cambiaron esquema, bloqueos o persistencia. No se probó todavía el recorrido de navegador de esta ruta nueva.

## Pendientes

Interfaz y sesión real del nuevo flujo, más preguntas/fuentes y sus límites, modelo privado/local evaluado si se habilita comprensión abierta, voz y accesibilidad, pruebas adversariales ampliadas, límites de ingreso/concurrencia del servidor y rendimiento. La longitud del campo se valida después del parser; no acredita un límite de bytes de ingreso. Faltan roles profesionales/delegados y consola corporativa Analemática. Un vocabulario determinista no cumple por sí solo todo Neuro-Assist ni prueba precisión de IA.

Sin datos del usuario modificados, commit, push o despliegue.
