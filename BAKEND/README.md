# Componentes backend

- `SGA-CD-BACKEND/`: API y servicios del sistema SGA-CD.
- `SGA-ERP-TUR-BAKEND/`: backend ERP turístico.
- `SGA-TUR-BAKEND/`: backend turístico.

Las tres carpetas se trasladaron desde la raíz sin cambiar sus nombres ni sus
módulos internos. Las rutas de Docker Compose, instaladores, CI, pruebas y enlaces
entre componentes se actualizaron al nuevo nivel. Los modelos de datos siguen
en `DB/SGA-CD-DB.git`; se conserva el mecanismo de importación existente.

Actualización de paneles SGA-CD:

```bash
python3 BAKEND/SGA-CD-BACKEND/scripts/update_panels.py --start
```

La consola del dueño conserva su instalador:

```bash
python3 Analematica-SGA-CD/deployment/start.py
```

La reorganización no mueve volúmenes Docker, no ejecuta SQL o migraciones y no
publica claves privadas. El arranque completo de los sistemas turísticos sigue
pendiente de resolver las incidencias preexistentes documentadas al importarlos.
