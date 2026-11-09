# Servicio de paquetes cifrados operado por el cliente

Este componente es independiente de la API, autenticación y base transaccional del ERP. No recibe contraseñas de cifrado, KEK o documentos descifrados. El token BYOS autoriza almacenamiento y es distinto de la contraseña del documento y del JWT del ERP.

## Preparación del destino

- Crear una base PostgreSQL dedicada del cliente, sin tablas del ledger del proveedor. La inicialización rechaza bases con `core_erp_journalentry`.
- Instalar `BACKEND/deployment/requirements-customer-store.txt` en un entorno independiente y conservar la misma fuente `core_erp` usada en las pruebas.
- Proteger el directorio de configuración y los archivos reales fuera de Git. Los JSON de configuración/grant deben ser archivos privados, sin permisos de grupo/otros; el servicio rechaza archivos públicos o symlinks.
- Configurar TLS válido entre navegador y API y conexión verificada a PostgreSQL según el entorno del cliente; el ejemplo usa `sslmode=verify-full`. La certificación/trust y los permisos reales requieren revisión del operador.

Esquema de configuración — los marcadores requieren datos legítimos del cliente:

```json
{
  "company_id": "UUID_EMPRESA_CONTABLE_VERIFICADA",
  "database": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "BASE_CLIENTE_DEDICADA",
    "USER": "ROL_MIGRACION_O_RUNTIME_SEGUN_ETAPA",
    "PASSWORD": "SECRETO_PRIVADO_DEL_CLIENTE",
    "HOST": "SERVIDOR_POSTGRES_CLIENTE",
    "PORT": "5432",
    "OPTIONS": {
      "sslmode": "verify-full",
      "sslrootcert": "/privado/ca-cliente.pem",
      "options": "-c statement_timeout=5000 -c lock_timeout=5000"
    }
  },
  "grant_file": "/privado/grant.json"
}
```

Usar el `company_id` del vínculo contable verificado, no asumir que coincide con el UUID de `TourismProvider`.

## Migración explícita y permisos

Con credenciales de migración propiedad del cliente:

```sh
PYTHONPATH=BACKEND/ANALEMATICA-BACKEND CUSTOMER_PACKAGE_CONFIG=/privado/config.json python -m core_erp.accounting.customer_package_api --initialize
```

La API no ejecuta esta migración al arrancar o al atender solicitudes. Una guarda ausente bloquea el acceso en lugar de repararse automáticamente.

Después, usar un rol de runtime separado con CONNECT a esa base, USAGE en el esquema y estos permisos de datos:

```sql
GRANT SELECT ON public.customer_fiscal_binding TO rol_runtime_cliente;
GRANT SELECT, INSERT ON public.customer_fiscal_packages TO rol_runtime_cliente;
```

El contrato PostgreSQL verifica ese rol mínimo, sin lectura de `customer_fiscal_envelopes`. No conceder UPDATE, DELETE, TRUNCATE, propiedad ni capacidad de alterar las guardas. La serialización utiliza un advisory lock transaccional por empresa; no necesita UPDATE sobre el vínculo.

## Autorización del cliente

Generar un token aleatorio independiente con `byos_` seguido de `secrets.token_urlsafe(32)`. Guardar el valor solo en los medios privados del cliente y entregar al usuario autorizado por el canal previsto. No usar un JWT del ERP, contraseña de documento o contraseña de base de datos.

El servidor conserva su SHA-256 en un grant privado:

```json
{
  "company_id": "UUID_EMPRESA_CONTABLE_VERIFICADA",
  "token_sha256": "SHA256_HEXADECIMAL_DEL_TOKEN_BYOS",
  "expires_at": "ISO8601_CON_ZONA_Y_VENCIMIENTO_NO_MAYOR_A_24_HORAS",
  "permissions": ["read", "append"],
  "allowed_origins": ["https://PANEL_AUTORIZADO"]
}
```

El grant se vuelve a leer en cada solicitud y antes de la operación SQL. Rotar/revocar su hash o permisos afecta a las solicitudes siguientes; no se afirma cancelación atómica de una transacción que ya esté en curso. Cambiar los orígenes CORS requiere reiniciar el servicio, además de actualizar el grant. El cliente web necesita `read` y `append` para consultar identidad antes de una carga.

## Arranque y rutas

Detrás del TLS y controles de red del cliente, con configuración privada y rol de runtime:

```sh
PYTHONPATH=BACKEND/ANALEMATICA-BACKEND CUSTOMER_PACKAGE_CONFIG=/privado/config.json uvicorn core_erp.accounting.customer_package_api:create_app --factory --host 127.0.0.1 --port 8210
```

| Ruta | Permiso | Resultado |
|---|---|---|
| GET `/v1/identity` | read | Empresa y capacidad estructural del destino |
| POST `/v1/packages` | append | Inserción/reintento de la misma versión opaca |
| GET `/v1/packages/{document_id}` | read | Última versión almacenada |
| GET `/v1/packages/{document_id}?revision=N` | read | Versión histórica exacta |

No hay endpoints de actualización/borrado, inicialización, credenciales de DB ni documentación pública. El token se envía exclusivamente en Authorization; el cliente omite cookies, referrer y redirecciones. Respuestas privadas/no-store, JSON acotado y CORS por origen exacto.

## Perfil público de frontend

El despliegue autorizado debe provisionar esta configuración pública antes de iniciar los paneles, mediante su mecanismo de configuración revisado:

```js
window.SGACDCustomerStorageProfiles = {
  "UUID_EMPRESA_CONTABLE_VERIFICADA": { origin: "https://API_BYOS_DEL_CLIENTE" }
};
```

Solo contiene empresa/origen HTTPS canónico, sin ruta final, token o contraseña. No hay entrada de URL libre, destino inferido ni fallback al proveedor. Sin un perfil, los dos paneles deshabilitan guardar/recuperar BYOS y muestran que falta configuración. El token temporal y la contraseña de descifrado se introducen por separado y se retiran de los campos al comenzar la operación.

La ruta cliente real se probó contra HTTPS loopback y PostgreSQL en un fixture aislado. Los paneles se probaron con destinos no provisionados para comprobar su bloqueo. El despliegue integrado con perfiles, identidades, TLS y permisos reales del cliente sigue pendiente; no se presenta la presencia de los controles como aceptación productiva.

## Consistencia y límites

Publicar primero la versión1 antes de publicar una rotación. Si falta una versión anterior, recuperar sus archivos legítimos y revisar el estado del cliente; no inventar metadatos ni saltar números de versión.

Una versión ya ocupada solo admite el mismo paquete; reintentos recuperan el resultado sin duplicación. Una versión nueva debe seguir a la cabecera y enlazar su digest. Dos escrituras competidoras no pueden adquirir la misma versión. Se verifican los bytes escritos antes de confirmar y se revierte la operación si un trigger inesperado los cambia.

El servidor comprueba forma, empresa, digest y secuencia. **No puede verificar HMAC/AES-GCM sin la contraseña del cliente**; su acuse mantiene `authenticated_ciphertext_verified=false` y no es aceptación fiscal o prueba de propiedad. El navegador autentica/descifra el paquete recuperado antes de mostrarlo.

El contrato admite hasta1.500.000 bytes por paquete y versiones1–1.000.000. No hay listado masivo ni poda de historial. SQL privilegiado, escritores que eludan el servicio, administración de grants, disponibilidad ante tokens comprometidos, retención y restauración física requieren cualificación. Los triggers y hashes no son WORM independiente.
