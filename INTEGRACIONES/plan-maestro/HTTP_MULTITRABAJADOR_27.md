# Contratos HTTP con dos trabajadores Django — corte 27

Se añadió un recorrido HTTP concurrente a la suite PostgreSQL aislada. Se
probaron contraseña real, cookies, sesiones almacenadas en SQL, CSRF y las rutas
de ingreso TOTP, recuperación y emisión. No se modificó el servicio funcional.

## Resultados

| Carrera HTTP contra dos procesos | Aceptadas | Rechazadas |
| --- | --- | --- |
| Dos desafíos de ingreso con el mismo TOTP | 1 | 1 |
| Dos desafíos con el mismo código de recuperación | 1 | 1 |
| Dos sesiones autenticadas emitiendo con el mismo TOTP | 1 | 1 |

Los clientes tienen cookies independientes y completan primero la contraseña.
Los POST sin CSRF se rechazan directamente en las rutas TOTP y recuperación.
Se comprueba que la sesión completada en un trabajador sea reconocida por el
otro. Para emisión, cada sesión completa MFA con un contador distinto; ambas
solicitudes compiten luego con una misma prueba nueva. Se comprueba el conjunto
persistido, el contador y un único evento de auditoría.

Cada solicitud concurrente se envía a un proceso diferente, comprobado mediante
una cabecera exclusiva del arnés de prueba; no se incorpora al producto.
La suite conserva las cinco carreras entre hilos y las cinco entre procesos:
13 escenarios correctos en la ejecución final. La caché de reutilización está
desactivada deliberadamente; el estado compartido se conserva en PostgreSQL.

## Reproducción y aislamiento

```bash
python BACKEND/deployment/tests/mfa_postgres_check.py
```

El comando ya está incluido en CI y ahora invoca mfa_http_contract.py. Crea
PostgreSQL temporal y dos procesos WSGI limitados a loopback, usando credenciales
y usuarios generados. Se cierran conexiones antes de fork y se terminan los
procesos y el contenedor al finalizar. No conecta a bases del proyecto.

## Límites precisos

Se usa HTTP local directo, esquema mínimo y un reloj sintético compartido para
avanzar los contadores sin esperas. No es una prueba de TLS, balanceador,
configuración productiva de Gunicorn, reloj/NTP real ni carga sostenida.
Los recorridos HTTPS de Nginx se acreditan por separado en los cortes anteriores.
Los datos no se imprimen: la evidencia contiene resultados, nunca contraseñas,
semillas, códigos ni cookies.

Siguen pendientes carga sostenida, migración integral PostgreSQL, respaldo y
restauración, notificaciones/SOC, custodia y permisos SQL, recuperación con
pérdida de ambos factores, identidad compartida, teléfonos físicos y módulos
de los tres sistemas. El plan no está al 100 % y producción permanece deshabilitada.
Sin cambios visuales, sin commit ni push. Ver http-workers-evidence-27.json.
