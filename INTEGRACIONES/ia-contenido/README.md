# Taller editorial privado

Primer flujo del frente 7: texto/guion → borrador cifrado → revisión de exactitud, derechos y privacidad → exportación JSON. No hay publicador, consumo de servicios pagados ni acceso a cuentas. Escribir un texto manual permite operar el taller sin modelo; no se etiqueta como generación IA.

## Configuración local

En el backend central, preparar expresamente la nueva tabla aditiva usando el procedimiento existente:

```bash
python -m app.services.assistance.schema
```

Conservar las claves de control fuera de Git. El taller reutiliza la clave Fernet de `ASSISTANCE_CONTROL_KEY_DIR`; sin ella los borradores cifrados no se recuperan. La fuente y métricas del modelo se guardan como metadatos, mientras el brief y texto quedan cifrados. La tabla no almacena claves de proveedores. No se ha ejecutado esta instalación sobre una base del usuario.

Activación optativa, deshabilitada por defecto:

```dotenv
ASSISTANCE_CONTENT_ENABLED=1
ASSISTANCE_CONTENT_OLLAMA_ENABLED=1
ASSISTANCE_CONTENT_OLLAMA_URL=http://127.0.0.1:11434
ASSISTANCE_CONTENT_OLLAMA_MODELS=llama3.2:3b
```

El modelo es un ejemplo de configuración, no una recomendación medida ni una descarga automática. Ollama y el modelo deben estar instalados por el operador, en el mismo espacio de red del backend. Un servidor en otro contenedor no es loopback; este adaptador rechaza hosts externos y no admite habilitarlos desde el navegador. No exportar claves de APIs externas para usarlo. La inferencia local consume CPU/RAM/electricidad aunque el coste de API externa sea cero.

Se limita la salida a 768 tokens solicitados, 131072 bytes de respuesta y 12000 caracteres útiles; tiempo total máximo 65 segundos y tres solicitudes por minuto según el limitador existente. Ese limitador no sustituye límites compartidos entre procesos ni una cola de capacidad. No se descargan modelos ni se reintenta con otro proveedor.

El administrador abre `/content.html` desde Analemática/SGA-CD con su sesión central vigente. El ERP y Turismo siguen con sesiones independientes; este enlace no crea SSO ni hereda permisos empresariales. No se amplió el acceso a la billetera.

## Contratos API

Prefijo `/api/v1/assistance/content`, autenticación administrativa activa del solicitante y organización:

- `POST /drafts`: `platform`, `brief`, `text`; crea versión 1 manual.
- `POST /generate`: `platform`, `brief`, `model`, `share_with_local_model=true`; crea borrador solo tras respuesta válida de Ollama. El consentimiento se solicita por operación.
- `GET /drafts`: últimos 50 del usuario en su organización.
- `GET /drafts/{id}`: contenido propio.
- `PUT /drafts/{id}`: campos de creación más `revision`; cambia texto y revoca la revisión anterior.
- `POST /drafts/{id}/review`: `revision`, `digest`, `accuracy_rights_privacy_checked=true`; vincula revisión al texto guardado.
- `GET /drafts/{id}/export`: únicamente versiones revisadas; `publication_enabled=false`.

No existe `/publish`. Una revisión editorial no sustituye las dos autorizaciones de control ni la tercera de impacto. No se conecta automáticamente texto generado con ejecutores de escritorio o móvil. Las sugerencias del modelo son texto sin herramientas.

## Comparación de proveedores y modalidades

| Alternativa | Integración de este corte | Evidencia real | Pendiente |
| --- | --- | --- | --- |
| Texto manual | Flujo completo implementado | API y navegador con datos de prueba | Recorrido con sesión real del usuario |
| Ollama, texto local | Adaptador implementado | Contratos HTTP simulados y fallos | Modelo instalado, calidad española, rendimiento/RAM y licencia |
| APIs externas de texto | No habilitadas | Ninguna llamada ni tarifa verificada | Consentimiento de datos, contrato, credenciales, calidad y coste vigente |
| Imagen/vídeo/voz/transcripción | No implementadas en este adaptador | Catálogo de referencia existente, no servicio probado | Evaluar cada proveedor/modelo antes de integración |

Los límites gratuitos de `free-ai-apis` son referencias que requieren comprobación actual; no se garantiza gratuidad ni se incorporan tokens publicados en conversaciones.

Para comparar modelos locales habilitados sobre el mismo brief público sintético:

```bash
PYTHONPATH=BACKEND/SGA-CD-BACKEND python BACKEND/INTEGRACIONES/ia-contenido/benchmark_local.py --model llama3.2:3b --authorize-local-inference --output /tmp/comparacion-ollama.json
```

Repetir `--model` compara modelos secuencialmente. Registra latencia, longitud y hash, no texto ni credenciales. Sale con error si alguno no genera. La calidad queda sin puntuar: un humano debe evaluar exactitud, español, claridad, derechos y uso de datos antes de recomendar un modelo. No ejecutar con datos reales de clientes como benchmark.

## Pendientes de producción

Validar Ollama real, autenticación y permisos integrados de los tres sistemas, respaldo/restauración de borradores y claves, retención/eliminación de datos, protección de sesión central (el panel sigue el mecanismo de token existente), límites compartidos y carga. El filtro de credenciales conocidas es auxiliar: no garantiza eliminar todos los datos sensibles. Las pruebas SQLite y de navegador simulado no certifican concurrencia PostgreSQL del taller ni uso productivo.
