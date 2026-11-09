# Implementación 42 · Recepción JSON acotada de consultas

**Avance: 38,89 % (28/72 hitos).** Refuerza ACC-020, ya puntuado; no acredita otro hito.

## Implementación

`AccountingQueryJSONParser` se aplica exclusivamente a la acción consulta-contable. Lee como máximo 8193 bytes y rechaza cuerpos mayores de 8192 antes de decodificar el JSON. Exige UTF-8 y objeto raíz; rechaza claves duplicadas incluso anidadas, constantes no estándar NaN/Infinity y JSON inválido sin reflejar contenido del usuario en errores.

Antes de json.loads, un escáner iterativo limita la anidación a ocho niveles respetando cadenas y escapes. Las primeras pruebas mostraron que depender de RecursionError era insuficiente porque el límite de recursión varía entre runtimes. El límite explícito ya no depende de esa configuración. La validación posterior del contrato sigue permitiendo solo preguntas/fechas soportadas.

No modifica parsers globales, formularios u otras rutas. Los errores controlados conservan las cabeceras de privacidad. El parser de la acción se configura mediante el router DRF; los tests directos as_view pasan expresamente esa configuración para reproducir el comportamiento real.

## Verificación final

178 métodos Python aprobados en doce suites, incluyendo siete pruebas del parser y una API adicional. Cubren lectura única acotada, frontera exacta de bytes, UTF-8, duplicados, constantes, raíz inválida, profundidad excesiva y delimitadores/escapes dentro de cadenas. Los cuerpos rechazados por el parser no alcanzan el despacho de herramientas.

33 comprobaciones integradas de Chromium con sesión/cookie/CSRF y Django aislado aprobadas. La nueva envía duplicados, NaN y un cuerpo excesivo a la ruta real; exige 400 y comprueba mensajes específicos del parser. Las consultas legítimas y paneles existentes siguen funcionando. Las 14 pruebas del verificador local también pasaron.

Evidencia: `evidencias/implementacion-42.json`. Fuente estable durante el perfil contable; sin cambios de esquema o bloqueo, no se repitió PostgreSQL.

## Pendientes

El límite protege la lectura de este parser, no prueba que proxy, servidor o middleware anteriores jamás hayan almacenado el cuerpo. Faltan límites de ingreso y concurrencia de infraestructura, rate limiting validado, carga/latencia y revisión de los demás endpoints. Una petición de menos de 8 KiB no implica bajo coste del reporte: permanecen pendientes optimización de consultas y límites operativos bajo carga.

No completa lenguaje abierto, voz, dispositivos reales ni la consola corporativa Analemática. Sin datos del usuario modificados, commit, push o despliegue.
