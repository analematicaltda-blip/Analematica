#!/usr/bin/env python3
"""Create VRoid-friendly texture derivatives from PNG files.

Outputs:
- original RGBA PNG copy
- resized PNGs for the requested maximum-side sizes, default 1024 and 512
- grayscale alpha mask PNG
- JPEG preview composited over a checkerboard background
- derivatives_manifest.json summarizing generated files
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image
except ImportError:  # pragma: no cover - depends on runtime environment
    Image = None  # type: ignore[assignment]

GENERATED_SUFFIXES = (
    "_original",
    "_1024",
    "_512",
    "_alpha_mask",
    "_preview",
)


def discover_pngs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path] if input_path.suffix.lower() == ".png" else []
    if not input_path.exists():
        return []
    pngs: list[Path] = []
    for path in input_path.rglob("*.png"):
        if any(path.stem.endswith(suffix) for suffix in GENERATED_SUFFIXES):
            continue
        if "formatos_finales" in path.parts or "alpha_masks" in path.parts or "previews" in path.parts:
            continue
        pngs.append(path)
    return sorted(pngs)


def default_output_dir(input_path: Path) -> Path:
    if input_path.is_file():
        return input_path.parent / "formatos_finales" / "texturas"
    if input_path.name == "vroid_modelos":
        return input_path / "formatos_finales" / "texturas"
    return input_path / "formatos_finales" / "texturas"


def resize_max_side(image: "Image.Image", target: int) -> "Image.Image":
    width, height = image.size
    if width <= 0 or height <= 0:
        raise ValueError("image has invalid dimensions")
    scale = target / max(width, height)
    new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def checkerboard(size: tuple[int, int], square: int = 16) -> "Image.Image":
    width, height = size
    background = Image.new("RGB", size, (240, 240, 240))
    alt = Image.new("RGB", (square, square), (200, 200, 200))
    for y in range(0, height, square):
        for x in range(0, width, square):
            if (x // square + y // square) % 2:
                background.paste(alt, (x, y))
    return background


def has_visible_alpha(image: "Image.Image") -> bool:
    alpha = image.getchannel("A")
    extrema = alpha.getextrema()
    return extrema[0] < 255


def process_png(path: Path, out_dir: Path, sizes: Iterable[int], preview_max_side: int | None) -> dict[str, object]:
    assert Image is not None
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = path.stem

    with Image.open(path) as opened:
        image = opened.convert("RGBA")

    record: dict[str, object] = {
        "source": str(path),
        "width": image.size[0],
        "height": image.size[1],
        "has_alpha": has_visible_alpha(image),
        "outputs": {},
    }
    outputs: dict[str, str] = {}

    original_path = out_dir / f"{stem}_original.png"
    image.save(original_path)
    outputs["original_png"] = str(original_path)

    for size in sizes:
        resized = resize_max_side(image, size)
        resized_path = out_dir / f"{stem}_{size}.png"
        resized.save(resized_path)
        outputs[f"png_{size}"] = str(resized_path)

    alpha_path = out_dir / f"{stem}_alpha_mask.png"
    image.getchannel("A").save(alpha_path)
    outputs["alpha_mask_png"] = str(alpha_path)

    preview_image = image
    if preview_max_side and max(image.size) > preview_max_side:
        preview_image = resize_max_side(image, preview_max_side)
    board = checkerboard(preview_image.size)
    board.paste(preview_image, (0, 0), preview_image)
    preview_path = out_dir / f"{stem}_preview.jpg"
    board.save(preview_path, quality=92, optimize=True)
    outputs["preview_jpg"] = str(preview_path)

    record["outputs"] = outputs
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate PNG derivatives, alpha masks, and checkerboard JPEG previews.")
    parser.add_argument("input", help="PNG file or directory containing source PNG textures.")
    parser.add_argument("--out", help="Output directory. Defaults to formatos_finales/texturas under the input.")
    parser.add_argument("--sizes", nargs="*", type=int, default=[1024, 512], help="Maximum-side PNG sizes to export.")
    parser.add_argument("--preview-max-side", type=int, default=1600, help="Maximum side for JPEG previews; use 0 for original size.")
    parser.add_argument("--manifest-name", default="derivatives_manifest.json", help="Name of the generated derivatives manifest.")
    args = parser.parse_args()

    if Image is None:
        print("ERROR: Pillow is required. Install with: python -m pip install pillow", file=sys.stderr)
        return 1

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        return 1

    sizes = [size for size in args.sizes if size > 0]
    if not sizes:
        print("ERROR: at least one positive size is required", file=sys.stderr)
        return 1

    out_dir = Path(args.out).resolve() if args.out else default_output_dir(input_path).resolve()
    preview_max_side = None if args.preview_max_side == 0 else args.preview_max_side
    pngs = discover_pngs(input_path)
    if not pngs:
        print(f"ERROR: no source PNG files found in {input_path}", file=sys.stderr)
        return 1

    records = []
    errors = []
    for png in pngs:
        try:
            records.append(process_png(png, out_dir, sizes, preview_max_side))
            print(f"processed: {png}")
        except Exception as exc:
            errors.append({"source": str(png), "error": str(exc)})
            print(f"ERROR processing {png}: {exc}", file=sys.stderr)

    manifest = {
        "input": str(input_path),
        "output_dir": str(out_dir),
        "sizes": sizes,
        "processed": len(records),
        "failed": len(errors),
        "items": records,
        "errors": errors,
    }
    manifest_path = out_dir / args.manifest_name
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"manifest: {manifest_path}")
    print(f"processed: {len(records)}")
    print(f"failed: {len(errors)}")

    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
