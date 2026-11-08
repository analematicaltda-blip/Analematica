# Concurrencia de recuperación y emisión — corte 24

Se amplió la prueba PostgreSQL existente con tres escenarios de recuperación
y emisión, conservando las dos regresiones de ingreso TOTP.

## Resultados observados

| Escenario | Aceptadas | Rechazadas |
| --- | --- | --- |
| Dos sesiones, mismo TOTP de ingreso | 1 | 1 |
| Dos solicitudes, mismo desafío TOTP | 1 | 1 |
| Dos sesiones, mismo código de recuperación | 1 | 1 |
| Dos solicitudes, mismo desafío de recuperación | 1 | 1 |
| Dos sesiones, mismo TOTP para emitir códigos | 1 | 1 |

La caché de protección contra reutilización se desactivó deliberadamente.
Las restricciones observadas dependen de los bloqueos, las versiones de factores
y los contadores en PostgreSQL. Cada trabajador utiliza una conexión independiente.

Además de contar respuestas, se comprobó que un solo desafío quedó consumido,
que el código de recuperación se marcó usado una sola vez y que su consumo no
modificó el contador TOTP. Para emisión se comprobó que el conjunto persistido
coincide con el de la única respuesta aceptada, los anteriores ya no sirven,
el contador avanzó una vez y se conserva un factor TOTP y uno de recuperación.

No fue necesario modificar el servicio funcional: los contratos de bloqueo
existentes superaron estas pruebas. La ampliación pertenece al comando de
prueba ya incluido en CI: BACKEND/deployment/tests/mfa_postgres_check.py.

## Aislamiento y reproducción

PostgreSQL16 en contenedor temporal, imagen fijada por digest, datos en tmpfs,
puerto aleatorio limitado a loopback, credenciales generadas en archivo privado
y eliminación del contenedor al terminar. No se conectó ninguna base del proyecto.
Se crean únicamente tablas necesarias para el contrato, no todas las migraciones.

```bash
python BACKEND/deployment/tests/mfa_postgres_check.py
```

El ejecutor requiere Docker local y sus dependencias de prueba. No imprime
códigos, contraseñas ni semillas. Ver postgres-recovery-evidence-24.json.

## Límites y trabajo pendiente

Esto verifica conexiones PostgreSQL concurrentes en hilos; no acredita procesos
WSGI separados, carga sostenida, recuperación ante caídas ni migración completa
del producto a PostgreSQL. Los recorridos HTTP, contraseña y CSRF se verifican
por separado en los cortes anteriores. No se repitieron sus cifras como pruebas
nuevas en este corte.

Continúan pendientes auditoría y notificaciones de emisión/uso, custodia de claves,
recuperación de ambos factores, correo verificado, dispositivos físicos,
identidad común y validación integral de los módulos del plan maestro.
Sin cambios visuales, sin commit, push ni despliegue productivo.
