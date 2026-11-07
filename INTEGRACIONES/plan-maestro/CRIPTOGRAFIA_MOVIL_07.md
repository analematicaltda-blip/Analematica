# Pool 01 de criptografía móvil

Se implementan bibliotecas propias en `pool-01-cryptography`, con Java AndroidKeyStore,
BiometricPrompt, Swift CryptoKit, Keychain y Secure Enclave. El cifrado es local y no
requiere APIs de nube. No se agregó blockchain, que no reemplaza esta protección.

La biblioteca Android se compiló con el android.jar oficial API35. Se ejecutaron
232 aserciones criptográficas Java y una comparación independiente en Python de
AES-256-GCM y PBKDF2-HMAC-SHA256. Pasan también las 15 pruebas de regresión de
billetera: esta incorporación no relaja ni reemplaza sus autorizaciones.

No hay teléfonos/Xcode en este host Linux. El código Swift y su CI se agregan,
pero no se certifica su compilación ni el hardware hasta observar esos resultados.
Los tests de AES usan vectores públicos y no sustituyen la prueba de Keystore,
StrongBox, Secure Enclave, cancelación o invalidación biométrica.

La aplicación móvil principal es Flet/Python; todavía no tiene un puente nativo
ni un recorrido financiero/documental conectado a estas bibliotecas. No se cambió
su importador ni se atribuye cifrado a archivos existentes. Se conserva el cierre
por defecto de operaciones financieras y no se migran saldos, documentos ni llaves.
Los pools 02/03/04 tienen contratos y criterios pendientes, no implementaciones
ficticias. Las detecciones heurísticas no borrarán llaves de usuarios.

Detalle técnico, límites, uso e integración: `pool-01-cryptography/README.md`.
Antes de activar: integrar puente Flet/Flutter con bytes en memoria, compilar hosts
firmados, verificar dispositivos físicos y definir recuperación. El plan maestro
sigue en ejecución; este corte no declara producción protegida ni custodia bancaria.
