# Pendientes de producción de la billetera

Producción: **NO HABILITADA**. Registro vivo; una prueba sintética no cierra validaciones físicas o de proveedores.

Actualizar el JSON canónico en `WALLET-BACKEND/offline/src/sgacd_wallet_offline/production_pending.json` y ejecutar `python WALLET-BACKEND/tools/update_pending_doc.py` en cada entrega. Cerrar solo con evidencia verificable, responsable y criterio de aceptación satisfecho.

Sin internet se permiten apuntes y borradores cifrados. No hay liquidación entre cuentas, retiros o depósitos fuera del servidor. Las dos revisiones locales no son firmas financieras ni permisos de control.

## WAL-001 · Raíces y políticas reales de atestación

Estado: **PENDIENTE** · Área: Android · Responsable: Seguridad

Aprobar raíces oficiales, paquete, firmantes y parches; verificar cadena y rechazos en dispositivos reales.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-002 · Ingesta autenticada y disponible del feed

Estado: **PENDIENTE** · Área: Revocación · Responsable: Seguridad

Probar actualización atómica, frescura, revocación y caída del feed sin aceptar datos inventados.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-003 · Alta y recuperación independientes reales

Estado: **PENDIENTE** · Área: Identidad · Responsable: Identidad

Conectar y auditar passkey con UV o recuperación verificada; bloquear contraseña/PIN como único factor.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-004 · Confianza remota de la llave financiera

Estado: **PENDIENTE** · Área: iOS · Responsable: Móvil

Definir y verificar evidencia Apple enlazada a llave/política, sin reemplazarla por un booleano.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-005 · Biometría y cambios de enrolamiento

Estado: **PENDIENTE** · Área: Dispositivos · Responsable: QA móvil

Validar firma por operación, cancelación, pérdida del equipo y cambios biométricos en Android/iPhone reales.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-006 · Dominios y pines de producción

Estado: **PENDIENTE** · Área: TLS · Responsable: Infraestructura

Configurar pines aprobados activo/respaldo, rotación, caducidad y pruebas MitM autorizadas.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-007 · Capturas, overlays, accesibilidad y multitarea

Estado: **PENDIENTE** · Área: Pantallas · Responsable: QA móvil

Probar FLAG_SECURE y protección iOS por escena; documentar límites de capturas individuales y falsos positivos.

Evidencia: Control SensitiveDisplay agregado al puente0.4.0; contrato Python probado. No validación física de pantallas.

## WAL-008 · Compilaciones e instalación firmadas

Estado: **PENDIENTE** · Área: Apps Flet · Responsable: Clientes

Construir APK/AAB/iOS y Windows/macOS/Linux; instalar, probar arranque sin internet y conservar licencias.

Evidencia: Fuentes Flet y paquetes Python creados. Binarios nativos no observados; Flet web depende de CanvasKit/fuentes externas no empaquetados. Panel estático probado offline.

## WAL-009 · Llaves y autenticación nativa financiera desktop

Estado: **PENDIENTE** · Área: Escritorio · Responsable: Seguridad desktop

Implementar y validar almacenamiento/autenticación por SO; caché con contraseña no equivale a llave bancaria.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-010 · Vinculación verificada con cuenta y jurisdicción

Estado: **PENDIENTE** · Área: Sesión · Responsable: Identidad

Conectar sesión financiera real, ámbito y cliente HTTPS nativo; no usar UUID del espacio local como identidad bancaria.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-011 · Revisión y reintentos en el servidor

Estado: **PENDIENTE** · Área: Sincronización · Responsable: Backend

Enviar solo preparación con idempotencia, pedir dos firmas frescas, conciliar recibos y no reenviar aprobaciones locales.

Evidencia: Corte35: pruebas HTTP sobre instalaciones SQLite nuevas de ERP y Turismo repiten dos autorizaciones, rechazo de replay y firmas con llaves de fixture. No acredita sincronización offline, identidad física ni conciliación productiva. Ver INTEGRACIONES/plan-maestro/BLOQUE08_OPERACION_35.md.

