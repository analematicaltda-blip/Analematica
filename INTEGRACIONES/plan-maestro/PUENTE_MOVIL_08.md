# Puente nativo de documentos para Flet

Se implementa `pool-01-cryptography/flet_bridge` como paquete instalable propio:
control Python Flet 0.28.3, barrera de metadatos Dart y plugins Android/iOS. Selector,
lectura, cifrado y almacenamiento permanecen en el cliente nativo. El transporte
Flet no entrega documentos en claro, llaves, nombres ni rutas al servidor Python.
No se expone exportación, descifrado remoto ni autorización de dinero.

Operaciones: alta explícita con confirmación local, importación de PDF/JPEG/PNG,
listado de UUID y comprobación local de integridad. Se liga cada respuesta al ámbito
solicitado y se rechazan campos y códigos de error no previstos antes del transporte.
Se preserva la doble autorización financiera del backend.

Se agregan cancelación del contexto Keychain iOS, guardas de alta simultánea y
exclusión por archivo de la provisión Android entre procesos. No se borran ni se
regeneran llaves ante error. Los cambios del núcleo se incluyen como recursos reales
del wheel y se verifican byte a byte para evitar distribuir una copia obsoleta.

## Evidencia observada

- 10 pruebas correctas del control Python contra Flet 0.28.3 real, con transporte
  simulado: ámbito, concurrencia, respuestas incorrectas, ausencia de plugin,
  consentimiento y rechazo de bytes/rutas/métodos financieros.
- Wheel construido e instalado en entorno temporal; recursos nativos descubiertos.
- 232 aserciones criptográficas del núcleo correctas e interoperabilidad Java/Python.
  Android compila contra SDK35; esto no ejecuta el plugin Flutter ni el hardware.
- 15 pruebas de billetera correctas: no se cambia su política financiera.
- Plantilla oficial Flet fijada y verificada; copia separada preparada con AGP8.9.2,
  Gradle8.11.1, Java17 y mínimos de sistema, sin alterar el checkout o la app principal.

## Pendiente y bloqueo concreto

No hay Flutter ni Xcode en este host. El intento de obtener el embedding oficial
Flutter de `storage.googleapis.com` respondió HTTP403. No se sorteó ese bloqueo.
Se añade CI de tests Dart y compilación de hosts Android/iOS, pero aún no se han
observado sus resultados. Tampoco hay pruebas de teléfono físico ni identidad
biométrica/atestación remota certificada.

La app principal sigue siendo académica y no proporciona todavía la vinculación
autenticada de UUID financieros. No se transforman IDs enteros académicos en
identidades de monedero ni se cifra su base por suposición. El ejemplo queda
inactivo si falta un ámbito real; no se reemplazaron los cargadores existentes.

Una selección original de galería/proveedor puede estar ya en claro fuera de esta
app. No se borra ni se protege retroactivamente. La cancelación puede llegar después
de una escritura cifrada: revisar listado antes de repetir. La protección local no
es un permiso para mover fondos ni completa por sí sola los pools 02/03/04.

Uso, comandos y límites: `pool-01-cryptography/flet_bridge/README.md`.
