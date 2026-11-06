---
name: vroid-asset-builder
description: build, improve, validate, and package vroid studio-compatible assets, png textures with alpha, alpha masks, checkerboard previews, and .vroidcustomitem custom items. use when the user works with vroid_modelos/manifest.json, vroid studio custom_items templates, tops, bottoms, shoes, hairfront, hairback, hairahoge, decals, outfits, texture derivatives, validacion_custom_items.json, or an import-ready vroid asset pack pipeline.
---

# VRoid Asset Builder

## Purpose

Use this skill to help create, improve, validate, and package VRoid Studio-compatible asset projects. Treat this as a normal ChatGPT skill: it guides and automates work on a user's project files, but it is not itself a VRoid model, custom item, or texture pack.

Prioritize native VRoid-friendly assets: PNG textures with alpha, alpha masks, JPEG previews over checkerboard backgrounds, documented `manifest.json` entries, and validated `.vroidcustomitem` files when the asset must be imported as a Custom Item.

## Non-negotiable compatibility rules

- Do not invent a finished `.vroidcustomitem` without using a real VRoid Studio template from the user's local `AppData/LocalLow/pixiv/VRoid Studio/custom_items` or a template the user provided.
- Do not claim validation passed unless `validar_custom_items_vroid.py` or `scripts/check_custom_item_report.py` confirms `failed: 0` in `validacion_custom_items.json`.
- Preserve editable PNGs as the source of truth. Keep alpha where transparency is needed.
- Generate or request these texture derivatives when relevant: original-size PNG, 1024 PNG, 512 PNG, alpha mask PNG, and checkerboard JPEG preview.
- Split complete outfits into importable parts: top, bottom, shoes, hair parts, and flat decals/accessories.
- Use `.vroidcustomitem` over generic formats whenever the asset needs to be importable through VRoid Studio Custom Items.
- If template remnants appear, regenerate custom items with `--replace-all-transferables`.
- Be honest when the current environment cannot access Windows VRoid Studio folders; continue with PNG/manual assets and note that Custom Item generation requires real local templates.

## Canonical categories

Use exactly these VRoid categories unless the user's project already defines a more precise compatible mapping:

| Asset type | Category |
|---|---|
| Upper clothing | `Tops` |
| Pants or skirts | `Bottoms` |
| Shoes | `Shoes` |
| Front hair | `HairFront` |
| Back hair | `HairBack` |
| Ahoge or special hair locks | `HairAhoge` |
| Flat decals or planar accessories | usually `Tops` or manual texture |

For masculine models, pay special attention to `Tops`, `Bottoms`, and `Shoes`; verify they are not accidentally built from incompatible feminine-only templates unless the user explicitly accepts that limitation.

## Standard workflow

1. Inspect `vroid_modelos/manifest.json` first.
2. Confirm each asset has a clear name, category, source texture path, output path, and intended import method.
3. Audit the project with `scripts/audit_vroid_project.py` when project files are available.
4. Generate or refresh base textures with the user's `crear_modelos_vroid.py`.
5. Generate texture derivatives with `scripts/export_texture_derivatives.py` when PNG outputs need masks, previews, 1024, or 512 versions.
6. Generate Custom Items with `crear_vroidcustomitem.py --batch` when local templates exist.
7. Validate Custom Items with `validar_custom_items_vroid.py`, then verify the report with `scripts/check_custom_item_report.py`.
8. Create final formats with `crear_formatos_vroid.py`.
9. Package the final pack with `generar_pack_vroid.bat` or the user's equivalent packaging command.
10. Update `README_ES.md`, `PASOS_VROID_STUDIO.md`, and `manifest.json` after every meaningful asset addition or category change.

For full command details, consult `references/vroid-workflow.md`. For manifest shape, consult `references/manifest-schema.md`. For final acceptance checks and troubleshooting, consult `references/vroid-quality-gates.md`.

## Bundled helper scripts

Run these scripts from the skill directory or copy them into the user's project when useful:

```bash
python scripts/audit_vroid_project.py /path/to/project --json audit_vroid_project.json
python scripts/export_texture_derivatives.py /path/to/project/vroid_modelos --out /path/to/project/vroid_modelos/formatos_finales/texturas
python scripts/check_custom_item_report.py /path/to/project/validacion_custom_items.json
python scripts/run_vroid_pipeline.py /path/to/project --dry-run
```

Use `run_vroid_pipeline.py` only after inspecting the project and confirming its scripts are present. Use `--replace-all-transferables` if validation or visual inspection suggests template leftovers.

## Output standards

When reporting results to the user, include:

- What was inspected or changed.
- The asset count by category.
- Whether Custom Item validation passed, failed, or could not be run.
- Paths to generated derivatives, reports, and final ZIP/package.
- Any remaining manual VRoid Studio steps, especially template import requirements.

Never hide failed validations. A pack is only ready when the validation report has `failed: 0`, required PNG derivatives exist, and documentation is updated.

