# Medición reproducible del motor contable

Comando local explícito, sin base de cliente ni proveedor:

```bash
/workspace/.integration-venv/bin/python BACKEND/deployment/benchmark_accounting.py \
  --synthetic-local --samples 100 --output /tmp/medicion-contable-nueva.json
```

El archivo de salida debe ser nuevo, absoluto, fuera del repositorio y sin enlaces simbólicos; se crea privado0600. El proceso rechaza reutilizar una aplicación Django ya cargada y verifica SQLite en memoria. La preparación importa fixtures aislados existentes; nunca selecciona la base configurada por el usuario ni un servidor productivo.

Por cada documento sintético se miden revisión, posteo, recuperación idempotente y conciliación integral. Se comprueban asiento único, cuatro líneas por compra y acumulación exacta de IVA. Se conserva la definición del dataset, digest, manifiesto de fuentes estable y metadatos de CPU visible/arquitectura/Python. No se registran credenciales o datos reales.

Se calculan p50/p95/p99 mediante nearest rank, media, mínimo, máximo, éxitos y errores. Los fallos y las colas lentas no se eliminan del denominador. El objetivo local250ms se compara con la duración sin redondear; una media baja no oculta un máximo que lo incumpla.

La función de evaluación de clasificaciones admite predicciones previamente etiquetadas, valida identidades y cuenta las abstenciones en el denominador. Es una herramienta de evaluación, no un clasificador. El ensayo contable no ejecuta un modelo IA: su precisión queda **NO EVALUADA**, sin acreditar99,8% por ausencia de errores del ledger o por etiquetas sintéticas perfectas.

Estas mediciones son secuenciales y dentro del proceso ORM; excluyen HTTP, red, dispositivos, DIAN, concurrencia y carga prolongada. No califican latencia extremo a extremo, una SLA universal o producción. Los resultados, incluso si superan250ms, deben conservarse y guiar la optimización posterior.
