# Seguridad y recursos de IA para SGA-CD

Se incorporan archivos reales de ambos proyectos, sin submódulos ni dependencia de enlaces para conservar el código:

| Copia | Revisión fijada | Licencia |
|---|---|---|
| `SEGURIDAD/AiSOC` | `010a3981bfc791266d62aaa31531f05798531efd` | MIT; conservar copyright, licencia y avisos; respetar `TRADEMARK.md`. |
| `llm/free-ai-apis` | `0c78ad5ccc6a2658e434e465c53fa2bea83605b7` | CC0-1.0, según su archivo LICENSE. |

Los manifiestos `*-upstream.json` registran cada archivo, blob Git, modo y SHA-256. Las copias mantienen todos los archivos versionados, incluso documentación, tests, reglas y ruedas de dependencias presentes en AiSOC. No se instalaron esas ruedas: varias son para macOS y no corresponden a este host Linux. Las carpetas `.git` de origen no se copiaron. Copiar permite mantener nuestra distribución y adaptar el código bajo sus licencias; no transfiere autoría ni acceso a las API listadas.

## Qué incorporamos al sistema

El panel `/resources.html`, enlazado desde el control y las guías, usa el JWT central y roles administrativos activos. Se publica bajo el origen de Analemática y SGA-CD; no almacena claves de proveedores en el navegador.

- Catálogo consultable de **102 entradas en 15 categorías**, compilado de la copia de `free-ai-apis`, con búsqueda y filtro de opciones locales. Son entradas por categoría, no 102 empresas distintas ni 102 API operativas verificadas.
- Estado explícito del SOC: copia presente, despliegue no verificado, transporte manual, respuesta automática deshabilitada. No inventa alertas o métricas.
- Exportación explícita de hasta 100 metadatos de autorizaciones propias por bloque, filtrados por usuario **y** tenant, firmados con la clave Ed25519 del motor existente. No transmite automáticamente a AiSOC.
- Verificador/extractor local `audit_bundle.py`: exige una clave pública confiada por separado y el tenant de origen esperado; rechaza alteraciones. El archivo resultante coincide con la forma de la solicitud de ingestión documentada por AiSOC, pero no se ha validado contra un SOC en ejecución.

Rutas bajo `/api/v1/assistance/resources`:

| GET | Comportamiento |
|---|---|
| `/providers?category=video&q=replicate&local_only=false` | Descubrimiento offline; no llama a proveedores. |
| `/security/status` | Alcance y estado no verificado de la integración. |
| `/security/control-audit-export?after_id=0&limit=100` | Descarga firmada, paginada, privada y sin contenido de las órdenes. |

Los tres endpoints llevan `Cache-Control: no-store`. No hay una ruta para activar proveedores, gastar créditos, ordenar respuestas SOC o saltarse las autorizaciones del motor.

## Para qué sirve AiSOC en nuestra arquitectura

| Área | Beneficio posible al conectar telemetría real | Estado en esta entrega |
|---|---|---|
| Motor de control de equipos | Revisar quién autorizó, qué clase de operación, qué plataforma y cuántas etapas. | Exportación de autorizaciones preparada. No registra todavía todos los rechazos de autorización ni eventos del SO. |
| Backends y cuentas administrativas | Correlacionar accesos anómalos, errores de autenticación, cambios de privilegios y actividad sospechosa. | Requiere instrumentar y configurar fuentes de esos eventos; no cubierto por la exportación actual. |
| Infraestructura Docker/servidores | Centralizar registros de hosts, nube, red y bases de datos mediante colectores. | Código upstream disponible; fuentes y credenciales no conectadas. |
| Investigación y soporte | Triage local con LLM y registros de las decisiones para revisar incidentes. | Necesita desplegar el pipeline y el modelo; no iniciado aquí. |
| Auditoría | Usar el Investigation Ledger y los paquetes de evidencia firmados upstream. | Existe el código. Nuestra exportación firmada no sustituye ese ledger ni demuestra que AiSOC haya recibido un evento. |

Las autorizaciones normales se exportan como `info`, sin etiquetarlas como ataques. Para detectar abusos específicos de SGA-CD harán falta reglas y validación sobre sus campos; no afirmamos que las reglas genéricas de AiSOC ya reconozcan esas situaciones.

El ledger upstream ofrece evidencia de alteraciones mediante cadenas y firmas; no vuelve físicamente inmutable cualquier base de datos frente a su administrador. La verificación requiere proteger las claves y establecer una referencia de confianza independiente. Nuestra firma protege la integridad del archivo desde la exportación, no certifica que nadie modificara antes los datos fuente.

