# WALLET-MOVIL · Flet

Aplicación Flet en `src/main.py`; los cuatro pools nativos completos están en `native/`. Comparten las mismas bibliotecas, límites y llaves separadas existentes; las rutas relativas entre pools se mantienen. El puente de compilación compartido se mantiene en `WALLET-FRONTEND/native_bridge` y comprueba19 recursos canónicos byte a byte.

Preparar dependencias y runtimes antes de desconectar. Desde un entorno del repositorio:

```sh
python -m pip install -e WALLET-BACKEND/offline -e WALLET-FRONTEND -e WALLET-FRONTEND/native_bridge
flet run WALLET-MOVIL/src/main.py
```

El código solo habilita almacenamiento móvil si existe `FLET_APP_STORAGE_DATA` proporcionado por el runtime empaquetado y el control nativo de protección de pantalla responde. No inventa tenant/cuenta a partir del espacio local. En un cliente Flet genérico sin el plugin compilado se mantiene bloqueado; no se reduce la seguridad para aparentar funcionamiento.

Compilar desde esta carpeta con Flet0.28.3, Flutter/Xcode/SDK correspondientes y los dev_packages de pyproject. Android requiere SDK35/min31; iOS15+ y compilador Swift5.9+. Verificar wheels cryptography/Python para cada ABI. No se observaron compilaciones/instalaciones Android/iOS reales en esta entrega: no hay APK/IPA certificado ni enlaces de descarga ficticios.

Sin internet: apuntes y borradores cifrados, revisiones locales y reglas del equipo. Sin liquidación, retiros, depósitos o sincronización automática. Dos revisiones locales nunca sustituyen las firmas frescas y la cuenta verificada en el servidor.

Pruebas de bibliotecas:

```sh
python WALLET-MOVIL/native/pool-01-cryptography/tests/verify.py --android-jar "$ANDROID_HOME/platforms/android-35/android.jar"
python WALLET-MOVIL/native/pool-02-biometrics/tests/verify.py --android-jar "$ANDROID_HOME/platforms/android-35/android.jar"
python WALLET-FRONTEND/native_bridge/sync_native.py
```

Registro único: [pendientes de producción](../ANALISIS/produccion/PENDIENTES-PRODUCCION-BILLETERA.md).
