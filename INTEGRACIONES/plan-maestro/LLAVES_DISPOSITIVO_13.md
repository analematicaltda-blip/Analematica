# Llaves financieras de dispositivo: implementación de la propuesta aprobada

Código implementado y probado localmente; no activación de producción.

Se añade verificación criptográfica Android Key Attestation contra raíces explícitas del servidor, políticas de hardware/biometría por operación, arranque verificado, aplicación/firmantes, parches y revocaciones. La lectura de la revocación es vigente en cada uso; datos ausentes/vencidos o una política distinta bloquean operaciones. No hay raíces de prueba por defecto ni confianza aprendida del cliente.

Se exige una autorización de alta independiente de la sesión y contraseña: token de servidor de propósito exclusivo, ligado a cuenta, audiencia, credencial, nonce, llave y reemplazo, máximo5min. Su emisión requiere un adaptador de identidad verificado que no está configurado por defecto; no hay endpoint para autoaprobarse. La transición atómica del alta impide replay de ese permiso tras activación. No se afirma haber implementado una verificación WebAuthn/KYC real sin su integración.

Una recuperación aprobada activa la nueva credencial y revoca la anterior/invalida sus retos de forma atómica. Un fallo conserva la credencial anterior. No elimina privadas ni documentos y no permite ejecutar con otro dispositivo una intención ya revisada. Las dos autorizaciones del mismo solicitante permanecen.

Se conservan P-256 y el bloqueo biométrico/invalidez por cambio de biometría nativos de Android/iOS ya existentes; no se duplican llaves ni se usa RSA como alternativa de Secure Enclave. El servidor de este corte acepta únicamente la evidencia Android soportada. Confianza remota iOS, identidad independiente real, renovación y hardware quedan pendientes; no se sustituyen con booleanos.

## Evidencia

- 28 pruebas nuevas de certificados/DER/política, autorización, HTTP, revocación viva y recuperación, con CA RSA/EC, intermediarios y llaves/evidencia de identidad sintéticas. La criptografía es real; los emisores no son fabricantes ni los usuarios son KYC verificados.
- 138 ejecuciones Python correctas en total: 28 nuevas, 13 del protocolo, 15 de billetera, 18 del dominio, 12 de proveedores, cuatro CRM, 14 de arranque, 16 de readiness y18 en bases migradas.
- Dos respaldos privados previos con restauración verificada. Migración0004 aplicada exclusivamente a las dos bases locales nuevas:166 migraciones y587 tablas en cada una. No se cambia el grafo histórico ni datos productivos.
- Código/CI y documentación de configuración incorporados; pruebas físicas, raíces oficiales e ingesta autenticada del feed no se observaron ni configuraron en esta sesión.

Configuración, flujo, límites y requisitos: `../../pool-02-biometrics/DEVICE_BOUND_FINTECH.md`.