## WAL-012 · Renovación, copias y recuperación probadas

Estado: **PENDIENTE** · Área: Continuidad · Responsable: Operaciones

Definir renovación de confianza, recuperar backups cifrados y medir pérdida de documentos sin exportar privadas.

Evidencia: Corte36: CLI de copia SQLite AES-256-GCM y restauración del modelo ContentDraft con clave de backup independiente y claves originales verificadas en fixture. No acredita recuperación integral de documentos/finanzas de billetera, claves hardware, almacenamiento externo ni RPO/RTO productivo. Ver INTEGRACIONES/plan-maestro/BLOQUE09_RESPALDOS_36.md.

## WAL-013 · PostgreSQL y migración histórica

Estado: **PENDIENTE** · Área: Datos · Responsable: Backend

Probar concurrencia, reversión y restauración PostgreSQL; resolver el grafo histórico sin alterar saldos existentes.

Evidencia: Corte35: instalación y contratos acotados en esquemas fresh-local SQLite verificados; migración histórica y concurrencia/restauración PostgreSQL de la billetera siguen pendientes. El ensayo PostgreSQL MFA/control no sustituye estas pruebas financieras.

## WAL-014 · Open Duet y agent-desktop en equipos reales

Estado: **PENDIENTE** · Área: Motores · Responsable: Automatización

Configurar proveedor local offline, registrar perfiles limitados y probar runtimes/accesibilidad con autorizaciones; no suponer conexión por copiar código.

Evidencia: Ocho trabajadores de reglas y perfiles limitados preparados; cuatro pruebas del conector. Sin proveedor local registrado ni equipo físico vinculado.

## WAL-015 · Automatización wallet y permisos offline

Estado: **PENDIENTE** · Área: Control · Responsable: Automatización

Integrar wallet en la política de control con verificación de permisos firmados y dos autorizaciones mínimas; nunca autoaprobar ni ejecutar pagos desde el ejército.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-016 · R8, firma y actualización segura

Estado: **PENDIENTE** · Área: Release · Responsable: Distribución

Verificar releases reales, mapas privados, actualizaciones, revocación y rollback; no declarar R8 activo por incluir fuentes.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-017 · Pasarelas y conciliación reales

Estado: **PENDIENTE** · Área: Finanzas · Responsable: Finanzas

Validar proveedores/contratos, recibos, límites y conciliación; no presentar transferencias internas de pruebas como retiros o depósitos reales.

Evidencia: No acreditado en producción; consultar cortes de pruebas del repositorio.

## WAL-018 · Revisión externa, aislamiento y sesión local

Estado: **PENDIENTE** · Área: UX y seguridad · Responsable: QA

Auditar cifrado/caché, bloqueo por inactividad, campos secretos, navegador sin acceso al vault, accesibilidad y falsa confirmación en equipos reales.

Evidencia: 15 pruebas offline y diez de interfaz Python correctas; panel web probado en Chromium sin red externa. ACL Windows y UX/capturas nativas no acreditadas.

## WAL-019 · Alta pública y panel exclusivo del administrador empresarial

Estado: **PENDIENTE** · Área: Identidad y empresas · Responsable: Identidad e integración ERP/SGA-CD

Conectar registro público e identidad real; adaptar autoridad empresarial ERP/SGA-CD con verificación de administrador titular; integrar panel web/escritorio y probar revocación. El equipo administrativo solo accede a su perfil personal si se inscribe.

Evidencia: Vínculo explícito prestador/empresa, revisión independiente y adaptador ERP-TUR opt-in implementados con pruebas ORM/HTTP. No habilitado por defecto. Identidad externa, recuperación/renovación, SSO SGA-CD y paneles web/escritorio productivos pendientes.

