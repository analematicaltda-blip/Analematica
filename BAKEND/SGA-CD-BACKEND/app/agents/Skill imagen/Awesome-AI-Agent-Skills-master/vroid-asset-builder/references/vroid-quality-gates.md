# VRoid quality gates and troubleshooting

Use these gates before saying a pack is complete.

## Final acceptance checklist

- `vroid_modelos/manifest.json` exists and parses as JSON.
- Every asset has a clear `name`, stable `id`, and valid category.
- PNG textures that need transparency have alpha preserved.
- Original, 1024, and 512 PNG outputs exist or are intentionally documented as not required.
- Checkerboard JPEG previews exist for user review.
- Alpha masks exist for transparent textures.
- `.vroidcustomitem` files were generated from real VRoid Studio templates, not fabricated.
- `validacion_custom_items.json` exists after validation and reports `failed: 0`.
- `README_ES.md` and `PASOS_VROID_STUDIO.md` describe the actual files in the final pack.
- The final ZIP or package was regenerated after the latest meaningful change.

## Common failure modes

### Missing local templates

Symptom: Custom Item generation cannot locate VRoid Studio templates.

Action: use the local Windows folder `%USERPROFILE%\AppData\LocalLow\pixiv\VRoid Studio\custom_items`, ask for exported templates, or continue only with PNG/manual outputs.

### Failed Custom Item validation

Symptom: `validacion_custom_items.json` has a nonzero `failed` value or per-item failures.

Action: inspect the failed item names, regenerate Custom Items, then rerun validation. If template remnants are mentioned or suspected, run with `--replace-all-transferables`.

### Wrong category

Symptom: asset imports into the wrong VRoid section or cannot be selected for the intended body part.

Action: update the manifest category and regenerate from a template belonging to the correct category. Avoid trying to force a `Tops` item into `Shoes` or hair categories.

### Broken PNG alpha

Symptom: transparent parts become black, white, or opaque.

Action: reopen the source as RGBA, regenerate alpha masks, and ensure exports remain PNG rather than JPEG except for previews.

### Masculine fit problems

Symptom: tops, bottoms, or shoes look misaligned on masculine models.

Action: verify template origin and model fit. Prefer templates tested on masculine models for `Tops`, `Bottoms`, and `Shoes`. Record fit status in the manifest.

## Report format for the user

Use this concise structure after a build or validation pass:

```markdown
## Resultado
[ready / blocked / failed]

## Revisado
- manifest: [ok/falta/error]
- assets por categoría: Tops n, Bottoms n, Shoes n, HairFront n, HairBack n, HairAhoge n
- texturas PNG: [n]
- custom items: [n]

## Validación
- validacion_custom_items.json: failed [n]
- errores principales: [lista breve]

## Archivos generados
- [paths]

## Pendiente
- [solo lo que falte para importación real en VRoid Studio]
```
