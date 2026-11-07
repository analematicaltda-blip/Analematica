# Pool04: protección de red y pantallas

Código incorporado a la rama de integración. No desplegado/instalado en dispositivos ni habilitado para producción.

Se conectan protecciones de pantalla Android y privacidad de escenas/captura iOS al núcleo documental, puente y autorizaciones. Se entregan clientes HTTPS con confianza del sistema, hostname y pin SPKI dentro del handshake, origen exacto, dos pines mínimos, caducidad, límites y rechazo de redirecciones. No sustituyen todas las conexiones existentes: la integración de sesión financiera final sigue pendiente. No se colocan pines de prueba en la configuración de producción.

Comprobado: 26 aserciones nuevas Java; cinco escenarios TLS locales reales; regresión de 232 aserciones criptográficas, nueve de mensajes, 11 pruebas de Flet y 13 del servidor. Android compilado contra API35; wheel0.3.0 construido con 19 recursos canónicos (siete nuevas fuentes de protección).

Pendiente: configurar dominios/pines reales, conectar la sesión nativa, compilar Apple/Flutter y validar dispositivos y releases/R8. iOS no puede impedir todas las capturas mediante APIs públicas. No se activan pagos ni se modifican bases de datos.

Los paquetes Swift se ubican bajo ios/SGAIntegrity e ios/SGAProtection con identidades distintas; dependencias y CI actualizados. Las comprobaciones Apple no se declaran ejecutadas.

Configuración y comandos: `../../pool-04-anti-phishing/README.md`.
