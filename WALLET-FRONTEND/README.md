# WALLET-FRONTEND

`src/sgacd_wallet_ui` contiene la interfaz Flet compartida por móvil y escritorio. `native_bridge` contiene el control Python/Dart y plugins que antes estaban en pool01/flet_bridge. `web` es un panel público de consulta sin frameworks, CDN, login ni acceso al espacio cifrado. No se presentan las páginas React antiguas como una implementación nueva ni se cambian sus rutas.

## Panel web local, sin recursos externos

```sh
python WALLET-FRONTEND/preview.py --port 8556
```

Abrir `http://127.0.0.1:8556`. Solo sirve seis recursos públicos fijados; no expone carpetas, documentos, vaults ni APIs financieras. Tiene equipo, búsqueda y registro de pendientes. Probado en Chromium con cero solicitudes externas y viewport móvil.

Los JSON públicos se generan desde el catálogo/registro canónicos:

```sh
python WALLET-FRONTEND/tools/sync_public_assets.py
python WALLET-BACKEND/tools/update_pending_doc.py
```

CI comprueba que no queden desactualizados. No contienen datos del usuario.

## Interfaz Flet compartida

Preparar un entorno propio con Python3.12 y las dependencias antes de trabajar desconectado:

```sh
python -m pip install -e WALLET-BACKEND/offline -e WALLET-FRONTEND -e WALLET-FRONTEND/native_bridge
python -m unittest discover -s WALLET-FRONTEND/tests -v
```

Las aplicaciones usan espacio cifrado local, apuntes, preparación/edición de borradores, dos revisiones locales, informe de los ocho soldados y pendientes. Se bloquea al perder actividad y tras5min sin acciones; formularios se limpian. Guardar antes de salir. Sin cuenta y sesión verificadas no muestra un saldo inventado ni habilita envío de dinero.

En móvil se monta `SensitiveDisplay` y se exige su respuesta antes de mostrar contraseña/datos. Esa respuesta solo protege pantalla: **no acredita identidad, atestación ni biometría financiera**. El navegador no puede desbloquear un vault aunque solicite modo native. En desktop se usa el caché con contraseña; llaves financieras desktop, ACL, capturas y binarios siguen pendientes.

## Vista Flet web opcional

`main.py` es una vista Flet de consulta sin acceso al espacio privado. Requiere el extra web con versiones fijadas por compatibilidad. Se detectó y corrigió un conflicto FastAPI reciente, pero el cliente Flet0.28.3 descargado requiere CanvasKit/fuentes externas que no están empaquetados aquí; la prueba con red externa bloqueada no pudo renderizarlo. **No se considera una UI Flet web offline validada.** Usar el panel web estático o compilar/proveer legalmente los assets oficiales compatibles antes de habilitar esa vista. No se usaron mirrors para eludir la política de red.

APK/IPA/EXE y la validación física no están entregados como binarios. Ver [pendientes](../PENDIENTES-PRODUCCION-BILLETERA.md).
