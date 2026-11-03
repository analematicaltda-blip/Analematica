---
name: comfy-local
description: Use when generating images or videos with a local ComfyUI server, ComfyUI API workflows, LoRA diffusion rendering, or localhost port 8188 automation.
---

# ComfyUI API Mastery

Host: `http://localhost:8188`

## Endpoints
- `POST /prompt`: Submit workflow (`{"prompt": {...}}`).
- `GET /history/{id}`: Job status/outputs.
- `GET /object_info/{Type}`: Node schema & available models/loras.
- `GET /view?filename={X}&type=output`: Download result.

## Formats
- **API (Prompt)**: `{"id": {"class_type": "T", "inputs": {"k": "v" or ["id", out_idx]}}}`.
- **UI (Graph)**: `{"nodes": [{"id": 1, "type": "T", "pos": [x,y], "size": [w,h], "widgets_values": [], "inputs": [{"link": id}], "outputs": [{"links": [id]}]}], "links": [[id, out_node, out_slot, in_node, in_slot, "TYPE"]]}`.

## Proven Pipelines (Standard Config)
- **T2I (Illustrious)**: `CheckpointLoader` -> `CLIPTextEncode` (pos/neg) -> `EmptyLatent` -> `KSampler` (Euler A, Karras, CFG 4.0) -> `VAEDecode` -> `SaveImage`.
- **I2V (LTX 2.3)**: `CheckpointLoader` -> `LTXVPreprocess` -> `LTXVConditioning` -> `KSampler` -> `VAEDecodeTiled`.

## Rules
1. **Validation**: Query `/object_info` before any new node usage.
2. **Naming**: `YYYYMMDD_descriptive-slug`.
3. **Batch**: Submit all -> Poll history loop.
4. **Missing Models**: HF URLs in `MarkdownNote`. Download with `curl -L` to `models/`.

