# Puente Flet → almacén nativo

Se implementa una extensión propia para Flet **0.28.3**: control Python, adaptación
Dart y plugins Android/iOS. No está activa en la aplicación principal ni representa
una nueva autorización financiera. El cliente debe ser una app móvil empaquetada
con la extensión; navegador, desktop o plugin ausente fallan sin alternativa software.

## Frontera de privacidad

Python/Flet puede ejecutarse en otro servidor. Por eso esta interfaz **no acepta
bytes, base64, rutas, URLs ni contraseñas** de documentos. El selector del sistema se
abre en el cliente nativo, que lee el archivo de origen, cifra en memoria y guarda
solo un sobre en almacenamiento privado. No hace una copia temporal plana propia.
El origen del proveedor/galería puede existir en claro: no se elimina ni se cifra
retroactivamente. No se usa un servicio de nube para cifrar o verificar.

Solo cruzan el transporte Flet tenant/cuenta/versión, UUID de solicitud/documento y
estados. Dart valida también valores y formas **antes** de devolverlos a Python.
No se devuelve el texto descifrado ni una ruta del proveedor, nombre real, llave,
firma o blob de documento. El método `verify_document` descifra con la protección
del sistema, descarta los bytes y comunica únicamente el resultado de integridad.
Los errores públicos son códigos cerrados, sin mensajes internos ni contenido.

- `provision(confirm_new_key=True)`: alta explícita más confirmación local en el
  teléfono. Una llave existente nunca se reemplaza ni borra.
- `import_document()`: selector nativo PDF/JPEG/PNG, máximo 8 MiB, UUID nuevo;
  el cifrado y almacenamiento se hacen dentro del cliente.
- `list_documents()`: devuelve hasta 64 UUID locales y `has_more`; no certifica
  integridad de esos archivos ni publica datos a otros dispositivos.
- `verify_document(uuid)`: biometría/operación privada del SO y verificación GCM.
  No muestra, exporta ni envía el contenido a Python.

Una sola operación por instancia nativa evita mezclar resultados; las solicitudes
se identifican y el desmontaje solicita cancelación. Una cancelación o timeout
**no demuestra ausencia de efectos** si la escritura cifrada ya concluyó: actualizar
el listado antes de repetir. No hay transacciones bancarias en esta interfaz.
La cancelación invalida el contexto de autenticación Keychain de esa instancia
en iOS y la señal biométrica en Android; también puede cancelarla el usuario en
la UI del sistema. No destruye llaves. Para reintentar se crea una instancia nueva
del control con el mismo ámbito/versión, no una llave nueva.

## Código canónico y distribución

`src/flutter/sgacd_vault` se distribuye en el wheel mediante el namespace `flutter`,
según el contrato de extensiones Flet. Incluye el núcleo propio de Pool 01 como
recursos de compilación; no depende de rutas externas al paquete ni de un enlace.
Los 19 recursos del núcleo y guards de integridad/protección se verifican byte a byte:

```sh
python FRONTEND/WALLET-FRONTEND/native_bridge/sync_native.py
# Solo tras modificar de forma intencional el núcleo canónico:
python FRONTEND/WALLET-FRONTEND/native_bridge/sync_native.py --sync
```

Se consultó el contrato público de flet-audio 0.1.0 (Apache-2.0, commit
`a146bf580a211c6d1f5c45070d15532ea2e92af7`); no se incorpora esa biblioteca ni su
lógica de audio. Flet es una dependencia, no una API remota de criptografía.

## Pruebas realizadas

10 pruebas Python con Flet 0.28.3 instalado verifican el contrato real de
`Control.invoke_method_async`, consentimiento explícito de alta, ámbitos UUID,
operación concurrente, errores y rechazo de contenido/rutas y campos inesperados.
Se construyó e instaló un wheel y se comprobó que distribuye los plugins y el núcleo
sin llaves, documentos, bases ni cachés Python. Los dobles de transporte de esos
tests no son un dispositivo ni acreditan llamadas al hardware.

