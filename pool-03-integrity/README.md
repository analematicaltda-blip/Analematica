# Pool 03 · Integridad del cliente

Estado: pendiente de implementación y builds firmadas verificables.

Aplicar firma de distribución de Android/iOS y verificar identidad del paquete,
actualizaciones y dependencia de una raíz de confianza del sistema. Un hash maestro
embebido puede ser cambiado junto al código y no demuestra integridad por sí solo.
Las señales locales de root, jailbreak y depuración son señales de riesgo eludibles;
no bastan para conceder confianza ni justifican destruir llaves permanentes.

Política prevista: bloquear operaciones sensibles, limpiar secretos efímeros de RAM,
registrar un diagnóstico sin datos personales y ofrecer revisión/recuperación.
Probar falsos positivos, accesibilidad, dispositivos de desarrollo y actualización.
No se implementan aquí técnicas evasivas ni se promete impedir ingeniería inversa.
