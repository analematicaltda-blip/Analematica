# 🌀 Manejo Dinámico de Workflows en ComfyUI

Este documento es de **LECTURA OBLIGATORIA** para el desarrollo de nodos y workflows avanzados en el ecosistema Claudebot.

## 1. Filosofía de Nodos Dinámicos
Los nodos no deben ser estáticos. Deben permitir la "conmutación" (switching) y la "derivación" (bypassing) para permitir que el usuario tome el control manual en cualquier momento.

### El Patrón Toggle/Bypass
Cuando diseñes un nodo que procesa strings o imágenes, siempre incluye un booleano `active` o un selector de `mode`. 
- **Objetivo:** Si el nodo está inactivo, debe pasar la entrada principal directamente a la salida sin cambios.
- **Integración con Widgets:** En ComfyUI, si conviertes un widget (ej. un STRING de prompt) en una entrada (`input`) y nada está conectado a ella, el sistema volverá a usar el valor del widget manual. Esto permite flujos híbridos.

## 2. Workflows Multimodelo (Auraflow)
Para manejar múltiples modelos simultáneamente (como el caso de Auraflow):
- Usa un único **CLIP Text Encode** para mantener la coherencia semántica.
- Implementa **Node Concatenation** para añadir prefijos o sufijos dinámicos por modelo.
- Utiliza visualizadores paralelos para comparación en tiempo real.

## 3. Carga de Prompts desde Archivos
El uso de `XenoAdvancedTextReader` permite iterar sobre listas de prompts masivas.
- **Modo Random:** Evita el sobreentrenamiento visual en pruebas de modelos.
- **Modo Forward:** Útil para comparaciones deterministas de modelos con el mismo set de datos.

## 4. Referencia de Inyección
Para inyectar nodos dinámicamente desde el CLI a ComfyUI, utiliza el script `scripts/update_comfy_node.py` que mantiene la integridad de los `NODE_CLASS_MAPPINGS`.