Continúan correctas las 232 aserciones criptográficas del núcleo y las 15 pruebas
de la billetera. Se añaden tests Dart de la barrera de metadatos y CI de compilación
Flutter para APK y simulador iOS. **No se observaron aún resultados de esa CI.**
Este host no tiene Flutter/Xcode; la descarga del embedding oficial Flutter desde
`storage.googleapis.com` respondió HTTP 403. No se usaron mirrors para eludirlo ni
stubs para afirmar una compilación nativa que no se ejecutó.

## Preparación reproducible

Usar un entorno Python separado; no actualizar la app principal a ciegas:

```sh
python -m pip install 'flet[cli]==0.28.3' build ./FRONTEND/WALLET-FRONTEND/native_bridge
python -m unittest discover -s FRONTEND/WALLET-FRONTEND/native_bridge/tests -v
python -m build --wheel FRONTEND/WALLET-FRONTEND/native_bridge
```

El proyecto `example` declara `tool.flet.dev_packages`: Flet descubre el paquete
local sin publicarlo en PyPI. Sus IDs deben provenir del dominio autenticado real,
no de UUID generados para aparentar una identidad financiera. El ejemplo permanece
inactivo si esos IDs no están configurados. No contiene llaves ni credenciales.

La plantilla oficial Flet 0.28.3 usa AGP/Gradle antiguos. Para preparar una copia
separada compatible, conservando licencia y original:

```sh
git clone --branch 0.28.3 --depth 1 https://github.com/flet-dev/flet-build-template.git /tmp/flet-official
python FRONTEND/WALLET-FRONTEND/native_bridge/prepare_flet_template.py --source /tmp/flet-official --destination /tmp/flet-vault-template
flet build apk FRONTEND/WALLET-FRONTEND/native_bridge/example --template /tmp/flet-vault-template
```

El preparador exige checkout limpio y SHA oficial fijado. Ajusta AGP 8.9.2,
Gradle 8.11.1, Java 17 e iOS 15 en la copia. El ejemplo declara Android mínimo31,
SDK objetivo35 y la descripción Face ID. Los directorios de salida deben ser
nuevos: no se sobrescribe un checkout ni se eliminan datos de otro proyecto.
`make_flutter_host.py` genera además un host aislado para comprobar el plugin en CI;
no es el build de la aplicación principal ni ejecuta la provisión de llaves.

## Antes de activar la aplicación

Falta observar compilaciones Flutter/iOS, verificar el puente en teléfonos físicos
y enlazar el ámbito con identidades autenticadas del sistema. La app principal
`MOVILES/SGA-CD-APK.git` usa actualmente usuarios académicos y no entrega ese
contrato financiero; no se equiparan sus IDs enteros a UUID de cuentas/organizaciones.
No se reemplazaron sus cargadores de currículos ni su base local por este ejemplo.

Probar selección/cancelación, segundo plano, desconexión, hardware ausente, límites
de archivo, biometría rechazada, cambio de huella y recuperación. No activar con
documentos irremplazables sin un procedimiento de recuperación aprobado. La
billetera conserva sus dos solicitudes de autorización; `stored` o `verified` no
son prueba de identidad, atestación remota ni permiso para transferir fondos.

## Integridad obligatoria (versión 0.2.0)

El host debe configurar los recursos nativos descritos en
`../../../MOVILES/WALLET-MOVIL/native/pool-03-integrity/release/README.md`. El puente no acepta esa configuración
por Python o por el canal de métodos. Si falta, las operaciones devuelven
`CLIENT_INTEGRITY_BLOCKED`. Compilar el ejemplo debug no autoriza acceso a documentos.
Se distribuyen también los guards canónicos del Pool03 dentro del wheel y se
comprueba su igualdad mediante `sync_native.py`. La aplicación principal sigue sin
activar el puente hasta contar con sesión financiera autenticada y validación física.

## Protección de pantalla (0.3.0)

El puente aplica las protecciones nativas del Pool04 antes de operaciones sensibles.
Android exige Activity y hilo principal y mantiene FLAG_SECURE; iOS oculta por
inactividad/captura detectada y requiere ventana activa. No se afirma bloqueo total
de capturas iOS ni validación física. Los clientes HTTPS incluidos no crean nuevas
conexiones del puente ni sustituyen automáticamente la red de Flet. Ver
`../../../MOVILES/WALLET-MOVIL/native/pool-04-anti-phishing/README.md` para configuración y límites.
