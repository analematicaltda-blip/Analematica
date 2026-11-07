# Backends

Los cuatro componentes están reunidos en esta carpeta:

- `ANALEMATICA-BACKEND/`: servicios y datos originales de Analemática, despliegue corporativo y gateway API seguro.
- `SGA-CD-BACKEND/`: API FastAPI y servicios de SGA-CD.
- `SGA-ERP-TUR-BAKEND/`: dominio ERP turístico Django.
- `SGA-TUR-BAKEND/`: proyecto turístico Django.

`deployment/compose.yaml` configura los cuatro procesos, variables, puertos,
comprobaciones de salud y almacenamiento persistente. Consulta
[deployment/README.md](deployment/README.md) para las pruebas locales y sus límites.
Los nombres de los dos componentes turísticos conservan `BAKEND` tal como fueron
solicitados; la carpeta común se llama `BACKEND`.

La importación Python `Analematica.backend` sigue resolviendo el mismo código
mediante un namespace de compatibilidad, sin duplicar ni restaurar la carpeta antigua.
Los dos servicios Django cargan dependencias reales de los componentes turísticos y
Analemática; son procesos y bases independientes, pero todavía comparten módulos.

La consola sobre la demo anterior conserva su instalador:

```bash
python3 BACKEND/ANALEMATICA-BACKEND/deployment/start.py
python3 BACKEND/SGA-CD-BACKEND/scripts/update_panels.py --start
```

La reorganización no elimina volúmenes ni bases existentes. La configuración nueva
no migra datos de las demos anteriores ni abre un servicio público.
