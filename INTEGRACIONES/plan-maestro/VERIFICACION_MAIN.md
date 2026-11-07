# Verificación previa y nivelación del repositorio remoto

Se consultó GitHub y se descargó main para comparar contenido, sin fusionar,
publicar ni crear commits.

- Main remoto: `56037ee337374527b88b4f2d2267202766b02067`.
- Su árbol de archivos coincide exactamente con `f1be1adc5` local.
- El trabajo anterior hasta ese corte está integrado; las fusiones posteriores
  de ese main no introducen diferencias de contenido frente a dicha base.
- Dos entregas locales siguen fuera de main: `85eef0c75` y `1f2f4af80`.
- Diferencia acumulada: 202 rutas detectadas por Git, incluyendo movimientos;
  no significa 202 archivos perdidos.

## Ya integrado

Organización previa del repositorio, motores de asistencia y control, fuentes
AiSOC/catálogo IA, primeras auditorías y correcciones turísticas/ERP, bases
locales nuevas, transferencias internas de prueba, cuatro pools y atestación
Android con los límites documentados en cada entrega.

## Conservado localmente, todavía no integrado

1. Organización WALLET-BACKEND/FRONTEND/MOVIL/DESKTOP, clientes Flet, caché
   cifrada offline, ocho reglas locales, perfiles de agentes limitados,
   registro de 19 pendientes y política de acceso personal/administrador empresarial.
2. Informe AVANCE_15, comprobación local del plan, bloqueo explícito de
   operaciones comerciales no verificadas, pruebas CRM y ajuste de CI.

No se detecta pérdida de contenido versionado entre esta base y main. Esta
comparación no puede acreditar cambios realizados en otros equipos que nunca
se guardaron aquí ni demostrar funcionamiento por la sola presencia del código.
Las cachés locales no versionadas se conservaron sin agregarlas.

## Regla de trabajo acordada

Continuar editando en la rama actual. No crear más commits ni publicar o fusionar
hasta terminar el trabajo final y recibir la indicación del usuario. Mantener
un único informe acumulado de pendientes de integración. Las dos entregas
existentes quedan conservadas; no se reescribe su historia ni se exige al usuario
aplicar parches parciales mientras seguimos desarrollando.

El detalle verificable está en VERIFICACION_MAIN.json. Este informe y la regla
de trabajo quedan en el directorio de trabajo sin commit.

## Nivelación autorizada

Después de esta verificación, el usuario autorizó integrar y publicar en main
todos los avances acumulados. Se integró main mediante una fusión sin conflictos,
conservando ambos historiales y las dos entregas pendientes. La preferencia de
no generar commits parciales sigue vigente para el trabajo posterior.
Este documento conserva el diagnóstico previo; el identificador de main arriba
corresponde al estado anterior a la nivelación.
