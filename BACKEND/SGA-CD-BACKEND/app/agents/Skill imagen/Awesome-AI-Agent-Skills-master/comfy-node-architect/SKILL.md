---
name: comfy-node-architect
description: Create, debug, and optimize custom ComfyUI nodes and interconnected workflows, including dynamic workflow wiring and validation.
---

# ComfyUI Node Architect

> [!IMPORTANT]
> **LECTURA OBLIGATORIA:** [DYNAMIC_WORKFLOWS.md](./DYNAMIC_WORKFLOWS.md) - Protocolos para el manejo dinámico de nodos y workflows.

Expertise in creating, debugging, and optimizing custom nodes and interconnected workflows.

## Connectivity & Auto-Wiring
Para conectar nodos programáticamente en formato UI (Graph):
1. **Punteros**: Cada entrada de un nodo debe tener un objeto `{"name": "input_name", "type": "TYPE", "link": link_id}`.
2. **Enlaces (Links)**: Se definen en la raíz del JSON como `[link_id, origin_node_id, origin_slot_idx, target_node_id, target_slot_idx, "TYPE"]`.
3. **Validación de Slots**:
   - `MODEL`: Slot 0 (CheckpointLoader).
   - `CLIP`: Slot 1 (CheckpointLoader).
   - `VAE`: Slot 2 (CheckpointLoader).
   - `CONDITIONING`: Slot 0 (CLIPTextEncode).
   - `LATENT`: Slot 0 (KSampler/EmptyLatent).

## Forge Commands
- `python scripts/generate_connected_workflow.py`: Genera un JSON con cableado automático validado.

