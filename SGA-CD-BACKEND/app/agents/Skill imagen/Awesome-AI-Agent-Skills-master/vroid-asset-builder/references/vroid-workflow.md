# VRoid asset workflow

Use this reference when executing or repairing a VRoid-compatible asset project.

## Expected project shape

A typical project should contain at least:

```text
project-root/
├── vroid_modelos/
│   ├── manifest.json
│   ├── texturas/                 # editable PNG source textures
│   ├── custom_items/             # generated .vroidcustomitem outputs, if any
│   ├── previews/                 # JPEG previews over checkerboard backgrounds
│   ├── alpha_masks/              # separate alpha masks
│   └── formatos_finales/         # final export-ready PNG/JPEG derivatives
├── crear_modelos_vroid.py
├── crear_vroidcustomitem.py
├── validar_custom_items_vroid.py
├── crear_formatos_vroid.py
├── generar_pack_vroid.bat
├── README_ES.md
└── PASOS_VROID_STUDIO.md
```

Do not require this exact layout if the user's project already works, but use it as the preferred target when creating or reorganizing a project.

## Execution sequence

Run the pipeline in this order unless the user gives a working project-specific order:

```bash
python scripts/audit_vroid_project.py /path/to/project --json /path/to/project/audit_vroid_project.json
python crear_modelos_vroid.py
python crear_vroidcustomitem.py --batch
python validar_custom_items_vroid.py
python scripts/check_custom_item_report.py validacion_custom_items.json
python crear_formatos_vroid.py
generar_pack_vroid.bat
```

When template remnants are detected or validation indicates copied template payloads are stale, rerun Custom Item generation as:

```bash
python crear_vroidcustomitem.py --batch --replace-all-transferables
python validar_custom_items_vroid.py
python scripts/check_custom_item_report.py validacion_custom_items.json
```

## Template handling

Use real VRoid Studio Custom Item templates from the local Windows folder when available:

```text
%USERPROFILE%\AppData\LocalLow\pixiv\VRoid Studio\custom_items
```

If running outside that machine, do not pretend templates were found. Ask for the template export or continue with PNG/manual texture outputs and clearly label `.vroidcustomitem` generation as blocked.

## Texture derivative rules

For every texture that ships as an importable/editable asset:

1. Keep the original PNG with alpha intact.
2. Export a 1024 version preserving aspect ratio.
3. Export a 512 version preserving aspect ratio.
4. Export a grayscale alpha mask when the PNG has an alpha channel.
5. Export a JPEG preview composited over a checkerboard background.

Use `scripts/export_texture_derivatives.py` for deterministic derivative generation when Pillow is available.

## Documentation update rules

After adding or materially changing an item:

- Update `vroid_modelos/manifest.json` with the asset entry.
- Update `README_ES.md` with what the pack contains and what imports directly.
- Update `PASOS_VROID_STUDIO.md` with exact import instructions and any manual texture application steps.
- Regenerate the final ZIP or pack so documentation and files stay synchronized.
