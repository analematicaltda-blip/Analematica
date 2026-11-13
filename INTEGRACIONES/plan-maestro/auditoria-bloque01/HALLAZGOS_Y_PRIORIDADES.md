# Hallazgos y orden de trabajo del bloque 1

**Estado comercial actual:** [GC-001 completada · 1/24 tareas y 3/72 hitos acreditados](#cierre-gc001).

**Análisis vigente de los tres módulos comerciales, CRM, agentes y multimedia:** [abrir evaluación del 11 de noviembre de 2026](#gestion-comercial). Los hallazgos iniciales B01 se conservan como historia.

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

<!-- COMMERCIAL_HOMOLOGATION_START -->

<a id="gestion-comercial"></a>

## Análisis vigente: gestión comercial, CRM, agentes y multimedia de SGA-CD, ERP turístico y Analemática

Fecha: **11 de noviembre de 2026, Colombia**. Base del código comercial: commit `363f4120ad97be5d86232ba1cb6218b8f4011d53`. El checkout incorpora además la reubicación local de billetera por capas. Los módulos comerciales no se movieron, fusionaron ni modificaron para realizar este análisis. Los hallazgos B01 anteriores son históricos: no deben confundirse con este diagnóstico actualizado.

**Conclusión:** existen funciones útiles y comprobables, pero los tres módulos todavía no tienen paridad. SGA-CD aporta CRM, permisos y campañas; el ERP aporta clientes, cotizaciones y controles de operación/devolución; Analemática aporta captación corporativa, administración del propietario y gobierno del ecosistema. Ninguno acredita por sí solo el ciclo completo, homogéneo y productivo de CRM → contenido → publicación/respuesta → venta → cobro → contabilidad.

La homologación debe igualar **capacidades, reglas, contratos y experiencia**, conservando los módulos y datos propios de cada sistema. No significa unificar carpetas ni otorgar a Analemática acceso automático a la información privada de las empresas.

### 1. Alcance y significado de las evidencias

Se revisaron fuentes, rutas, modelos, consumidores frontend, agentes y pruebas existentes. Se ejecutaron pruebas seleccionadas con datos desechables; los resultados se detallan al final. La existencia de una clase, botón o adaptador no acredita una función operativa.

- **Verificada local:** existe evidencia ejecutada para los casos especificados; no equivale a aceptación productiva o de proveedor.
- **Parcial:** existe implementación, pero faltan partes del recorrido o validación.
- **Bloqueada:** la ruta rechaza una operación deliberadamente antes de aparentar una venta, pago o factura.
- **Plantilla/maqueta:** devuelve datos fijos, mensajes de éxito o estructuras sin ejecutar el negocio anunciado.
- **No verificada:** se encontró código, pero no se comprobó su recorrido completo en esta evaluación.

No se calcula un porcentaje comercial global: todavía no existe una matriz de aceptación común aprobada para los tres módulos. El indicador de 72 hitos contables mide otro alcance y no sirve para certificar marketing, CRM o redes sociales.

### 2. Cómo está constituido cada sistema

| Sistema | Backend y datos observados | Frontend observado | Dependencias y límite actual |
|---|---|---|---|
| SGA-CD | `BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints/workspace.py`, modelos `workspace.py`, servicios `workspace_service.py` y campañas. FastAPI + SQLAlchemy. | `FRONTEND/SGA-CD-WEB.git/js/workspace.js`, `campaigns.js`, vistas administrativas y páginas de checkout. | Hay CRM persistente con alcance empresarial y permisos. El estudio usa un servicio separado `BACKEND/infra/node6`; algunas herramientas comerciales heredadas son plantillas. |
| ERP turístico | `BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/`: clientes, cotizaciones, disponibilidad, cancelaciones, facturas, marketing, funnels, IA y automatización. Django/DRF. | `FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-comercial/`: panel, clientes, productos, ventas, facturas, cotizaciones, políticas y componentes multimedia. | Parte de los modelos se importa desde `apps.domain_business.comercial`, físicamente en el backend turístico heredado; usa también `core_erp` de Analemática. Tener carpetas separadas no implica independencia de todos los dominios. |
| Analemática | `BACKEND/ANALEMATICA-BACKEND/`: gateway, módulos administrativos, núcleo contable y agentes. El canal corporativo probado está implementado en `BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints/corporate.py` y usa `WorkspaceLead` con alcance `platform`. | `FRONTEND/ANALEMATICA-FRONTEND/`: landing, consola, contenido y pestaña comercial. | La captación corporativa tiene implementación real, pero depende del backend/base de SGA-CD en el despliegue gateway. La ruta Django `comercial/` apunta a un módulo compartido cuyo `urlpatterns` está vacío. El ejército contable nativo no sustituye un CRM comercial propio completo. |

**Distinción importante:** `BACKEND/ANALEMATICA-BACKEND/integrated_server.py` es otro servidor presente en el repositorio, con almacenamiento JSON e imports históricos. No se presume que sea el despliegue activo. El gateway y `deployment/start.py` muestran otra vía de ejecución, hacia el backend existente. No se deben mezclar sus garantías ni tratar ambos como equivalentes.

SGA-TUR nacional sigue siendo institucional. Se menciona únicamente por dependencias físicas heredadas; no es el cuarto ERP ni el objeto comercial de esta comparación.

### 3. Fortalezas y debilidades por sistema

**SGA-CD**

Fortalezas:

- CRM persistente: crear, listar y editar contactos, con estados `nuevo`, `contactado`, `propuesta`, `ganado`, `cerrado`.
- Autorización desde identidad de base, plan y permisos delegados; las pruebas comprueban aislamiento, revocación y bloqueo de rutas heredadas.
- Campañas con audiencia autorizada, baja, programación, cola, cuotas, variantes multimedia y estados por destino.
- Servicio Node 6 con render local de Reels y adaptación real de MP4; conserva el original.

Debilidades:

- El CRM básico no acredita un modelo completo de oportunidad con valor, moneda, probabilidad, responsable, tareas, siguiente contacto, motivo de pérdida y conversión contable.
- `herramientas_crm_completo.py` contiene **90 funciones de retorno de texto**, sin persistencia ni integración dentro de esas funciones. Esto no invalida el CRM real de `workspace.py`; son implementaciones distintas.
- La división heredada `ventas_crm_colonel.py` encadena algunas de esas herramientas y compila un mensaje de misión exitosa. Ese resultado no demuestra una captación o cotización ejecutada.
- Coexisten Bold y rutas de otros proveedores; el checkout no acredita por sí solo confirmación del pago, suscripción activada o asiento contable.
- Hay métricas fijas en una vista administrativa heredada y falta demostrar su reemplazo completo por fuentes reales.

**ERP de empresas turísticas**

Fortalezas:

- Clientes propios por empresa, controles de identidad empresarial y rechazo de acceso cruzado.
- Cotizaciones con precios del servidor, validación de cantidades y moneda, instantáneas, digest, caducidad e idempotencia.
- Disponibilidad y reservas temporales de capacidad verificadas para sus casos actuales. **Esto no equivale al RAT integral**, que sigue siendo un proyecto separado.
- Políticas de cancelación por versión, aceptación y días de anticipación, con pruebas de retención, límites, permisos y reintentos.
- Controles que mantienen bloqueadas operaciones/POS y emisión fiscal sin contrato probado, en vez de fabricar un resultado exitoso.

Debilidades:

- La venta/POS general permanece bloqueada; una cotización guardada no es una venta confirmada.
- Consumidores frontend solicitan `facturas-venta/` y `operaciones-comerciales/`, mientras el router revisado registra `facturas/` y `operaciones/`. Es una inconsistencia estática pendiente de resolver por contrato; no se afirma que se haya probado un 404 en cada variante de despliegue.
- Hay varios modelos/namespaces de identidad, archivos `models.py` y paquete `models/`, servicios comerciales alternativos y un `main_config` distinto. Deben identificarse consumidores activos antes de reutilizar o retirar código.
- Hay componentes con datos mock, rutas de IA de otro perfil de arranque e imports absolutos como `infrastructure` o `sales`; su integración al backend principal no está acreditada.
- Existen funciones heredadas de validación de precio que devuelven siempre `True`, y ramas de servicios que usan nombres no importados. No se deben habilitar por copiar una interfaz.

**Analemática**

Fortalezas:

- Landing corporativa y captación con validación, consentimiento obligatorio, identificador repetible, trampa antispam y asignación al alcance de plataforma.
- Administración restringida al propietario, publicación de contenido con revisión de versión y rechazo de datos sensibles en contenido público.
- Consola de consultas/órdenes permitidas y gobierno central; existen puentes contables y generales nativos con validación de empresa.
- Las fuentes de Jarvi, Neko y SOUP están centralizadas en su backend conforme a la directriz del usuario.

Debilidades:

- No se identificó en su backend una carpeta comercial propia equivalente a `gestion_comercial` del ERP con todo el CRM, campañas, cotizaciones, ventas y posventa.
- La implementación comercial efectiva de la landing está en SGA-CD; su identidad corporativa y el servicio que la ejecuta no son todavía la misma unidad física de módulo.
- `urls.py` deriva `comercial/` a rutas compartidas vacías. El contrato `CommercialContract` contiene DTOs de plan/suscripción y una interfaz `pass`, no un catálogo completo de operaciones comerciales.
- El panel muestra inicialmente cifras como `142`, `94.2%` y CAC/LTV fijos. Algunas actualizaciones usan comprobaciones de valor verdadero, que pueden dejar una cifra anterior cuando el valor real es cero.
- Las unidades comerciales `AgentUnit.execute()` revisadas devuelven estructura de éxito con el payload; eso no acredita campaña enviada, CRM actualizado ni métrica calculada.

### 4. CRM: base común que falta homologar

| Capacidad | SGA-CD | ERP turístico | Analemática |
|---|---|---|---|
| Captación persistente y acceso propio | Verificada en el CRM de workspace | Clientes verificados; prospecto y oportunidad no son la misma entidad | Captación corporativa verificada en el alcance plataforma |
| Embudo básico | Estados básicos persistentes | Modelos/componentes declarados; pipeline completo no verificado | Resumen por etapa y contactos corporativos; ciclo comercial completo parcial |
| Historial, tareas y seguimiento | Notas disponibles; cronología y agenda completas no acreditadas | Parcial/no verificado para oportunidad | Parcial/no verificado |
| Consentimiento y bajas | Audiencia de campañas implementada | No acreditada una política omnicanal equivalente | Consentimiento en captación; no equivale a autorizar todos los canales |
| Catálogo/precio/cotización | Planes y catálogos presentes; cotización comercial completa no acreditada | Cotización del servidor y borrador verificados | Planes/DTOs y puentes; paridad no acreditada |
| Conversión a venta, pago y asiento | No acreditada integralmente desde el CRM | POS/operación general bloqueados; otros flujos contables tienen controles específicos | No acreditada integralmente desde captación corporativa |
| Posventa, devolución y fidelización | Componentes/servicios específicos; paridad CRM no acreditada | Políticas y reembolso financiado tienen controles comprobados para su alcance | Puentes existentes; integración completa al CRM pendiente |

Modelo objetivo común: contacto/prospecto, empresa, consentimiento por finalidad/canal, oportunidad, etapa y motivo, responsable, tareas/actividad, oferta/cotización versionada, aceptación, venta, referencia de cobro, referencia de asiento, devolución, posventa y evidencias. Cada registro debe conservar `system_id`, empresa, actor, origen, fecha y versión. No se equiparan identificadores de bases distintas por coincidencia numérica.

### 5. Motor multimedia: creación y cambio de tamaños

El servicio existente más concreto es **`BACKEND/infra/node6`**. Se conecta desde SGA-CD mediante `workspace_service.worker()` y autenticación interna. No se verificó que los tres módulos comerciales consuman de manera equivalente ese servicio.

| Función solicitada | Evidencia existente | Límite y siguiente criterio |
|---|---|---|
| Guiones/textos | Node 6 y borradores editoriales; adaptadores a modelos configurados | Separar texto generado de mensaje enviado; medir calidad/coste con proveedor autorizado |
| Crear imágenes | `Engine.image()` valida respuesta PNG/JPEG, tamaño y píxeles; guarda PNG | Pruebas de contrato no son inferencia real del modelo; completar perfiles de salida y trazabilidad de derechos |
| Crear videos/Reels | `Engine.reel()` compone imagen/texto y renderiza MP4 1080×1920 con FFmpeg | Declara `ai_video=False`: no es evidencia de video generativo cinematográfico o avatar con voz |
| Adaptar videos/Reels | `adaptation.py`: FFprobe + escala proporcional y bandas; genera variante por plataforma | Solo MP4 en ese adaptador; no hay acreditación de editor universal, recorte inteligente o cambio automático de toda clase de activo |
| Cambiar tamaño de imágenes | Existe conversión de imagen y ajuste de fondo para Reel | No se identificó un servicio común completo de exportación de imágenes por red y tamaño a disposición de los tres módulos |
| Biblioteca de activos | `WorkspaceAsset`, archivos privados y variantes por campaña | Homologar versiones, propietario, formato, metadatos, derechos, cuotas y caducidad en los tres módulos |

Perfiles internos actuales del adaptador de video: Instagram/TikTok/YouTube 1080×1920, Facebook 1080×1080, X/Gmail 1280×720, WhatsApp 480×854. Tienen límites locales de duración/peso. **Son configuraciones del proyecto, no certificación de las especificaciones vigentes de cada red.** Deben versionarse y validarse por tipo de publicación, especialmente anuncios, Stories, Reels, Shorts e imágenes.

La plantilla actual de Reel incorpora marca y texto de SGA-CD. Para homologar se necesitan plantillas de marca por sistema/empresa; no debe publicarse un anuncio de una empresa turística con marca SGA-CD por defecto.

### 6. Publicación, mensajes y Meta Ads: capacidades distintas

La cola de campañas declara adaptadores de salida para YouTube, Instagram, Facebook, WhatsApp, X, TikTok y Gmail. Su presencia no acredita aprobación OAuth ni envío real. Los controles permiten deshabilitar entregas y diferencian resultados inciertos para evitar reintentos ciegos.

| Canal | Qué se encontró | Qué falta acreditar para la solicitud del usuario |
|---|---|---|
| Meta: Facebook/Instagram | Adaptadores de publicación de video/Reels; vinculación y webhooks firmados para activos configurados | Bandeja por empresa, correlación de conversación/comentario con lead, lectura y respuesta con permisos y ventanas del producto aplicable |
| Meta Ads | Consultas de cuentas, campañas e insights; borradores y configuración; no se presume compra de pauta | Un anuncio, un comentario del anuncio y un mensaje de Messenger/Instagram son objetos diferentes. Crear/editar/gastar presupuesto y responder deben tener contratos separados |
| Gmail | Salida de campañas por destinatario, consentimiento y baja | Leer correo, conservar `threadId`, correlacionar contacto y responder al hilo no están acreditados por el envío de una campaña |
| YouTube | Subida y seguimiento de publicación; el canal de workspace enfatiza publicación privada | Publicación según permisos reales y gestión de comentarios/respuestas. No tratar YouTube como una bandeja genérica de mensajes privados |
| TikTok | Adaptador de publicación, opciones de privacidad y seguimiento de estado | Calificación de aplicación/cuenta y alcance de comentarios/mensajería realmente disponible; no prometer acceso universal a DMs |
| WhatsApp | Plantillas/salida de campañas y recepción firmada declarada en Meta | Conversaciones empresariales, consentimiento, asignación y respuestas sujetas al producto/permisos aplicables |

**Hallazgo comprobado:** `/workspace/inbox/status` declara `automatic_replies=False` y explica que la bandeja requiere autorizaciones/webhooks propios. El receptor Meta almacena eventos firmados con alcance `platform`, sin inferir enrutamiento hacia empresas y sin emitir respuesta. **Recibir un webhook no significa tener atención omnicanal operativa.**

Se debe definir una matriz por proveedor con: activo/cuenta autorizados, publicación soportada, recepción soportada, respuesta soportada, alcance OAuth, vencimiento/revocación, aprobación humana, comprobante remoto y límites. Una capacidad no autorizada debe mostrarse como pendiente, no sustituirse silenciosamente por automatización de navegador.

### 7. Agentes integrados: funciones reales y límites

**Cadena establecida por el usuario:** Neko es el General conversacional; Jarvi es el General operativo; SOUP es el General optimizador de procesos. Después vienen Coronel → Capitán → Teniente → Sargento → Soldado. El agente de voz fluida es una función separada; su nombre/proveedor no quedó identificado y no se acredita su implementación por admitir transcripciones.

| Estructura | Función real observada | Fortaleza | Límite que debe quedar visible |
|---|---|---|---|
| SGA-CD: estado mayor compatible y `ventas_crm_colonel.py` | Clasificación/delegación y un grafo comercial que invoca herramientas | Hay una cadena y puntos de entrada reutilizables como diseño | El grafo comercial heredado usa herramientas que retornan texto y datos fijos; una misión exitosa no demuestra cambios en CRM |
| Analemática: generales, proyectos completos y división `comercial_general` | Fuentes centralizadas; consola con operaciones permitidas; unidades de división y automatización de formularios | Puede gobernar contratos, catálogo y trazabilidad del ecosistema | Las unidades `AgentUnit` y textos prefijados no son conectores reales ni autorización de publicación |
| Ejércitos contables nativos de Analemática y ERP | 29 nodos lógicos por backend; misiones acotadas y consulta real de balance, integridad, cola comercial, rentabilidad y liquidez | Autoridad empresarial revalidada, auditoría, idempotencia, resultados y evaluación por SOUP | Son consultas/diagnósticos. No son un ejército comercial completo de campañas, atención, cobros ni 29 procesos de IA autónomos |
| ERP: sargentos y servicios comerciales/IA heredados | Hay métodos, tareas y adaptadores de proveedores; algunos rechazan falta de proveedor | Puntos de extensión propios del dominio | `validar_precio()` devuelve siempre `True`; hay imports y perfiles alternativos. No habilitar esta rama como control de precio real |
| Open Duet + agent-desktop | Contratos/acoplamientos limitados y configuración separada | Permite planificación/control con permisos delimitados | La prueba de un protocolo simulado o una sonda de estado no acredita modelo local activo, voz fluida ni control del equipo del cliente |

Neko debe entender y preparar la intención; Jarvi debe comprobar actor, empresa, permiso y estado antes de despachar. Los soldados deben invocar las mismas APIs de dominio que usa la interfaz y devolver evidencias, no frases de éxito. SOUP debe medir errores, tiempos, calidad y coste y proponer cambios; no puede modificar reglas, entrenar/activar candidatos, publicar, enviar ni pagar por su cuenta.

Para CRM, contenido y atención, cada misión debe identificar empresa, contacto/campaña/activo, finalidad, destino autorizado, versión/digest, aprobaciones, herramienta y resultado remoto. La transcripción de voz, la decisión del modelo o la orden de otro agente no reemplazan una aprobación humana o firma financiera requerida.

### 8. Hallazgos prioritarios para el futuro pool

| ID | Prioridad | Hallazgo y evidencia | Criterio de subsanación |
|---|---|---|---|
| COM-01 | Alta | Dependencias cruzadas: gateway corporativo en SGA-CD y modelos comerciales del ERP en dominio heredado. `deployment/api.py`, `domain/models.py`, `tourism_bindings.py` | Cada módulo expone su contrato propio y límites de datos; dependencias explícitas. No mover carpetas para aparentar independencia |
| COM-02 | Alta | 90 herramientas CRM de retorno textual y grafo que compila éxito. `herramientas_crm_completo.py`, `ventas_crm_colonel.py` | Cada herramienta habilitada debe demostrar escritura/lectura autorizada o declararse no operativa; pruebas de rechazo y reintento |
| COM-03 | Alta | Inconsistencia de rutas de facturas/oportunidades entre consumidores y router ERP | Contratos ejecutados desde cada pantalla hasta su endpoint real; pruebas de lectura, permiso, error y paginación |
| COM-04 | Alta | La paridad de embudo/seguimiento y consentimiento no está definida | Mismo contrato de oportunidad y consentimiento en los tres, con extensiones de sector y sin intercambio implícito de datos |
| COM-05 | Alta | Cifras fijas y datos mock en paneles; actualización condicional puede ignorar ceros | Métricas con fuente, fecha/corte y estado sin datos; cero correcto; ninguna cifra de demostración presentada como real |
| COM-06 | Alta | El adaptador Bold devuelve estructura `success` ante error de transporte: reproducido aisladamente | Diferenciar enlace propuesto/creado, error e incertidumbre; referencia única; confirmación auténtica e idempotente antes de dinero/asiento |
| COM-07 | Alta | POS/operación y DIAN mantienen bloqueos; no hay cierre de ciclo completo de CRM | Aceptación comercial, cotización, pago y contabilidad ligados; fiscalidad explícita. No retirar bloqueos sin pruebas |
| COM-08 | Alta | Redimensionamiento es de MP4 y ajuste de fondo, no servicio completo de todo formato | Perfiles versionados para imágenes y video; preview, calidad, peso, audio/subtítulos y original conservado |
| COM-09 | Alta | Recepción firmada Meta no es bandeja ni respuesta; Gmail/YouTube/TikTok carecen de paridad acreditada de atención | Enrutamiento por empresa/contacto, lectura y respuesta por capacidad autorizada, revisión y recibo real |
| COM-10 | Alta | Video FFmpeg se puede confundir con video generativo; proveedores no cualificados | UI y API distinguen composición, inferencia y maqueta; calidad/coste/privacidad evaluados |
| COM-11 | Alta | Plantillas de marca SGA-CD y comportamiento de agentes no homologados | Marca por sistema/empresa, API real por soldado y cadena de autoridad comprobable |
| COM-12 | Media/alta | Builds, identidades, paquetes y perfiles de arranque alternativos no tienen aceptación comercial integral | Instalación y recorrido repetibles por sistema, matriz de permisos y pruebas de contrato visual/API |

Los hallazgos son de implementación/estructura y cobertura observada. No se presenta una vulnerabilidad explotada ni una caída productiva sin haberla reproducido.

### 9. Pool propuesto para homologar sin fusionar carpetas

Es una propuesta de implementación posterior; este análisis no ejecuta ni da por terminado el pool.

| Tarea | Frente/responsable funcional | Entregable común en los tres sistemas | Aceptación verificable |
|---|---|---|---|
| C01 | Arquitectura y contratos | Diccionario, estados, OpenAPI/eventos, permisos y matriz de capacidades por sistema | Mismo juego de contratos responde en cada backend; cada carpeta y dueño se conservan |
| C02 | CRM y privacidad | Prospectos, clientes, oportunidades, responsable, historial, tareas, consentimiento y bajas | Crear/seguir/cerrar sin perder historia; rechazar otra empresa; baja bloquea envíos |
| C03 | Comercial | Catálogos, precios, descuentos aprobados y cotizaciones versionadas | Totales del servidor, moneda/impuestos explícitos, caducidad y reintento seguro |
| C04 | Ventas y ledger | Aceptación → venta → cobro/pendiente → asiento y reversión | Cero doble venta/cobro/asiento; estados no se confunden; no omitir autorizaciones |
| C05 | Pagos y posventa | Bold cualificado, políticas por anticipación, devolución, billetera y seguimiento | Error/incertidumbre visibles; fondos/consentimiento y firmas; comprobantes legítimos |
| C06 | Activos y marca | Biblioteca privada de originales, variantes, derechos y plantillas por sistema/empresa | Acceso propio, metadatos/hashes, conservación del original y separación de marcas |
| C07 | IA de imágenes/texto | Adaptadores configurables, tareas, revisión y coste por activo | Diferenciar generación real de maqueta; sin exponer credenciales en frontend |
| C08 | Video y Reels | Render, títulos, audio/subtítulos y proveedores generativos separados | MP4 reproducible; calidad verificada; composición identificada como tal |
| C09 | Adaptación multimedia | Tamaños/aspectos para imágenes y video por destino y tipo de publicación | Perfil validado, preview, duración/peso/calidad y política de recorte explícitos |
| C10 | Publicación | Calendario, revisiones, cola, destinos, recibos y recuperación | No publicar al guardar; reintento no duplica; una cuenta no usa activos ajenos |
| C11 | Atención omnicanal | Bandeja por empresa y contacto: Meta, Gmail, YouTube y TikTok según capacidad autorizada | Evento firmado/auténtico → hilo/contacto → borrador → revisión → respuesta/recibo; capacidad no soportada permanece visible |
| C12 | Meta Ads | Lectura de anuncios/insights y solicitudes explícitas de cambios/presupuesto | Lectura separada de gasto; aprobación específica antes de cambiar/publicar anuncios |
| C13 | Analítica comercial | Embudo, conversiones, ingresos y métricas de campañas con fuente/corte | Ceros/sin datos correctos; no sumar borradores o publicaciones fallidas como conversión |
| C14 | Agentes | Jarvi/Neko/SOUP y cadena comercial con herramientas reales de C02–C13 | Autoridad y empresa se revalidan; cada resultado trae evidencia; los agentes no se autoaprueban |
| C15 | Frontend y experiencia | Menú, fichas, tablas, formularios y estados muy similares; azul metalizado/celeste/blanco | Mismos recorridos base, teclado, móvil, errores y permisos; sin fusionar sus fuentes |
| C16 | Calidad y operación | Pruebas de contrato, regresión por sistema, observabilidad y reversión | Instalación repetible, aceptación por flujo y proveedor, sin aumentar métricas por duplicar pruebas |

Orden recomendado: C01 → CRM/precios C02–C03 → cierre C04–C05. En paralelo lógico de diseño, C06 define activos para C07–C09; solo después C10 y C11–C12 con permisos reales. C13–C16 verifican y consolidan cada incremento, no se posponen como una comprobación final única. El modelo de autorización de agentes se define desde C01, antes de habilitar cualquier herramienta de escritura.

Los campos específicos se conservan: matrículas/acudientes y oferta cultural/deportiva en SGA-CD; servicios/clientes/condiciones turísticas en el ERP; venta B2B/B2G y servicios de plataforma en Analemática. El RAT y la optimización hotelera no forman parte de este pool comercial inicial.

### 10. Validación, pendientes y evidencia

**Resultados: 202 pruebas en 14 suites seleccionadas, detalladas al final del bloque.** Solo se ejecutaron suites seleccionadas; no se certifica build completo de los tres frontends, inferencia generativa real, cuentas sociales, modelos de voz, entrega de correos, pauta, pagos, facturación DIAN ni producción.

Pendientes implementables en local: contratos y rutas, CRM/consentimiento, sustitución de placeholders, formularios y estados, perfiles de adaptación, correlación de eventos, bandeja y borradores con transportes controlados, pruebas, observabilidad y bibliotecas de activos propias.

Requisitos externos de aceptación: aplicaciones OAuth y activos/cuentas autorizados, permisos/revisión de cada proveedor, límites y políticas actuales de publicación/comentarios/mensajería, servicios/modelos y derechos de uso, muestras consentidas, infraestructura objetivo, credenciales Bold/DIAN y acuses legítimos cuando corresponda. Se configuran por canal seguro; no se requieren secretos por chat. Tener una integración declarada no demuestra estos requisitos.

**Decisión propuesta:** conservar lo operativo de cada módulo y homologar mediante contratos, adaptadores propios y aceptación equivalente. Priorizar CRM y sus permisos, resolver respuestas de éxito no respaldadas, y después conectar generación/adaptación, publicación y atención con evidencia por canal. No copiar interfaces incompletas para aparentar paridad.


### Resultado reproducible de esta evaluación

**202 pruebas aprobadas en 14 suites seleccionadas:** 117 de CRM/campañas/clientes/cotizaciones/disponibilidad/cancelaciones/captación corporativa; 52 de la cadena Jarvi–Neko–SOUP y sus límites; 33 de Node 6, adaptadores multimedia y webhooks Meta. No se suman aquí las pruebas de reubicación de billetera.

| Suite | Casos | Resultado |
|---|---:|---|
| `erp_customers` | 6 | Aprobada local |
| `availability` | 14 | Aprobada local |
| `sga_workspace` | 11 | Aprobada local |
| `cancellation` | 18 | Aprobada local |
| `cancellation_days` | 19 | Aprobada local |
| `sga_campaigns` | 18 | Aprobada local |
| `ana_corporate` | 4 | Aprobada local |
| `erp_quotation_identity` | 27 | Aprobada local |
| `accounting_agent_army_check.py` | 30 | Aprobada local |
| `accounting_army_staff_check.py` | 17 | Aprobada local |
| `accounting_army_http_check.py` | 5 | Aprobada local |
| `node6_creation` | 9 | Aprobada local |
| `node6_adapters` | 12 | Aprobada local |
| `meta_webhooks` | 12 | Aprobada local |

Las dos suites multimedia encontraron inicialmente una configuración de salida `/state` no escribible; se configuró `NODE6_OUTPUT` en directorios temporales y se repitieron únicamente esas suites. No se cambió el código comercial para hacerlas pasar. Los proveedores de generación/publicación usan transporte simulado en estas pruebas; el render/adaptación FFmpeg sí se ejecuta localmente. Los tests HTTP usan bases y servicios temporales.

La comprobación aislada de Bold confirma una respuesta `success` ante fallo de transporte, sin cargar configuración privada ni contactar a Bold. No acredita un cobro ni diagnostica un pago real. Las 90 funciones de retorno textual se contaron por AST, no como 90 funcionalidades implementadas.

Se verificaron 26 fuentes representativas contra el commit base: permanecen idénticas. Evidencia, comandos, resultados y SHA-256 se conservaron en el registro técnico existente `ANALISIS/entregas/evidencias/recuperacion-originales-20261110/verificacion.json`, entrada `followups.commercial_crm_agents_multimedia_audit_20261111`. Las fuentes detalladas son:

- [`BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints/workspace.py`](../../../BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints/workspace.py)
- [`BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints/corporate.py`](../../../BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints/corporate.py)
- [`BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints/meta_ads.py`](../../../BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints/meta_ads.py)
- [`BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints/meta_webhooks.py`](../../../BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints/meta_webhooks.py)
- [`BACKEND/SGA-CD-BACKEND/app/services/payment_gateway_adapter.py`](../../../BACKEND/SGA-CD-BACKEND/app/services/payment_gateway_adapter.py)
- [`BACKEND/SGA-CD-BACKEND/app/services/campaign_service.py`](../../../BACKEND/SGA-CD-BACKEND/app/services/campaign_service.py)
- [`BACKEND/SGA-CD-BACKEND/app/tools/herramientas_crm_completo.py`](../../../BACKEND/SGA-CD-BACKEND/app/tools/herramientas_crm_completo.py)
- [`BACKEND/SGA-CD-BACKEND/app/agents/corps/ventas_crm_colonel.py`](../../../BACKEND/SGA-CD-BACKEND/app/agents/corps/ventas_crm_colonel.py)
- [`BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/urls.py`](../../../BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/urls.py)
- [`BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/views.py`](../../../BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/views.py)
- [`BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/quote_drafts.py`](../../../BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/quote_drafts.py)
- [`BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/domain/sargentos.py`](../../../BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/domain/sargentos.py)
- [`BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/domain/models.py`](../../../BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/domain/models.py)
- [`BACKEND/ANALEMATICA-BACKEND/deployment/api.py`](../../../BACKEND/ANALEMATICA-BACKEND/deployment/api.py)
- [`BACKEND/ANALEMATICA-BACKEND/urls.py`](../../../BACKEND/ANALEMATICA-BACKEND/urls.py)
- [`BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/agent_army_staff.py`](../../../BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/agent_army_staff.py)
- [`BACKEND/ANALEMATICA-BACKEND/agents/comercial_general/tenientes/teniente_crm.py`](../../../BACKEND/ANALEMATICA-BACKEND/agents/comercial_general/tenientes/teniente_crm.py)
- [`BACKEND/SGA-TUR-BAKEND/apps/domain_business/comercial/urls.py`](../../../BACKEND/SGA-TUR-BAKEND/apps/domain_business/comercial/urls.py)
- [`FRONTEND/SGA-CD-WEB.git/js/workspace.js`](../../../FRONTEND/SGA-CD-WEB.git/js/workspace.js)
- [`FRONTEND/ANALEMATICA-FRONTEND/admin.html`](../../../FRONTEND/ANALEMATICA-FRONTEND/admin.html)
- [`FRONTEND/ANALEMATICA-FRONTEND/js/admin.js`](../../../FRONTEND/ANALEMATICA-FRONTEND/js/admin.js)
- [`FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-comercial/services/sales.ts`](../../../FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-comercial/services/sales.ts)
- [`FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-comercial/hooks/useComercialApi.ts`](../../../FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-comercial/hooks/useComercialApi.ts)
- [`BACKEND/infra/node6/engine.py`](../../../infra/node6/engine.py)
- [`BACKEND/infra/node6/adaptation.py`](../../../infra/node6/adaptation.py)
- [`BACKEND/infra/node6/social.py`](../../../infra/node6/social.py)

<!-- COMMERCIAL_HOMOLOGATION_END -->

<!-- POOL08_PLAN_START -->

<a id="plan-pool08"></a>

## Plan maestro vigente POOL-08: 24 tareas y 72 hitos comerciales

Este plan sustituye la propuesta anterior de 16 frentes como enumeración operativa. Conserva la auditoría como evidencia histórica y adopta la directriz entregada por el usuario con su aclaración posterior: **SOUP solo conserva la optimización de los agentes de toda la cadena; no es el productor multimedia.** Jarvi dirige la operación y Neko la conversación. Producción creativa se delega a la división correspondiente bajo Jarvi.

Se mantiene el objetivo de homologar **SGA-CD, ERP turístico y Analemática** sin fusionar ni trasladar carpetas comerciales. SGA-CD conserva su dominio cultural/deportivo; la descripción administrativa/documental del documento no autoriza reemplazar el sistema completo por una bóveda. Turismo Nacional permanece institucional y fuera de este plan de tres módulos comerciales.

### Enumeración y alcance faltante

| Tarea | Qué falta implementar o nivelar | Resultado de aceptación |
|---|---|---|
| **GC-001 · Contratos, capacidades y DAG POOL-08** | **COMPLETADA:** 20 capacidades, contratos 1.0/1.1, DAG, tipos de intención, APIs privadas y gateway nativo. | Tres backends y gateway verificados, errores/contexto/versiones coherentes, sin ejecución ficticia; GCH-001 a GCH-003 acreditados. |
| **GC-002 · Identidad empresarial, roles, permisos y consentimientos** | Homologar matriz por empresa, vendedor, marketing, supervisor y auditor; mapear identidad entre sistemas sin inferir igualdad de IDs. | Pruebas positivas y negativas empresa A/B; revocación efectiva; marketing no obtiene billetera por herencia de rol; contexto privado correcto en cada frontend. |
| **GC-003 · CRM común de prospectos, contactos y clientes** | Completar origen, deduplicación revisada, historial, responsable, tareas, consentimiento por canal y conversión a cliente. | Crear, buscar, actualizar y seguir un contacto en los tres sistemas sin duplicar ni mezclar empresas; baja/consentimiento conservados. |
| **GC-004 · Oportunidades, embudo, seguimiento y scoring** | Homologar etapas y motivos de pérdida, valor/moneda, tareas, próximas acciones y scoring con fuente; reemplazar plantillas activas. | Transiciones autorizadas e historia íntegra; un cambio a ganado no acredita cobro; scoring identificado como no calibrado mientras no haya evaluación. |
| **GC-005 · Catálogo, tarifas, descuentos e impuestos de oferta** | Definir producto/servicio, vigencia, moneda, reglas de descuento y tratamiento tributario revisado, conservando particularidades de sector. | Precio y total provienen del servidor; descuento fuera de permiso y precio manipulado rechazados; no usar Float para dinero. |
| **GC-006 · Cotizaciones dinámicas, vigencia y aceptación** | Homologar cotización interactiva, contenido multimedia propio, vigencia, aceptación y revalidación de precio/capacidad. | Cotización por empresa verificable, sin cobro ni reserva definitiva implícitos; aceptación registra versión y reintento no duplica. |
| **GC-007 · Venta confirmada, operación y contabilidad** | Implementar evento de venta confirmado, validación operativa, outbox/idempotencia, asiento/reversión y referencias fiscales/documentales; conectar nómina/SG-SST cuando aplique. | No consumar venta sin reglas/precondiciones; no duplicar asiento ni cupo; reintentos y fallos de proveedor recuperables; borrador/venta/factura diferenciados. |
| **GC-008 · Bold: checkout, intención de pago y confirmación** | Referencias únicas, importes canónicos, estado incierto/error, acuse auténtico y conciliación. Corregir respuesta de enlace no respaldada. | Un hash declarado o retorno de navegador no confirma dinero; webhook/consulta auténticos se vinculan al pago; reintento no duplica cobro/asiento. |
| **GC-009 · Cancelaciones, retención, devoluciones y posventa** | Integrar reglas versionadas, aceptación, anticipación y excepciones al CRM; reembolso financiado, seguimiento y fidelización. | Retención correcta y topes; consentimiento, fondos y autorizaciones; saldo/movimiento/asiento atómicos; billetera personal accesible sin afiliación turística. |
| **GC-010 · Constructor de landing pages propias de empresa/prestador** | Homologar plantillas, bloques, editor, versiones, preview, aprobación/publicación y despublicación. Adaptar SGA-CD para organizaciones culturales/deportivas. | Cada empresa crea y publica solo su página, restaura una versión y conserva su marca; otra empresa no modifica ni publica; ninguna carpeta comercial se fusiona. |
| **GC-011 · Landing: formularios, captación, SEO y atribución CRM** | Conectar formularios y ofertas al CRM con consentimiento, UTM/origen, antispam, SEO/metadatos y métricas auténticas. | Formulario real crea un solo prospecto con origen/página/empresa correctos; baja y consentimiento trazables; anuncio comercial no equivale a registro institucional/RNT. |
| **GC-012 · Biblioteca multimedia, derechos, marca y activos** | Originales privados, versiones, hashes, derechos, cuotas y plantillas por marca/sistema; separar soportes fiscales cifrados de activos públicos. | Una empresa no descarga ni publica archivos de otra; original preservado; marca correcta; secretos y soportes privados no se exponen en landing/CDN. |
| **GC-013 · Generación de guiones, textos e imágenes** | Adaptadores de modelo configurables con trabajo asíncrono, coste, cuotas, revisión y resultados persistentes; eliminar éxito simulado. | Texto/imagen reales o error explícito; origen/modelo/derechos trazables; no exponer API keys al navegador ni sustituir falta de proveedor por dato ficticio. |
| **GC-014 · Creación de videos, Reels, voz y subtítulos** | Render por marca, música/voz/subtítulos y adaptadores generativos separados; producción dirigida por división creativa bajo Jarvi. | MP4 reproducible y revisable; composición identificada como tal; voz autorizada; SOUP conserva optimización de agentes y no se convierte en productor. |
| **GC-015 · Tamaños y formatos de imágenes, videos y Reels** | Perfiles versionados 9:16, 1:1 y 16:9, crop/pad explícitos, resolución, peso, duración, audio/subtítulos y preview; imagen y video con contratos distintos. | Se prueban dimensiones, calidad y límites reales; original intacto; no anunciar 4K/8K/inferencia/reencuadre neuronal por reescalar una fuente. |
| **GC-016 · Correos masivos y campañas email** | Plantillas HTML/texto, segmentos, personalización, agenda, cuotas, exclusiones, bajas, rebotes y recibos por destinatario; homologar las tres UIs. | Nunca enviar al guardar; baja bloquea pendiente; no duplicar por reintento; separar aceptado/enviado/entregado/abierto y no inventar aperturas. |
| **GC-017 · SMS, MMS y mensajería multimedia por WhatsApp** | Adaptadores separados: SMS de texto, MMS celular y WhatsApp multimedia; consentimiento por canal, plantillas, enlaces/adjuntos, coste, límites y estados. | Probar cada capacidad soportada por su proveedor; video/imagen no se afirma enviado por SMS; alternativa por enlace/canal solo bajo política y autorización explícitas. |
| **GC-018 · Publicación orgánica y calendario multicanal** | Publicar según formato/cuenta autorizados en Meta, YouTube y TikTok; programación, revisiones, reintentos inciertos y recibos por destino. | No publicar un borrador; cuenta y activos propios; no duplicar envíos; mostrar estado remoto real sin inferir éxito de HTTP 200 genérico. |
| **GC-019 · Bandeja omnicanal y respuestas: mensajes y comentarios** | Conversaciones/hilos por empresa y contacto, asignación, borradores/revisión, respuesta y derivación. Separar DMs, comentarios públicos, correo y WhatsApp. | Evento auténtico llega a empresa/lead correctos; respuesta al hilo correcto; sin acceso cruzado ni responder por canal no autorizado; YouTube/TikTok según capacidad real de sus APIs. |
| **GC-020 · Anuncios y pauta: Meta, TikTok y Google/YouTube Ads** | Campañas pagadas, creativos, presupuesto, A/B y propuestas de optimización con permisos. Separar pauta, publicación orgánica y atención. | Leer no concede gastar; presupuesto/cambio/publicación requieren aprobaciones y recibo; límites por empresa y resultados inciertos visibles. |
| **GC-021 · Cadena de agentes, herramientas reales y motores** | Jarvi operativo, Neko conversacional y SOUP optimizador de coroneles/capitanes/tenientes/sargentos/soldados; conectar herramientas de dominio y Open Duet/agent-desktop con límites. | Un agente devuelve resultado/evidencia real o bloqueo; sin autoaprobación, SQL/shell libre, gasto o cambio de política por SOUP; voz fluida separada y sin valor de firma. |
| **GC-022 · Indicadores, embudo, atribución y predicción** | Datos con fuente/corte, conversiones y atribución a landing/canal/campaña; costes, CAC/LTV y predicción calibrada sin inventar series. | Ceros y sin datos correctos; borrador no cuenta como venta; métricas trazables al CRM/ledger/proveedor; pronóstico con supuestos y evaluación. |
| **GC-023 · Nivelación de frontends y recorridos de los tres módulos** | Menús y recorridos muy similares para las mismas capacidades, formularios, carga, errores, estados vacíos, móvil y accesibilidad; azul metalizado/celeste/blanco. | Mismos casos de aceptación desde cada frontend a su backend propio; ninguna pantalla funcional se reemplaza sin justificación ni se fusionan carpetas. |
| **GC-024 · Calidad, seguridad, rendimiento, operación y cierre** | Regresión completa, trazabilidad por evento, colas offline de borradores, carga, telemetría, restauración y reversión; validar los cuatro DOD del usuario con alcance medido. | 72 hitos con evidencia; instalación repetible; cero cierres ficticios; objetivos 1,2 s/3 s/60 s y consistencia solo aceptados con mediciones/hardware/proveedores reales. |

### Landing pages, correos masivos y SMS/MMS: alcance confirmado

- **GC-010 y GC-011:** constructor y captación. El ERP contiene `LandingPage`, `Embudo`, `FunnelVersion`, `LeadCapture` y un editor visual. Analemática contiene CMS/landing corporativa y unidades comerciales, pero no se ha acreditado un builder empresarial equivalente completo. SGA-CD tiene edición de landing y CRM; se incorporará la capacidad de páginas propias para sus organizaciones culturales/deportivas, sin convertirlas en prestadores turísticos obligatorios.
- **GC-016:** correos masivos. Homologar lo aprovechable de campañas/audiencias/consentimiento, agenda, plantillas HTML/texto, bajas y trazabilidad. La existencia de `email/render` o un sargento de envíos no acredita despacho real.
- **GC-017:** se separan SMS de texto, MMS celular y WhatsApp multimedia. Un SMS no transporta por sí mismo un video; el soporte MMS debe confirmarse con el proveedor que opere en Colombia. No sustituir automáticamente MMS por WhatsApp o enlaces sin política y autorización explícitas.

Fuentes revisadas: `BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/infrastructure/models.py`, `funnels/models.py`, `domain/services/funnel_service.py`, `marketing/models.py`, `marketing/views.py`; `FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-comercial/components/funnel-builder/`; `BACKEND/ANALEMATICA-BACKEND/landing_cms.py`, `agents/comercial_general/`; y el workspace/campañas real de SGA-CD. No se ha probado la integración completa de esos builders ni MMS auténtico.

### Regla de cierre y medición

Cada tarea tiene tres hitos de igual peso, exigidos para los tres sistemas:

1. **F · Funcionalidad:** cumple el alcance local completo definido en su fila; un incremento parcial no basta.
2. **T · Pruebas:** casos reproducibles de éxito, permisos, aislamiento, error y reintento de ese alcance en los tres sistemas.
3. **A · Aceptación:** recorrido integral y evidencias externas legítimas cuando apliquen. Una prueba simulada no cierra proveedor, producción, hardware o requisito profesional.

Los identificadores son **GC-001…GC-024** y **GCH-001…GCH-072**, distintos de ACC y de los 72 hitos contables. La base comercial tiene fragmentos operativos existentes; no se declara que parte de cero. **La revisión de la línea base completa sigue pendiente:** el porcentaje de crédito mide únicamente hitos formalmente acreditados, no todo el código existente ni preparación productiva. Hay **1/24 tareas cerradas y 3/72 hitos acreditados (4,17 % del plan acreditado)**. Las capacidades existentes de las demás tareas siguen pendientes de acreditar contra esta base; no se estima su porcentaje de implementación por contar código o pruebas.

Las matrices canónicas son `ANALISIS/gestion-comercial/plan-pool08.json` y `matriz-hitos-pool08.csv`. Cada hito conserva estado y evidencia; no se cerrará por documentación, número de archivos ni apariencia de un panel.

### Orden de implementación y dependencias

**GC-001 está cerrada**. La siguiente tarea es **GC-002**, todavía pendiente de implementación/nivelación. El orden numerado organiza el trabajo: fundamentos/CRM 1–4; transacción 5–9; landing/activos/multimedia 10–15; canales/atención/pauta 16–20; cadena de agentes, métricas, experiencia y cierre 21–24. Identidad, pruebas, interfaz y observabilidad son requisitos transversales desde el primer incremento. Las dependencias exactas están en JSON/CSV; una tarea dependiente no adquiere aceptación porque exista otra pantalla.

No se fuerza paridad copiando mocks o retirando bloqueos de seguridad. Las capacidades se habilitan por dominio, empresa y canal después de probarlas. Los requisitos externos pendientes se registran y no se presentan como completados. RAT/hotelería queda fuera de la implementación comercial inicial; solo se conectará a disponibilidad existente mediante contrato.

### Primer incremento histórico de GC-001 (superado por el cierre siguiente)

- Contrato JSON Schema estricto, catálogos de 15 capacidades y validación de DAG en carpetas propias de los tres backends. Rechaza propiedades desconocidas, importes flotantes, monedas implícitas, tokens/documentos personales en los campos prohibidos, ciclos, IDs no canónicos y contextos de otra empresa/actor. No verifica por sí mismo consentimiento, precio, pago o fiscalidad.
- API SGA-CD: `/api/v1/commercial-unified/capabilities` y `/intents/validate`, con identidad, plan y permiso CRM.
- API ERP: `/api/v1/mi-negocio/comercial/unified/capabilities/` e `/intents/validate/`, con JWT/sesión y selección empresarial verificada.
- API nativa Analemática: `/api/v1/commercial-unified/capabilities/` e `/intents/validate/`, en su servicio Django nativo. En ese primer incremento el gateway rechazaba el prefijo. El cierre siguiente añade el canal configurable al backend nativo; la homologación general de identidad/frontend pertenece a GC-002/GC-023.
- Los resultados son `VALIDATED_DRAFT`, con ejecución, pago, factura, reserva, almacenamiento y llamadas externas en `false`. No se deshabilitan por ello los flujos existentes: son límites del nuevo punto de preparación. Esta limitación del primer incremento quedó subsanada para GC-001 por el contrato 1.1 de 20 capacidades descrito en su cierre; las herramientas comerciales reales se implementan en sus tareas.
- **35 pruebas del incremento y 104 de regresión aprobadas**, con manifiesto de fuentes estable para el perfil comercial, incluidas FastAPI y HTTP real/JWT en ERP/Analemática y rechazo de Turismo institucional. Comando reproducible: `python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial --output /tmp/pool08-evaluacion-nueva`. Usar un destino inexistente para conservar evidencia anterior.

La directriz original, su SHA-256, las aclaraciones del usuario y evidencias se conservan en el registro técnico existente de entregas. Los objetivos de reacción conversacional, render, consistencia, almacenamiento soberano y alta concurrencia siguen siendo metas pendientes de medir y cualificar; esta entrega no los certifica. No hay commit/push nuevo ni despliegue productivo.

<!-- POOL08_PLAN_END -->

<!-- GC001_COMPLETION_START -->

<a id="cierre-gc001"></a>

## Cierre GC-001 · Contratos, capacidades y DAG · 2026-11-11

**Tarea 1 completada en su alcance contractual local, con GCH-001, GCH-002 y GCH-003 verificados.** El plan registra **1/24 tareas cerradas, 3/72 hitos acreditados: 4,17 % de crédito verificable**. No se acreditan por ello las tareas de construcción de landing pages, campañas, publicaciones, pagos, identidad unificada o frontend comercial completo.

### Implementación entregada

- Contrato **1.1** común y verificable en los tres backends, conservando el contrato **1.0** y sus 15 capacidades originales. El catálogo actual tiene **20 capacidades**, incluidas gestión/captación de landing, email masivo, SMS/MMS y WhatsApp multimedia. Cada fuente permanece en su backend propio; no se trasladaron módulos comerciales.
- Dos tipos de intención: `SALE_PREPARATION` exige referencias comerciales y valores decimales explícitos; `CAPABILITY_PLAN` permite planificar landing/campañas sin inventar compra, precio o depósito documental. Ambos son borradores y no autorizan ejecución.
- DAG acotado hasta 32 nodos en 1.1: referencias canónicas, dependencias existentes, rechazo de duplicados/ciclos, orden determinista, caducidad y límite de cuerpo. Precios, consentimiento, stock, pago y fiscalidad se revalidarán en sus dominios antes de cualquier efecto.
- Descubrimiento autenticado del esquema, hash, límites, estados, rutas y capacidades. `X-POOL08-Contract-Version` permite negociar 1.0/1.1; se rechazan versiones incompatibles sin cambiar silenciosamente el significado de la solicitud.
- Códigos contractuales coherentes entre frameworks: 400 para JSON inválido, 403 para contexto ajeno, 409 para versión/caducidad, 413 para tamaño y 422 para estructura/DAG. `X-POOL08-Error-Code` identifica el error sin reflejar datos de entrada. Las respuestas privadas usan `no-store`. Los rechazos de identidad/plan conservan las reglas de cada backend.
- Cada nodo preparado devuelve su estado `REQUIRES_DOMAIN_BINDING` y su evidencia real de implementación, sin declarar que se ejecutó la herramienta. SOUP sigue siendo el optimizador de agentes; producción creativa es una división bajo Jarvi.
- Recibo API determinista: identificador, versión, hashes y orden del plan. La instrumentación `pool08.audit` registra solo metadatos de validación y digests; las pruebas verifican que no contiene cuerpo, referencia de cliente ni tokens. No es un asiento ni una certificación de pago ni una historia persistente de misiones.

### Rutas disponibles

| Sistema | Prefijo propio | Operaciones |
|---|---|---|
| SGA-CD | `/api/v1/commercial-unified/` | `GET capabilities`, `GET contract`, `POST intents/validate` |
| ERP turístico | `/api/v1/mi-negocio/comercial/unified/` | `GET capabilities/`, `GET contract/`, `POST intents/validate/` |
| Analemática nativa | `/api/v1/commercial-unified/` | `GET capabilities/`, `GET contract/`, `POST intents/validate/` |

El gateway de Analemática enruta exclusivamente estas operaciones a su servicio nativo cuando se configura `ANALEMATICA_COMMERCIAL_API_URL`, por ejemplo `http://analematica-army:8000`. El origen debe ser interno permitido, sin usuario/contraseña, ruta, query o fragmento; el backend debe incluir su hostname real en `DJANGO_ALLOWED_HOSTS`. En local se probó con `http://localhost:<puerto>`.

Si no hay canal configurado o el nativo cae, devuelve 503 y no recurre al contrato de SGA-CD. Se rechazan redirecciones y destinos arbitrarios; se acotan cuerpo y respuesta. Cada petición reenvía su autorización/cookie de forma explícita, sin reutilizar credenciales de otra persona ni aceptar sobrescritura de Host/tenant desde el cliente. El backend nativo autentica y verifica empresa/actor; no se implementó ni se presume intercambio SSO de tokens entre bases.

### Evidencia y alcance de aceptación

**69 pruebas del perfil comercial y 104 de regresión aprobadas, sin saltos declarados.** Los 69 casos incluyen 37 de contrato, 12 de SGA/gateway, 12 de HTTP real multibackend y 8 del registro de hitos. No se suman a los conteos históricos para inflar avance. El manifiesto de fuentes permaneció estable durante la verificación final.

La prueba HTTP levanta servicios desechables de SGA-CD, ERP, Analemática, gateway y Turismo institucional: verifica paridad de esquemas, los 20 tipos de capacidad, versiones, contexto ajeno, errores, reintentos y exclusión institucional. El gateway se prueba con el backend antiguo inaccesible para demostrar que usa el nativo. Las pruebas de transporte simulado adicionales verifican límites, caída, redirecciones y aislamiento de cookies; no sustituyen la prueba HTTP real.

El cierre es aceptación del **contrato/API de preparación** y su auditoría técnica. GC-001 no requiere proveedor real, GPU, certificado DIAN o equipo físico. Esos requisitos permanecen en sus propias tareas; no se afirma que una campaña se publicó, un pago se liquidó o una función de negocio se implementó porque esté catalogada. Producción sigue sin habilitar.

Evidencia y hashes: `ANALISIS/entregas/evidencias/recuperacion-originales-20261110/verificacion.json`, entrada `followups.gc001_contract_completion_20261111`. La matriz referencia el hash de esa entrada.

Comprobaciones reproducibles:

```sh
python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial --output /tmp/gc001-evaluacion-nueva
python ANALISIS/gestion-comercial/tools/update_plan.py --check
```

El destino del perfil debe ser nuevo. La regeneración del seguimiento valida IDs, dependencias, evidencias y hashes antes de dar crédito; no deduce aceptación por presencia de archivos. La publicación de este cierre sigue pendiente de un próximo commit consolidado autorizado.

<!-- GC001_COMPLETION_END -->


### GC-003 · Incremento CRM de dominio · 2026-11-11

Se añadieron implementaciones propias `pool08/crm.py` en los backends SGA-CD, ERP y Analemática, sin trasladar módulos ni cambiar roles. El agregado SQLite permite contactos con origen/responsable, búsqueda, historial, seguimiento con vencimiento, conversión, baja y consentimiento explícito por canal. Duplicados requieren revisión expresa del conjunto actual de candidatos; no se fusionan automáticamente. Comandos con UUID e idempotencia, revisión optimista y auditoría atómica. Los consentimientos locales no autorizan envíos.

Verificación: `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/deployment/tests/pool08_crm_check.py`: 24 pruebas aprobadas (8 por backend), incluyendo separación empresarial, conflicto/reintento y reversión cuando falla la auditoría. Pruebas en SQLite en memoria; ninguna base existente se modifica.

Pendiente: resolver pertenencia de responsables desde la identidad nativa y permisos vigentes por solicitud; integrar ORM/migraciones del CRM existente sin crear un registro paralelo operativo; APIs, pantallas, conservación/baja de datos y recorridos completos. La tarea GC-002 sigue sin cierre acreditado. Se necesitan muestras consentidas para aceptación de uso. GC-003 no está terminada; este incremento no acredita F/T/A ni aumenta el porcentaje comercial. Turismo Nacional conserva su autorización institucional y no recibe permisos empresariales por este trabajo.


### GC-003 · CRM integrado y verificado localmente · 2026-11-11

El incremento anterior queda sustituido por el CRM conectado al ORM, APIs privadas y pantallas propias de los tres sistemas. SGA-CD conserva WorkspaceLead y sus IDs/notas; ERP y Analemática reutilizan Cliente al convertir, sin copiar clientes al consultar. Incluye origen, responsable activo de la empresa, búsqueda paginada, deduplicación revisada con motivo, historial paginado, tareas/vencimientos y conversión atómica. No se fusionan titulares ni se heredan consentimientos. Las bajas y cambios de correo/teléfono revocan el consentimiento local por canal/finalidad; SGA-CD aplica esa restricción también antes de despachar sus campañas existentes. Las rutas antiguas rechazan sobrescribir contactos ya adoptados por el CRM.

Cada petición consulta la autoridad nativa vigente. Se comprobaron delegación explícita, revocación, cambios de rol, empresa ajena y los cargos institucionales de Turismo Nacional. No se alteraron los modelos de roles de SGA-CD ni CustomUser. Turismo Nacional conserva su función institucional y no expone estos endpoints empresariales. El CRM no concede permisos financieros ni restringe el derecho de cualquier persona a su billetera personal. Los agentes y sus autorizaciones conservan su separación; no se habilitó ejecución del DAG por declarar una capacidad disponible.

La recuperación usa UUID idempotente y recibo privado: respuesta perdida después de guardar, reintento y recarga recuperan el mismo contacto. En sessionStorage quedan únicamente IDs/metadatos del intento, sin contraseñas, tokens o datos del contacto. Se integraron los recursos en los manifiestos de publicación, el catálogo público permitido y la preparación Next; el formulario se monta dentro de los paneles, sin debilitar la política contra frames. Se conserva azul metalizado, azul claro y texto blanco.

Verificación final: 140 pruebas del perfil comercial y estructura, 88 comprobaciones Chromium con HTTP real en escritorio/móvil, 104 regresiones de flujos existentes, 13 pruebas de esquema/restauración, 4 de sesión nativa CSRF/TOTP, 22 multimedia, 5 SSO, 1 Flet SSO, 3 de preparación web y 5 de seguridad web; preparación Flet, publicación desechable, tipos estrictos del nuevo componente y hashes de terceros también comprobados. Son conteos de suites independientes: no equivalen a hitos adicionales ni a aceptación productiva. Evidencias y manifiesto de fuentes estables: ANALISIS/gestion-comercial/evidencias/gc003-20261111/. La prueba de navegador utiliza clientes sintéticos; el build completo de Next no se acredita por comprobar este componente.

Por aclaración del usuario, se trasladó el código que estaba fuera de las capas principales: DB/infra/seguridad/catálogos y herramientas a BACKEND; renderizadores y pruebas web a FRONTEND; herramientas/pruebas Flet y matrix-os a DESKTOP. Los ejecutables de integración viven en BACKEND/INTEGRACIONES. Colibri y matrix-os conservan sus SHA de submódulo; sus entradas Git se trasladaron sin crear commit. Los informes permanecen en ANALISIS, INTEGRACIONES, docs y verificaciones. Git, CI, instrucciones y compose de entrada conservan su ubicación técnica. Se guardaron respaldo previo y manifiesto comprimido con hashes anteriores/actuales; no se borraron fuentes para reorganizarlas.

Estado: GC-003 acredita funcionalidad y pruebas locales (GCH-007/GCH-008), no aceptación integral (GCH-009). Matriz comercial: 5/72 hitos acreditados = 6,94%; 1/24 tareas con aceptación completa. El porcentaje global de implementación sigue sin estimación mientras no se revise toda la base. Pendientes: muestras consentidas, revisión de políticas/usuarios de GC-002, instalación/habilitación del canal nativo y CSRF del servidor, migración histórica/PostgreSQL y cualificación productiva. Las pruebas no hacen auténtica una evidencia de consentimiento. No se avanzó a GC-004. No hubo commit, push ni despliegue.


### GC-004 · Oportunidades, embudo y seguimiento · 2026-11-11

Problema: los tres sistemas tenían recorridos comerciales desiguales, componentes de demostración y oportunidades del ERP sin moneda/contacto verificables. Se implementó un servicio propio y persistente en cada backend y su interfaz en cada frontend, conservando roles y empresas nativos. El embudo controla etapas, motivos de pérdida, revisión optimista, responsable, valor/moneda, próximas acciones y tareas. Reapertura de cierres restringida al administrador. Ganar una oportunidad no acredita cobro, factura, asiento ni ingreso. No se conceden permisos empresariales a cargos institucionales de Turismo Nacional.

El ERP conserva los UUID y el historial StageHistory existente, exige adopción explícita cuando faltan datos y detecta cambios externos posteriores. Una etapa antigua desconocida requiere revisión administrativa. Se amplió el campo de valor mediante migración; SQLite rechaza y revierte importes que no conserva exactamente. No se infieren monedas, contactos ni empresas. La prioridad presenta cinco reglas con fuentes, sin calibración, probabilidad ni precisión predictiva acreditadas. Se sustituyeron el embudo simulado activo del ERP y los indicadores comerciales ficticios de Analemática.

Seguridad y recuperación: autorización nativa vigente en cada petición, aislamiento por empresa, recibos privados, UUID idempotente, recuperación tras respuesta perdida y recarga, historia encadenada y comprobación previa a nuevas escrituras. La regresión detectó que una escritura podía extender una historia previa alterada: se corrigió y se verifica que el comando se rechace sin aumentar la revisión. Interfaz azul metalizado, azul claro y blanco; recursos incluidos en publicación y preparación web, sin trasladar módulos entre sistemas. Jarvi, Neko y SOUP conservan sus funciones.

Verificación: 185 pruebas en 14 suites del perfil comercial, incluidas 45 específicas de oportunidades; 120 comprobaciones Chromium del nuevo recorrido en escritorio/móvil contra HTTP real y 88 del CRM previo. Además, 104 regresiones de agentes/campañas/workspace, 13 pruebas de base desechable, 4 de sesión CSRF/TOTP, 3 de preparación web y 5 de seguridad web; migración sin deriva de modelos, publicación desechable y tipos estrictos de componentes ERP aprobados. Evidencias y hashes: ANALISIS/gestion-comercial/evidencias/gc004-20261111/. Son verificaciones locales con datos sintéticos; no acreditan build completo de Next, PostgreSQL/concurrencia productiva ni aceptación de usuarios reales.

Estado: GC-004 acredita GCH-010/GCH-011 (funcionalidad/pruebas); GCH-012 sigue pendiente. Matriz comercial: 7/72 = 9,72%; aceptación integral 1/24 tareas. Pendientes explícitos: dataset consentido y evaluación predictiva, usuarios/datos legítimos y dependencias GC-002/GC-003, migración histórica y cualificación productiva. No se aumenta el porcentaje contable. No hubo commit, push, despliegue ni operaciones sobre cuentas reales.


### GC-005 · Catálogo, tarifas, descuentos e impuestos de oferta · 2026-11-11

Problema: los tres sistemas no compartían un recorrido verificable de tarifas vigentes, permisos de descuento y tratamiento tributario declarado. Se implementó un catálogo de tarifas propio por sistema/empresa, separado de catálogos institucionales o de agentes, con código, tipo producto/servicio, sector, moneda, vigencia, condiciones, estado y revisión. El administrador mantiene sus versiones y límites; los delegados requieren capacidades explícitas y solo calculan sin descuentos. No se asignan roles comunes ni se concede acceso empresarial a Turismo Nacional. Las fuentes y recursos permanecen en BACKEND/FRONTEND; los generales conservan sus funciones.

El cliente envía únicamente referencias/revisiones, cantidades y descuentos. El servidor lee precios/políticas, rechaza importes manipulados, vigencias vencidas, moneda mezclada, revisiones antiguas y descuentos fuera de permiso/política. Usa Decimal y cadenas decimales persistentes, sin Float para dinero; redondea HALF_UP por línea y agrega subtotal, descuento, base, impuesto declarado y total. El perfil admite monedas de dos decimales, sin FX; CLP está excluido. La tarifa es antes del impuesto declarado de la línea; este alcance no sustituye un motor fiscal exhaustivo.

Se registran gravado/exento/excluido/no sujeto con tasa, referencia de política, soporte y revisión declarada. No se atribuye autorización profesional ni autenticidad externa a un digest. Se corrigió que cambiar solo precio renovara implícitamente la revisión tributaria: conserva su fecha/revisor; cambiar tipo, sector o moneda exige revisión expresa. No se importan ni sobrescriben automáticamente tarifas históricas sin revisión. La vista previa histórica del ERP ya calcula su precio en servidor y permanece no vinculante, sin impuestos ni total pagadero; las rutas antiguas de operaciones siguen bloqueadas. La integración de documentos/cotizaciones se aborda en su tarea correspondiente.

Cada escritura y su auditoría comparten transacción; revisión optimista, historia encadenada comprobada antes de escribir, comando UUID y recibo privado impiden duplicados y permiten recuperar respuesta perdida/recarga. El cálculo conserva instantáneas de tarifa/condiciones/impuesto y caducidad: recuperar un recibo no revalida tarifas ni extiende su vigencia. Es una estimación, no factura, reserva, cobro, asiento ni ingreso. Pantallas en cada frontend, enlace de tarifas ERP y herramientas CRM, recursos de publicación y preparación actualizados. Se conserva azul metalizado, azul claro y texto blanco.

Verificación final: 236 pruebas en 18 suites comerciales (incluidas 51 específicas de tarifas); 104 comprobaciones Chromium nuevas contra HTTP real en escritorio/móvil y 208 de CRM/embudo previos. También 104 regresiones de agentes/campañas/workspace, 13 de base desechable, 4 de sesión CSRF/TOTP, 3 de preparación web y 5 de seguridad web; migración 0005 sin deriva de modelos, publicación desechable y tipos estrictos seleccionados ERP aprobados. Evidencias y manifiesto de fuentes estables: ANALISIS/gestion-comercial/evidencias/gc005-20261111/. No se acredita build completo de Next, PostgreSQL/concurrencia ni datos fiscales auténticos con estos fixtures.

Estado: GC-005 acredita GCH-013/GCH-014; GCH-015 sigue pendiente de precios/condiciones/soportes legítimos, revisión profesional y aceptación de usuarios/políticas de GC-002, migración histórica y cualificación productiva. Matriz comercial: 9/72 = 12,50%; aceptación integral 1/24 tareas. La matriz contable no cambia. Se preservaron las evidencias anteriores y los archivos locales; no hubo commit, push ni despliegue.


### GC-006 · Cotizaciones dinámicas, multimedia, vigencia y aceptación · 2026-11-11

Problema: SGA-CD y Analemática no tenían el recorrido completo de cotización y el ERP conservaba borradores no vinculantes. Se incorporaron servicios/tablas propios, herramientas CRM y ruta web propia en cada sistema, aprovechando precios/versiones del catálogo y contactos/oportunidades autorizados. Se conserva la interfaz de borradores históricos del ERP, sus funciones de sesión/recuperación y un enlace a cotizaciones dinámicas; no se descartan ni migran automáticamente sus registros.

El servidor calcula y congela precios, impuestos declarados, condiciones, adjuntos y vigencia efectiva. Emisión y aceptación revalidan versiones/precios, contacto y disponibilidad desde fuentes propias: espacios, reservas y clases de SGA; servicios, reservas y holds del proveedor en ERP/Analemática. Cada versión de tarifa requiere política de capacidad revisada por administrador, con soporte declarado; ausencia de revisión bloquea. Consultas conservadoras agrupan demanda por recurso/intervalo, bloquean ambigüedad heredada y no crean holds ni reservas. Se conservan los límites y la clasificación tributaria de GC-005; RAT/ADR no se modificaron.

Se implementó vista del destinatario sin sesión empresarial, protegida por enlace HMAC vinculado a empresa/cotización/versión/digest. El token no se guarda en registros ni almacenamiento del navegador y se retira del fragmento al abrir la página. Revisar o retirar invalida enlaces anteriores; falta de clave explícita falla cerrada. La aceptación registra versión, digest, momento y revalidación, con método LINK_POSSESSION e identidad del cliente explícitamente no verificada. No firma fiscal, cobro, asiento, ingreso ni reserva implícitos. Los UUID, recibos y transacción con auditoría impiden duplicados al perder una respuesta, recargar o reintentar una confirmación. El historial conserva instantáneas y se comprueba antes de escribir.

Multimedia propia: imágenes verificadas/normalizadas sin metadatos y vídeos MP4/WebM verificados/remuxados, acceso por empresa o enlace autorizado, comprobación de hash y cuotas. Límites locales: 10 conceptos y 5 adjuntos por cotización; 256 KiB por activo, 100 activos/20 MiB por empresa. Se requieren Pillow y ffmpeg/ffprobe; archivos o runtime inválidos no se sustituyen por éxito simulado. La clave de enlaces se configura de forma segura por backend mediante COMMERCIAL_QUOTE_LINK_KEY, sin valor por defecto ni compartirla entre sistemas; ejemplos en cada pool08.

Hallazgos subsanados en entrega: el fondo del destinatario quedaba blanco y se corrigió a azul metalizado/azul claro/texto blanco; se agregaron comprobaciones de fondo/tipografía. La CSP bloqueaba los Blob de imagen/vídeo, el proxy ERP heredaba 16 KiB para multimedia y no encaminaba los enlaces, y la revisión Basic impedía abrir el shell del destinatario. Se habilitaron únicamente Blob de imagen/vídeo, carga acotada de 256 KiB, rutas exactas de enlace y tres recursos públicos del destinatario. Paneles y otras APIs conservan protección; no se habilitan finanzas heredadas. Nginx oficial compilado en /tmp, sin sudo ni servicio del sistema, validó sintaxis y flujo real TLS con CA local verificada: shell/adjuntos/aceptación/reintento y límites, sin abrir paneles privados. El navegador también aplica la CSP durante sus pruebas.

Verificación final: 288 pruebas en 23 suites comerciales (49 específicas de cotizaciones y 3 de contrato de entrega añadidas); 176 comprobaciones nuevas Chromium en 1280/390 con HTTP real y CSP, más 312 de CRM/embudo/tarifas previos. Además, 104 regresiones de agentes/campañas/workspace, 13 de base desechable, 4 de sesión CSRF/TOTP, 3 de preparación web, 5 de seguridad web y 3 específicas Nginx/TLS; migración 0006 sin deriva, publicación desechable y tipos seleccionados ERP aprobados. Fuentes estables, comandos, hashes, imágenes y versión de Nginx: ANALISIS/gestion-comercial/evidencias/gc006-20261111/. Sin build completo de Next, datos reales, aceptación de proveedor/usuario ni cualificación productiva por fixtures.

Estado: GC-006 acredita GCH-016/GCH-017; GCH-018 pendiente de condiciones/precios aprobados y revisión empresarial del mecanismo de aceptación/entrega, dependencias GC-004/GC-005 y cualificación de custodia/rotación, PostgreSQL/concurrencia, infraestructura y restauración real. Matriz comercial: 11/72 = 15,28%; aceptación integral 1/24 tareas. Contabilidad no cambia. Jarvi/Neko/SOUP y los derechos de billetera personal permanecen separados de estas autorizaciones. Trabajo respaldado en el entorno; sin commit, push ni despliegue.


### GC-007 · Venta confirmada, operación y contabilidad · 2026-11-12

Problema: aceptar la cotización no consumaba una venta validada contra operación y libro mayor. Se codificó el ciclo propio en los tres backends y frontends, conservando identidad, roles, datos y carpetas. Una venta pasa por borrador, revisión y confirmación separada del administrador; exige cotización aceptada/versionada, hecho económico, cuentas revisadas por empresa, período abierto y referencias/huellas documentales. La fecha se comprueba contra el día contable local; se corrigió la diferencia con UTC alrededor de medianoche. La versión aceptada se conserva sin repricing arbitrario por cambios posteriores del catálogo.

El asiento usa el ledger existente, Decimal y cuentas autorizadas por función, sin permitir que una cuenta de efectivo suplante cartera. Derecho de cobro incondicional: cartera contra obligación de contrato; servicio prestado: cartera contra ingreso e impuesto declarado. Venta, asiento, auditoría, cupos y outbox son atómicos en ERP/Analemática. La contrapartida requiere nueva revisión y segunda confirmación. Se bloquearon el posteo/reversión por rutas genéricas del ledger y la liberación genérica de holds propios de ventas. Referencias fiscales con hash no equivalen a factura emitida o aceptada; no se mueve dinero.

SGA conserva sus reservas y se comunica con un ledger ERP/Analemática configurado por origen HTTPS fijo. No existe ledger alternativo simulado en SGA ni equivalencia inferida de IDs/roles. El vínculo de identidad/empresa y su renovación/revocación requieren revisor independiente vigente, comparación de versión y soporte; las sesiones/JWT nativos y CSRF/MFA son propios. HMAC autentica contexto y acuse entre servidores. Antes del envío se conserva intención y cupo; ante resultado incierto se retienen y se consulta el estado firmado con verificación del asiento real. La respuesta declara cross_database_atomic=false. Los tests inyectan pérdida de acuse después de contabilizar y después de revertir, sin duplicar ni liberar prematuramente. El trigger SQL impide borrar/cambiar geometría de reservas vivas; las canceladas se excluyen de disponibilidad solo si su claim liberado y su identificación coinciden. Se corrigió el retorno DELETE de PostgreSQL y se acotó su introspección a la tabla, sin acreditar ejecución PostgreSQL.

Un intento no ejecutado puede cancelarse, liberar su cupo tras comprobar el resultado y volver a revisarse bajo la misma venta; no requiere duplicar cotización, asiento o cupo. Se conservan revisión optimista, UUID de intención original y cadena histórica. Se corrigieron cuerpos incompletos, rechazo de permisos en el ingreso firmado y manejo de cancelación ya registrada. Cuando hay personal se consulta el despacho SG-SST con autorización profesional/EPP/descanso; el servicio prestado exige cierre registrado y costos vigentes de nómina ya contabilizada. El caso positivo completo usa el registro laboral que produce el cierre del despacho y atribuye costo sin crear otro gasto ni pago.

Interfaz: botón Ventas y contabilidad en los tres CRM, selección de cotización aceptada, revisión del hecho/cuentas/soportes, segunda confirmación, asiento legible, historia, contrapartida y recuperación. El detalle técnico de auditoría queda plegado. SGA permite la sesión contable propia y solo empresas vinculadas revisadas; falta de configuración falla cerrada. Se preservan azul metalizado/azul claro/blanco y navegación. Migración aditiva 0007 propia ERP/Analemática e instalación aditiva SGA; sin alterar bases reales o ventas históricas.

Verificación final: 356 pruebas en 31 suites comerciales sobre fuentes finales estables; 112 comprobaciones nuevas Chromium en 1280/390, más las de CRM/embudo/tarifas/cotizaciones existentes. Además 320 regresiones en 15 suites de ledger, nómina, SG-SST, costos, FX, reservas, agentes y permisos; migración SQLite desechable sin deriva, publicación desechable, tipos seleccionados y 3 pruebas de preparación/5 de seguridad web. Comandos, logs, hashes y capturas: ANALISIS/gestion-comercial/evidencias/gc007-20261112/. El navegador SGA comprueba acceso/fallo cerrado sin peer configurado; su recorrido financiero positivo, pérdidas y revisión vencida se verifican por puente HTTP/JWT/HMAC real en suite separada. Ese servidor comparte conexión SQLite de prueba: no demuestra concurrencia ni TLS productivo. No se acredita build integral Next ni equipos físicos.

Estado: GCH-019/GCH-020 acreditados; GCH-021 pendiente. Plan comercial 13/72 = 18,06%, aceptación integral 1/24 tareas. Pendientes cuentas/hechos/soportes y revisión contable/laboral legítimos, vínculo empresarial y configuración/rotación de origen/sesiones/TLS, aceptación de dependencias, PostgreSQL/concurrencia, datos históricos, carga y restauración en infraestructura objetivo. Alcance local acotado a COP; FX no cualificado se rechaza. DIAN, custodia y documento fiscal auténticos siguen en su frente. Outbox permanece PENDING sin consumidor externo acreditado. NO_LABOR_REVIEWED y aceptación por enlace no son certificaciones de personal ni identidad. RAT/ADR y la elegibilidad de la billetera no se modifican. Indicador contable separado sin cambio: 79,17% (57/72, 9/24). Sin commit, push ni despliegue.


### GC-008 · Bold: incremento parcial y cierre pendiente · 2026-11-11 (America/Bogota)

Estado honesto: tarea EN_EJECUCION, alcance funcional y verificación completos todavía no acreditados. El usuario ya había indicado que entregó la API de pruebas; no se le solicita repetir esa confirmación. En este proceso no están configuradas BOLD_IDENTITY_KEY, BOLD_SECRET_KEY ni COMMERCIAL_BOLD_MERCHANTS y no existe el archivo privado recuperado .runtime/bold-test.env en el checkout. La configuración aplicada de red no incluye Bold. Esto describe el entorno seleccionado, no niega la entrega previa de las claves. No se imprimieron valores, se incorporaron secretos a Git ni se hicieron cobros externos.

Hallazgos corregidos: el adaptador devolvía success y fabricaba una URL aunque fallara Bold; truncaba importes con int y exponía datos de integración innecesarios. El checkout anónimo reutilizaba una referencia derivada del correo y no persistía intención. Ahora el adaptador solo devuelve un enlace recibido de un origen permitido, limita respuesta, rechaza redirecciones, conserva la incertidumbre y no redondea/trunca fracciones. La antigua ruta de suscripción queda bloqueada con PERSISTED_PAYMENT_INTENT_REQUIRED; requiere adaptación autorizada, no se presenta como operativa. Cinco herramientas de agentes que respondían ejecutada con éxito ante texto libre ahora declaran bloqueo y executed=false.

Código propio en los tres backends/frontends: intención persistente vinculada a venta contabilizada, importe/moneda del servidor, una intención por venta/empresa con restricción SQL y referencia aleatoria sin correo, revisión del administrador y solicitud separada, recibos/historia con digest, revisión optimista y recuperación tras respuesta perdida. DISPATCHING se confirma en base antes de I/O. UNKNOWN no permite reenvío ni cancelación local que finja anular un cobro; consultar el registro no hace otro POST. Configuración sandbox explícita por empresa y referencias de secretos, sin aplicar una clave global a todos; se conserva metadata de comercio/perfil antes del envío. Una venta con enlace/resultado pendiente no se revierte sin conciliación; divergencia de columnas de índice/documento falla cerrada. El flujo nativo no cobra aparte una venta cuyo origen es SGA. No se cambian roles, elegibilidad de billetera ni carpetas entre sistemas.

La interfaz Pagos · Bold permite preparar intención, revisar estado, solicitar enlace y recuperar recibo local; muestra pago sin confirmar o bloqueado, conservando azul metalizado/azul claro/texto blanco y vista móvil. Un retorno del navegador, un hash declarado o un enlace no confirman dinero. El verificador auténtico no se sustituye por el hash del SDK: permanece bloqueado y no se contabiliza un recaudo.

Verificación del incremento: 392 pruebas en 37 suites comerciales con fuentes finales estables; 144 comprobaciones nuevas Chromium a 1280/390 sobre HTTP local, incluyendo recuperación y bloqueo real sin credenciales. Además 339 regresiones en 16 suites, 13 pruebas de instalación SQLite desechable, restricciones únicas/migración 0008 sin deriva, publicación desechable, tipos seleccionados, 3 comprobaciones de preparación y 5 de seguridad web. Respuestas positivas del transporte son sintéticas; no prueban firma, recibo o pago Bold. Comandos/logs/hashes/capturas: ANALISIS/gestion-comercial/evidencias/gc008-parcial-20261111/. Las pruebas del incremento no completan el alcance de la tarea.

Desarrollo pendiente: implementar el verificador del cuerpo HTTP original y el esquema/estados reales de Bold conforme a contrato cualificado; consulta autenticada para incertidumbre; vínculo y deduplicación de acuses por comercio/referencia/importe/moneda/ID; conciliación y asiento de recaudo atómico/idempotente contra cartera en ERP/Analemática y mediante el puente de origen SGA. También falta cualificar fracciones/límites de Bold y adaptar o retirar formalmente el checkout antiguo de suscripciones. No atribuir estos pendientes de código únicamente a falta de credenciales.

Requisitos externos: recuperar/vincular el acceso de pruebas ya entregado mediante canal seguro en este entorno, habilitación de red aplicada, comercio/contrato y acuses legítimos; después aceptación empresarial/profesional, PostgreSQL/concurrencia, históricos y restauración en infraestructura objetivo. No se infiere autenticidad de un SHA declarado ni se simula su aprobación. No se activaron webhook de confirmación, asiento de recaudo, retiro, pago o reembolso bancario. Plan comercial sin aumento: 13/72 = 18,06%, aceptación integral 1/24; GC-008 no acredita GCH-022/023/024. Contabilidad separada sin cambio: 79,17% (57/72, 9/24). Sin commit, push ni despliegue.


### GC-009 · Posventa integrada: incremento parcial · 2026-11-12 (America/Bogota)

Implementado y probado: rutas propias de posventa en ERP y Analemática y puente propio SGA con autenticación nativa, contexto firmado y vínculos revisados de empresa/prestador. El actor no se acepta desde el cliente. Los tres CRM exponen políticas versionadas por días, aceptación, excepciones y recuperación del caso; conservan sus carpetas, roles e identidad azul metalizado/azul claro/texto blanco. Seguimiento interno por contacto/responsable de su propio CRM, revisión e identificador de petición para reintento en memoria, sin enviar mensajes. No se supone que contacto, cliente, venta y reserva de sistemas distintos sean la misma identidad.

El acceso CRM reutiliza el motor financiero existente de reembolso financiado: consentimiento, fondos previos, dos autorizaciones, firmas exigidas según configuración y saldo/movimiento/asiento atómicos. En las pruebas positivas desechables se deshabilita explícitamente la exigencia de dispositivo para comprobar atomicidad; otra prueba la activa y rechaza la firma ausente. Esto no prueba claves físicas ni atestación. La billetera personal no exige afiliación turística. Los casos aceptados siguen siendo propuestas: no se afirma cancelación efectiva ni devolución bancaria.

Verificación del incremento: 414 pruebas contabilizadas en 41 suites comerciales sobre fuentes finales estables. La corrida completa tuvo un fallo en oportunidades navegador (gateway/reintento); su repetición independiente pasó 120 comprobaciones, pero no se identificó/corrigió aún la causa de la intermitencia, por lo que el informe original conserva local_checks_complete=false. Las cuatro suites nuevas GC-009 sí pasaron; 58 comprobaciones nuevas Chromium a 1280/390 con HTTP local; 401 regresiones en 19 suites, tipos seleccionados ERP, sintaxis/equivalencia de las tres copias propias, publicación desechable, 3 pruebas de preparación y 5 de seguridad web. Las suites nuevas cubren políticas, topes, rechazo de suplantación/otra empresa/vínculo revocado, reintentos sin duplicar dinero y posventa por API. Evidencias, comandos, hashes y capturas: ANALISIS/gestion-comercial/evidencias/gc009-parcial-20261112/. No son aceptación integral ni productiva.

Desarrollo pendiente: vínculo verificable CRM/venta/reserva financiera/titular y cancelación efectiva de la fuente con recibo completo; fidelización y recorrido consentido completo; interfaz de firma física y recuperación del seguimiento pendiente tras recarga (hoy conserva nonce en memoria). El reembolso bancario depende además del verificador, consulta y liquidación auténticos todavía pendientes de GC-008. No atribuir estos pendientes de código solamente a proveedores o credenciales.

Requisitos externos: políticas empresariales aprobadas y revisión profesional, identidad/vínculos legítimos, acceso Bold ya entregado vinculado por canal seguro en este entorno y acuses auténticos; dispositivos y PostgreSQL/concurrencia/aceptación de usuarios. No se reitera la pregunta de disponibilidad de la API. GC-009 queda EN_EJECUCION sin acreditar GCH-025/026/027. Comercial conserva 13/72 = 18,06%, aceptación 1/24; contabilidad separada 57/72 = 79,17%, 9/24. Sin commit, push, despliegue ni acciones sobre cuentas reales.


### GC-010 · Constructor propio de landing pages · 2026-11-12 (America/Bogota)

Funcionalidad y pruebas locales terminadas: cada CRM tiene acceso Landing pages, con sus roles y datos propios. ERP y Analemática conservan backends/frontends propios; SGA-CD usa su propio constructor, adecuado a organizaciones culturales/deportivas. No se fusionan carpetas ni roles, y Turismo Nacional no adquiere acceso empresarial. Se conservan los editores de embudos y páginas históricos; no se han migrado ni modificado sus datos automáticamente.

Flujo implementado: crear página con marca, título, descripción y plantilla Servicios/Turismo/Cultura/Deportes; aplicar bloques prediseñados, añadir/editar/ordenar/quitar HERO/TEXT/CTA; guardar versiones, vista previa privada, aprobación y publicación separadas, URL pública de la aplicación, restauración como nuevo borrador y despublicación inmediata. Los cambios no guardados bloquean aprobación/publicación desde el editor. Editar o restaurar invalida la aprobación pero conserva la versión pública anterior hasta publicar otra; restaurar nunca sobrescribe la historia. El HTML público no contiene auditoría, actores ni identificadores privados.

Protecciones: administrador autenticado y acceso empresarial vigente comprobados en cada operación y reintento; recibos ligados también al prestador; revisión optimista, identificador de petición y eventos encadenados. Otra empresa no puede consultar/modificar/publicar ni recuperar recibos privados. Una falla de auditoría revierte el estado en ORM. Contenido estructurado y escapado, sin HTML/JS arbitrario, URLs HTTPS validadas, CSP restrictiva, no-store y despublicación anónima 404. Identidad visual azul metalizado/azul claro/texto blanco. Los límites actuales son 12 bloques, 20 versiones de contenido y 200 revisiones ordinarias por página, permitiendo siempre el retiro final de una página pública; listados paginados con resúmenes evitan enviar historiales completos.

Verificación final: 120 pruebas en 10 suites del perfil commercial-landings, todas aprobadas sin skips sobre fuentes finales estables; 128 comprobaciones Chromium a 1280/390, cubriendo los tres sistemas y el gateway, publicación anónima real por HTTP local, retiro, restauración, ordenación y recuperación tras respuesta perdida/recarga sin duplicar. Además 13 pruebas sobre SQLite desechable, migraciones propias y fresh 0009 aplicadas sin deriva, unicidad por empresa/prestador/código, publicación sobre copia desechable, tipos seleccionados ERP, tres pruebas de preparación y cinco de seguridad web. Evidencias, logs, comandos/hashes y capturas: ANALISIS/gestion-comercial/evidencias/gc010-landings-20261112/. No es una regresión completa de todo el perfil comercial; permanece el fallo intermitente anterior de oportunidades documentado en GC-009.

Hallazgos corregidos durante el trabajo: recibos aislados también por prestador cuando comparten empresa; validaciones de estructuras/URLs malformadas; referencia correcta de migración 0008 en la nueva 0009; listado con resúmenes/paginación en vez de historiales completos; bloqueo de publicación con borrador sin guardar. No queda desarrollo conocido pendiente para el alcance local delimitado de GC-010. La importación de páginas históricas, captura de leads, envíos y trackers no forman parte de este constructor y no se presentan como implementados.

Aceptación integral pendiente: revisión de marca, textos/derechos y recorrido por administradores reales; cualificación de roles/datos, PostgreSQL/concurrencia/carga y restauración en infraestructura objetivo. Si se decide usar dominio propio, faltan titularidad, DNS, TLS y enrutamiento autorizados; esta entrega usa rutas de la aplicación y no configura dominios. No se publicó contenido de clientes en internet. GCH-028/029 quedan verificados, GCH-030 pendiente: GC-010 tiene 2/3 hitos, sin declarar cierre integral. Comercial pasa de 13/72 a 15/72 = 20,83%, aceptación 1/24. Contabilidad separada sin cambios: 57/72 = 79,17%, 9/24. No se creó commit ni se actualizó main.


### GC-011 · Formularios públicos, consentimiento y atribución CRM · 2026-11-12 (America/Bogota)

Funcionalidad y pruebas locales terminadas en los tres módulos propios. El editor permite incluir formulario de solicitud comercial, aviso de tratamiento, enlace HTTPS de privacidad y oferta de su catálogo. La vista previa es de solo lectura; la captación exige una versión publicada y aprobada. Campos públicos: nombre, correo, teléfono opcional, aceptación del tratamiento y marketing separado/opcional, sin casillas premarcadas. La declaración no verifica titularidad del correo, no habilita envíos y no crea usuario, registro institucional ni inscripción RNT.

Ingreso: la empresa/prestador y el responsable proceden de la página y del publicador vigente, nunca del visitante. Se verifican identidad/roles actuales y oferta propia activa/vigente con su integridad de catálogo. Una transacción contiene prospecto canónico, declaración, captación y auditoría; fallo de auditoría revierte todo. Las coincidencias por correo/teléfono generan revisión sin duplicar ni sobrescribir datos o reactivar una baja. Se conserva página/versión, aviso y su hash, oferta y etiquetas UTM declaradas, sin fingir atribución auténtica de una plataforma.

Recuperación y baja: cada formulario tiene nonce, firma separada por sistema/empresa/prestador, vínculo al navegador y vencimiento de 30 minutos. Reintentar conserva el resultado sin duplicar. Una solicitud ya aceptada recupera su comprobante aunque la página se retire; un envío nuevo de página retirada o versión anterior se rechaza. El comprobante no muestra correo ni ID de contacto y lleva el permiso de retirada en un campo del formulario, no en la URL. La retirada es idempotente y se registra en captura e historial CRM; revoca exclusivamente las declaraciones nacidas en esa solicitud. No borra autorizaciones posteriores del administrador ni desactiva un cliente evolucionado. Un prospecto inicial sin modificaciones queda de baja. Se conservan los procesos de derechos/identidad verificada del administrador.

Protecciones y SEO: formulario HTML del mismo origen, sin scripts públicos, parser acotado a 12 KB/campos únicos, campo trampa, firma/cookie y límite persistente de diez solicitudes aceptadas por hora/empresa/prestador/cliente pseudonimizado; no se guarda IP cruda ni se confía en X-Forwarded-For arbitrario. El gateway valida el origen del navegador antes de remitirlo exclusivamente a su destino nativo fijo. Rutas/métodos incorrectos devuelven rechazo controlado, no errores de argumentos. El aviso y la marca se escapan; CSP, no-store y azul metalizado/azul claro/texto blanco. Canonical por ruta sin UTM ni hostname interno y metadatos Open Graph sobre contenido publicado. Se corrigió el bloqueo robots.txt de SGA-CD con una excepción solo para landing pages públicas; las APIs privadas siguen excluidas y la preparación/publicación conserva esa regla.

Métricas privadas y paginadas: solicitudes únicas aceptadas, prospectos creados, coincidencias pendientes y retiradas. Muestran origen/campaña declarados. No se inventan visitas, CTR, conversiones, indexación ni respuestas de proveedores. No se enviaron correos, campañas o mensajes reales. Los tres backends/frontends conservan sus carpetas, roles y datos; Turismo Nacional no se convierte en ERP.

Verificación final: 140 pruebas en 12 suites del perfil commercial-capture, todas aprobadas sin skips con fuentes finales estables; 192 comprobaciones Chromium a 1280/390 en SGA-CD, ERP, Analemática y su gateway. Incluyen formulario anónimo real, consentimiento opcional verdadero/falso, origen UTM, oferta, retiro y métricas, además de regresiones del constructor. ORM comprueba rollback completo, límites, revocación, otra empresa, prueba vencida/navegador distinto y preservación de autorización posterior. Además 13 pruebas de SQLite desechable, migraciones propias/fresh 0010 aplicadas sin deriva, restricciones únicas, publicación desechable, tipos seleccionados ERP, cuatro pruebas de preparación (incluido robots) y cinco de seguridad web. Evidencias, comandos, hashes y capturas: ANALISIS/gestion-comercial/evidencias/gc011-captacion-20261112/. Es un perfil acotado; no se presenta como regresión global ni resolución de la intermitencia previa de oportunidades GC-009.

Límites y aceptación pendiente: antispam básico sin garantía absoluta; la vigencia técnica actual de declaraciones es de 365 días, no una validación legal ni política de retención. Revisar aviso, vigencia, retención y derechos con la empresa real antes de publicar. Las firmas dependen de la llave de aplicación; cualificar rotación/soporte y derechos cuando un comprobante no esté disponible. Validar IP del proxy/NAT, capacidad/rate, PostgreSQL/concurrencia, restauración, TLS/dominio y rastreo/indexación en infraestructura objetivo. UTM continúa declarado y el correo no verificado. No queda desarrollo conocido pendiente en el alcance local delimitado; no se acredita aceptación real por los fixtures. GCH-031/032 verificados, GCH-033 pendiente: GC-011 conserva 2/3 hitos sin cierre integral. Comercial pasa de 15/72 a 17/72 = 23,61%, aceptación integral 1/24. Contabilidad separada sigue en 79,17% (57/72, 9/24). Sin commit, push ni despliegue.


### GC-012 · Biblioteca multimedia propia, derechos y originales · 2026-11-12 (America/Bogota)

Funcionalidad y pruebas locales terminadas. Biblioteca multimedia integrada en el CRM de SGA-CD, ERP y Analemática, con backends/frontends propios y permisos actuales de administrador con capacidad multimedia. No se fusionan carpetas o roles ni se incorporan rutas empresariales a Turismo Nacional. Se conservan WorkspaceAsset, ContentAsset y activos de cotización históricos; no se movieron ni reinterpretaron sus derechos automáticamente.

Originales y versiones: almacenamiento BLOB privado en la base del backend, original exacto y copia procesada separados, SHA-256 de ambos y versiones inmutables de contenido/derechos/marca. Descarga original con autenticación y empresa vigentes, nunca por la ruta anónima. Revisión de marca/licencia reutiliza el blob original; otra carga crea versión sin sobrescribir anteriores. Transacción y auditoría atómicas; falla revierte item y blobs. Si la copia procesada se corrompe, un original cuyo hash sigue íntegro permanece recuperable. Otra empresa no puede descargar originales, aprobar/publicar ni recuperar recibos privados del titular.

Procesamiento: PNG/JPEG/WebP y MP4/WebM; rechazo de PDF, XML, SVG y clasificación no comercial, sin rutas de archivos, URLs remotas ni IDs de bóveda fiscal. Las copias de imagen no conservan EXIF/textos/anexos; se corrige orientación y se preserva transparencia de logos. Video se decodifica/recodifica, elimina metadatos/capítulos/streams no seleccionados y limita protocolos, tamaño, duración y dimensiones. No se pretende detectar datos privados visibles en píxeles o audio: la revisión humana de la copia sigue siendo necesaria. Esta biblioteca no es un almacén fiscal de conocimiento cero.

Derechos y marca: titular, tipo/referencia de licencia, permiso web y vencimiento declarados; la autenticidad queda expresamente sin verificar. Licencia sin confirmar o vencida impide aprobar/publicar. Aprobación de derechos/privacidad y publicación son acciones separadas, con versión/revisión actual y permisos revalidados. Retirada y reintento idempotentes. La URL pública sirve solo la copia procesada de la versión publicada, con derechos vigentes y publicador autorizado; el original sigue privado. Una copia que el titular decide publicar es de acceso público. Cambiar el borrador no sustituye ni retira automáticamente la versión pública anterior: usar Retirar publicación cuando corresponda. El retiro local no borra copias ya descargadas por terceros.

Interfaz propia con marca/lema versionados y plantillas de composición cuadrada, vertical u horizontal; la vista previa no se presenta como un archivo renderizado/exportado. Original descargable, hashes, selección de versiones, cuotas y recuperación tras recarga, sin restaurar confirmaciones ni reenviar automáticamente. El vencimiento conserva la hora local de Bogotá al editar, sin ampliarlo por conversión UTC. Un rechazo conocido por derechos permite corregir los campos y guardar otra revisión. Identidad azul metalizado/azul claro/texto blanco. Límites: 8 MiB original, 16 MiB copia, imágenes de entrada hasta 16 MP con copia de hasta 2048x2048, videos hasta 120 segundos/1080p, 200 originales y 200 MiB de bytes originales/copias por empresa/prestador/sistema; 20 versiones y 200 revisiones ordinarias, con retirada final siempre permitida.

Hallazgo de publicación subsanado: el publicador de pruebas guardaba respaldos en el árbol fuente y alteraba el manifiesto durante la medición. Ahora los guarda en private-backups de la instalación, fuera de web, con directorio 0700 y archivos 0600. Se probó que publicar una copia desechable no altera los respaldos fuente, conserva configuración, es repetible y rechaza conflictos. Los respaldos históricos existentes se conservaron.

Validación final: 122 pruebas en 12 suites del perfil commercial-library, todas aprobadas sin skips sobre fuentes finales estables; 152 comprobaciones Chromium a 1280/390 y zona America/Bogota para los tres sistemas y el gateway. Incluyen pérdida de respuesta/reintento, recuperación tras recarga, original byte a byte, copia pública sin metadatos/anexo de prueba, marca/versiones, corrección de licencia y retirada. ORM verifica cuota, rollback, revocación y corrupción; decodificadores reales incluyen PNG/JPEG/paleta/EXIF y MP4/WebM. Además 13 pruebas SQLite desechables, migraciones propias/fresh 0011 aplicadas sin deriva, unicidad, publicación desechable con respaldos privados, tipos seleccionados ERP, cuatro pruebas de preparación y cinco de seguridad web. Evidencias/logs/hashes/capturas: ANALISIS/gestion-comercial/evidencias/gc012-biblioteca-20261112/. Perfil acotado, sin atribuir aprobación global ni corregir la intermitencia anterior de oportunidades GC-009.

Aceptación pendiente: licencias y contenido reales revisados por sus titulares; almacenamiento autorizado y política de roles, retención, protección en reposo y restauración; PostgreSQL/concurrencia/carga, revisión de decodificadores y despliegue/TLS en infraestructura objetivo. No se certifica copyright, DLP, almacenamiento soberano ni producción mediante fixtures. No queda desarrollo conocido pendiente del alcance local delimitado. GCH-034/035 verificados, GCH-036 pendiente: GC-012 tiene 2/3 hitos sin cierre integral. Comercial pasa de 17/72 a 19/72 = 26,39%, aceptación integral 1/24. Contabilidad separada continúa 79,17% (57/72, 9/24). Sin commit, push, CDN externa ni publicación de archivos de clientes reales.


### Auditoría GC-001 a GC-012 · 2026-11-12

Alcance: las doce tareas comerciales solicitadas (GCH-001 a GCH-036), sus criterios originales, módulos propios de SGA-CD/ERP/Analemática, ORM, APIs, gateway y recorridos web. Turismo Nacional conserva su identidad institucional. Se revisaron implementación, pruebas y aceptación por separado; no se convirtió existencia de código en cierre. Contabilidad y billetera conservan sus controles y mediciones independientes.

Fallos reproducidos y subsanados:

- Aislamiento de medios de cotización: los adaptadores Django filtraban por empresa, pero no por prestador. Otro prestador de la misma empresa podía obtener bytes conociendo el UUID. Ahora lectura, escritura y cuota incluyen prestador. Migración aditiva 0012 propia/fresh de ambos backends; filas históricas sin atribución quedan conservadas y bloqueadas, sin adivinar propietario ni borrar originales. La API exige la migración antes de usar medios. Falta una revisión legítima de titularidad para rehabilitar cada activo histórico.
- Integridad entre índices y documento: un digest válido del JSON no comprobaba por sí solo identidad/revisión/estado/código de la fila. Los stores propios revalidan esos vínculos y rechazan discrepancias con 503. La búsqueda de códigos incluye el código canónico del documento, evitando admitir otro registro porque se corrompió el índice. La consulta de política de capacidad usa esa misma protección. No se afirma resistencia frente a un administrador que reescriba todas las pruebas y respaldos.
- Landing bloqueada por rechazo definitivo: publicar sin aprobación devolvía 409 y dejaba el editor atado a una petición que nunca podía completarse. Chromium lo reprodujo antes de la corrección. Ahora los rechazos conocidos permiten corregir y confirmar de nuevo; conflictos desconocidos o de referencia y errores inciertos conservan recuperación con la misma referencia. Tres interfaces propias sincronizadas, sin rediseñar ni cambiar paleta; manifiestos de publicación actualizados.

Pruebas nuevas: seis casos ORM nativos y dos SQLAlchemy; manipulación independiente de índices, reserva de código canónico, identidad del documento y conservación/cuarentena de medios históricos. La regresión de landing añade ocho recorridos de rechazo y recuperación (tres sistemas y gateway, escritorio/móvil). La preparación inicial del fixture SGA necesitó corregir su método login; los dos casos finales pasan. El primer perfil fue interrumpido para incorporar estas correcciones; no se usa como evidencia de cierre.

Validación final: **540 pruebas en 57 suites**, todas aprobadas, sin skips, perfil commercial completo sobre fuentes finales estables. Los conteos de comprobaciones Chromium se conservan por recorrido en la evidencia y no se suman como nuevas tareas. Incluye contratos/roles, CRM, oportunidades, catálogo, cotizaciones, ventas, Bold parcial, posventa parcial, landings, captación, biblioteca, esquema/organización y runner. Migraciones 0012 aplicadas en SQLite desechable, ambas parejas canónica/fresh idénticas y modelos sin deriva; 153 comprobaciones de sintaxis y verificaciones adicionales de preparación/seguridad web. Las pruebas usan datos sintéticos, firmas de laboratorio y HTTP local: no acreditan PostgreSQL, concurrencia productiva ni autenticidad externa. El recorrido de oportunidades vuelve a verificarse, sin dar por resuelta la intermitencia histórica sin causa identificada.

| Tarea | Hitos acreditados | Implementado y probado | Pendiente real |
|---|---:|---|---|
| GC-001 | 3/3 | Aceptada para su contrato local | Sin pendientes del contrato/API y DAG definidos para GC-001. Las funciones de negocio y proveedores permanecen en las tareas correspondientes. |
| GC-002 | 0/3 | Desarrollo parcial; sin crédito de cierre | Pendiente de desarrollo: APIs e interfaz propias de administración de permisos/consentimientos, mapeo explícito de identidades entre sistemas y fuente revisada de consentimientos. Existen controles de acceso usados por los módulos; no constituyen cierre del recorrido de administración. Preservar roles nativos distintos y exclusión de Turismo Nacional institucional. Aceptación con usuarios y políticas revisadas pendiente. |
| GC-003 | 2/3 | Funcionalidad y pruebas locales acreditadas | Aceptación de uso con muestras consentidas y cierre de revisión de usuarios/políticas GC-002. Las migraciones se validaron solo en SQLite desechable; habilitación de servidor, datos históricos y producción requieren su cualificación. |
| GC-004 | 2/3 | Funcionalidad y pruebas locales acreditadas | Aceptación integral pendiente: dataset consentido y evaluación para scoring predictivo; validación con usuarios/datos y dependencias GC-002/GC-003. La prioridad por reglas se declara no calibrada; migración histórica y PostgreSQL/concurrencia productiva sin cualificar. |
| GC-005 | 2/3 | Funcionalidad y pruebas locales acreditadas | Aceptación integral pendiente: precios/condiciones/soportes legítimos y revisión tributaria profesional; usuarios y políticas de GC-002, revisión de migración histórica y cualificación productiva. El cálculo actual es estimación comercial y no acredita factura, pago ni aceptación fiscal. |
| GC-006 | 2/3 | Funcionalidad y pruebas locales acreditadas | Aceptación integral pendiente: condiciones/precios legítimos aprobados por empresa y revisión de aceptación/entrega al destinatario; dependencias GC-004/GC-005 y cualificación productiva de custodia/rotación, infraestructura, datos/concurrencia y restauración. La aceptación actual acredita posesión del enlace, no identidad verificada ni pago/reserva. |
| GC-007 | 2/3 | Funcionalidad y pruebas locales acreditadas | Flujo local de confirmación, operación, outbox/asiento y recuperación acreditado por su evidencia F/T. Pendientes aceptación de condiciones/soportes y reglas contables/laborales por actividad, identidad GC-002 y cualificación productiva/concurrencia. Factura DIAN y custodia auténticas pertenecen a sus integraciones; venta confirmada no acredita cobro. |
| GC-008 | 0/3 | Desarrollo parcial; sin crédito de cierre | Checkout e intenciones locales parciales, con importes canónicos y estados diferenciados. Pendiente de desarrollo: verificador del acuse Bold según contrato auténtico, consulta de estado del proveedor y conciliación/liquidación enlazada al asiento. Pendiente externo: contrato/accesos sandbox y acuses auténticos configurados por canal seguro. Retorno del navegador, hash declarado o enlace creado no prueban dinero. |
| GC-009 | 0/3 | Desarrollo parcial; sin crédito de cierre | Políticas versionadas y reembolso financiado interno parcial disponibles. Pendiente de desarrollo: vinculación verificable CRM/contacto/venta/reserva/destinatario, cancelación efectiva completa, recorrido de firma y fidelización integral. El reembolso bancario depende del cierre GC-008 y del proveedor. Pendientes políticas legítimas y aceptación de usuarios; el acceso personal a billetera no exige afiliación turística. |
| GC-010 | 2/3 | Funcionalidad y pruebas locales acreditadas | Constructor, versiones, previsualización, aprobación/publicación y retirada locales acreditados F/T. Pendientes aceptación de titulares/roles GC-002, revisión del contenido y cualificación de datos históricos, concurrencia y despliegue. Dominio/DNS/TLS y autorización si se usa dominio propio. |
| GC-011 | 2/3 | Funcionalidad y pruebas locales acreditadas | Captación local enlazada al CRM, origen canónico, consentimiento, baja, antispam, SEO y métricas de envíos aceptados acreditados F/T. Pendientes contenido/políticas de publicación legítimos, aceptación de titulares, retención y despliegue. No acredita titularidad del email, autorización de campañas, métricas de anuncios ni registro institucional/RNT. |
| GC-012 | 2/3 | Funcionalidad y pruebas locales acreditadas | Biblioteca local privada con originales exactos, copias procesadas, versiones, derechos declarados, marca y cuotas acreditada F/T. Pendientes licencias/contenido auténticos revisados, almacenamiento autorizado, política de retención y protección en reposo, restauración y cualificación PostgreSQL/concurrencia/decodificadores en infraestructura objetivo. Plantillas actuales son composición de vista previa, no exportación renderizada. |

Medición sin crédito nuevo: primeras doce tareas **19/36 hitos = 52,78%**, aceptación integral **1/12**. Plan comercial completo **19/72 = 26,39%, 1/24 aceptada**. No es porcentaje de producción. Las tareas 002, 008 y 009 mantienen desarrollo pendiente; las otras requieren su aceptación indicada antes del cierre integral. Se corrigieron textos obsoletos del campo missing sin cambiar criterios, dependencias, ponderaciones ni evidencias históricas. Contabilidad permanece 57/72 = 79,17%, 9/24 aceptadas; esta auditoría no acredita tareas contables.

Evidencia técnica, revisión individual y registros: ANALISIS/gestion-comercial/evidencias/auditoria-gc001-012-20261112/. Entrada única añadida al registro de entregas; hashes canónicos de todas las entradas anteriores preservados. Sin commit, push, pago real ni despliegue. El cierre de los pendientes externos necesita sus pruebas auténticas; no se sustituye por más fixtures.


#### Segunda revisión · Recuperación de resultados · 2026-11-12

Nueva revisión de las doce tareas comerciales contra sus criterios y la matriz vigente; se conservan los estados individuales de la tabla anterior. El delta técnico frente a la primera auditoría contiene 22 rutas de fuente y se conserva con hashes en la evidencia. No se alteraron los criterios, roles ni la separación de módulos. El backend de identidad administrativa GC-002, la confirmación/conciliación auténtica Bold GC-008 y el cierre integral de posventa GC-009 continúan con desarrollo pendiente. Las otras tareas conservan sus validaciones de aceptación pendientes; GC-001 mantiene únicamente su cierre del contrato local.

Falla reproducida: después de recibir confirmación del guardado, los editores de landing, biblioteca y CRM eliminaban la referencia antes de cargar el documento/listado. Una interrupción de esa lectura dejaba la operación guardada, pero sin recuperación disponible en la interfaz. Antes de corregir, Chromium reprodujo pérdida de la referencia (0 en vez de 1). Ahora la referencia permanece hasta completar la carga; el reintento de una operación ya confirmada solo consulta su resultado y no vuelve a enviar el POST. También se conserva ante rechazo/interrupción al consultar un recibo, y el control de ocupación se libera al terminar o fallar.

Aislamiento y recarga: las claves pendientes de landing y CRM incluyen sistema/empresa/prestador/actor, igual que biblioteca. El CRM propio transmite el prestador explícitamente. Referencias antiguas sin prestador se conservan para consulta de recibo con autorización vigente; no se atribuyen ni se reenvían automáticamente. Una huella SHA-256 local del comando exacto y, para cargas, de bytes/MIME originales, impide sustituir una petición pendiente por otra acción después de recargar. El reintento exacto conserva el UUID original. Solo se guardan referencia y huella: no textos, archivos, tokens ni casillas de aprobación. La huella no concede autorización; el servidor conserva sus controles. Se requiere HTTPS o localhost confiable para Web Crypto; sin esa capacidad no se inicia una escritura nueva.

Durante la primera regresión de esta revisión apareció un timeout al recuperar un contacto en la vista móvil del gateway. Se interrumpió el perfil y se conservó como ejecución no aprobada. Una repetición diagnóstica pasó; no se tomó como prueba de subsanación. Después se reprodujo un defecto de arranque con carga inicial retrasada: el formulario ya estaba habilitado antes de asignar la clave de recuperación, permitiendo guardar una referencia vacía o sin contexto. Ahora se resuelven clave/pendiente antes de mostrar una interfaz interactiva y se mantiene bloqueada hasta completar carga/recuperación. Una prueba determinista falla antes y pasa después en los tres clientes; 24 comprobaciones adicionales cubren arranque y recuperación CRM. Esto demuestra la corrección de esa carrera, sin atribuirle sin evidencia todos los timeouts históricos.

El siguiente perfil general terminó con 58 suites aprobadas y un fallo de cotizaciones: después de emitir, el panel regeneraba controles habilitados aunque seguía cargando sus imágenes. Un clic de generar enlace podía descartarse por estar la operación aún ocupada. Se reprodujo con una respuesta de imagen retrasada y se corrigió haciendo que los controles regenerados hereden el bloqueo hasta completar la carga. La prueba falla antes y pasa después en los tres clientes (9 comprobaciones). Se revalidaron las pruebas afectadas de cotizaciones (ORM, SGA, HTTP, navegador, entrega y ejecutor) tras esa corrección.

Validación final **compuesta**: **559 pruebas en 61 suites únicas**, todas con evidencia aprobada, sin skips; combina la pasada general y la revalidación de los componentes afectados. **No es una única pasada general verde sobre el mismo árbol final.** Los hashes comprueban que entre ambas solo cambiaron la interfaz de cotizaciones, sus pruebas/registro de ejecución y manifiestos; el código de negocio backend y los demás componentes no cambió. Se conservan ambos reportes originales, incluido el fallo, y la relación de fuentes/resultados. **93 comprobaciones nuevas** de DOM real (60 de landing/biblioteca, 24 de CRM y 9 de cotizaciones) de los tres clientes con transporte controlado. Incluyen guardado confirmado seguido de fallo de lectura, reintento sin otro POST, referencia de otro prestador intacta, fallo al recuperar, cambio de acción bloqueado y reintento exacto tras remontar con el mismo UUID. Estas 93 no acreditan un backend ni un proveedor auténtico. Los recorridos HTTP/Chromium existentes del CRM, oportunidades, catálogo, cotizaciones, venta, Bold parcial, posventa parcial, captación, landings y biblioteca se volvieron a ejecutar y sus reportes/capturas se conservan por tarea. La composición incluye 19 pruebas del runner, sin duplicar las suites repetidas. Doce verificaciones de sintaxis y paridad de los cuatro archivos cliente en las tres copias propias, más preparación/seguridad web. Se conservaron estructura y paleta azul metalizado/azul claro/texto blanco. Se corrigió la carrera de arranque reproducida; no se acreditó que cada timeout histórico del gateway u oportunidades tuviera esa misma causa ni su eliminación permanente.

Límites: una referencia antigua sin huella solo permite recuperar su recibo; si este no existe, necesita resolución revisada y no se reutiliza para una acción diferente. Las imágenes de cotización sin atribución legítima siguen preservadas y bloqueadas. No se validaron usuarios/licencias reales, PostgreSQL/concurrencia, cuentas bancarias, DIAN ni producción mediante estas pruebas. No se incorporaron funciones ajenas al alcance 1–12 ni se efectuaron publicaciones en servicios reales.

Porcentajes sin crédito nuevo: primeras doce tareas 19/36 = 52,78%, aceptación integral 1/12; plan comercial completo 19/72 = 26,39%, 1/24 aceptada. Contabilidad separada conserva 57/72 = 79,17%, 9/24. Evidencia técnica: ANALISIS/gestion-comercial/evidencias/auditoria-gc001-012-recuperacion-20261112/. Se preservaron los hashes de las 64 entradas anteriores del registro. Sin commit ni push.


#### Tercera revisión · Integridad de eventos · 2026-11-12

Se revisaron nuevamente los puntos comerciales GC-001 a GC-012 y sus 36 hitos, tomando como base los criterios y pendientes vigentes. Los estados de la tabla individual se mantienen: GC-001 aceptada para su contrato local; GC-002, GC-008 y GC-009 incompletas en desarrollo; GC-003 a GC-007 y GC-010 a GC-012 con funcionalidad/pruebas locales y aceptación pendiente. No se sustituyen roles ni se considera a Turismo Nacional un ERP. La matriz y los requisitos de proveedor/usuarios conservan su alcance.

Hallazgo reproducido: un documento de evento podía conservar un hash válido y, aun así, no corresponder a las columnas SQL usadas para localizarlo. Los adaptadores devolvían el JSON de la fila sin cotejar el UUID del evento, su empresa y su documento/recurso asociado. La prueba previa de ORM nativo falló en sus 32 casos de lectura/historial, con 80 aserciones fallidas, al alterar esos índices o el tipo JSON en datos desechables. No se presenta como una intrusión observada ni como protección frente a un administrador que reescriba todas las pruebas.

Corrección: cada backend conserva su verificador propio de vínculo evento/fila. Recibo por UUID, último evento e historial completo rechazan divergencias con error de dominio 503. El alta de eventos coteja su empresa antes de persistir y rechaza un evento ajeno sin insertar una fila. El acceso público a landing revalida también la fila del último evento. Se mantiene la validación criptográfica existente del documento/cadena; no se regeneran hashes ni se editan asientos o eventos históricos. El formato de auditoría CRM heredado es distinto: no se afirma que esta revisión le haya añadido un UUID dentro de sus eventos antiguos.

Aplicación en los ocho dominios propios de cada sistema: oportunidades, catálogo/tarifas, cotizaciones, ventas, intenciones de pago, landings, captaciones y biblioteca. Se conservan namespaces/tablas y backend/frontend separados. No hay migración ni borrado de datos. Los eventos existentes correctamente vinculados se leen igual; una discrepancia queda bloqueada para revisión y no se corrige silenciosamente. Las consultas Django de historial cargan únicamente los campos necesarios y mantienen lotes de 50 filas; SQLAlchemy conserva su iteración acotada.

Pruebas nuevas: **72 casos automatizados** (48 ORM nativos y 24 SQLAlchemy), repartidos entre ocho dominios por sistema. Cubren ID/empresa/recurso discrepantes con JSON cuyo hash no cambió, historial reasignado por índice, JSON malformado, rechazo de registro para empresa ajena y conservación del evento válido tras restaurar los índices del fixture. La preparación del fixture requirió incluir las tablas heredadas de oportunidades ERP y corregir la generación del bucle Python; las ejecuciones finales pasan. La manipulación y restauración ocurrieron solo en bases desechables, nunca en datos del usuario.

La pasada general detectó además un fallo de recuperación móvil de oportunidades. Se reprodujo un defecto del embudo con carga inicial retrasada: mostraba el formulario antes de leer su referencia pendiente y completar la lista, y descartaba referencias antes de cargar el resultado confirmado. Se corrigió en los tres clientes: referencia resuelta antes del formulario, controles bloqueados hasta estar listo, reintento de escritura confirmada que solo consulta, referencia por prestador y huella del comando exacto. Las referencias antiguas se conservan para consulta, sin reutilizarlas en otra acción. Las 21 comprobaciones nuevas de DOM real con transporte controlado fallaron antes y pasan después; no acreditan proveedor ni datos reales. Se revalidaron oportunidades en ORM/API/HTTP/Chromium y el CRM padre. Esto demuestra esa corrección concreta; no atribuye sin evidencia todos los timeouts históricos a esa causa.

Validación final compuesta: **631 pruebas en 64 suites únicas**, todas con evidencia aprobada y sin skips. Combina la pasada general con la revalidación de los componentes afectados; **no fue una única pasada general verde sobre el mismo árbol final**. Se conservaron el reporte general con su fallo y el de la revalidación posterior. Los hashes comprueban que entre ambas no cambió el código de negocio backend; los cambios finales quedaron acotados al embudo, su invocación desde CRM, sus pruebas/registro y manifiestos. Incluye contratos, permisos/contextos, CRM, oportunidades, catálogo, cotizaciones, venta/asiento/recuperación, Bold parcial, posventa/billetera interna parcial, landings, captación y multimedia. Se repitieron los recorridos HTTP y Chromium de los tres sistemas y gateway, con escritorio/móvil según cada suite, y las regresiones de arranque/carga retrasada/recuperación de la revisión anterior. La composición incluye 19 pruebas del ejecutor, sin duplicar suites repetidas; además pasaron 150 comprobaciones de sintaxis Python y las verificaciones de preparación/seguridad web. Los resultados de navegador se conservan por recorrido, sin sumarlos como tareas o como nuevas aceptaciones externas.

Evidencia: ANALISIS/gestion-comercial/evidencias/auditoria-gc001-012-eventos-20261112/. Incluye matriz individual de los 12 puntos, delta de fuentes, reproducción previa, pruebas nuevas, manifiesto/logs del perfil completo y capturas. La corrección frontend se acotó al arranque/recuperación del embudo y al paso de prestador desde CRM; no cambió ninguna hoja de estilos y se conservaron diseño, navegación y colores. Las 65 entradas anteriores del registro mantienen sus hashes canónicos. La regresión satisfactoria no demuestra que todos los timeouts históricos hayan desaparecido permanentemente.

Pendientes: siguen faltando administración completa de identidad/permisos GC-002, confirmación/consulta/conciliación auténtica Bold GC-008 y vinculación/cancelación/firma/fidelización integral de GC-009. En los otros puntos siguen aplicando sus requisitos de usuarios, contenido/licencias, condiciones comerciales, revisión profesional y cualificación de infraestructura/históricos/concurrencia indicados en la tabla vigente. No se han validado producción, PostgreSQL, cuentas/proveedores reales ni hardware mediante fixtures.

Medición sin crédito adicional: primeras doce tareas 19/36 = 52,78%, aceptación integral 1/12; plan comercial completo 19/72 = 26,39%, 1/24 aceptada. Contabilidad independiente sin cambios: 57/72 = 79,17%, 9/24. Las correcciones y pruebas adicionales no convierten una aceptación pendiente en un cierre. Sin commit, push, publicación externa ni movimiento de dinero real.


#### GC-013 · Inventario existente y generación privada · 2026-11-12

Se consultó el inventario existente antes de pedir más datos al usuario: BACKEND/IA/llm/manifest.json registra Gemma3 4B/Ollama y dos formatos de Phi3 Mini (ONNX y GGUF); esos formatos no prueban servidores activos. El router y Nodo6 documentan cinco familias: Ollama, Colibrí, Open Generative AI, SkyReelsV2 y Gemini/Nodo6. SkyReels corresponde a vídeo/GC-014. También existen referencias a phi3:mini y phi-4; no se confunden con modelos instalados aquí. Los hashes de blobs históricos no se usan como digest de modelo de /api/tags. El usuario dispone de Ollama; la sonda local de este entorno no encontró accesibles los cinco puertos predeterminados, lo que no determina el estado de su otro equipo.

Incremento escrito en cada backend propio: perfiles por sistema/empresa/prestador, cola persistente y trabajador optativo, cuotas y presupuesto estimado LOCAL_CREDIT (sin afirmar gasto monetario), comprobación de identidad del modelo, resultados privados, revisión humana separada y auditoría con integridad. Adaptadores para Ollama, Colibrí, SD-WebUI, Nodo6 texto/imagen y Open Generative AI; los gateways remotos requieren autorización explícita ligada al perfil. No hay fallback ficticio, ejecución de shell ni publicación automática. Se añadieron migraciones 0013 propias/frescas y controles de generación en los tres clientes, conservando estilos. La configuración de ejemplo queda en generation-runtime.env.example dentro de cada pool08. Los workers están apagados por defecto. SOUP conserva su función optimizadora.

Hallazgos subsanados: el router heredado presentaba un archivo de imagen inexistente o texto de reserva como éxito; ahora declara indisponibilidad o contenido no verificado. El endpoint heredado distingue borrador de renderizado/programación ejecutados. La prueba HTTP detectó que el gateway de Analemática rechazaba las rutas nuevas; se añadió su lista permitida y el límite de descarga privada. Se conservan autenticación nativa, permisos propios y aislamiento.

Verificación acotada: 85 pruebas en seis suites aprobadas (42 nativas, 20 SGA, 6 HTTP incluyendo comprobaciones heredadas del fixture, 11 del endpoint heredado, 2 sin fallback y 4 de preparación web). Migración fresca SQLite y ausencia de divergencia de modelos comprobadas; sintaxis de 24 módulos de generación y tres scripts cliente comprobada. Las respuestas de modelos de las pruebas fueron controladas, no inferencia real. Evidencia: ANALISIS/gestion-comercial/evidencias/gc013-generacion-20261112/incremento.json, logs y sonda de disponibilidad. No es una regresión completa de toda la aplicación.

Pendiente antes de acreditar GC-013: recorridos completos de navegador y tipos ERP, arranque/despliegue del trabajador e incorporación a la regresión reproducible, inferencia auténtica con Ollama accesible, generador real de imágenes y revisión de licencias/calidad/privacidad/costos. No se activa automáticamente un proveedor por existir en la documentación. Sin crédito nuevo: comercial 19/72 = 26,39%, aceptación 1/24; contabilidad independiente 57/72 = 79,17%, 9/24. Sin commit ni push.


#### GC-014 · Composición local de vídeos/Reels · 2026-11-12

Incremento propio en SGA-CD, ERP y Analemática: compositor FFmpeg con MP4 H.264, formatos vertical 360×640, cuadrado 480×480 y horizontal 640×360; marca y textos de escenas temporizados, paleta azul/azul claro/blanco. Hasta seis escenas y treinta segundos; son resoluciones de previsualización, no se acredita master publicitario HD. No se afirma generación visual por IA, reconocimiento de voz ni subtitulado automático de habla. La división creativa sigue bajo Jarvi; SOUP conserva su optimización.

La voz grabada y la música se extraen únicamente de MP4 privados de la biblioteca de la empresa/prestador, con versión y hash exactos, revisión y derechos declarados vigentes. Se comprueban duración y pista de audio, se mezcla música atenuada cuando existen ambas fuentes y se vuelven a validar fuentes bajo el bloqueo de empresa antes de persistir el resultado. Las pruebas de mezcla usan tonos sintéticos, no voces humanas autorizadas. No hay clonación de voz ni certificación de derechos.

Los trabajos reutilizan la cola durable, presupuesto estimado, recibos idempotentes, permisos nativos y auditoría de GC-013. Se exige además media.reel.render. El trabajador está deshabilitado por defecto; el perfil ffmpeg-composition necesita configuración explícita por empresa. Su huella vincula código del compositor, versión de FFmpeg, tipografía y Pillow; puede obtenerse ejecutando el módulo propio video_composition, sin habilitar trabajadores. El cliente incorpora formulario por escenas, fuentes de biblioteca, reproducción y descarga privadas y revisión humana separada. No publica ni programa contenido.

Hallazgo reproducido y corregido: la concatenación de imágenes recortaba un vídeo de dos segundos a aproximadamente uno; se añadió conversión explícita de fotogramas y extensión de la última imagen. FFprobe comprueba códec, dimensiones, duración y presencia de audio antes de guardar. Las pruebas también rechazan cambio del renderizador, referencias ajenas, audio sin revisión, cambios de derechos, plan/manipulación de herramientas, exceso de duración y vencimiento del proceso, sin producir éxito ficticio. Se mantienen límites de bytes, CPU, tiempo y protocolos locales, sin shell ni URL aportada por el usuario.

Una pasada consolidada del perfil commercial-video: **141 pruebas en 12 suites**, todas aprobadas y fuentes estables; incluye **36 comprobaciones Chromium** adicionales de los tres clientes, en vista móvil, con transporte controlado y reproducción de un MP4 real. Los recorridos HTTP prueban cola, recibos, reintento exacto, cancelación, acceso ajeno y ausencia de un endpoint público de trabajador en los tres backends y gateway. Los casos ORM ejecutan el compositor real, conservan resultado privado y registran revisión. No se presenta la combinación de estas pruebas separadas como un recorrido único navegador-HTTP-trabajador independiente ni como aceptación de usuarios reales. Regresiones de generación y biblioteca previas incluidas; no es la suite general de toda la plataforma. Evidencia, capturas y MP4 demostrativo: ANALISIS/gestion-comercial/evidencias/gc014-video-20261112/.

GC-014 permanece **en ejecución**, sin crédito de cierre: falta completar/calificar el adaptador separado de vídeo generativo (SkyReels), arranque independiente y recorrido integral del trabajador en destino, y aceptación de contenidos/derechos reales. Ollama disponible por sí solo no acredita un generador de vídeo. No se acreditan GPU, proveedores, voces o licencias por usar tonos de laboratorio. La matriz conserva 19/72 = 26,39%, aceptación comercial 1/24; contabilidad independiente sin cambios, 57/72 = 79,17%, 9/24. Se preservaron las 66 entradas anteriores del registro. Sin commit ni push.


#### GC-015 · Tamaños y formatos reales de multimedia · 2026-11-12

Problema: el selector de plantilla de la biblioteca solo cambiaba la composición visual, sin producir un archivo con dimensiones de entrega. Se añadieron módulos propios media_adaptation.py en los tres backends y controles en sus tres clientes. Perfiles locales inmutables por identificador/versionado 1.0: imágenes PNG 1080×1920, 1080×1080 y 1920×1080; vídeo MP4 H.264 720×1280, 720×720 y 1280×720. No se certifican perfiles actuales de ninguna red. El recorte centrado exige confirmación; las bandas conservan todo el encuadre. La ampliación es optativa y se declara sin mejora de detalle ni reencuadre neuronal. Se respeta la relación de aspecto de píxeles anamórficos.

Contratos de imagen y vídeo separados por tipo/perfil: imagen sin audio; vídeo con conservar o silenciar audio. La política de subtítulos es explícita: conserva los textos quemados como píxeles, avisa de su posible pérdida al recortar y no exporta pistas de texto ni inventa transcripción. El vídeo se recodifica con pérdida (CRF 23, H.264/AAC); no se afirma copia bit a bit ni calidad superior. Límite local de salida 16 MiB y fuente de hasta 120 segundos, con cotas existentes de entrada, resolución, almacenamiento, tiempo y procesos. Se verifican bytes, dimensiones, códec, duración y audio reales antes de guardar. No hay shell, URL de entrada ni conexión a un proveedor.

Cada adaptación parte del original preservado y crea una versión privada con perfiles, decisiones, dimensiones y huellas; invalida la aprobación de la copia nueva y mantiene intacta una versión pública anterior. Se calcula fuera del bloqueo y se vuelve a comprobar empresa, permisos, revisión y huella de la fuente bajo transacción antes de guardar blob/versión/auditoría atómicamente. Los UUID ajenos se rechazan antes de comparar la huella de reintento. Se comprobó rollback por fallo de auditoría, fuente modificada durante procesamiento, tipos/perfiles manipulados, cuotas, ampliación sin consentimiento, acceso ajeno y revocación real de identidad. La adaptación respeta el máximo existente de 200 revisiones; se probó con un historial real hasta ese límite. No hay migración de tablas ni modificación de versiones históricas.

Interfaz: selector de perfil por tipo, bandas/recorte, consentimiento de ampliación y recorte, audio, dimensiones/peso de la copia, vista previa y descarga del original privado. Preserva estructura y azul metalizado/azul claro/texto blanco; se inspeccionó captura móvil de Analemática. Los recorridos completos navegador→HTTP→backend ejecutan adaptaciones reales de imagen/vídeo en SGA-CD, ERP, Analemática y gateway, a 1280 y 390 px. Incluyen pérdida de respuesta confirmada, reintento con UUID idéntico, recuperación tras recarga, descargas con hash del original intacto y ausencia de publicación automática. No son mocks de resultados.

Validación final: **131 pruebas en 14 suites** aprobadas en una pasada del perfil commercial-adaptation sobre fuentes estables, con **168 comprobaciones nuevas de navegador y 152 de regresión de biblioteca**, separadas del conteo unittest. Incluye regresiones de decodificación, biblioteca y composición GC-014. Comprobaciones adicionales reales de WebM/Opus→MP4/H.264/AAC y orientación EXIF de JPEG. La pasada exploratoria anterior aprobó sus suites, pero quedó invalidada como cierre por el cambio final del límite de revisiones; se conserva su reporte con source_stable=false y no se suma a los conteos finales. No es una prueba de toda la plataforma. Evidencias, capturas, logs y MP4: ANALISIS/gestion-comercial/evidencias/gc015-adaptacion-20261112/.

Se acreditan únicamente GCH-043 (funcionalidad local) y GCH-044 (verificación). GC-015 queda implementada/verificada localmente, con GCH-045 pendiente: perfiles vigentes de cada red, rendimiento/concurrencia e infraestructura objetivo, derechos/contenidos y aceptación de usuarios reales. No se afirma aprobación por Meta/TikTok/YouTube ni rendimiento productivo. Comercial: **21/72 = 29,17%, aceptación completa 1/24**. Contabilidad independiente sin cambios: 57/72 = 79,17%, 9/24. Se conservan los hashes de las 67 entradas anteriores del registro; sin commit ni push.


#### GC-016 · Correos masivos y campañas email · 2026-11-12

Implementación propia en los tres backends y clientes, conservando roles, empresa/prestador y carpetas: borradores persistentes, plantillas Carta/Aviso con HTML escapado y texto, personalización limitada a nombre/empresa, segmentos estáticos seleccionados del CRM, exclusiones y deduplicación por correo. Máximo local de 100 destinatarios y 50 campañas por ámbito. No se habilita envío al guardar. Primera confirmación de contenido/audiencia y segunda confirmación de impacto/programación del mismo administrador; agenda en UTC y cuotas diarias verificadas por el trabajador. Este selecciona primero campañas cuyo horario ya venció, evitando que campañas futuras ocupen el lote. Los clientes históricos customer:… de ERP/Analemática conservan su referencia y consentimiento; sus identificadores no se insertan literalmente en Message-ID.

Persistencia y control: tablas EmailCampaignRecord/EmailCampaignEvent propias, migración aditiva 0014 por app y copia fresca; instalación explícita SGA. Estados/auditoría con hashes y vínculo de fila, UUID de comando idempotente, recibos recuperables y bloqueo por empresa. Consentimiento EMAIL:MARKETING vigente, dirección y huella de consentimiento se revisan de nuevo antes de despachar; también perfil autorizado y permisos actuales. Supresiones durables por dirección, motivo y hash de soporte, sin subir el archivo de soporte desde el cliente. La baja pública tiene prueba HMAC acotada a empresa/campaña/destinatario, no revela correo en la URL, GET solo confirma y POST bloquea pendientes. Sigue operativa después de revocar al administrador; no permite consultar campañas ni enviar mensajes. Un mensaje ya despachado no puede retirarse.

Transporte disponible: SMTP exclusivamente de loopback:1025, optativo y deshabilitado por defecto. Los comandos propios run_commercial_email_campaigns y el módulo email_campaign_worker exigen COMMERCIAL_EMAIL_WORKER_ENABLED=1 y política de remitente por ámbito; ejemplo email-campaign-runtime.env.example dentro de cada pool08. No se configuró ni ejecutó un relay a cuentas reales. Cada destinatario se reclama durablemente antes de SMTP y se comprueban permisos/consentimiento/supresión bajo bloqueo antes de enviar; un resultado incierto no se reenvía automáticamente. Recuperación tras interrupción marca incertidumbre para revisión. SMTP aceptado se registra como ACCEPTED, nunca como SENT/DELIVERED/OPENED. Recibos de adaptador normalizado tienen clave independiente, firma, evento único, Message-ID/fecha/orden comprobados y fuente declarada; rebote/queja reportados suprimen otros pendientes. No se acredita autenticidad de un proveedor por poseer una clave de laboratorio. No existen píxeles ni aperturas inventadas.

Interfaz homologada: acceso desde CRM, audiencias/exclusiones, creación, vista previa HTML aislada en iframe sandbox, confirmaciones separadas, fecha local convertida a UTC, cancelación y estado por destinatario. Entregas se muestran como reportes del adaptador, no certificaciones. Se conserva azul metalizado/azul claro/texto blanco y la navegación existente. Los recorridos web reales incluyen escritorio y móvil de SGA-CD, ERP, Analemática y gateway; la pérdida de respuesta y recuperación por UUID no duplican el comando ni envían correo.

Hallazgos corregidos: el servicio heredado imprimía/logueaba «enviado» y retornaba True sin transporte; ahora retorna False y no imprime destinatario/asunto. Su prueba histórica se ajustó al rechazo correcto y se agregó una regresión aislada; no se ejecutó toda aquella suite pytest ni se acredita envío histórico. Un botón regenerado tras programar podía habilitarse mientras seguía la lectura; ahora conserva el bloqueo, probado con lectura retrasada. La selección inicial rechazaba alias históricos del CRM: la prueba reprodujo dos errores nativos antes de corregir referencias y rutas de preview/baja. La selección de lote también descarta campañas futuras antes de aplicar el límite.

Verificación final: **127 pruebas en 12 suites** del perfil commercial-email y **168 comprobaciones Chromium** (80 de campañas y 88 de regresión CRM), aprobadas en una pasada sobre fuentes estables. Incluye SMTP real contra un sumidero local que no reenvía, mensajes separados sin Bcc, recepción/HTML/texto, bajas tras revocación, cancelación, cuotas, consentimiento modificado, incertidumbre, firmas/replay y rebotes reportados. Solo direcciones example.test y datos sintéticos. Migración 0014 aplicada en SQLite desechable y sin divergencia de modelos. Las pasadas intermedias y el fallo anterior de alias se conservan sin sumarlos a los conteos finales; dos pasadas intermedias quedaron invalidadas como cierre por cambios posteriores de fuentes. No es una regresión completa de la plataforma. Evidencia: ANALISIS/gestion-comercial/evidencias/gc016-correos-20261112/.

Se acreditan GCH-046 y GCH-047, funcionalidad y pruebas locales. **GCH-048 pendiente**: remitente/dominio legítimos, proveedor/OAuth o relay autorizado, identidad/derechos/consentimientos reales, cuotas y reputación, validación de recibos auténticos y sus órdenes/resultados inciertos, rotación/retención de claves y aceptación en infraestructura objetivo. No se promueven métricas heredadas ni se habilita producción. Comercial: **23/72 = 31,94%, aceptación completa 1/24**; contabilidad separada permanece 57/72 = 79,17%, 9/24. Las 68 entradas anteriores del registro mantienen sus hashes. Sin commit ni push.


#### GC-017 · SMS, MMS celular y WhatsApp multimedia · 2026-11-12

Se añadieron módulos, tablas, APIs, trabajador y controles propios en SGA-CD, ERP y Analemática, conservando identidad y carpeta de cada sistema. Adaptadores separados twilio-sms, twilio-mms y meta-whatsapp: SMS usa únicamente Body; MMS celular añade MediaUrl; WhatsApp usa plantilla declarada con nombre/idioma, encabezado imagen/vídeo y cuerpo parametrizado. No se convierte automáticamente un canal en otro. Un SMS con enlace solo se prepara cuando el usuario elige ese modo y confirma la alternativa, la política lo permite y existe una copia pública revisada de su biblioteca. No es un adjunto SMS. No se acepta una URL externa arbitraria en el texto para eludir ese control. Las imágenes/vídeos se atan a versión, hash, derechos declarados y publicación vigente; se comprueban tipo, bytes y duración según perfil. La cabecera y la vista declarada del cuerpo de WhatsApp quedan visibles para revisar; la autenticidad de aprobación externa no se certifica.

Consentimiento independiente SMS/MMS/WHATSAPP: una autorización SMS no habilita MMS ni WhatsApp. Se exige móvil colombiano en E.164, contacto de la propia empresa/prestador y permiso específico del canal; se conservan alias históricos customer:… en los backends nativos. Borrador sin red, primera confirmación de contenido/destinatario y segunda confirmación del mismo administrador con impacto/estimación aprobados. Segmentación GSM-7 y UCS-2/UTF-16, incluidos caracteres de extensión y emoji; límites de segmentos, medios y cuota local diaria UTC. Los importes COP son estimaciones declaradas por operador, no precios verificados, cargos efectivos ni asientos contables. El coste real permanece desconocido.

El trabajador y la red están deshabilitados por defecto. Credenciales exclusivamente en variables de entorno vinculadas por perfil/ámbito; hosts de API fijos, sin redirects ni proxy heredado. Se reclama el trabajo durablemente antes de llamar al proveedor y se vuelven a validar permisos, consentimiento, política y medio bajo bloqueo. Timeout, redirect o acuse malformado producen incertidumbre, sin segundo intento automático. La recuperación tras interrupción exige revisión después de 15 minutos. Las bajas se conservan por canal y bloquean otros pendientes de ese ámbito. Los recibos normalizados usan firma, ID de evento, ámbito y Message-ID comprobados; entrega/lectura no se deducen de aceptación. SMS/MMS no admiten lectura inferida. WhatsApp puede registrar lectura únicamente como reporte firmado, sin inventar envío/entrega anteriores. Estas firmas pertenecen al adaptador normalizado; no sustituyen validar las firmas nativas Twilio/Meta ni cualifican su autenticidad.

Interfaces propias: selección de canal/modo/contacto/activo, vista de texto/plantilla/remitente y estimación, dos confirmaciones, cola, cancelación, auditoría y recibo visible. Se conserva la estructura y CSS azul metalizado/azul claro/texto blanco. Se añadió recuperación de validaciones conocidas de enlaces para corregir una autorización omitida sin quedar bloqueado con un UUID no confirmado; también se evita escribir referencias nuevas desde un panel ya descartado. Los recorridos reales navegador→HTTP→backend cubren tres canales y SMS con enlace, escritorio/móvil, SGA-CD/ERP/Analemática/gateway, pérdida de respuesta, reintento exacto, recuperación tras recarga, presupuesto, auditoría y cancelación. No ejercitan un teléfono ni un proveedor real.

Persistencia: MobileMessageRecord/MobileMessageEvent propios; migración aditiva 0015 por app y copia fresca, más instalación explícita SGA. Se aplicó en SQLite desechable sin divergencia de modelos; no se cualifica PostgreSQL ni se alteran datos históricos. Configuración deshabilitada en mobile-messaging-runtime.env.example y esquema ilustrativo mobile-policy.example.json dentro de cada pool08. Los comandos propios run_commercial_mobile_messages exigen habilitación explícita. Los ejemplos no son cuentas, plantillas ni pruebas de cobertura autorizadas. Jarvi sigue operativo, Neko conversacional y SOUP optimizador; no se habilitaron herramientas autónomas ni se cambiaron roles. Turismo Nacional conserva su condición institucional.

Verificación final: **175 pruebas en 13 suites** y **344 comprobaciones Chromium** (256 de mensajería y 88 de regresión CRM), todas aprobadas en una pasada acotada sobre fuentes estables. Se ejecutó además la regresión de correo. Las pruebas de adaptador usan **httpx.MockTransport**: las URLs api.twilio.com/graph.facebook.com de los logs no son conexiones a esos proveedores. Se probaron por contrato imagen/vídeo MMS/WhatsApp, SMS sin adjuntos, alternativa por enlace solo autorizada, cabecera de plantilla, consentimiento separado, cuotas, claves/rol revocados, medios retirados, límites, Unicode inválido, rollback, firmas y falta de reenvío ante incertidumbre. Las llamadas HTTP reales son locales contra backends desechables; el SMTP de la regresión de correo usa un sumidero local sin reenvío. No se enviaron SMS, MMS, WhatsApp ni correos a destinatarios reales. Las ejecuciones previas se conservan sin sumarlas; una intermedia quedó invalidada como cierre por cambios posteriores de fuentes. Evidencias: ANALISIS/gestion-comercial/evidencias/gc017-mensajeria-20261112/. No es una regresión completa de la plataforma.

Se acreditan **GCH-049/GCH-050**, código y verificación locales; **GCH-051 continúa pendiente**. Para aceptación real: proveedor telefónico y cobertura MMS demostrable hacia Colombia (no se presume de Twilio), cuenta/plantillas/idioma/medios WhatsApp aprobados, destinatarios y consentimientos legítimos, mapeo/firmas nativas/tiempos y alcance de bajas del operador, precios/cuotas/facturación reales e infraestructura objetivo. Si un proveedor no soporta MMS a Colombia, esa capacidad seguirá no disponible; no se reemplaza silenciosamente con SMS o WhatsApp ni se cambia el alcance aceptado. Comercial: **25/72 = 34,72%, aceptación completa 1/24**. Contabilidad independiente permanece 57/72 = 79,17%, 9/24. Se preservaron los hashes de las 69 entradas anteriores. Sin commit ni push.


#### GC-018 · Publicación orgánica y calendario · 2026-11-12

Problema: no existía una cola comercial homologada propia con calendario y recibo por destino. El servicio antiguo de SGA devolvía éxito con una subida privada de YouTube y Meta construía una URL con post_id_placeholder. Se deshabilitaron sus entradas directas: requieren usar el calendario revisado; no se borraron componentes externos ni se hicieron publicaciones reales.

Código: PublishingRecord/PublishingEvent, API privada, migración aditiva 0016, instalación SGA explícita y trabajador propios en los tres backends. Cada trabajo enlaza una cuenta configurada, formato, visibilidad explícita y versión/hash de la copia pública revisada en biblioteca. DRAFT → REVIEWED → SCHEDULED exige dos confirmaciones separadas del mismo administrador, conserva cancelación, revisión optimista, UUID idempotente y auditoría encadenada. Las fechas se convierten a UTC; la interfaz indica la hora del equipo. El calendario filtra vencimiento antes de limitar. Guardar/programar no hace solicitudes externas.

Formatos implementados: Facebook foto PNG/JPEG de biblioteca, Instagram Reel MP4 vertical 9:16 desde720px y3–120s, YouTube MP4 y TikTok MP4 hasta120s, sujetos al límite más estricto del creador. Imágenes hasta5MiB y vídeos hasta16MiB. La biblioteca entrega PNG saneado para imagen. No se afirman todos los formatos posibles de cada plataforma. Contenido orgánico sin promoción de marca/patrocinio; publicidad/disclosures ampliados no se activaron. Visibilidad pública, privada o no listada solo donde el perfil lo admite; TikTok privado completado sin prueba suficiente queda REMOTE_REVIEW, no se presenta como publicación pública.

Transporte: destinos API fijos, Bearer en cabecera, límites de tiempo/tamaño, sin redirecciones/proxies heredados ni claves en DTO/log. Perfiles versionados por sistema/empresa/prestador y referencias de secreto en entorno; derechos/propiedad documentales declarados no se certifican por un hash. Se consulta identidad/cuenta con el proveedor antes de mutar. Claim persistido antes de red, revalidación de autoridad/perfil/activo y checkpoint de contenedor Instagram antes de media_publish. Un ID de subida pasa a VERIFY; solo lectura explícita del objeto remoto, cuenta y estado acreditan PUBLISHED o REMOTE_PRIVATE. Un HTTP200 genérico nunca lo hace. Timeout, ACK sin ID, fallo al persistir después de subida o recuperación de mutación interrumpida quedan inciertos y no se reenvían automáticamente. Revisión de lease a15min; consultas a30s, máximo60; cuota local UTC por cuenta y límite global500 trabajos activos. No se presentan esos límites como cuotas/garantías de los proveedores.

Interfaz propia de SGA-CD/ERP/Analemática con entrada desde CRM, selección de activo/formato/visibilidad, dos confirmaciones, fecha, recibo/estado, auditoría, cancelación y recuperación exacta tras pérdida de respuesta. Se conservaron navegación y colores azul metalizado/azul claro/blanco. La revisión visual encontró desbordamiento de las pruebas de auditoría en móvil; se corrigió y se verificó ausencia de desplazamiento horizontal. Jarvi permanece operativo, Neko conversacional y SOUP optimizador; no se habilitaron acciones autónomas ni se alteraron roles. Turismo Nacional sigue institucional.

Pruebas: **163 pruebas en 12 suites**, más **64 comprobaciones Chromium de publicación** y la regresión CRM incluida en el manifiesto. Pasada final sobre fuentes estables, con SQLite/HTTP desechables. Se comprueban las etapas por contrato de los cuatro adaptadores usando **httpx.MockTransport**; las URLs sociales de los logs no son conexiones reales. Los vídeos de biblioteca son MP4 generados por ffmpeg en laboratorio. Se aplicó0016 en ambas apps frescas, sin divergencia de modelos. La ejecución intermedia se conserva, no se suma ni acredita cierre porque hubo correcciones posteriores. Evidencias automáticas: ANALISIS/gestion-comercial/evidencias/gc018-publicacion-20261112/.

Se acreditan GCH-052 yGCH-053 locales. GCH-054 sigue pendiente: aplicaciones OAuth, cuentas/dominio propiedad del cliente, permisos y revisión de aplicaciones, perfiles/versiones de API/formatos vigentes, recibos auténticos, visibilidad/moderación/latencias/cuotas y revocación reales. PostgreSQL, concurrencia/carga y aceptación productiva siguen sin cualificar. Trabajador/red están deshabilitados por defecto y los ejemplos no contienen credenciales. **GC-018 no está cerrada integralmente. Comercial:27/72=37,50%; aceptación completa1/24.** Contabilidad independiente:57/72=79,17%,9/24, sin cambios. Se conservaron las 70 entradas previas del registro con sus hashes. Sin commit ni push.


#### GC-019 · Bandeja omnicanal y respuestas · 2026-11-12

Problema: Meta archivaba eventos firmados en plataforma sin enrutamiento empresarial/contacto; no existían hilos/revisiones/respuestas homologados propios en las tres aplicaciones. Se conservó ese archivo, sin inferir empresas por identificadores o compartir sus secretos. Se añadieron InboxRecord/InboxEvent, migración0017 e instalación explícita SGA, APIs privadas, bandeja y trabajador propios.

Cada hilo separa empresa/prestador, cuenta, canal, hilo remoto e interlocutor. Entrada normalizada con HMAC por ámbito/cuenta, UUID y deduplicación de mensaje; cambio de cuerpo, canal o participante se rechaza. No crea contactos ni responde a desconocidos: se exige vínculo CRM con revisión de identidad y responsable miembro actual. Borrador visible tras recarga, revisión de contenido/hilo y confirmación de impacto separadas del mismo administrador; una nueva entrada invalida revisiones pendientes. Se revalidan contacto activo, canal, pertenencia, perfil y ancla antes de salida. DM y WhatsApp respetan una ventana local de24h. Texto/HTML recibido se muestra como texto; no se cargan adjuntos ni enlaces externos.

Respuestas de texto implementadas por contrato para Facebook/Instagram DM, comentarios Facebook/Instagram, Gmail, WhatsApp y comentarios YouTube. Solo a cuenta/hilo/parent/destinatario vinculados; comprobación de cuenta propietaria y del padre público. Gmail consulta el hilo real, coteja From/Message-ID, construye texto MIME con In-Reply-To/References y exige threadId del acuse. Se registra ACCEPTED con identificador ligado al destino, nunca entrega. Claim persistente antes de red; timeout,200 sin identificador, destinatario distinto o fallo posterior conservan incertidumbre sin reenvío automático. Recuperación a15min conserva el texto de resultado incierto. Los bloqueados no consumen el lote del trabajador y no impiden procesar el siguiente autorizado. TikTok DM/comentarios: derivación humana, sin API inventada.

Recepción específica: importación privada del cuerpo original Meta, verificación HMAC antes de JSON y mapeo explícito de ID de cuenta. Admite un evento de texto DM/WhatsApp o comentario añadido FB/IG; cuerpo máximo8KiB, lotes/eco/no-texto se rechazan para revisión. El adaptador normalizado no se presenta como firma nativa. Gmail/YouTube disponen de lectura OAuth explícita y acotada a10 elementos: buzón propio, texto plano sin adjuntos, comentarios superiores de canal propio; sin marcar leído ni responder. Se informa si hay más página y no se afirma sincronización histórica completa. El puente autenticado desde callbacks/archivo de plataforma, lotes, contenido no textual, backfill y comentarios anidados siguen pendientes; no se ocultan como cuentas configuradas. Fuente/protocolo firmado no demuestra identidad legal del remitente ni cuenta real cualificada.

Interfaz integrada desde CRM en SGA-CD/ERP/Analemática y gateway: bandeja, texto recibido, vínculo, responsable, borrador persistido, confirmaciones, cola, cancelación, derivación, cierre y auditoría acotada visualmente. Se corrigió el paso de la firma por el gateway y se verificó la revisión optimista cuando gateway y Analemática comparten el mismo hilo real. Se conservan azul metalizado/azul claro/blanco, navegación y roles; no se dota a Turismo Nacional de un ERP. Jarvi operativo, Neko conversacional y SOUP optimizador; respuesta automática deshabilitada.

Verificación: **131 pruebas en11 suites**, **88 comprobaciones Chromium de bandeja**, más regresión visual de publicación y CRM consignada en el manifiesto. SQLite/HTTP/Chromium desechables, firmas nativas/normalizadas con claves sintéticas y transporte de proveedor httpx.MockTransport: los URLs externos de logs no son conexiones reales. Se aplicó0017 en ambas apps sin divergencia de modelos. Una pasada anterior quedó invalidada como cierre por ampliar recepción; se conserva sin sumar conteos. Evidencias: ANALISIS/gestion-comercial/evidencias/gc019-bandeja-20261112/.

GCH-055/GCH-056 acreditados para este alcance funcional local; GCH-057 pendiente de evento/cuenta/permiso/recibo auténticos, puente de callbacks y cualificación de campos/ventanas/API, datos e identidad legítimos, privacidad/retención/cifrado de operación, PostgreSQL/concurrencia y aceptación productiva. Workers, red y lectura de fuentes deshabilitados por defecto; no se enviaron respuestas reales. Comercial **29/72=40,28%, aceptación completa1/24**. Contabilidad permanece57/72=79,17%,9/24. Se preservaron las71 entradas previas y sus hashes. Sin commit/push.


#### GC-020 · Pauta, presupuestos y A/B · incremento parcial · 2026-11-12

Se continúa después de GC-019 local. Hallazgo: las lecturas/borradores Meta existentes no conceden permiso ni implementan ejecución de pauta homologada. Se implementaron AdsRecord/AdsEvent, migración0018 y APIs/interfaces propias en SGA-CD, ERP y Analemática; no se trasladan módulos ni se depende de un backend SGA encendido.

Funcionalidad implementada y probada: planes separados Meta/TikTok/Google-YouTube con cuenta declarada por ámbito, creativos de la biblioteca revisada enlazados por versión/hash, titulares A/B y pesos20–80% que suman100. COP en enteros de centavos: se rechazan float/bool, fracciones de unidad mínima y distribución incoherente. Hasta30 días; límites versionados globales por empresa, no repetidos por cuenta/proveedor. Revisión de creativos/presupuesto y segunda confirmación de impacto del mismo administrador. La reserva planificada agrega total y diario de todos los planes reservados de la empresa bajo su bloqueo transaccional; se detectó/corrigió que limitar cada diario individualmente no bastaba. Cancelar libera exclusivamente planificación; no hay bloqueo de fondos ni asiento financiero, campaña remota o gasto registrado como real.

Observaciones manuales versionadas y acotadas a20 por plan, hash de soporte calculado en cliente, sin subir su contenido; origen/autenticidad declarados no verificados. Sugerencia determinista por CPC declarado cuando hay al menos100 clics por variante y diferencia superior al25%, con aritmética entera y pesos acotados. La sugerencia no modifica pesos/presupuesto, no acredita rendimiento real ni ROI y no es una prueba causal A/B. Sin datos suficientes lo informa. No se entrega esta función de pauta a SOUP: conserva optimización de agentes.

Motor existente, no una pregunta repetida sobre cuentas: se revisaron el conector, catálogo (meta.campaign, tiktok.campaign, youtube.ads), BrowserDriver/MobileDriver, verifyGrant y política de control del repositorio. La propuesta propia del plan enlaza sistema/empresa/prestador, ID/revisión/digest y el contrato versionado Open Duet+agent-desktop. Jarvi operativo, Neko conversacional, SOUP optimizador. Propone apertura/observación en orígenes oficiales; no contiene referencias de elementos inventadas, claves, firma ni permiso de gasto. El verificador real del motor rechaza usarla como grant. Conserva2 autorizaciones independientes para lectura y3 para interacción según la política existente. Una observación nueva/cancelación invalida la propuesta preparada. No se autoenvía ni autoaprueba.

Diagnóstico medido del ejecutor actual: Linux, runtime agent-desktop configurado no instalado, doctor de perfiles por defecto desktop/Android/iOS devuelve paired:false; OPEN_DUET_URL/token no configurados en este proceso. Esto describe estas rutas de esta sesión, no prueba que otros equipos del usuario estén sin vincular. No se inspeccionaron cuentas Ads ni se confirmó una sesión remota. El código del motor existe y se conserva. Sin dispositivo/observación vigente y grants no se pueden inventar referencias de UI ni ejecutar acciones; no se instalará un runtime Linux fingiendo que conecta por sí mismo Windows/Mac/iPhone. Evidencia doctor en gc020-pauta-20261112.

Interfaces reales: formulario de plan/variantes/presupuestos, dos confirmaciones, reserva agregada visible, cancelación, observaciones/soporte local, propuesta A/B, propuesta para el motor, auditoría y recuperación de respuesta perdida sin duplicar la orden local, en escritorio/móvil de los tres sistemas y gateway. Paleta/navegación conservadas. No se añade un ERP a Turismo Nacional.

Pruebas de este corte: **91 pruebas en13 suites** y **136 comprobaciones Chromium de pauta**, más regresiones de bandeja, publicación y CRM en el manifiesto final. ORM/API/HTTP y SQLite desechables; verificador real de grants rechaza el brief sin autorización. No hubo anuncios ni gasto real. Se aplicó0018 en ambas apps sin divergencia de modelos. La pasada anterior también pasó para su versión anterior; no incluye el contrato de motor añadido después, se conserva sin sumar pruebas. Evidencias automáticas: ANALISIS/gestion-comercial/evidencias/gc020-pauta-20261112/.

**Alcance de GC-020 todavía pendiente (desarrollo):** transporte de campañas/conjuntos/creativos y cambios/pausa/activación en proveedores, o conexión completa del plan con el ejecutor supervisado y las sesiones reales; métricas/recibos auténticos; checkpoints y reconciliación de resultados remotos inciertos; mapeo de administrador/empresa y retorno de resultados del motor. execute() falla explícitamente con ADS_PROVIDER_EXECUTION_NOT_QUALIFIED: la aprobación local no autoriza gastar. Estas carencias no se presentan como resueltas por disponer del motor o por aprobar tests de planificación.

**Requisitos externos:** vinculación/sesión del dispositivo en el ejecutor apropiado, observación fresca, autorizaciones independientes del administrador; cuentas/permisos/facturación/moneda/cuotas/formatos reales y autorización específica antes del gasto. PostgreSQL/concurrencia, carga, dispositivos físicos y aceptación productiva pendientes. Se usará el sistema de acceso de escritorio/móvil existente; no se vuelve a preguntar genéricamente por las cuentas.

**GC-020 permanece EN_EJECUCION,0/3 hitos acreditados**: no se acredita F/T con un incremento parcial. Comercial permanece **29/72=40,28%, aceptación1/24**; contabilidad57/72=79,17%,9/24 sin cambios. Se conservaron las72 entradas previas del registro con sus hashes. Sin commit ni push.


#### GC-021 · Cadena comercial, herramientas y motores · 2026-11-12

Hallazgo subsanado: el camino heredado devolvía texto de coroneles comerciales y Neko lo rotulaba incondicionalmente COMPLETED_SUCCESS con un modelo fijo, sin recibo. Además inventaba admin_general cuando faltaban roles. Se corrigió en la fuente canónica ANALEMATICA-BACKEND/agents/legacy_command_staff.py: marketing/ventas y fallback desconocido bloquean hasta usar la misión autenticada; Neko propaga BLOCKED y otras salidas no probadas se muestran NO_VERIFICADO. Roles omitidos quedan vacíos. No se presenta esto como cualificación de todos los demás caminos heredados.

Se añadieron adaptadores comerciales propios en los tres backends, ArmyRecord/ArmyEvent, migración0019, APIs/instalación explícitas y pantalla desde CRM. Se conservan fuentes completas de generales en Analemática; no se copian modelos/pesos ni se requiere un servicio SGA para ejecutar las consultas nativas ERP/Analemática. Turismo Nacional sigue institucional. Jarvi dirige, Neko prepara por alias acotado o selección explícita y SOUP mide procesos de agentes. La voz fluida es separada, no configurada/cualificada; una transcripción no es una aprobación ni firma.

Herramientas reales: contactos CRM (muestra20), oportunidades (muestra20), biblioteca, cola de publicaciones, bandeja, correo, mensajería y planes de pauta. Cada una consulta su servicio propio con autorización vigente; devuelve conteo/estado/truncamiento y hash de la fuente, sin persistir nombres/correos/cuerpos. Los soldados no invocan las90 herramientas textuales heredadas. Las otras capacidades del catálogo se registran con bloqueo explícito DOMAIN_WORKFLOW_REQUIRED; no se afirma que una misión genérica publique, responda, cambie políticas o gaste. Siguen los flujos autorizados de cada módulo, incluida GC-020 aún parcial.

La cadena de mando no es solo un dibujo: el despacho recorre y valida Jarvi→Coronel→Capitán→Teniente→Sargento→Soldado, reautoriza en cada paso y solo la hoja enlazada puede llamar la herramienta. Omitir un rango impide alcanzar la función. Es orquestación determinista de herramientas, no una afirmación de93 modelos autónomos entrenados. Hay dos confirmaciones locales separadas del mismo administrador, revisión optimista/UUID, contexto de empresa/prestador tomado del backend, fingerprint de permisos actuales y actor propietario. Cambios de permisos invalidan lectura/ejecución/recibo de la misión anterior. Evidencia y telemetría se encadenan en la misma transacción que el estado.

Motores: adaptadores locales de protocolo existentes, con configuración comercial propia por sistema/administrador/empresa y deshabilitados por defecto. Open Duet recibe únicamente sistema, instrucción estática y nombres/estados de tareas; plan-only, memoria deshabilitada y sin preguntas/contactos/secretos en el prompt. Un acuse válido deja ENGINE_QUEUED, answer_verified:false: no es una respuesta de modelo completada. agent-desktop exige binario absoluto fijado por SHA256 y ejecuta solo status, sin shell ni argumentos libres, con límites10s/32KiB y contrato JSON de plataforma/versión/permisos. La respuesta de una fixture no cualifica hardware; no se captura/controla un escritorio desde este módulo. El ejecutor de dispositivos existente conserva sus propios grants/autorizaciones.

Se persiste RUNNING antes de solicitar el motor, se valida la reserva antes del despacho y no se mantienen transacciones de BD durante la petición de planificación/sonda. Caída, salida malformada o acuse incierto quedan sin reintento automático; recuperación de interrupción a15min. SOUP utiliza estados/tiempos observados para recomendar resolver precondiciones/perfilar latencia; no cambia política, entrena, promueve candidatos ni optimiza campañas por su cuenta. Los tiempos no acreditan precisión de IA ni SLA integral.

Interfaz propia: preparación sin ejecutar, selección de herramientas/motor/origen, dos confirmaciones, ejecución de consultas, resultado/evidencia/bloqueo por herramienta, SOUP, auditoría, cancelación y recuperación de respuesta perdida sin repetir el motor. Se conservaron navegación/azul metalizado/azul claro/blanco y roles propios. Evidencias visuales de SGA-CD/ERP/Analemática/gateway en1280 y390px, sin desbordamiento horizontal.

Verificación final: **104 pruebas en12 suites**, **128 comprobaciones Chromium del ejército** y regresiones visuales de pauta/CRM según logs. ORM/API/HTTP SQLite desechables; Open Duet se verificó con httpx.MockTransport y agent-desktop con ejecutable temporal fijado por hash: no son modelos/equipos reales. Se aplicó0019 en ambas apps sin divergencia de modelos. Una ejecución intermedia pasó sus suites pero quedó invalidada como cierre por endurecer después la cadena; se conserva sin sumar conteos. Evidencia: ANALISIS/gestion-comercial/evidencias/gc021-agentes-20261112/.

Se acreditan GCH-061/GCH-062 locales. GCH-063 sigue pendiente: motores/modelos y workspace/propietario reales, finalización/calidad/privacidad del modelo, dispositivos/vinculación/permisos físicos, agente de voz separado, PostgreSQL/concurrencia/carga/retención y aceptación productiva. No se accedió a cuentas ni se publicaron/enviaron/pagaron operaciones reales. **Comercial31/72=43,06%, aceptación1/24**. GC-020 permanece EN_EJECUCION0/3. Contabilidad57/72=79,17%,9/24, sin cambios. Se conservaron las73 entradas previas con sus hashes. Sin commit/push.


#### GC-022 · Indicadores comerciales con fuentes y escenarios explícitos · 2026-11-12

Problema: métricas fragmentadas, cifras fijas de CAC/LTV/recompra y pronóstico aleatorio en el panel legado ERP; una venta confirmada en SGA no acredita por sí sola el estado actual del asiento nativo. Riesgo adicional: confundir datos ausentes con cero, estados CRM con ingreso y UTM declarado con atribución auténtica del proveedor.

Solución: módulos propios de cada backend y frontend, tablas/eventos privados, migraciones0020 aditivas, rutas y gateway autenticados. El informe conserva corte económico y tiempos/digests de consulta por fuente; cuenta contactos y oportunidades reales por estado sin reconstruir conversiones históricas inexistentes. Los ingresos/reversiones provienen de líneas REVENUE y asientos propios verificados, excluyendo IVA/pasivos de contrato y borradores. SGA vuelve a consultar su enlace HMAC/JWT al ledger nativo; un hash alterado pasa a fuente no disponible. Nunca se declara ingreso de toda la empresa con este subconjunto comercial.

Landing/canal/campaña se enlazan a captura íntegra y consentimiento vigente; muestran conversión CRM actual e ingresos/reversiones del período ligados al contacto. Son declaraciones, no pruebas de causalidad ni impresiones medidas. Los costes se consultan, únicamente si se solicita y configura, mediante adaptadores de lectura Meta/TikTok/Google Ads con identidad/currency COP, destinos fijos, límites y precisión de micros. No se usan presupuestos estimados como gastos. Se rechazan alias duplicados de la misma cuenta y paginaciones TikTok inconsistentes/incompletas, evitando doble gasto o falsos ceros. CAC se etiqueta como ratio limitado de costes configurados frente a nuevos clientes del módulo; sin fuentes/denominador queda nulo.

LTV es un escenario de margen bruto esperado con horizonte finito: ingresos observados + política versionada/vigente que declara margen, abandono, horizonte, justificación y soporte. Sin política o cohorte suficiente queda nulo. No equivale a beneficio neto vitalicio, a ARPU ni a calibración profesional. El pronóstico usa días explícitos de la fuente completa del módulo, mínimos de historia, elección temporal de línea base y siete días de prueba independientes; informa MAE y supuestos, nunca precisión garantizada. El panel legado ERP perdió las cifras ficticias y utiliza el workspace autenticado; su función de pronóstico aleatorio ahora rechaza la llamada.

Pruebas: **136 pruebas en 15 suites**, más **72 comprobaciones Chromium** en cuatro destinos HTTP (SGA-CD, ERP, Analemática y gateway),1280/390px. Incluye journal/reversión reales de laboratorio, contrato sin ingreso, manipulación de hash, captura/retirada reales, protocolos de los tres proveedores con MockTransport, LTV condicionado, separación temporal de entrenamiento/prueba, idempotencia, recuperación, permisos y aislamiento. Dos componentes pasan tipos estrictos aislados y la función legada rechaza series falsas. Instalación SQLite fresca y makemigrations --check sin deriva; no se usaron cuentas/proveedores externos. Regresión final estable: `a8771f2759de91149b95a0761955ff44d4fb12a53397a234a86042eeb9674260`. Evidencia técnica `ANALISIS/gestion-comercial/evidencias/gc022-indicadores-20261112`.

Alcance pendiente y requisitos externos: cuentas/grants y respuestas auténticas de proveedores, series consentidas del negocio para calibración, revisión de fuentes/supuestos/soportes y aceptación productiva, PostgreSQL/concurrencia/carga y consistencia de corte entre fuentes. El informe es una observación de varias fuentes con tiempos explícitos, no una instantánea ACID distribuida. La política declarada y el digest de soporte no certifican autenticidad. GC-020 continúa parcial: no se habilita gasto/publicación por estas consultas. Producción no habilitada.

Medición: GCH-064/F y GCH-065/T verificados localmente; GCH-066/A pendiente. **Comercial33/72=45,83%, aceptación1/24**; GC-022 no está cerrada al100% ni calibrada para producción. Contabilidad permanece57/72=79,17%,9/24 aceptadas, sin cambios de crédito. No se hace commit, push ni merge. Se conserva el registro previo completo y se prepara respaldo verificable del acumulado.


#### GC-023 · Nivelación de recorridos y ciclo de vida de los frontends · 2026-11-12

Problemas encontrados: paneles acumulados abiertos, estados de bloqueo del padre que podían reactivar controles internos, pérdida del HTTP403 al listar contactos y falta de limpieza de dominios hijos, paginación habilitada sin resultados, carga inicial de oportunidades vacía y sin reintento. La sesión nativa acumulaba escuchadores; podía redibujarse después de desmontarse, duplicar un envío MFA o cambiar de empresa mientras cerraba la sesión. Una consulta secundaria finalizada podía liberar el selector aunque otra operación quedara sin confirmar.

Implementado: navegación equivalente de17 entradas en los tres frontends propios, sin trasladar carpetas ni sustituir sus formularios/API. Una región visible, atributos aria-controls/pressed, activación por teclado y foco en contenido. Los formularios permanecen montados y conservan sus referencias de recuperación. La actividad y las referencias pendientes se agregan antes de liberar menú/empresa; el bloqueo del padre conserva controles de dominios hijos. Los errores de permisos mantienen su estado HTTP y limpian todos los clientes montados. Hay carga/reintento de acceso y oportunidades, mensaje visible si falta un recurso y paginación correcta en vacío.

La vista previa de correo conserva su sandbox sin permisos añadidos; bloquea la revisión hasta cargar/pintar, limita HTML/espera y limpia al fallar/desmontarse, sin marcar confirmaciones. El diagnóstico del clic conservó sus eventos: tras desplazar junto al iframe no alcanzaba al documento padre. La regresión espera el pintado del padre y sigue usando clic real, sin forzar estados. Se protegió además el foco para no sacarlo de un campo donde el usuario ya interactúa.

La sesión nativa usa un escuchador ligado a su ciclo de vida, cancelación/guardas de desmontaje, contraseña/código borrados del formulario, exclusión de envíos MFA y cierres simultáneos, reintento de acceso/cierre y bloqueo de empresa mientras haya actividad. El estado vacío conserva la salida de sesión. Los roles continúan siendo propios de cada backend; la interfaz no crea ni hereda permisos. Se conserva Jarvi operativo, Neko conversacional y SOUP optimizador mediante su flujo existente. No se habilitan acciones de proveedor por navegar.

Identidad y accesibilidad comprobadas: azul metalizado, celeste y texto blanco en el módulo; foco visible, regiones identificadas, objetivos de44px, formularios de una columna y menú móvil de dos. Se conservaron estructura/entradas de las aplicaciones; el menú interno ahora muestra el contenido seleccionado y mantiene los demás formularios en memoria. No se presenta como certificación completa WCAG ni validación física.

Evidencia: **804 comprobaciones nuevas** sobre las páginas reales de SGA-CD, ERP, Analemática y gateway, en1280/390/320px; incluye carga fallida/reintento, recuperación tras respuesta perdida, bloqueo combinado,17 secciones, teclado, vacío, recurso ausente y rechazo de acceso. La sesión nativa dispone de comprobaciones aisladas de protocolo simulado, separadas de aceptación MFA real. La regresión final ejecutó **37 pruebas Python y16 suites/comprobadores**, con recorridos CRM, oportunidades, cotizaciones, captación, correos, publicaciones, inbox, agentes e indicadores; dos componentes pasan tipos estrictos aislados. Desglose de comprobaciones en `ANALISIS/gestion-comercial/evidencias/gc023-frontends-20261112/browser-checks.json`; fuentes estables `c49b57d8810ece4090fd21a31e3acc6529ba4ccdbe0ad3713783ca61637b80cf`. No se ejecutaron envíos/publicaciones reales, pagos, reasignaciones de roles ni migraciones de datos productivos.

Alcance de calidad pendiente enGC-024: compilación integral de las aplicaciones/plataformas y cualificación del release, separadas del chequeo de componentes y navegadores de esta entrega.

Requisitos externos para la aceptación deGC-023: usuarios con sus roles y empresas legítimas, equipos físicos Android/iOS/escritorio y tecnologías de asistencia; revisión de accesibilidad y aceptación de los recorridos. Las pruebas de protocolo de sesión son simuladas; el HTTP de dominio utiliza bases y usuarios desechables. La paridad visual no cierra la cualificación externa de proveedores, modelos ni módulos anteriores.

Medición: GCH-067/F y GCH-068/T acreditados localmente; GCH-069/A pendiente. **Comercial35/72=48,61%, aceptación1/24**. GC-023 queda2/3, no cerrada al100% integral. Contabilidad permanece57/72=79,17%,9/24 aceptadas; sin cambio de crédito. Registros anteriores íntegros. Sin commit/push/merge; respaldo verificable del acumulado local.


<!-- GC024-BEGIN -->
#### GC-024 · Operación y cierre · en ejecución2026-11-12

Funcionalidad implementada y probada: cada backend propio de SGA-CD, ERP y Analemática dispone de diagnóstico acotado a 14 dominios y trazas privadas que verifican cadena, revisión, estado, empresa, usuario y permisos vigentes. Una fuente ausente se informa no disponible, nunca cero. Las sondas no consultan proveedores ni escriben en ledger; no exponen recibos ni contenido de contactos. Se restringieron explícitamente los métodos de la vista nativa para impedir heredar POST del CRM.

Cada frontend conserva su propia cola de textos cifrados AES-256-GCM/PBKDF2, ligada a sistema/empresa/prestador/usuario; revisión optimista, rotación, respaldo y restauración cifrados. La recarga sin red funciona después de una preparación inicial online. Se añadió invalidación de respuestas tardías: una operación pendiente no vuelve a mostrar el texto después de pagehide/bloqueo; la regresión dispara la salida durante el cifrado real. Comparación con las fuentes originales respaldadas: fallo reproducido en 3 sistemas y evitado en los 3 corregidos, 12 verificaciones con Chromium/WebCrypto reales. No se guardan credenciales, consentimientos o firmas ni se envía/sincroniza automáticamente: el usuario revisa el texto en una sesión autenticada. El realm declarado no acredita identidad del servidor, y este cifrado de navegador no equivale a hardware seguro ni elimina XSS. La integración Nginx sirve solo cinco recursos estáticos exactos por origen; las rutas privadas permanecen protegidas.

Operación: ensayo de respaldo cifrado y restauración de registros comerciales SQLite en destino nuevo, con integridad/FK y preservación del original. No reemplaza bases vivas ni incluye medios, llaves de aplicación o grants. El gate comprueba evidencia de los 72 hitos y permanece bloqueado; nunca habilita producción. Corregidos imports ERP hacia runtimes propios, alias UI inexistente, estado degradado sin variable y componentes sin imports. El POS heredado tenía importes corruptos y botones sin ejecución: dirige a las cotizaciones reales y declara la caja independiente no habilitada. No se acredita POS productivo. Se conservan roles propios, identidad azul/blanco, Jarvi operativo, Neko conversacional y SOUP optimizador.

Pruebas: regresión específica con fuentes estables, 8 suites y 24 pruebas Python aprobadas;75 comprobaciones Chromium de cifrado/IndexedDB/recarga offline en tres clientes;21 comprobaciones Nginx real desechable protegiendo rutas privadas;21 pruebas del runner. La regresión amplia sobre el corte de partida terminó con 108/109 suites aprobadas, 943 pruebas Python en suites aprobadas; pendientes de esa ejecución:[{"id": "pool08_payments_browser", "status": "FAILED"}]. Durante esa ejecución se corrigió el caso pagehide: el manifiesto detectó exactamente 10 archivos distintos (editores/workers propios, manifests, su test y la navegación del test de pagos); por eso source_stable es falso y no se presenta como una regresión integral inmutable del estado final. El delta de editores se revalidó después en las 8 suites específicas con fuentes estables. El único recorrido de pagos fallido intentaba escribir en Ventas sin regresar desde Pagos; se corrigió el test para navegar de verdad y verificar la exclusión de paneles, conservando el fallo original y la repetición aprobada de 150 comprobaciones por separado. Comandos, logs y hashes en `ANALISIS/gestion-comercial/evidencias/gc024-operacion-20261112/`. El intento previo de 109 suites fue interrumpido por reinicio y no se presenta como aprobado; tampoco se acepta como fuente estable el intento durante el cual se terminó un test. Se corrigió la duplicación de suites/logs al combinar perfiles. Las mediciones HTTP son loopback, 8 muestras y concurrencia 4 por destino, no SLA productivo.

Alcance local pendiente: compilación estricta ERP con 966 diagnósticos en 257 archivos y Turismo con 938 en 249; son diagnósticos, no defectos únicos. No se deshabilitaron tipos estrictos. Pendientes cola/sincronización por dominio, carga y observabilidad completas, reversión/restauración integral y dependencias sin cerrar. Requisitos externos separados: infraestructura/carga objetivo, proveedores y datos legítimos, llaves/grants/medios, equipos físicos y aceptación profesional/productiva. No se califican objetivos 1,2s/3s/60s ni RPO/RTO con pruebas sintéticas.

Estado: GC-024 conserva 0/3 hitos; comercial 35/72=48,61%, aceptación 1/24, producción no habilitada. Código parcial y más pruebas no otorgan crédito de cierre. No se hicieron commits, push ni despliegues.

Respaldo local de fuentes monitorizadas y evidencia: `/workspace/recuperacion-original-sgacd-20261110T110746Z/organizacion-codigo-20261111T203523Z/gc024-operacion-20261112.tar.gz`; manifiesto SHA-256 lateral, sin incluir secretos ni sustituir una entrega Git.
<!-- GC024-END -->


<!-- GC-AUDIT24-BEGIN -->
#### Auditoría comercial de GC-001 a GC-024 · 2026-11-12

Revisión por tarea: inventario de fuentes propias, evidencia declarada validada por hashes, dependencias abiertas, pruebas relacionadas y aceptación externa. La presencia de código no acredita funcionalidad completa. Perfil reproducible nuevo: `python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-audit --output /tmp/directorio-nuevo`. Revisión detallada: `ANALISIS/gestion-comercial/evidencias/auditoria24-20261112/revision-24.json`; herramienta propia `BACKEND/INTEGRACIONES/operacion/commercial_audit.py --quality <directorio> --output <archivo-nuevo>`.

Hallazgos subsanados: la traza podía declarar corrupción al coincidir con una revisión legítima; ahora vuelve a leer y reintenta solo si cambió el documento, máximo dos intentos, y rechaza cadenas corruptas estables. Reproducción antes/después con bytes originales respaldados y revisión ORM real: fallo previo y corrección comprobados. El muestreo ahora resume el documento comprobado, no la revisión de la lista anterior. Pagos y captación se incluyeron en los 16 dominios; una fuente ausente no se convierte en cero. La regresión anterior omitía GC-013 específico; el perfil integral incluye generación nativa/SGA/HTTP, jerarquía de agentes y las 24 familias, con IDs sin duplicar. También se corrigieron dos workflows: Node/Playwright/FFmpeg/fuentes y rutas del runtime comercial se preparan antes de probar; se usan dependencias dev del lockfile, se ofrece el perfil integral y se amplían disparadores para herramientas/frontends propios. YAML, sintaxis shell y orden fueron comprobados localmente; no se ejecutó GitHub Actions ni se acredita CI verde. No cambia funciones de Jarvi/Neko/SOUP ni roles nativos; Turismo Nacional no se convierte en ERP.

Ejecución integral inicial: **122/123 suites aprobadas y 1.258 pruebas Python aprobadas**. Fuentes monitorizadas estables; hash y logs completos en el registro técnico. La incidencia inicial fue el recorrido de Pagos.

Fallo corregido: la inicialización de Pagos permitía solaparse con comandos/recuperación y volver a pintar una intención anterior. Se serializó en los tres clientes, los controles nuevos respetan el bloqueo y una carga fallida permite reintentar. Se reprodujeron los controles activos con las fuentes originales respaldadas; las corregidas pasan 27 comprobaciones de ciclo de vida y reintento.

Verificación posterior: **15 suites específicas aprobadas, 72 pruebas Python y 804 comprobaciones de navegación real**. El recorrido HTTP de pagos pasa 150 comprobaciones. Estos conteos se solapan y no deben sumarse como casos únicos. Fuentes finales monitorizadas estables: `1dd13bc36be5f9c013ee5e7281e12f026e294866ba03fa91b72fb5720729fa37`.

Las 123 suites corresponden al perfil anterior al nuevo caso de ciclo de vida. El perfil vigente incorpora ese caso; después de corregir se repitieron las suites afectadas y navegación, no el perfil integral de 124 suites. El fallo inicial y las repeticiones aprobadas se conservan separados en `revision-24.json`, `regression/` y `quality/`.

Los mapeos por tarea se solapan. F/T/A significa funcionalidad de todo el alcance definido, verificación y aceptación integral; esta revisión no otorga crédito nuevo.

| Tarea | F/T/A acreditados | Ejecuciones base y posteriores | Requisitos externos pendientes |
|---|---|---|---|
| GC-001 · Contratos, capacidades y DAG POOL-08 | Sí/Sí/Sí | 2 vinculadas; 0 incidencias base; 0 revalidadas | No para su alcance cerrado |
| GC-002 · Identidad empresarial, roles, permisos y consentimientos | No/No/No | 2 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-003 · CRM común de prospectos, contactos y clientes | Sí/Sí/No | 6 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-004 · Oportunidades, embudo, seguimiento y scoring | Sí/Sí/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-005 · Catálogo, tarifas, descuentos e impuestos de oferta | Sí/Sí/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-006 · Cotizaciones dinámicas, vigencia y aceptación | Sí/Sí/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-007 · Venta confirmada, operación y contabilidad | Sí/Sí/No | 8 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-008 · Bold: checkout, intención de pago y confirmación | No/No/No | 6 vinculadas; 1 incidencias base; 7 revalidadas | Sí |
| GC-009 · Cancelaciones, retención, devoluciones y posventa | No/No/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-010 · Constructor de landing pages propias de empresa/prestador | Sí/Sí/No | 5 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-011 · Landing: formularios, captación, SEO y atribución CRM | Sí/Sí/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-012 · Biblioteca multimedia, derechos, marca y activos | Sí/Sí/No | 5 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-013 · Generación de guiones, textos e imágenes | No/No/No | 3 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-014 · Creación de videos, Reels, voz y subtítulos | No/No/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-015 · Tamaños y formatos de imágenes, videos y Reels | Sí/Sí/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-016 · Correos masivos y campañas email | Sí/Sí/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-017 · SMS, MMS y mensajería multimedia por WhatsApp | Sí/Sí/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-018 · Publicación orgánica y calendario multicanal | Sí/Sí/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-019 · Bandeja omnicanal y respuestas: mensajes y comentarios | Sí/Sí/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-020 · Anuncios y pauta: Meta, TikTok y Google/YouTube Ads | No/No/No | 4 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-021 · Cadena de agentes, herramientas reales y motores | Sí/Sí/No | 5 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-022 · Indicadores, embudo, atribución y predicción | Sí/Sí/No | 8 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-023 · Nivelación de frontends y recorridos de los tres módulos | Sí/Sí/No | 3 vinculadas; 0 incidencias base; 0 revalidadas | Sí |
| GC-024 · Calidad, seguridad, rendimiento, operación y cierre | No/No/No | 9 vinculadas; 0 incidencias base; 8 revalidadas | Sí |

Estado real: 1 tarea con aceptación completa, 16 con F/T acreditados y aceptación pendiente, 7 todavía parciales o por nivelar; 35/72 hitos=48,61%. GC-013 conservaba una descripción de planificación: se actualizó para distinguir sus adaptadores/cola existentes de lo pendiente, sin otorgar crédito. Los campos de alcance y requisitos externos detallados se conservan por cada tarea en revision-24.json.

Pendientes locales prioritarios: administración de permisos/consentimientos e identidades (GC-002); verificación/consulta Bold y conciliación (GC-008); vínculo verificable y cancelación/firma/fidelización (GC-009); trabajadores independientes, flujo navegador-trabajador y vídeo generativo (GC-013/014); ejecución supervisada/provisión/recibos/recuperación de pauta (GC-020); sincronización offline por dominio, observabilidad/carga y restauración/reversión integrales (GC-024). Se repitieron las compilaciones completas y tsc estricto: 966 diagnósticos en 257 archivos ERP y 938 en 249 Turismo; se conservan los logs e inventarios, sin confundir diagnósticos con defectos únicos. Estos fallos son locales, no dependen de conectar un proveedor. La lectura consistente por registro no cualifica un snapshot transversal, un cierre financiero ni PostgreSQL bajo carga.

Requisitos externos separados: cuentas/proveedores/OAuth y acuses auténticos; consentimientos, políticas, soportes, licencias y series legítimos; modelos/hardware/dispositivos objetivo; aceptación profesional y productiva. Ninguno se cierra con transporte simulado. Se mantienen paleta y carpetas propias; sin envíos, gastos, acciones de dispositivo, despliegue, commit o push.

Respaldo final de fuentes monitorizadas y evidencias: `/workspace/recuperacion-original-sgacd-20261110T110746Z/organizacion-codigo-20261111T203523Z/auditoria24-20261112.tar.gz`, con manifiesto SHA-256 lateral. No sustituye publicación Git ni respaldo productivo de medios/llaves/grants.
<!-- GC-AUDIT24-END -->


<!-- GC003-SEQUENCE-BEGIN -->
#### Cierre secuencial de las 16 tareas comerciales con F/T · 2026-11-12

Nueva directriz del usuario: cerrar una a una las 16 tareas con funcionalidad/pruebas acreditadas y aceptación pendiente. Orden: GC-003, GC-004, GC-005, GC-006, GC-007, GC-010, GC-011, GC-012, GC-015, GC-016, GC-017, GC-018, GC-019, GC-021, GC-022 y GC-023. Única activa GC-003; las otras 15 no avanzan por esta entrega. Secuencia en el campo sequential_closure del plan existente. No se modifican alcance, criterios ni ponderaciones.

GC-003: se reprodujeron y corrigieron tres defectos en los tres backends propios: correos con caracteres de control aceptados, huellas de consentimiento numéricas convertidas implícitamente a texto y Unicode escapado inválido que provocaba UnicodeEncodeError. Ahora se rechazan antes de guardar contacto/historial o alterar su revisión; los datos válidos conservan su normalización y los consentimientos siguen declarados no auténticos/no autorizadores de envío. No se reescriben datos históricos. Comparación de Unicode con fuentes originales respaldadas: error sin controlar antes y rechazo de dominio después; las APIs verifican 422. El primer ensayo negativo reproduce los otros dos fallos.

Validación local: 8 suites aprobadas, 179 pruebas Python y 88 comprobaciones Chromium/HTTP sobre SGA-CD, ERP, Analemática y gateway, con datos sintéticos y SQLite desechable. Compatibilidad del hash compartido: 71 pruebas adicionales (30 inbox, 16 mensajería y 25 publicaciones), sin implementar ni cerrar esas otras tareas. La ejecución canónica tiene fuentes monitorizadas estables. El intento SGA manual dentro del sandbox no completó; se conserva separado y no se cuenta como aprobado. Evidencia técnica: ANALISIS/gestion-comercial/evidencias/gc003-secuencial-20261112/.

Bloqueo integral: GC-002 sigue pendiente de desarrollo/aceptación de administración de identidad/permisos/consentimientos; además, el usuario respondió que no dispone del conjunto solicitado de muestras autorizadas y políticas revisadas. La respuesta no acredita autenticidad ni permite sustituir aceptación real por fixtures. La cualificación histórica/PostgreSQL/productiva permanece separada. No se declara cerrado GC-003 ni se pasa a GC-004: GC-003 conserva 2/3, cierres de esta secuencia 0/16 y matriz 35/72=48,61%. Sin producción, commit o push. Los 78 seguimientos anteriores se conservan mediante comprobación de hashes, con el conteo exacto en el registro.

La revisión previa al cambio de objetivo detectó riesgos de ciclo de vida en Ventas/Cotizaciones/Posventa (carga inicial sin exclusión, respuestas tardías, copia duplicada y seguimiento concurrente). No se alteraron esos módulos al reorientar la tarea a GC-003; quedan consignados para resolverlos al llegar a sus tareas, respetando el orden del usuario.

Respaldo de fuentes monitorizadas, instrucciones y evidencia: /workspace/recuperacion-original-sgacd-20261110T110746Z/organizacion-codigo-20261111T203523Z/gc003-secuencial-20261112.tar.gz; manifiesto SHA-256 lateral. Es respaldo de trabajo, no entrega Git ni restauración de producción.
<!-- GC003-SEQUENCE-END -->


<!-- COMMERCIAL-REMAINING37-BEGIN -->
#### Plan de trabajo · 37 hitos comerciales restantes · 2026-11-12

Base confirmada: 35/72 hitos acreditados (48,61%); 37 pendientes: 7 de funcionalidad, 7 de pruebas y 23 de aceptación integral. No todos se resuelven únicamente escribiendo código. Los 23 de aceptación pertenecen a las 23 tareas que aún no tienen aceptación completa; entre ellas están las 16 ya acreditadas F/T y las 7 todavía parciales. No se cambia el denominador ni se otorga crédito por planificar.

Este plan es una descomposición de trabajo sobre los IDs GCH originales, no 37 tareas nuevas ni un reinicio. La numeración 1–37 identifica pasos de trabajo; las tareas continúan siendo GC-001..GC-024. GC-003 conserva el primer cierre activo de las 16; antes hay que completar GC-002, su dependencia. Por eso los pasos 1–3 corresponden a GC-002 y el paso 4 a la aceptación de GC-003. El próximo desarrollo es el paso 1 (GCH-004), no volver a implementar GC-001.

| Paso | Hito y tarea originales | Tipo | Trabajo pendiente |
|---|---|---|---|
| 1 | GCH-004 · GC-002 | Desarrollo | Administración de identidad y permisos. Completar APIs y pantallas propias de permisos, consentimientos y vínculos de identidad; conservar los roles nativos y prohibir herencia de acceso a billetera. |
| 2 | GCH-005 · GC-002 | Pruebas | Pruebas de identidad y aislamiento. Verificar empresa A/B, roles distintos, revocación, caducidad, reintento e intento de acceso financiero desde marketing. |
| 3 | GCH-006 · GC-002 | Aceptación | Aceptación de identidad. Revisar usuarios, matriz de permisos, políticas y consentimientos con los administradores legítimos. |
| 4 | GCH-009 · GC-003 | Aceptación | Aceptación del CRM. Validar alta, búsqueda, actualización, seguimiento, duplicados, conversión y baja con muestras autorizadas, después de GC-002. |
| 5 | GCH-012 · GC-004 | Aceptación | Aceptación de oportunidades. Validar embudo, responsables, transiciones e historial; evaluar scoring con datos consentidos y mantenerlo no calibrado mientras falte evaluación. |
| 6 | GCH-015 · GC-005 | Aceptación | Aceptación de catálogo y precios. Revisar tarifas, descuentos, impuestos y condiciones contra fuentes legítimas. |
| 7 | GCH-018 · GC-006 | Aceptación | Cierre de cotizaciones. Subsanar copia duplicada, respuestas tardías y carga inicial; validar versiones, vigencia, enlaces y aceptación del destinatario. |
| 8 | GCH-021 · GC-007 | Aceptación | Cierre de venta, operación y ledger. Subsanar inicialización y respuestas tardías de Ventas; revisar precondiciones, cupos, costos, asiento y recuperación. |
| 9 | GCH-022 · GC-008 | Desarrollo | Confirmación auténtica Bold. Completar verificador de acuses según contrato oficial, consulta de estado, resultados inciertos y conciliación con asiento. |
| 10 | GCH-023 · GC-008 | Pruebas | Regresión Bold. Probar firmas inválidas, repetición de eventos, orden invertido, importes distintos, timeouts, consulta y recuperación idempotente. |
| 11 | GCH-024 · GC-008 | Aceptación | Aceptación Bold. Validar el ciclo con comercio de pruebas autorizado, acuses auténticos y conciliación; configurar credenciales por canal seguro. |
| 12 | GCH-025 · GC-009 | Desarrollo | Posventa y devolución completas. Completar vínculo contacto/venta/reserva/destinatario, cancelación, bandas de retención por anticipación, firma y fidelización; impedir seguimiento concurrente duplicado. |
| 13 | GCH-026 · GC-009 | Pruebas | Regresión de devoluciones. Probar topes acumulados, límites de fechas, doble solicitud, consentimiento, fondos, autorizaciones y rollback de saldo/movimiento/asiento. |
| 14 | GCH-027 · GC-009 | Aceptación | Aceptación de posventa. Revisar políticas legítimas y validar los recorridos de devolución interna y bancaria que correspondan al alcance. |
| 15 | GCH-030 · GC-010 | Aceptación | Aceptación del constructor de landing. Revisar marca, contenido, publicación, retirada y restauración de versión por titular; validar dominio propio si se utiliza. |
| 16 | GCH-033 · GC-011 | Aceptación | Aceptación de captación y SEO. Validar formularios con usuarios autorizados, atribución de origen, consentimiento, baja, antispam y retención. |
| 17 | GCH-036 · GC-012 | Aceptación | Aceptación de biblioteca multimedia. Revisar licencias, marca, almacenamiento privado, originales, versiones, retención y restauración. |
| 18 | GCH-037 · GC-013 | Desarrollo | Generación de texto e imagen completa. Completar arranque independiente del trabajador, configuración de modelos y recorrido navegador-HTTP-trabajador; corregir los tipos ERP que lo bloqueen. |
| 19 | GCH-038 · GC-013 | Pruebas | Pruebas de generación. Probar cola, permisos, cancelación, reintento, pérdida de trabajador, resultados inválidos y recuperación sin duplicación. |
| 20 | GCH-039 · GC-013 | Aceptación | Aceptación de generación. Validar inferencia auténtica de texto con Ollama y un motor de imágenes disponible, además de calidad, licencias, privacidad y coste. |
| 21 | GCH-040 · GC-014 | Desarrollo | Vídeos, Reels, voz y subtítulos completos. Completar trabajador independiente, adaptador generativo de vídeo y recorrido integral; conservar composición/render como capacidad diferenciada. |
| 22 | GCH-041 · GC-014 | Pruebas | Pruebas de producción multimedia. Verificar reproducción, dimensiones, audio/subtítulos, permisos, límites, cuotas, cancelación y caída del trabajador. |
| 23 | GCH-042 · GC-014 | Aceptación | Aceptación multimedia. Validar modelos/hardware, contenido y derechos de voz/audio con el responsable autorizado. |
| 24 | GCH-045 · GC-015 | Aceptación | Aceptación de tamaños y formatos. Comprobar perfiles vigentes por red, calidad, dimensiones, límites y rendimiento en hardware objetivo. |
| 25 | GCH-048 · GC-016 | Aceptación | Aceptación de correo masivo. Validar remitente/dominio, proveedor/OAuth o relay autorizado, bajas, consentimientos, cuotas y recibos auténticos. |
| 26 | GCH-051 · GC-017 | Aceptación | Aceptación SMS/MMS/WhatsApp. Validar por separado cada canal y proveedor, MMS en Colombia, plantillas WhatsApp, firmas, costes y destinatarios autorizados. |
| 27 | GCH-054 · GC-018 | Aceptación | Aceptación de publicación orgánica. Validar cuentas propias, OAuth/permisos, formatos, visibilidad, calendario, estados inciertos y recibos por red. |
| 28 | GCH-057 · GC-019 | Aceptación | Aceptación de bandeja omnicanal. Validar recepción auténtica, firmas/webhooks, empresa/hilo/destinatario, asignación y respuesta autorizada. |
| 29 | GCH-058 · GC-020 | Desarrollo | Ejecución supervisada de pauta. Completar provisión de campañas/conjuntos/creativos, ejecución y recuperación con adaptadores o dispositivo real y control Open Duet/agent-desktop. |
| 30 | GCH-059 · GC-020 | Pruebas | Pruebas de pauta. Verificar presupuesto agregado, reservas concurrentes, cambio de cuenta, permisos, rechazo, duplicación, timeout y recuperación remota. |
| 31 | GCH-060 · GC-020 | Aceptación | Aceptación de pauta. Validar cuentas Ads, permisos, facturación, objetivos y recibos auténticos bajo autorización explícita de cada acción real. |
| 32 | GCH-063 · GC-021 | Aceptación | Aceptación de agentes y motores. Cualificar motores/modelos y herramientas en equipos objetivo, cadena de mando, privacidad y agente de voz fluida separado. |
| 33 | GCH-066 · GC-022 | Aceptación | Aceptación de indicadores y predicción. Validar fuentes de CRM/ledger/campañas, series consentidas, atribución, CAC/LTV, supuestos y evaluación temporal. |
| 34 | GCH-069 · GC-023 | Aceptación | Aceptación de los tres frontends. Resolver fallos de ciclo de vida restantes y validar recorridos, roles propios, accesibilidad, dispositivos y preparación de release. |
| 35 | GCH-070 · GC-024 | Desarrollo | Operación y calidad completas. Corregir compilación y contratos API/DTO, completar instalación repetible, sincronización offline por dominio, observabilidad, respaldo y reversión integrales. |
| 36 | GCH-071 · GC-024 | Pruebas | Pruebas finales de seguridad y operación. Ejecutar regresión integral sobre fuentes estables, instalación limpia, concurrencia, carga, fallo de red, restauración y reversión. |
| 37 | GCH-072 · GC-024 | Aceptación | Aceptación integral del motor comercial. Cerrar dependencias y requisitos externos, verificar los72 hitos, restauración completa y objetivos medidos en infraestructura objetivo. |

Cada paso tiene responsable por función, dependencias, criterio original y evidencia de salida en `ANALISIS/gestion-comercial/plan-pool08.json`, campo remaining_work_plan.steps. Desarrollo = completar el alcance funcional pendiente; pruebas = verificarlo con casos positivos/negativos, aislamiento, reintento y recuperación; aceptación = revisión legítima de usuarios/políticas/datos/proveedores/equipos según la tarea. Un resultado de laboratorio no cubre esos requisitos externos. Algunos desarrollos y pruebas también necesitan contrato/proveedor auténtico antes de completarse.

Trabajo transversal desde el principio: abordar los errores de compilación y contratos API/DTO, estados de carga, respuestas tardías, duplicación de handlers/solicitudes y restauración que bloqueen el paso activo. El inventario actual conserva 966 diagnósticos ERP y 938 Turismo; no se consideran defectos únicos ni se ocultan. Estos preparativos no cierran por sí solos GCH-070/071. Las incidencias de Ventas/Cotizaciones/Posventa consignadas en la revisión se incorporan a sus pasos de cierre/desarrollo.

Reglas: una tarea no obtiene aceptación por tener archivos o pruebas sintéticas. Se preserva la secuencia de cierre de las 16; no se salta un cierre bloqueado ni se inventa el dato externo. El usuario ya declaró no disponer del conjunto de muestras autorizadas/políticas revisadas; sigue pendiente. SGA-CD, ERP y Analemática conservan módulos, datos, roles y carpetas propios; azul metalizado/celeste/blanco. Turismo Nacional conserva su carácter institucional. Jarvi operativo, Neko conversacional y SOUP optimizador; los agentes no se autoautorizan. La billetera mantiene acceso personal general sin afiliación turística.

DIAN continúa como integración fiscal propia pendiente: una venta, cotización o asiento no se presenta como factura aceptada. Bold conserva el papel de pasarela elegida; credenciales por canal seguro y acuses legítimos. Publicación, gasto, envío real, control de dispositivo y producción necesitan las autorizaciones aplicables. No se activan por crear este plan.

Estado de esta entrega: plan preparado y contrastado con los 37 IDs pendientes. Ningún paso nuevo ejecutado ni hito acreditado; 35/72=48,61%, producción deshabilitada. Sin commit ni push. El detalle de cada pendiente se mantiene en el plan existente y este seguimiento, sin generar otro informe Markdown.
<!-- COMMERCIAL-REMAINING37-END -->


<!-- GC002-STEP1-BEGIN -->
### Paso 1 del plan comercial restante · GC-002/GCH-004 · 2026-11-12

**Funcionalidad del paso 1 implementada y comprobada localmente en SGA-CD, ERP y Analemática.** Cada módulo conserva su backend/frontend y sus roles. Desde CRM → Contactos y seguimiento → Administrar acceso comercial, el administrador consulta el equipo, asigna capacidades limitadas al techo del rol, revoca permisos, registra/revoca declaraciones de consentimiento y referencias externas, consulta historial y recupera recibos. No se alteran las 17 opciones de navegación ni la paleta azul/celeste/blanco. Turismo Nacional mantiene su función institucional y no recibe estos privilegios.

Problema resuelto: los controles de identidad existentes no tenían rutas ni recorrido administrativo. Se añadieron `access_admin.py` y `access_api.py` propios en cada backend, rutas `/crm/access/…`, paso explícito por el gateway de Analemática y formularios propios integrados en `js/commercial-crm.js` de cada frontend. Se reutilizan las tablas/migraciones aditivas existentes; no se ejecutó migración en una base real. Las bases desechables HTTP ahora incluyen también esas cuatro tablas de identidad.

Los comandos usan UUID, revisión esperada, huella del rol, vigencia y soporte SHA-256; el recibo permite recuperar resultados sin repetir efectos. Cada petición revalida autoridad local; las escrituras toman el bloqueo empresarial del CRM dentro de su transacción. La asignación no cambia roles ni admite capacidades de billetera o funciones no delegables. Los vínculos identifican sistema, empresa y cuenta externa de forma expresa, permanecen sin verificación remota y nunca conceden acceso entre sistemas.

Para registrar consentimiento se exige contacto local, revisión vigente y declaración CRM otorgada para el mismo canal/finalidad, soporte y período. El cotejo y la escritura comparten transacción; la baja, una revisión obsoleta o un soporte distinto bloquean el registro. Este cotejo verifica coherencia interna: **no autentica el soporte ni sustituye una política legítima revisada y no autoriza envíos**. Se completó el vocabulario de canal/finalidad en los tres CRM para que las referencias de atribución no se confundan con marketing o servicio.

Durante las pruebas se corrigió la captura del formulario antes de deshabilitar sus campos. Ante respuesta perdida, la pantalla conserva el comando en memoria para repetir exactamente el mismo identificador; tras recarga conserva solo UUID/operación con clave por sistema/empresa/actor y consulta el recibo. No persiste cuerpos de comandos, contactos, soportes ni credenciales en ese registro. La denegación de sesión/permisos elimina el panel. Descartar un intento local no cancela un efecto ya registrado: la interfaz pide revisar el historial.

**Evidencia:** `ANALISIS/gestion-comercial/evidencias/gc002-paso1-20261112/summary.json`. Ejecución reproducible: `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-access --profile commercial-crm --output .runtime/<directorio-nuevo>`. Resultado: 10 suites aprobadas, 183 pruebas Python y 244 comprobaciones de navegador (156 del panel nuevo y recuperación; 88 de regresión CRM), HTTP local auténtico con datos sintéticos, fuentes estables y hashes de evidencia comprobados. Los cuatro destinos son los tres backends propios y el gateway de Analemática; vistas 1280/390/320. Diez pruebas adicionales del registro comercial aprobaron. Se mantienen los 79 registros previos de evidencia sin alteración.

**Medición:** se acredita exclusivamente GCH-004/F. El crédito comercial pasa de 35/72 a **36/72 = 50,00 %**; aceptación integral permanece **1/24 tareas**. La revisión completa de la base sigue pendiente y el campo `implementation_percent` permanece sin acreditar: el 50 % expresa crédito de hitos, no un porcentaje certificado de implementación global ni producción. Paso 2/GCH-005 continúa pendiente de cualificación exhaustiva de roles/caducidad/concurrencia y recorridos de todas las operaciones; estas pruebas de desarrollo no acreditan automáticamente ese siguiente paso. Paso 3/GCH-006 requiere usuarios y políticas revisadas que el usuario indicó no tener disponibles. GC-003 sigue siendo el primer cierre integral activo, dependiente de la aceptación de GC-002. No se avanzó a otra tarea de la secuencia de 16.

**Requisitos externos y límites:** no se validó legitimidad jurídica de consentimientos, identidad remota, PostgreSQL/concurrencia de producción ni equipos físicos. No se operaron cuentas reales, proveedores, anuncios, envíos o billetera; la billetera personal mantiene su elegibilidad general. La contabilidad no cambia de crédito. Sin commit, push, merge ni actualización de main; fuentes y evidencias conservadas localmente.
<!-- GC002-STEP1-END -->

<!-- GC002-STEP2-BEGIN -->
### Paso 2 del plan comercial restante · GC-002/GCH-005 · 2026-11-12

**Paso 2 completado para su alcance de verificación local:** identidad, aislamiento y recuperación de los tres módulos comerciales, cada uno con sus roles, backend y frontend propios. Se acreditó solamente GCH-005/T; GC-002 conserva pendiente GCH-006/A. El crédito comercial pasa a **37/72 = 51,39 %**, con **1/24 tareas aceptadas integralmente**. La revisión global de la base no está completa: `implementation_percent` permanece sin acreditar. El porcentaje expresa crédito de hitos, no preparación productiva ni porcentaje certificado de toda la implementación.

Hallazgos subsanados con código:

- Revocación incompleta: revocar el registro administrativo de consentimiento dejaba otorgada la declaración del CRM. Ahora se revoca también su canal/finalidad en el CRM, con historial y recibo, dentro de la transacción de política. Un fallo inyectado al guardar la auditoría revierte tanto el contacto y su historial como la política. La revocación es restrictiva incluso si entretanto se renovó el soporte; no otorga ni autentica consentimientos y no ejecuta envíos.
- Importación circular en SGA-CD al entrar por `crm_api`: se resolvieron de forma diferida las dependencias del adaptador de administración y sus errores. Se verificó el arranque y el acceso HTTP propios.
- Otorgante nativo inactivo: una excepción contable podía escapar como error interno. Los backends propios de ERP y Analemática traducen ese fallo de autoridad conocido a rechazo de acceso, y consideran inválido al otorgante revocado. No se ocultan excepciones desconocidas.
- Revisión del formulario: al seleccionar consentimiento o referencia para revocar se mostraba revisión cero. Las tres interfaces cargan ahora la revisión del registro elegido, también al cambiar selección o recargar. El servidor conserva el rechazo CAS ante una revisión realmente obsoleta; la interfaz no lo elude.

Pruebas añadidas: dos empresas verificadas y sus administradores, rechazo entre empresas y roles, roles institucionales sin privilegio empresarial heredado, reclamaciones JWT falsas, cuenta inactiva, cambio de rol y revocación del otorgante, caducidad con reloj controlado, capacidades no delegables y de billetera, integridad alterada, recibos ajenos, UUID reutilizado con cuerpo distinto, límites de cuerpo/JSON/tipo de contenido/contexto, fuentes de consentimiento y todos sus canales/finalidades. Dos conexiones SQLite independientes compiten por la misma revisión: una confirma y otra recibe conflicto, sin doble registro. En los nativos se usa una copia desechable en archivo para disponer de conexiones realmente separadas; no se presenta como cualificación PostgreSQL.

El navegador ejecuta los seis comandos (`grant`, `revoke_grant`, `record_consent`, `revoke_consent`, `link_identity`, `revoke_alias`) en SGA-CD, ERP, Analemática y gateway, a 1280/390/320 píxeles. Comprueba doble submit, pérdida de respuesta, recarga/recibo sin repetición, revisión automática, efecto de la revocación en el CRM y retirada del panel al recibir 403. Se conservan las 17 opciones de navegación y la identidad azul/celeste/blanco. La billetera personal continúa disponible a toda persona registrada; no se modifican sus requisitos ni se conceden privilegios financieros por marketing. Turismo Nacional sigue siendo institucional.

**Resultado final:** 12 suites aprobadas, **263 pruebas Python y 424 comprobaciones de navegador** (336 de administración y 88 de regresión CRM), sin saltos; fuente estable y hashes comprobados. No se suman los intentos anteriores ni las repeticiones para aumentar resultados o hitos. El primer intento incompleto se conserva separado y no acredita aprobación; al actualizar la prueba de baja se tuvo en cuenta la nueva revisión que produce la revocación CRM. Diez comprobaciones adicionales del registro comercial aprobaron. Evidencia técnica: `ANALISIS/gestion-comercial/evidencias/gc002-paso2-20261112/summary.json`. Se preservan sin alteración los 80 registros anteriores de evidencia.

Reproducir con un directorio nuevo: `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-access --profile commercial-crm --output .runtime/<directorio-nuevo>`. El perfil `commercial-access` queda incorporado también a `commercial-audit`; esta entrega ejecutó los 12 trabajos seleccionados, no una nueva auditoría de todos los frentes.

**Pendiente externo:** paso 3/GCH-006, aceptación con usuarios y políticas legítimos/revisados. El usuario indicó que no dispone de ese conjunto; no se solicita otra vez ni se sustituye por datos sintéticos. No están cualificados PostgreSQL/carga de infraestructura objetivo, equipos físicos ni producción. La secuencia de cierres sigue detenida en GC-003 hasta la aceptación correspondiente; no se cerró otra tarea. No se operaron cuentas reales, proveedores o servicios pagados. Sin cambio de crédito contable, commit, push, merge ni actualización de main. Se conserva el respaldo verificable de fuentes y evidencias.
<!-- GC002-STEP2-END -->


<!-- GC002-STEP3-BEGIN -->
### Paso 3 comercial · preparación de aceptación GC-002/GCH-006 · 2026-11-13

**Preparación codificada y probada; aceptación externa pendiente.** El paso original exige revisar usuarios, permisos, políticas y consentimientos con administradores legítimos y obtener aprobación trazable. El usuario ya indicó que no dispone de las muestras autorizadas/políticas revisadas. No se vuelve a pedir ese conjunto ni se sustituye por cuentas sintéticas. No se acredita GCH-006: el crédito sigue en37/72=51,39%,aceptación1/24 y producción deshabilitada. El porcentaje es crédito de hitos; la medición completa de implementación continúa sin acreditar.

Se añadió `BACKEND/INTEGRACIONES/operacion/commercial_identity_acceptance.py`, una herramienta de preparación de solo lectura, independiente de los runtimes comerciales. Reutiliza la validación del registro F/T, comprueba el hash del informe del paso2, sus trabajos requeridos, logs, manifiesto y coincidencia actual de las fuentes comerciales de identidad. Detecta cambios de código, evidencia ausente o alterada, saltos/errores de pruebas y rutas fuera del repositorio. No ofrece bandera de aprobar, no ingiere aprobaciones por cuenta propia ni modifica permisos, usuarios, billetera o crédito. El perfil `commercial-identity-acceptance` queda disponible en el runner y en la auditoría comercial general.

Resultado actual: integridad local comprobada;337 fuentes de identidad coinciden con las probadas en el paso2. Checklist externo sin verificación independiente: legitimidad de administradores; matriz de roles/permisos propios; políticas y consentimientos revisados; usuarios/muestras autorizados; acta trazable de revisión y sus pendientes. Un hash de documento no acredita esas condiciones. El resultado es `BLOCKED_EXTERNAL_ACCEPTANCE`, no autorización de publicación ni aceptación de la tarea.

Pruebas nuevas:8 contratos aprobados (evidencia alterada, cambio de código, ausencia de pruebas, límites de rutas/symlinks, imposibilidad de autoaceptar y estado real del repositorio). También aprobaron21 contratos del runner y10 del registro comercial. No se repitieron ni sumaron las263 pruebas/424 comprobaciones históricas del paso2 como si fueran nuevas: sus artefactos se contrastan por integridad y337 fuentes declaradas. No se certifica la infraestructura objetivo, PostgreSQL o dispositivos físicos con esta preparación.

Evidencia técnica: `ANALISIS/gestion-comercial/evidencias/gc002-paso3-20261113/summary.json`; checklist verificable en `quality/identity-acceptance.json`. Reproducir con `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-identity-acceptance --output .runtime/<directorio-nuevo>`. El éxito de las pruebas del verificador no cambia el resultado bloqueado de aceptación.

Se mantienen los81 registros anteriores de evidencia sin alteración. Paso3 queda en preparación local completada y aceptación externa bloqueada; no se pasa al siguiente cierre secuencial ni se cierra GC-003. No hubo operación sobre usuarios reales, servicios pagados, proveedores, cuentas, despliegue, commit, push o actualización de main. Se conserva respaldo verificable; sin cambio de crédito contable.
<!-- GC002-STEP3-END -->


<!-- GC003-STEP4-BEGIN -->
### Paso 4 comercial · preparación de aceptación del CRM · 2026-11-13

**Preparación local codificada; el paso de aceptación no está terminado.** GCH-009 exige aceptar los recorridos del CRM en SGA-CD, ERP y Analemática con muestras autorizadas y después de aceptar GC-002. El usuario indicó no disponer del material de aceptación; GC-002/GCH-006 permanece abierto. No se solicita otra vez el mismo conjunto ni se certifican usuarios sintéticos. Resultado: `BLOCKED_DEPENDENCY_AND_EXTERNAL_ACCEPTANCE`. No se salta la dependencia ni se acredita GCH-009.

Se amplió la herramienta existente `BACKEND/INTEGRACIONES/operacion/commercial_identity_acceptance.py` con `--task GC-003`, manteniendo GC-002 como valor predeterminado. Comprueba las dependencias según la aceptación integral registrada, las siete familias de regresión CRM del paso2 y sus logs/manifiesto/fuentes actuales. La procedencia de esa regresión se declara explícitamente como GC-002: no se reescribe la evidencia histórica de GC-003 ni se presenta el contraste de hashes como una ejecución nueva. Las337 fuentes de alcance declarado siguen coincidiendo. No se modificaron los módulos de aplicación de los tres sistemas para fabricar un incremento funcional ya existente.

El checklist externo cubre alta, búsqueda, actualización, seguimiento, revisión de duplicados, conversión, baja y consentimiento/historial. Todos quedan sin verificación independiente. La herramienta no admite autoaprobar ni modifica usuarios, permisos, datos de clientes, billetera o producción. Turismo Nacional conserva su carácter institucional; los módulos comerciales y roles propios no se fusionan.

Verificación:12 pruebas de contrato de la herramienta aprobadas (ocho existentes y cuatro adicionales para CRM),21 del runner y10 del registro comercial:43 en esta ejecución. Tres trabajos del perfil aprobados, con fuentes estables y hashes comprobados; el éxito de las pruebas del verificador no convierte su resultado bloqueado en aceptación. No se repitieron ni sumaron las pruebas CRM históricas para inflar el avance. Evidencia: `ANALISIS/gestion-comercial/evidencias/gc003-paso4-20261113/summary.json`; resultado detallado en `quality/crm-acceptance.json`.

Reproducir: `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-identity-acceptance --output .runtime/<directorio-nuevo>`. También puede emitirse solo el diagnóstico con la herramienta existente, `--task GC-003 --output <archivo-nuevo.json>`.

Crédito sin cambios:37/72=51,39%,1/24 tareas aceptadas; la implementación global continúa sin porcentaje certificado y producción deshabilitada. Pendientes concretos: aceptación legítima de identidad GC-002 y recorridos del CRM con muestras consentidas y titulares autorizados. Se mantienen los82 registros anteriores de evidencia; no se cierra otra tarea de la secuencia. Sin cambios contables, acciones sobre cuentas reales, commit, push o actualización de main. Respaldo de fuentes y evidencia conservado y verificado.
<!-- GC003-STEP4-END -->


<!-- GC004-STEP5-BEGIN -->
### Paso 5 comercial · revisión de aceptación de oportunidades · 2026-11-13

**Regresión local aprobada; aceptación GCH-012 no completada.** Este paso de la matriz original corresponde a GC-004/A: embudo, responsables, transiciones e historia con casos autorizados y revisión comercial, después de GC-003. GC-003 continúa sin aceptar; tampoco se dispone del conjunto de aceptación autorizado indicado en el seguimiento. No se cambia el alcance a una función nueva ni se acredita aceptación mediante cuentas sintéticas.

Se ejecutó el perfil existente `commercial-opportunities` para comprobar su integración tras las correcciones recientes de identidad. Ocho suites aprobaron:69 pruebas Python y229 comprobaciones de navegador/recuperación (120 del embudo y sus recorridos HTTP propios,88 de regresión CRM y21 de recuperación con transporte controlado). No hay saltos ni cambios de fuente durante la ejecución; hashes verificados. Se conservan la separación por empresa, responsables y roles nativos, transiciones autorizadas, historia, recuperación y reintento. Un estado ganado conserva cobro no verificado y no acredita factura, asiento o ingreso financiero.

El código y la interfaz existentes identifican la prioridad por reglas como `NOT_CALIBRATED`, con probabilidad/precisión predictivas sin acreditar. No se entrenó ni activó un predictor, ni se fabricó un dataset consentido. La evaluación predictiva con datos consentidos sigue pendiente; se mantiene la declaración de no calibrado. Las pruebas no encontraron una falla nueva que exigiera cambiar el código de aplicación. **Esta entrega verifica lo existente: no se declara una nueva implementación funcional ni se añade otro verificador para aparentar avance.**

Evidencia: `ANALISIS/gestion-comercial/evidencias/gc004-paso5-20261113/summary.json`, con informe, manifiesto, logs y artefactos visuales. Reproducir con `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-opportunities --output .runtime/<directorio-nuevo>`. Los resultados corresponden a esta ejecución y no se suman a cifras históricas.

Pendientes: aceptación legítima de GC-003 y sus dependencias; revisión del embudo con responsables comerciales y muestras autorizadas; dataset consentido/evaluación para scoring predictivo. Paso5 queda `BLOCKED_DEPENDENCY_AND_EXTERNAL_ACCEPTANCE`. La secuencia de cierres continúa con GC-003 activa; no se cierra GC-004 ni se pasa a otro cierre por este diagnóstico. Crédito sin cambios:37/72=51,39%,1/24 tareas aceptadas; implementación global aún sin porcentaje certificado. Se preservan los83 registros previos de evidencia. Sin cambios contables, acciones reales, producción, commit, push o actualización de main; respaldo verificable conservado.
<!-- GC004-STEP5-END -->


<!-- GC005-STEP6-BEGIN -->
### Paso 6 comercial · catálogo, precios y aceptación · 2026-11-13

**Corrección monetaria implementada en los tres backends y probada; GCH-015/A sigue pendiente.** El paso original exige revisar precios, descuentos, impuestos y condiciones contra fuentes legítimas, con GC-002 aceptada. Esa dependencia y la revisión comercial/tributaria auténtica siguen abiertas. No se acredita una aceptación con políticas sintéticas:37/72=51,39%,1/24 tareas aceptadas; producción deshabilitada e implementación global sin porcentaje certificado.

Hallazgo real reproducido: `Pricing.estimate` fijaba precisión50, pero heredaba límites de exponente, flags y traps del contexto global Decimal. Una petición con precio válido, con límites/traps ambientales más restrictivos, provocaba `decimal.Overflow` en vez de devolver una estimación. La prueba nueva falló antes de la corrección; se conserva el log `before-decimal-failure.log`.

Solución en los `pricing.py` propios de SGA-CD, ERP y Analemática: contexto Decimal nuevo y explícito por cálculo, con precisión, redondeo, exponentes, flags y traps definidos. Se conserva redondeo HALF_UP por línea y dos decimales, sin Float. No se modifica el contexto del llamador ni se amplían permisos, descuentos, tasas o monedas. La prueba `test_offer_is_independent_of_ambient_decimal_traps_and_exponents` comprueba los importes exactos y que el contexto ambiental continúa intacto. El servidor sigue rechazando precio/total manipulados y descuento no permitido; los tratamientos tributarios siguen siendo revisiones declaradas, sin legitimidad certificada.

Se añadió el perfil reproducible `commercial-pricing` al runner existente. Resultado: seis suites aprobadas,78 pruebas Python del perfil y104 comprobaciones de navegador HTTP local. Además aprobaron49 pruebas de los consumidores de precios:30 de cotizaciones nativas,16 SGA-CD y3 HTTP. Total Python de la entrega:127; no se suman ejecuciones históricas. El conteo preliminar de53 cotizaciones fue corregido a49 al consolidar los logs. Las fuentes permanecieron estables y sus hashes se verificaron. No se operaron servicios ni usuarios reales.

Evidencia: `ANALISIS/gestion-comercial/evidencias/gc005-paso6-20261113/summary.json`, con regresión antes/después, informe, logs de cotizaciones y evidencias visuales. Reproducir el perfil con `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-pricing --output .runtime/<directorio-nuevo>`. Los tres scripts de cotizaciones y sus conteos/hashes se conservan en la evidencia adicional.

El cambio de pricing modifica fuentes incluidas en el manifiesto histórico del paso2. Los prechecks de aceptación que contrastan ese corte amplio deben requerir revalidación cuando detecten esa diferencia; los registros anteriores se preservan como históricos. No se alteraron sus hashes ni se atribuyó vigencia universal a una prueba anterior.

Pendientes de cierre: aceptar identidad/usuarios GC-002 y revisar tarifas/condiciones legítimas y tratamiento tributario con los responsables correspondientes. El paso6 queda `BLOCKED_DEPENDENCY_AND_EXTERNAL_ACCEPTANCE`; esta corrección mejora F/T ya acreditados y no produce crédito nuevo de aceptación. Se conservan84 registros previos sin alteración; sin cambios contables, commit, push ni actualización de main. Respaldo de fuentes y evidencias verificado.
<!-- GC005-STEP6-END -->


<!-- GC006-STEP7-BEGIN -->
### Paso 7 comercial · cotizaciones y respuestas tardías · 2026-11-13

**Correcciones de interfaz implementadas en SGA-CD, ERP y Analemática; aceptación integral pendiente.** El alcance original incluye copia, carga inicial, respuestas tardías, versiones, enlaces y aceptación del destinatario. Sus dependencias GC-004/GC-005 y las condiciones comerciales aprobadas por empresa siguen sin aceptación. No se acredita GCH-018/A:37/72=51,39%,1/24 aceptadas, producción deshabilitada e implementación global sin porcentaje certificado.

Cambios en los `js/commercial-quotations.js` propios:

- Carga inicial con bloqueo efectivo y guardia de preparación; error recuperable mediante botón de reintento. Navegación/empresa pueden recuperarse del error mientras el formulario continúa protegido.
- Una operación de copia en curso impide reentrada; se revisó el código actual y había un solo manejador, por lo que no se atribuye una eliminación de duplicado inexistente. Opciones y líneas se actualizan bajo bloqueo y con selección vigente.
- Generaciones de petición para opciones, listado y detalle: una respuesta de una selección anterior no reemplaza la actual. Las opciones se publican al completar sus tres lecturas vigentes.
- Controles recién renderizados mantienen el bloqueo; recursos y adjuntos respetan preparación, cierre y señales de cancelación. Los callbacks comprueban el cierre antes de tocar el panel.
- Fallo reproducido y corregido: un rechazo400 tardío después del cierre podía borrar el identificador de recuperación de una instancia nueva en el mismo contexto. La lectura ahora descarta respuestas de paneles cerrados antes y después de procesar el cuerpo, conservando el identificador nuevo. La prueba falló antes y pasa después en las tres interfaces; se conserva `late-receipt-before.log`.

Se añadieron33 comprobaciones Chromium de ciclo de vida con transporte controlado: error inicial/reintento, doble evento de copia, selección con respuestas invertidas, cierre durante carga y preservación del recibo de una instancia nueva. La regresión final del perfil `commercial-quotations` aprobó ocho suites,73 pruebas Python y218 comprobaciones de navegador:176 de recorridos HTTP reales locales,33 de ciclo de vida y9 de bloqueo durante multimedia. Las pruebas de backend mantienen versión/vigencia, enlaces, reintentos sin duplicación y aceptación sin cobro ni reserva definitiva. No se presenta la posesión de un enlace como verificación de identidad civil. Las condiciones tributarias/comerciales de los fixtures son sintéticas.

La navegación y paleta se conservan; los manifiestos web/Flet incorporan el hash vigente y mantienen los anteriores. Evidencia: `ANALISIS/gestion-comercial/evidencias/gc006-paso7-20261113/summary.json`, informe, manifiesto, logs y artefactos visuales. Reproducir con `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-quotations --output .runtime/<directorio-nuevo>`. Se acredita solamente lo ejecutado en la regresión final; las ejecuciones anteriores no se suman.

Pendientes de aceptación: GC-004 y GC-005; condiciones aprobadas por cada empresa y recorridos con participantes autorizados. El paso queda `BLOCKED_DEPENDENCY_AND_EXTERNAL_ACCEPTANCE`, sin cerrar otro hito integral. Se preservan85 registros previos sin alteración. Sin cambio de crédito contable, acciones sobre cuentas reales, despliegue, commit, push o actualización de main. Respaldo de fuentes/evidencia verificado.
<!-- GC006-STEP7-END -->


<!-- GC007-STEP8-BEGIN -->
### Paso 8 comercial · venta, operación y ledger · 2026-11-13

**Correcciones implementadas en las tres interfaces; aceptación GCH-021 pendiente.** Se revisó el flujo existente de venta, precondiciones, fuente, costos laborales, asiento y recuperación. El cierre integral sigue condicionado a GC-006, revisión contable/laboral legítima y aceptación fiscal/documental aplicable. Crédito sin cambios:37/72=51,39%,1/24 aceptadas; producción deshabilitada e implementación global sin porcentaje certificado.

Cambios en los `js/commercial-sales.js` propios de SGA-CD, ERP y Analemática:

- Preparación inicial bloqueada hasta completar cotizaciones, ventas y recuperación. Un error conserva el formulario protegido y ofrece reintento; la carga de un panel cerrado no toca la instancia nueva.
- Lecturas descartadas al cerrar el panel; generaciones para listado, detalle, cuentas y vínculos evitan actualizar selecciones antiguas. Los controles creados al renderizar mantienen bloqueo durante las cuentas y comandos.
- Recuperación con validación JSON/UUID: una referencia malformada se descarta con aviso para revisar las ventas del servidor; no borra registros financieros ni consulta una ruta arbitraria. Las respuestas tardías de un panel cerrado conservan el recibo de la instancia nueva.
- Fallo de acceso al ledger reproducido sobre el respaldo anterior: el formulario lleno enviaba `{}` porque `FormData` se leía después de deshabilitar sus controles. Los campos se capturan antes del bloqueo; la contraseña se borra del objeto y del formulario en `finally`. La prueba usa exclusivamente valores sintéticos dentro de Chromium y conserva el log de fallo anterior.

El perfil nuevo `commercial-sales` del runner existente aprobó10 suites,89 pruebas Python y144 comprobaciones de navegador:112 de recorridos HTTP locales y32 del ciclo de vida con transporte controlado. Cubre modelos nativos, fuente documental, recuperación/saga, puente, controles laborales, HTTP e interfaz. Las revisiones y confirmaciones de la venta se mantienen separadas; las pruebas distinguen borrador, venta/asiento y factura/pago, y comprueban reintentos/recuperación sin duplicación. No se modificó la lógica de contabilización ni de cupos para lograr la corrección visual, ni se desarrolló el RAT. La navegación y paleta se conservan; hashes web/Flet actualizados.

La prueba de login del ledger en navegador es sintética; no acredita acceso a una cuenta contable real. El artefacto visual declara expresamente sus límites del peer SGA, y las suites HTTP/puente registran la evidencia local complementaria. No se transmitieron credenciales reales ni se operaron bancos, DIAN o almacenamiento de clientes. Una venta contabilizada en los fixtures no acredita factura fiscal ni movimiento bancario.

Evidencia: `ANALISIS/gestion-comercial/evidencias/gc007-paso8-20261113/summary.json`, informe, manifiesto, logs, comparativa del login y evidencias visuales. Reproducir con `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-sales --output .runtime/<directorio-nuevo>`. Conteos de la ejecución final, sin sumar repeticiones históricas; fuentes estables y hashes comprobados.

Pendientes: aceptación GC-006 y sus dependencias; soportes/casos reales revisados por los responsables contables/laborales; DIAN y custodia reales para la aceptación fiscal/documental que corresponda. Paso8 queda `BLOCKED_DEPENDENCY_AND_EXTERNAL_ACCEPTANCE`; no se cierra otro hito integral. Se preservan86 registros anteriores sin alteración. Sin cambio de crédito contable, commit, push o actualización de main; respaldo verificado de fuentes y evidencias.
<!-- GC007-STEP8-END -->


<!-- GC008-STEP9-BEGIN -->
### Paso 9 comercial · confirmación auténtica Bold · 2026-11-13

**Paso funcional bloqueado, no terminado ni acreditado.** GCH-022/F requiere verificador de acuses según contrato oficial, consulta auténtica, resultados inciertos y conciliación idempotente enlazada al asiento. El código actual contiene el transporte de checkout y la intención durable, pero `verify_webhook` y la confirmación auténtica siguen bloqueados. No se reemplazaron por un HMAC/endpoint supuesto, un hash declarado ni una respuesta de navegador. El alcance funcional sigue incompleto; crédito37/72=51,39%,1/24 aceptadas, producción deshabilitada e implementación global sin porcentaje certificado.

Se intentó consultar documentación pública en developers.bold.co. La petición dentro del sandbox no alcanzó el proxy; el reintento autorizado fuera del sandbox fue rechazado en CONNECT por el proxy403 (curl56). No fue una respuesta HTTP del origen Bold ni un rechazo de la revisión automática de aprobación. El entorno indica política aplicada y actual, pero el dominio de documentación no está permitido y no hay secretos vinculados. Se inspeccionaron únicamente nombres de variables, sin imprimir valores, del proceso y de los dos .env conocidos; no se encontraron las vinculaciones Bold que exige este módulo. Esto describe este entorno, no niega que el usuario hubiese entregado una API anteriormente.

Acción para desbloquear red: se leyó la configuración existente y se guardó una propuesta parcial que agrega únicamente `developers.bold.co`, preservando los seis dominios personalizados anteriores, presets, instalación, repositorios y demás configuración. Persistencia confirmada en revisión10; `requires_publish=true`. La propuesta **no está aplicada al runtime**: el usuario debe revisar, guardar y publicar la configuración del entorno. No se agregó permiso para crear pagos ni se contactó una API financiera. La política actual se volvió a consultar y continúa sin permitir el dominio.

Regresión ejecutada con el perfil existente `commercial-payments`: siete suites aprobadas,36 pruebas Python y177 comprobaciones de navegador (150 HTTP locales con datos sintéticos y27 de ciclo de vida/control de transporte). Se mantienen rechazos a pruebas falsas de dinero, aislamiento comercial, control del envío e incertidumbre. Un resultado incierto no se resuelve repitiendo automáticamente un POST. Estos resultados verifican fronteras existentes; **no prueban firma Bold, cobro, consulta auténtica ni asiento de liquidación**. No hubo llamadas al proveedor ni cambios en código de aplicación para simular una implementación.

Evidencia: `ANALISIS/gestion-comercial/evidencias/gc008-paso9-20261113/summary.json`; diagnóstico de red/vinculaciones sin secretos en `network-and-bindings.json`, informe y artefactos de pruebas en sus subcarpetas. Reproducir la regresión con `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-payments --output .runtime/<directorio-nuevo>`.

Pendientes concretos de desarrollo: contrato oficial verificable y acuses legítimos para implementar la firma sobre el formato auténtico; contrato y entorno cualificados para la consulta de estado; conciliación de resultado ligada a venta/importe/empresa y asiento sin duplicación. Pendientes externos: aplicación de la red propuesta, configuración privada de pruebas del comercio/acuses y aceptación GC-007. No se vuelve a pedir claves por chat ni se da por configurada una vinculación ausente.

Paso9 queda `BLOCKED_PROVIDER_CONTRACT_AND_CONFIGURATION`, GCH-022 en ejecución sin crédito. Se preservan87 registros anteriores. Sin cambios contables, cobros, despliegue, commit, push ni actualización de main; respaldo de fuentes y evidencia verificado. La propuesta de entorno se conserva en la configuración administrada, no es una publicación de código.
<!-- GC008-STEP9-END -->


<!-- GC008-STEP10-BEGIN -->
### Paso 10 comercial · regresión auténtica Bold · 2026-11-13

**Bloqueado por el paso9; GCH-023/T sin acreditar.** La matriz exige comprobar firmas inválidas, repetición/orden de eventos, discrepancias de importe/venta/empresa, consulta auténtica, incertidumbre y liquidación idempotente. El verificador/consulta/conciliación del contrato auténtico de GCH-022 aún no están implementados. La ejecución de pruebas de frontera existentes no sustituye esos escenarios ni completa F/T.

Se volvió a consultar el entorno:developers.bold.co continúa fuera de la política aplicada y no hay secretos vinculados por la configuración administrada. La propuesta de red del paso9 permanece guardada y requiere revisión/guardado/publicación para aplicarse. No se repitió una petición ya rechazada por la misma política ni se inventó el contrato de firma. El usuario ya explicó que había entregado una API antes; este diagnóstico se limita a las vinculaciones observables del entorno actual.

Verificación local efectuada: hashes de todos los artefactos del paso9 comprobados y digest de fuentes actuales idéntico al de su regresión. Esa regresión se conserva como evidencia histórica; no se volvió a ejecutar ni se presenta como pruebas nuevas. El inventario técnico identifica siete escenarios bloqueados por la ausencia funcional: firma inválida; replay; orden invertido; discrepancia de importe/comercio/venta; consulta auténtica; resolución de resultados inciertos; liquidación/asiento sin duplicación.

Evidencia: `ANALISIS/gestion-comercial/evidencias/gc008-paso10-20261113/summary.json`, con procedencia explícita de la regresión previa. No hay cambio de código de aplicación ni nuevas pruebas de una función ausente. Para completar el paso se debe implementar primero GCH-022 contra contrato/acuses auténticos y luego ejecutar estos escenarios con sandbox autorizado y persistencia real de prueba. Los acuses sintéticos y un hash declarado no se convierten en aceptación de dinero.

Crédito sin cambios:37/72=51,39%,1/24 aceptadas; producción deshabilitada e implementación global sin porcentaje certificado. Se mantienen88 registros anteriores sin alteración. Sin cobros, asientos de liquidación nuevos, cambios contables, commit, push o actualización de main. Se conserva respaldo de metadatos y evidencias; las fuentes de aplicación siguen respaldadas en el corte del paso9.
<!-- GC008-STEP10-END -->


<!-- GC008-STEP11-BEGIN -->
### Paso 11 comercial · aceptación Bold · 2026-11-13

**Aceptación GCH-024 bloqueada; sin cierre ni crédito.** Se comprobó el estado actual del entorno y la matriz: GCH-022/F y GCH-023/T continúan sin verificar; developers.bold.co sigue fuera de la política aplicada y no hay secretos vinculados por la configuración administrada. La propuesta de red del paso9 está guardada para revisión/guardado/publicación, aún sin aplicar. Estas observaciones no niegan la entrega anterior de una API por el usuario; no se vuelve a pedir una clave en chat.

Para completar este paso se requiere cerrar la implementación/regresión auténticas de los pasos9/10 y validar un comercio de pruebas autorizado: acuse ligado a venta/empresa/referencia/importe/moneda, conciliación y asiento revisados, idempotencia y resolución auténtica de incertidumbre. Un documento declarado, un enlace o una prueba sintética no sustituyen la evidencia del proveedor. La habilitación productiva y el gasto mantienen su autorización separada.

No hubo nuevos tests, llamadas Bold ni código de aplicación en esta comprobación; los resultados históricos siguen referenciados en la evidencia de los pasos9/10. Registro técnico consolidado en `ANALISIS/entregas/evidencias/recuperacion-originales-20261110/verificacion.json`, `followups.gc008_step11_provider_acceptance_blocker_20261113`; sin crear otro informe por diagnóstico.

Paso11 queda `BLOCKED_FUNCTIONAL_AND_PROVIDER_ACCEPTANCE`;37/72=51,39%,1/24 tareas aceptadas, producción deshabilitada e implementación global sin porcentaje certificado. Se preservan89 registros anteriores sin alteración. Sin cambios contables, cobros, commit, push ni actualización de main; respaldo de los metadatos actualizado y fuentes conservadas en el corte del paso9.
<!-- GC008-STEP11-END -->


<!-- GC009-STEP12-BEGIN -->
### Paso 12 comercial · posventa y devolución · 2026-11-13

**Incremento parcial implementado y probado; GCH-025/F no se acredita como completo.** Se corrigió el seguimiento de posventa y se verificaron políticas/reembolso interno existentes. Siguen pendientes vinculación verificable CRM/contacto/venta/reserva/destinatario, cancelación efectiva completa y recorrido integral de firma/fidelización del alcance original. El backend conserva `customer_binding_verified=false`: ni el nombre, correo ni coincidencia de IDs se utilizan para simular esa identidad. La devolución bancaria auténtica depende de GC-008/proveedor. Políticas legítimas y aceptación siguen pendientes.

Fallos subsanados en las tres interfaces propias: doble evento de seguimiento antes de terminar el GET del contacto; pérdida de UUID/revisión al reabrir el componente; respuestas de una instancia cerrada y selección de proveedor durante comandos. La guardia se activa antes de cualquier await. Se conserva en sessionStorage solo UUID, revisión original y fingerprint, con clave por sistema/empresa/actor/proveedor; no guarda el cuerpo ni soporte/credenciales. Un intento pendiente en memoria se muestra como reintento y mantiene sus datos protegidos. La reapertura exige los mismos datos para reutilizar ese UUID/revisión. Si no se puede guardar la referencia, el cliente no transmite. Descartar la referencia es explícito y pide revisar el historial: no cancela un registro confirmado. Contactos tienen carga/reintento y las operaciones usan contador de actividad para no desbloquear un comando aún en curso.

Protección añadida en el servidor, en `after_sales_followup.py` propio de cada backend: bloqueo empresarial y chequeo de tarea exacta (contacto/reserva/título/fecha/responsable) dentro de la transacción CRM, conservando el protocolo de UUID/fingerprint y la forma original de la fecha para replay. Una petición con el mismo UUID y mismo cuerpo recupera el recibo; cambiar el cuerpo conserva conflicto. Otro UUID no puede repetir ese seguimiento exacto, incluso con revisión fresca. Instantes equivalentes con codificación de zona distinta se reconocen como duplicados. La inserción y el evento comparten commit; un fallo de auditoría revierte ambos. Esto protege el endpoint de seguimiento; no acredita la identidad del beneficiario ni genera recompensa.

Pruebas: ocho suites aprobadas,68 pruebas Python y94 comprobaciones de navegador (58 HTTP locales de políticas y36 con transporte controlado). Incluyen bandas de30/15/7/0 días, reembolso interno financiado e idempotente, rechazo al omitir firma requerida, duplicados/replay, aislamiento, rollback y dos conexiones SQLite con un solo seguimiento. La prueba de reapertura desmonta/remonta el componente y conserva sessionStorage; no es una prueba de recarga completa de página ni de proveedor real. No se certifican dispositivos físicos: los fixtures de reembolso declaran sus límites de firma.

El cliente anterior generaba dos UUID distintos ante dos eventos concurrentes; se reprodujo contra el respaldo y se conserva el fallo. No se afirma que esos dos envíos hubieran confirmado dos tareas, porque el control de revisión previo podía rechazar uno. La nueva protección de servidor también impide la repetición con otro UUID y revisión fresca. Los reintentos y los recibos se conservan sin inflar contadores por ejecuciones anteriores.

Evidencia: `ANALISIS/gestion-comercial/evidencias/gc009-paso12-20261113/summary.json`, informe, manifiesto, logs y visuales. Reproducir con `PYTHONDONTWRITEBYTECODE=1 /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-after-sales --output .runtime/<directorio-nuevo>`. Se mantienen navegación/paleta y módulos propios, sin fusionar carpetas. La billetera personal sigue disponible a toda persona registrada, sin exigir afiliación turística; no se inventa saldo, premio, cobro ni devolución bancaria.

Paso12 queda `PARTIAL_IMPLEMENTATION_VERIFIED`: falta desarrollo además de requisitos externos; no se presenta como cierre local total. Crédito sin cambios37/72=51,39%,1/24 aceptadas; implementación global sin porcentaje certificado y producción deshabilitada. Se preservan90 registros anteriores sin alteración. Sin cambio de crédito contable, acciones reales, commit, push ni actualización de main. Respaldo de fuentes y evidencia verificado.
<!-- GC009-STEP12-END -->


<!-- COMMERCIAL-STEPS01-12-AUDIT-20261113 -->
### Evaluación y subsanación de los pasos 1–12 del plan comercial restante · 2026-11-13

Alcance: los pasos numerados del plan restante de37 hitos, correspondientes a GC-002–GC-009; no se confunden con las primeras12 tareas originales ni con el motor contable. Se revisaron implementaciones propias, aislamiento, transacciones, reintentos, errores de interfaz, evidencia y dependencias. No se fusionaron carpetas ni roles; Turismo Nacional sigue siendo institucional. Jarvi, Neko y SOUP conservan sus funciones y no reciben nuevas facultades financieras.

**Fallos encontrados y subsanados:**

- Posventa ignoraba un JSON de reintento dañado o ilegible y podía preparar otro UUID. Los tres clientes propios ahora conservan un estado de referencia no recuperable, impiden enviar y muestran revisión/descartado explícito tras consultar el historial. Se valida UUID, huella y revisión entera segura. La reproducción contra el respaldo anterior emitió la petición número3 cuando debía conservar2; la regresión corregida conserva2. Transporte controlado: no demuestra dos reembolsos ni movimientos bancarios reales.
- La carga de contactos no tenía exclusión propia y no mantenía ocupado el panel padre. Se añadió bloqueo durante esa carga, evitando lecturas superpuestas y habilitación prematura. Si falla eliminar una referencia, el cliente no la descarta silenciosamente. Se mantienen las guardias anteriores de doble envío, cierre de instancia y recuperación idempotente.
- Tres expectativas del test de aceptación suponían que el corte histórico seguía siendo el actual. Fallaron al comprobar el código posterior, mientras el verificador bloqueaba correctamente la evidencia obsoleta. Se separaron las pruebas del bloqueo externo de la comprobación de vigencia y se añadió una regresión explícita: evidencia con fuentes cambiadas no puede aceptar GC-002 ni GC-003. No se relajó el verificador ni se reescribieron resultados históricos.

Tras aprobar la regresión conjunta se renovó únicamente la referencia de verificación local GCH-005 con el corte actual. La referencia anterior queda conservada en la evidencia técnica y su registro original no cambia. El nuevo registro acredita de nuevo ese hito existente; no concede crédito nuevo ni aceptación de las demás tareas. El verificador de preparación vuelve a evaluar fuentes actuales y mantiene bloqueadas la aceptación externa y las dependencias.

**Verificación reproducible:**54 suites distintas aprobadas,578 pruebas Python y1320 comprobaciones de navegador, sin sumar reejecuciones ni conteos de entregas anteriores. Se aprobaron además10 pruebas de coherencia de la matriz. Las13 pruebas de aceptación se repitieron después de renovar la referencia: esa repetición no aumenta578. El manifiesto antes/después fue estable y los hashes de logs/fuentes se verificaron después de copiar la evidencia. Se conservaron los91 registros previos mediante comparación de sus hashes canónicos; se añadió un registro de auditoría.

La batería cubre administración de acceso, CRM, integridad de eventos, oportunidades, importes Decimal, cotizaciones, saga/puente de ventas, pagos bloqueados y posventa. Incluye HTTP local entre servicios, rollback, aislamiento, disputas de revisión, recuperación y Chromium. Los visuales conservan azul metalizado, azul claro y texto blanco. Las pruebas usan datos sintéticos; las firmas de laboratorio y SQLite no acreditan hardware, PostgreSQL, fiscalidad ni proveedor auténtico. No se califica una compilación completa de Next.js, una auditoría de seguridad independiente ni aceptación móvil física mediante estos perfiles.

| Paso | Resultado real después de la evaluación | Pendiente para cierre |
|---|---|---|
|1 · Identidad y permisos | Funcionalidad local verificada. | Aceptación de personas, autoridad y políticas del paso3. |
|2 · Pruebas de identidad | Regresión actual aprobada y evidencia renovada. | No equivale a aceptación integral. |
|3 · Aceptación de identidad | Bloqueada. | Administradores legítimos, roles y consentimientos revisados, muestras autorizadas y revisión trazable. |
|4 · Aceptación CRM | Bloqueada por identidad y aceptación propia. | Recorridos con muestras legítimas y políticas revisadas; disponibilidad ya declarada como inexistente, no se solicita otra vez. |
|5 · Oportunidades | Regresión local aprobada; aceptación bloqueada. | Aceptar CRM y criterios empresariales; el score de reglas no es probabilidad calibrada. |
|6 · Catálogo/precios | Cálculo y regresión aprobados; aceptación bloqueada. | Tarifas y tratamiento tributario legítimos revisados. |
|7 · Cotizaciones | Regresión local aprobada; aceptación bloqueada. | Dependencias, términos y revisión empresarial autorizados. |
|8 · Venta/ledger | Saga y puente verificados localmente; aceptación bloqueada. | Cotización aceptada y revisión contable/laboral/fiscal legítima. |
|9 · Confirmación Bold | Funcionalidad auténtica incompleta. | Contrato vigente y configuración segura para implementar confirmación/reconciliación/asiento auténticos. El retorno del navegador no acredita dinero. |
|10 · Regresión Bold | Pruebas de bloqueos aprobadas; hito auténtico pendiente. | Completar9 y probar acuses reales, duplicados, importe/moneda/empresa, incertidumbre y conciliación. |
|11 · Aceptación Bold | Bloqueada. | Cerrar9/10 y aceptación legítima de proveedor/comercio; no hay liquidaciones reales acreditadas. |
|12 · Posventa | Incremento parcial corregido y probado; alcance funcional completo pendiente. | Vínculo verificable contacto/venta/reserva/destinatario, cancelación efectiva y recorrido integral de firma/fidelización; devolución bancaria depende de Bold. |

**Medición sin cambios:37/72 hitos acreditados=51,39%;1/24 tareas aceptadas; producción deshabilitada. No existe un porcentaje global de implementación certificado mientras la revisión de la base siga incompleta.** No se aumenta el indicador por corregir defectos o repetir pruebas ya acreditadas. La billetera personal conserva acceso general sin afiliación turística; no se crea saldo, pago, recompensa ni reembolso bancario ficticio. RAT/ADR y el alcance contable no cambian.

Evidencia técnica: `ANALISIS/gestion-comercial/evidencias/auditoria-pasos01-12-20261113/summary.json`, `quality/report.json`, manifiesto, logs, visuales, preparación de aceptación actualizada y referencia anterior. Reproducir con `BACKEND/INTEGRACIONES/operacion/verify_local.py` y los perfiles `commercial-access`, `commercial-crm`, `commercial-identity-acceptance`, `commercial-opportunities`, `commercial-pricing`, `commercial-quotations`, `commercial-sales`, `commercial-payments` y `commercial-after-sales`, usando un directorio nuevo bajo `.runtime` y las dependencias web existentes. La lista exacta de comandos está en el informe técnico.

Fuentes y evidencias se conservan en un respaldo verificado fuera del checkout: `auditoria-pasos01-12-20261113.tar.gz`, bajo el directorio de recuperación existente; manifiesto y SHA-256 en su sidecar. Rama conservada, sin commit, push, merge ni actualización de main durante esta evaluación.


<!-- COMMERCIAL-CREDITS01-37-AUDIT-20261113 -->
### Evaluación de los37 créditos comerciales y del plan original de37 pasos · 2026-11-13

Se enumeraron los37 créditos registrados, conservando sus identificadores GCH originales, y se revisaron sus referencias, hashes, informes, logs disponibles, código propio y regresiones actuales. Los ordinales1–37 de esta revisión no renumeran GCH-001–GCH-072 ni alteran la matriz. Se incluyen las24 tareas y los37 pasos del plan original: dos pasos ya estaban verificados localmente, por lo que quedan35 hitos sin acreditar, no37 pendientes nuevos.

**Hallazgos y subsanaciones de código:**

1. El auditor asociaba GC-002 con `crm.py` y las suites de contratos/API generales. Se corrigió para observar los tres `access_admin.py` propios y mapear exclusivamente la familia `pool08_access_`. No se utiliza una prueba de catálogo como prueba de administración de permisos.
2. El informe anterior no exponía una revisión individual de los créditos ni su integridad histórica. Ahora entrega ordinal, GCH, etapa, tarea, referencia anclada por hash, verificación de los artefactos históricos, resultado de regresión relacionada, desarrollo pendiente y requisitos externos por cada crédito. Los informes repetidos se revisan una vez por referencia mediante caché; la presencia del archivo no concede crédito.
3. Se añadió un criterio explícito de regresión vigente: misma huella de fuentes antes/después y en el árbol actual, ejecución completa, IDs únicos y ninguna suite fallida, omitida o con logs truncados/incompletos. Tener un checksum coherente o un hash final coincidente no basta. Las nueve pruebas del auditor incluyen alteración posterior de un informe anclado, rutas externas, evidencia histórica frente a ejecución actual, duplicados, omisiones y fallos.

**Resultado de evidencia:**37/37 referencias de crédito coherentes con el registro;34 créditos tienen artefactos/logs históricos verificables. Los otros3 corresponden a GC-001 y conservan informe/manifiesto incrustados en el registro anclado por hash interno; no se afirma haber verificado logs originales externos sin una ruta anclada. El nuevo corte aporta regresión actual de los contratos con logs conservados, sin reescribir la historia ni convertir esa evidencia interna en autenticidad independiente. Los37 créditos tienen pruebas relacionadas aprobadas en el corte actual. Esto no reacredita de forma independiente el alcance funcional completo de cada tarea.

**Pruebas de este corte:**136 suites distintas aprobadas, 1410 pruebas Python y 3837 comprobaciones de navegador contadas de los informes de Chromium. No se suman pruebas de entregas anteriores ni repeticiones de validadores. La batería completa `commercial-audit` incluye las24 familias de tareas: contratos/permisos/CRM, oportunidades, tarifas/cotizaciones, ventas/ledger/pagos/posventa, landing/captación/biblioteca, generación/vídeo/adaptación, correo/mensajería/publicación/bandeja/anuncios, agentes, analítica, interfaces y recuperación. Se verificaron tipos de componentes aislados; no una compilación completa de Next.js ni dispositivos físicos. Se conservaron las fuentes sin cambios durante la ejecución; hashes y logs se comprobaron posteriormente.

| Crédito de revisión | Hito original | Tarea | Etapa | Evidencia histórica / regresión relacionada actual |
|---:|---|---|---|---|
|1|GCH-001|GC-001|F|Informe incrustado íntegros / aprobada|
|2|GCH-002|GC-001|T|Informe incrustado íntegros / aprobada|
|3|GCH-003|GC-001|A|Informe incrustado íntegros / aprobada|
|4|GCH-004|GC-002|F|Artefactos/logs íntegros / aprobada|
|5|GCH-005|GC-002|T|Artefactos/logs íntegros / aprobada|
|6|GCH-007|GC-003|F|Artefactos/logs íntegros / aprobada|
|7|GCH-008|GC-003|T|Artefactos/logs íntegros / aprobada|
|8|GCH-010|GC-004|F|Artefactos/logs íntegros / aprobada|
|9|GCH-011|GC-004|T|Artefactos/logs íntegros / aprobada|
|10|GCH-013|GC-005|F|Artefactos/logs íntegros / aprobada|
|11|GCH-014|GC-005|T|Artefactos/logs íntegros / aprobada|
|12|GCH-016|GC-006|F|Artefactos/logs íntegros / aprobada|
|13|GCH-017|GC-006|T|Artefactos/logs íntegros / aprobada|
|14|GCH-019|GC-007|F|Artefactos/logs íntegros / aprobada|
|15|GCH-020|GC-007|T|Artefactos/logs íntegros / aprobada|
|16|GCH-028|GC-010|F|Artefactos/logs íntegros / aprobada|
|17|GCH-029|GC-010|T|Artefactos/logs íntegros / aprobada|
|18|GCH-031|GC-011|F|Artefactos/logs íntegros / aprobada|
|19|GCH-032|GC-011|T|Artefactos/logs íntegros / aprobada|
|20|GCH-034|GC-012|F|Artefactos/logs íntegros / aprobada|
|21|GCH-035|GC-012|T|Artefactos/logs íntegros / aprobada|
|22|GCH-043|GC-015|F|Artefactos/logs íntegros / aprobada|
|23|GCH-044|GC-015|T|Artefactos/logs íntegros / aprobada|
|24|GCH-046|GC-016|F|Artefactos/logs íntegros / aprobada|
|25|GCH-047|GC-016|T|Artefactos/logs íntegros / aprobada|
|26|GCH-049|GC-017|F|Artefactos/logs íntegros / aprobada|
|27|GCH-050|GC-017|T|Artefactos/logs íntegros / aprobada|
|28|GCH-052|GC-018|F|Artefactos/logs íntegros / aprobada|
|29|GCH-053|GC-018|T|Artefactos/logs íntegros / aprobada|
|30|GCH-055|GC-019|F|Artefactos/logs íntegros / aprobada|
|31|GCH-056|GC-019|T|Artefactos/logs íntegros / aprobada|
|32|GCH-061|GC-021|F|Artefactos/logs íntegros / aprobada|
|33|GCH-062|GC-021|T|Artefactos/logs íntegros / aprobada|
|34|GCH-064|GC-022|F|Artefactos/logs íntegros / aprobada|
|35|GCH-065|GC-022|T|Artefactos/logs íntegros / aprobada|
|36|GCH-067|GC-023|F|Artefactos/logs íntegros / aprobada|
|37|GCH-068|GC-023|T|Artefactos/logs íntegros / aprobada|

**Lectura real de la matriz:**18 hitos F,18 T y1 A=37/72=51,39% de crédito registrado. Una tarea aceptada (GC-001, contratos/catálogo/APIs privadas y DAG local),17 con F/T y aceptación pendiente, y6 sin crédito F/T. Permanecen35 hitos sin acreditar. El porcentaje global de implementación continúa sin certificar (`baseline_review_complete=false`, `implementation_percent=null`); producción deshabilitada. No se sube el porcentaje por esta auditoría.

**Pendientes que esta batería no cierra:** identidad, autoridad, muestras y consentimientos legítimos; tarifas/términos y revisión contable/tributaria; confirmación/reconciliación/asiento auténticos Bold; vínculo verificable de beneficiario y recorrido completo de posventa; proveedores y recibos reales de canales, entrega/publicación, modelos y series evaluados; partes del alcance de bandeja y producción multimedia; almacenamiento/derechos/retención, concurrencia e infraestructura objetivo; accesibilidad/release/Next.js, dispositivos y restauración integral. Las fuentes, límites y requisitos específicos están preservados por tarea y por crédito en `credit-review.json`; las pruebas sintéticas no cierran esos requisitos. No se vuelven a solicitar muestras o credenciales ya declaradas no disponibles.

Los módulos conservan carpetas propias, identidad visual azul metalizado/azul claro/texto blanco y roles propios. Jarvi sigue operativo, Neko conversacional y SOUP optimizador; no se amplían permisos. Turismo Nacional no se convierte en ERP. La billetera mantiene acceso personal general sin afiliación turística; ninguna prueba acredita pagos o publicaciones en cuentas reales. El motor contable y RAT/ADR no cambian.

Evidencia: `ANALISIS/gestion-comercial/evidencias/auditoria-creditos01-37-20261113/credit-review.json`, resumen, comandos exactos, manifiesto, logs y visuales. Reproducir con `PYTHONDONTWRITEBYTECODE=1 NODE_PATH=/tmp/sgacd-full-web-deps/node_modules /workspace/.integration-venv/bin/python BACKEND/INTEGRACIONES/operacion/verify_local.py --profile commercial-audit --web-dependencies /tmp/sgacd-full-web-deps/node_modules --output .runtime/<directorio-nuevo>`; luego ejecutar `commercial_audit.py --quality <directorio> --output <archivo-nuevo>` y verificar la matriz con `update_plan.py --check`.

Los92 registros anteriores conservan sus hashes canónicos. Se añadió un registro de auditoría sin atribuir hitos nuevos y sin sustituir las referencias históricas. Código y evidencias quedan en el respaldo verificado `auditoria-creditos01-37-20261113.tar.gz` y su manifiesto/SHA-256, dentro del directorio de recuperación existente. No se modifica la historia Git, no hay commit, push ni actualización de main en esta evaluación.


<!-- CONSOLIDATED-DELIVERY-20261113 -->
### Entrega consolidada de los avances · 2026-11-13

El usuario autorizó entregar todo el acumulado. Se prepara un solo commit consolidado y publicación normal a main, sin force ni reescritura, después de comprobar que main remoto coincide con la base363f4120ad97be5d86232ba1cb6218b8f4011d53. La ruta Analematica tiene acceso confirmado. El nombre de la carpeta local no se interpreta como nombre canónico de GitHub. No se hace despliegue productivo.

Se incluyen organización en BACKEND/FRONTEND/MOVILES/DESKTOP, módulos contables y comerciales propios, billetera, integración de agentes, clientes, pruebas y evidencias acumuladas. Se preservan37647 reubicaciones:37578 coincidencias exactas de blob y los restantes destinos revisados como ajustes de rutas/contenido o punteros de submódulos heredados. No hay eliminaciones de código sin destino. Cuatro recursos upstream previamente versionados quedaban ignorados en su nueva ubicación; se incluyen explícitamente después de verificar identidad exacta con sus blobs originales, sin agregar indiscriminadamente cachés o medios generados. Se preservan los dos punteros originales de submódulos, sin fingir que estén inicializados.

Los124 archivos fuente/evidencia del otro worktree coinciden con el corte original ya respaldado o con la versión actual; no se detectó un avance posterior sin capturar. Su directorio y archivos privados se conservan intactos. El inventario de entrega no contiene nuevos archivos de ejecución privada ni coincidencias de las reglas de secretos de alta confianza examinadas; esto no constituye certificación de ausencia de vulnerabilidades. Los ZIP/respaldos privados y cachés no se publican.

Al comprobar la entrega se encontró y corrigió un error real en el empaquetador trasladado: `.read_bytes()` se aplicaba al literal de ruta y fallaban11 de12 pruebas. Ahora usa `Path(__file__).read_bytes()`; las12 pruebas de empaquetado, ejecución, aplicación, conflicto, rollback y reintento pasan. También pasan21 pruebas del runner,4 de organización y las comprobaciones de coherencia contable/comercial y de pendientes de billetera. El único cambio de fuente respecto al corte comercial de136 suites es este helper de entrega: se conservan sus1410 pruebas Python/3837 comprobaciones de navegador como evidencia histórica, sin afirmar que se reejecutaron para publicar ni sustituir su manifiesto. La corrección final tiene pruebas dirigidas y manifiesto propio.

Comercial sigue37/72=51,39% de crédito y1/24 aceptadas, sin porcentaje global de implementación certificado. Contabilidad conserva57/72=79,17% y9/24 aceptadas. Producción deshabilitada. DIAN, Bold y proveedores/cuentas auténticos, muestras/políticas legítimas, hardware, cualificación de release/Next.js e infraestructura siguen con sus pendientes existentes. La publicación del código no cierra esos requisitos.

Evidencia técnica consolidada: `ANALISIS/entregas/evidencias/consolidado-20261113/summary.json`, mapa de reubicaciones, contraste del otro worktree, manifiesto de fuentes y logs. La confirmación de publicación se obtiene comparando el SHA del único commit con `refs/heads/main` de GitHub después del push; no se declara realizada anticipadamente. El seguimiento y los informes históricos se conservan en sus carpetas; no se crea un nuevo análisis narrativo de entrega en la raíz.
