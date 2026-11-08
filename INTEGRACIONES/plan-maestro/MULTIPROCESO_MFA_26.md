# MFA y recuperación en procesos independientes — corte 26

Se ampliaron los contratos PostgreSQL con cinco escenarios ejecutados en dos
procesos Linux independientes por escenario. Se conservaron las cinco pruebas
con hilos del corte anterior. Los diez escenarios pasaron.

## Comportamiento observado

| Escenario en procesos separados | Aceptadas | Rechazadas |
| --- | --- | --- |
| TOTP, sesiones distintas y mismo código | 1 | 1 |
| TOTP, mismo desafío | 1 | 1 |
| Recuperación, sesiones distintas y mismo código | 1 | 1 |
| Recuperación, mismo desafío | 1 | 1 |
| Emisión, sesiones distintas y mismo TOTP | 1 | 1 |

Cada par se sincroniza con una barrera; se comprueba que respondan dos PID
independientes. Se cierran todas las conexiones ORM antes de crear procesos y
cada proceso abre su propia conexión; no se heredan conexiones libpq activas.
La caché de protección contra reutilización permanece desactivada deliberadamente.

Las aserciones comprueban un desafío consumido, un código de recuperación usado,
un único evento de auditoría de recuperación/emisión y el contador persistente
esperado. En emisión, el conjunto persistido coincide por SHA-256 con la única
respuesta aceptada y los códigos anteriores quedan invalidados. Los códigos
nuevos no se imprimen ni se envían en la evidencia; entre procesos se devuelve
solo aceptación, PID y digest del conjunto para comprobar consistencia.

No fue necesario modificar el servicio funcional: las protecciones existentes
superaron la validación ampliada. El script ya pertenece al flujo CI del plan.

## Alcance y reproducción

`BACKEND/deployment/tests/mfa_postgres_check.py` crea PostgreSQL16 temporal,
imagen fijada, datos en tmpfs, credenciales efímeras y puerto local aleatorio.
Usa exclusivamente tablas mínimas del contrato y usuarios sintéticos. El
contenedor se elimina al terminar. No se conecta a bases del proyecto.

```bash
python BACKEND/deployment/tests/mfa_postgres_check.py
```

La comprobación multiproceso utiliza fork y requiere Linux. Es una prueba del
servicio con ORM y PostgreSQL; no inicia varios servidores WSGI ni envía HTTP
simultáneo a través de un balanceador. Los controles HTTP/CSRF se verificaron
separadamente en cortes previos. No certifica carga sostenida, disponibilidad,
caídas entre commit y respuesta ni migración completa de todos los módulos.

## Pendientes del plan

Carga y trabajadores HTTP reales; migración integral PostgreSQL; notificaciones
de seguridad y exportación supervisada a SOC; permisos SQL y retención de
auditoría; recuperación de ambos factores y correo verificado; custodia de
llaves, dispositivos físicos, identidad compartida y módulos de las tres
plataformas. Este corte no cambia la interfaz ni cierra el plan al 100 %.
Sin commit, push ni despliegue productivo. Ver multiprocess-evidence-26.json.
