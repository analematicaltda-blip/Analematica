# ESCENARIOS DE VALIDACIÓN FUNCIONAL REAL - FASE 3.2

## Escenario Maestro: "Ciclo de Vida de una Operación Turística"

| Paso | Módulo | Acción del Soldado | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| 1 | **Perfil** |  | Datos del prestador cargados correctamente. |
| 2 | **Clientes** |  | Registro persistido en DB con UUID único. |
| 3 | **Productos** |  | Catálogo disponible para vincular a reserva. |
| 4 | **Inventario** |  | Afectación real de existencias tras asignación. |
| 5 | **Horarios** |  | Confirmación de disponibilidad en fecha/hora. |
| 6 | **Reservas** |  | Cambio de estado de PENDIENTE a CONFIRMADA. |
| 7 | **Costos** |  | Impacto financiero en el módulo de costos. |
| 8 | **Documentos** |  | Metadatos registrados y vínculo con la operación. |
| 9 | **Valoraciones**|  | Registro de reputación post-operación. |
| 10 | **Estadísticas**|  | Actualización de métricas en el panel operativo. |

## Escenario de Control: "Integridad y Restricciones"

1. **Aislamiento Tenant**: Validar que el  bloquea intentos de lectura de clientes entre  distintos.
2. **Validación de Reglas**: Impedir  si el horario está marcado como CERRADO en .
3. **Persistencia Forense**: Verificar que cada acción del Sargento deja un log en .
