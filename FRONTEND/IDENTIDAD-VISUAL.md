# Identidad común SGA-CD

Instrucción vigente del usuario: azul metalizado, azul claro y texto blanco en
todos los sistemas. Se toman como referencia la paleta metálica de
ANALEMATICA-FRONTEND/css/admin.css y los acentos de SGA-CD-WEB.git/css/sky-theme.css.
La indicación actual de texto blanco prevalece sobre los textos celestes de
algunos estilos históricos. No se cambió la estructura de SGA-CD.

| Uso | Color |
|---|---|
| Fondo | #060B17 |
| Azul metálico profundo | #0A1128 |
| Superficie | #0E1B38 |
| Panel elevado | #142850 |
| Acento metálico | #1A3262 / #2563EB |
| Borde / foco celeste | #60A5FA / #7DD3FC |
| Detalle azul claro | #38BDF8 |
| Texto | #FFFFFF |

Usar azul claro para bordes, foco y detalles; mantener fondos de botones lo
suficientemente oscuros para que el texto blanco sea legible. Los avisos conservan
su significado mediante etiquetas y bordes semánticos, con texto blanco.

Correcciones de este corte: cotizaciones React, billetera web estática, tema
compartido Flet móvil/escritorio y variables globales del frontend compartido
Turismo/ERP. Se preservan componentes y reglas de distribución. Esto no acredita
una revisión visual de todas las pantallas heredadas o de releases nativas.

Pruebas: cotizaciones en Chromium con colores computados, vista móvil y flujo
funcional; billetera web con búsqueda y privacidad; diez regresiones Flet Python.
La integración de sesión ERP continúa en desarrollo, deshabilitada por defecto.
