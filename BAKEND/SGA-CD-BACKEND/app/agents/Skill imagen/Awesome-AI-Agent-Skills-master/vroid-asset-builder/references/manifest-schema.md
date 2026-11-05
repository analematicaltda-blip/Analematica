# Recommended manifest schema

Use this reference when creating or editing `vroid_modelos/manifest.json`.

## Preferred top-level structure

```json
{
  "project": "nombre-del-pack",
  "vroid_studio_version": "detectada-o-desconocida",
  "updated_at": "2026-04-25",
  "assets": [
    {
      "id": "camiseta-basica-negra",
      "name": "Camiseta básica negra",
      "category": "Tops",
      "model_fit": "masculine",
      "source_png": "texturas/camiseta_basica_negra.png",
      "alpha_mask": "alpha_masks/camiseta_basica_negra_alpha_mask.png",
      "preview_jpg": "previews/camiseta_basica_negra_preview.jpg",
      "custom_item": "custom_items/camiseta_basica_negra.vroidcustomitem",
      "import_method": "custom_item",
      "status": "ready",
      "notes": "probado en Tops"
    }
  ]
}
```

## Required fields for each asset

- `id`: stable lowercase identifier using letters, numbers, and hyphens.
- `name`: clear user-facing name.
- `category`: one of `Tops`, `Bottoms`, `Shoes`, `HairFront`, `HairBack`, `HairAhoge`, or a documented manual-texture category.
- `source_png`: editable PNG source path when the item uses a texture.
- `import_method`: `custom_item`, `manual_texture`, or `reference_only`.
- `status`: `draft`, `needs_template`, `generated`, `validated`, `ready`, or `failed`.

## Strongly recommended fields

- `model_fit`: `masculine`, `feminine`, `unisex`, or `unknown`.
- `alpha_mask`: path to the separate alpha mask PNG.
- `preview_jpg`: path to the checkerboard preview JPEG.
- `custom_item`: path to the generated `.vroidcustomitem`, when applicable.
- `template_source`: path or description of the real VRoid Studio template used.
- `resolution_exports`: object or list documenting original, 1024, and 512 outputs.
- `validation`: object containing the latest validation result and timestamp.
- `notes`: concise warnings, manual import steps, or fit limitations.

## Category mapping

```json
{
  "ropa_superior": "Tops",
  "pantalones_faldas": "Bottoms",
  "calzado": "Shoes",
  "pelo_frontal": "HairFront",
  "pelo_trasero": "HairBack",
  "ahoge_mechones": "HairAhoge",
  "decals_accesorios_planos": "Tops"
}
```

## Validation expectations

A manifest is not complete if an item marked `ready` is missing its source PNG, preview, alpha mask where needed, or Custom Item validation result. Use `scripts/audit_vroid_project.py` to identify missing files and invalid categories.
