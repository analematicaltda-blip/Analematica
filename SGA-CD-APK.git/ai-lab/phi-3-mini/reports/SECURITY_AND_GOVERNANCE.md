# SGA-CD — Arquitectura de Seguridad y Gobernanza de Asistente IA Local

## 1. Contexto y Objetivos
En una eventual integración de Phi-3 Mini (o modelos SLM equivalentes) dentro de las aplicaciones cliente (APK Android, Desktop) o backend de SGA-CD, el modelo actuará como una interfaz de asistencia en lenguaje natural sin capacidades directas de ejecución autónoma de acciones sensibles.

---

## 2. Principios Fundamentales de Seguridad

### A. Principio de Mínimo Privilegio y Aislamiento Multiinquilino (`inquilino_id`)
1. **Verificación de Identidad**: El modelo local nunca almacena ni determina los permisos del usuario. Todos los datos de contexto inyectados al prompt se obtienen a través de peticiones autorizadas con JWT emitido por la API REST de SGA-CD.
2. **Filtrado Múltiple por Inquilino**: Toda la información expuesta al asistente se filtra estrictamente por el `inquilino_id` y el rol activo del usuario (`profesor`, `coordinador`, `alumno`, `admin_empresa`, etc.).
3. **Imposibilidad de Auto-Concesión de Permisos**: Las respuestas generadas por el modelo no tienen el poder de alterar roles, omitir tokens JWT o ejecutar operaciones de escritura en la base de datos sin autorización previa.

### B. Validación de Operaciones Sensibles (Human-in-the-Loop)
1. **Acciones de Lectura / Consulta**: El asistente responderá preguntas frecuentes, procedimientos informativos o resúmenes de datos pre-filtrados.
2. **Acciones de Escritura / Modificación**: Ninguna acción (e.g. registrar calificación, aprobar currículo, reservar espacio) se ejecuta automáticamente desde el texto generado. El asistente presentará una tarjeta de acción con un botón de confirmación explícita que dispara la llamada API autorizada con token del usuario.

### C. Desacoplamiento Offline vs. Online
1. **Modo Sin Conexión (Offline)**: El modelo responde utilizando únicamente la base de conocimiento local empaquetada (guías institucionales, manual de rol, preguntas frecuentes estáticas). No intentará contactar con servidores externos ni enviar datos del dispositivo a la nube.
2. **Modo Conectado (Online)**: Para consultas en tiempo real (e.g., disponibilidades de horarios de escenarios, estado de cuotas de inventario), el cliente Flet consulta primero a la API REST de SGA-CD y luego le pasa la respuesta estructurada en JSON como contexto al modelo local para su formateo.

### D. Descargo de Responsabilidad Oficial (Información No Vinculante)
1. **Respuestas Informativas**: Toda respuesta emitida por el modelo en el cliente local incluye una marca visual de "Asistente IA - Sugerencia No Oficial".
2. **Información Oficial**: Los trámites oficiales, calificaciones definitivas y ratificaciones administrativas requieren el flujo estándar en las vistas correspondientes de la aplicación.