El SOC se mantiene como despliegue separado del backend transaccional: sus almacenes, secretos y recursos no deben mezclarse con las bases de SGA-CD. Sus respuestas no se conectaron al ejecutor de escritorio/móvil. Cualquier integración futura que ordene acciones al motor debe pasar por las dos autorizaciones del administrador solicitante y la confirmación de impacto cuando corresponda.

## Para qué sirve el catálogo de API

| Función del sistema | Candidatos que el directorio permite investigar | Qué falta para habilitarla |
|---|---|---|
| Creatividades publicitarias e imágenes | Replicate/FLUX, Stability AI, Leonardo, opciones locales. | Revisar términos, modelos, cuotas, uso comercial y tratamiento de datos; implementar/probar el adaptador. |
| Reels y vídeo | Categoría `video`, incluidos Replicate, Kling y modelos alojados. | Validar disponibilidad API y facturación; trabajos asíncronos, límites de duración/tamaño y revisión humana. |
| Guiones y asistencia | Categoría `text`, Ollama, Gemini, Groq y otros. | Seleccionar por tarea, calidad medida, privacidad y coste; configurar el router existente. |
| Subtítulos y voz | `transcription`, `speech` y `translation`. | Conectar un proveedor autorizado o modelo local y validar idiomas/calidad. |
| Búsqueda documental y análisis | `embeddings`, `search`, `vision`, `extraction`, `moderation`. | Validar permisos de documentos y aislamiento por tenant antes de enviar datos. |

`free-ai-apis` es documentación, no un SDK, una clave de API o un servicio de renderizado. Todas sus cuotas se conservan como **afirmaciones no verificadas de la fuente** (`terms_verified=false`, `provider_enabled=false`, `zero_cost_guaranteed=false`). No repetimos como garantía que un proveedor entregue créditos, no requiera tarjeta o permita uso ilimitado. Una oferta de la web comercial puede diferir de su API. Los modelos locales consumen hardware, memoria y energía.

El catálogo no reemplaza ni modifica silenciosamente `app/services/ai_router.py`. Antes de registrar un proveedor real: comprobar su documentación vigente, elegir modelos concretos, guardar secretos fuera de Git y del frontend, probar coste/privacidad y mantener la autorización de publicación/gasto. No se ejecutó el ejemplo Replicate ni se usó el token compartido en la conversación; debe revocarse y sustituirse fuera de Git.

## Despliegue AiSOC pendiente

La documentación upstream indica para CORE unos **16 servicios, 8 GiB RAM y 20 GiB de disco libres**, más la descarga del modelo local. No iniciamos el stack: este entorno tiene menos de 1 GiB libre. La existencia de código no constituye protección activa y los números upstream no son mediciones realizadas en nuestros servidores.

En un host de pruebas dedicado con capacidad suficiente, revisar primero `SEGURIDAD/AiSOC/AGENTS.md`, `README.md`, `SECURITY.md`, `.env.example` y la guía de instalación. Luego usar los comandos upstream (`make up`, `make doctor`, `make smoke`) con su aislamiento y secretos generados. No compartir el secreto de sesión, usuarios o bases transaccionales de SGA-CD con el SOC. No publicar bases, Kafka, Ollama o MCP sin una configuración de acceso revisada. El Compose upstream enlaza los puertos al loopback de forma predeterminada.

Antes de enviar una exportación, establecer el mapeo del tenant SGA-CD al tenant AiSOC y generar una credencial de ingestión específica de destino. El tenant receptor lo determina la credencial AiSOC, no el número incluido en nuestra firma. Una firma de origen válida no autoriza a enviar a cualquier tenant. No se suministró una credencial ni se habilitó un emisor automático.

## Verificación y uso local

```bash
python INTEGRACIONES/seguridad-ia/verify_vendor.py
python INTEGRACIONES/seguridad-ia/sync_catalog.py --check
PYTHONPATH=BACKEND/SGA-CD-BACKEND python -m unittest discover -s BACKEND/SGA-CD-BACKEND/tests -p test_resources.py -v
```

Verificar una descarga usando la clave pública Ed25519 del servidor obtenida por un canal confiable, no simplemente la que viene dentro del archivo:

```bash
python INTEGRACIONES/seguridad-ia/audit_bundle.py --bundle exportacion.json --trusted-key clave-publica-servidor.pem --source-tenant 123 --output ingest-batch.json
```

No sobrescribe archivos existentes y no transmite nada. Guardar el archivo de auditoría con acceso privado; la clave privada del servidor nunca se exporta.

El catálogo se regenera con `sync_catalog.py` después de actualizar deliberadamente la copia upstream y su manifiesto. El verificador exige igualdad de archivos y hashes: no modificar las copias originales para ocultar diferencias. Las personalizaciones de integración permanecen fuera de ellas.
