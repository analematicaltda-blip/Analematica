#!/usr/bin/env python3
"""Audit a VRoid-compatible asset project.

This script checks the manifest, expected pipeline scripts, referenced files,
VRoid category names, PNG basics, and Custom Item validation report status.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys
from pathlib import Path, PureWindowsPath
from typing import Any

ALLOWED_CATEGORIES = {"Tops", "Bottoms", "Shoes", "HairFront", "HairBack", "HairAhoge"}
EXPECTED_PIPELINE_SCRIPTS = [
    "crear_modelos_vroid.py",
    "crear_vroidcustomitem.py",
    "validar_custom_items_vroid.py",
    "crear_formatos_vroid.py",
    "generar_pack_vroid.bat",
]
PATH_FIELDS = [
    "source_png",
    "texture",
    "texture_png",
    "texture_path",
    "png",
    "source",
    "alpha_mask",
    "preview_jpg",
    "preview",
    "custom_item",
    "custom_item_path",
    "template_source",
]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def add(report: dict[str, Any], level: str, message: str) -> None:
    report[level].append(message)


def resolve_project(root: Path) -> tuple[Path, Path, Path]:
    root = root.resolve()
    if root.name == "vroid_modelos" or (root / "manifest.json").exists():
        vroid_dir = root
        project_root = root.parent if root.name == "vroid_modelos" else root
    else:
        project_root = root
        vroid_dir = root / "vroid_modelos"
    return project_root, vroid_dir, vroid_dir / "manifest.json"


def load_manifest(path: Path, report: dict[str, Any]) -> Any | None:
    if not path.exists():
        add(report, "errors", f"manifest missing: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        add(report, "errors", f"manifest is not valid JSON: {exc}")
        return None


def extract_assets(manifest: Any) -> list[Any]:
    if isinstance(manifest, list):
        return manifest
    if isinstance(manifest, dict):
        for key in ("assets", "items", "modelos", "models"):
            value = manifest.get(key)
            if isinstance(value, list):
                return value
        # Fall back to any list of dictionaries if a legacy manifest uses a custom key.
        for value in manifest.values():
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                return value
    return []


def clean_path(value: str) -> str:
    return value.replace("\\", "/").strip()


def resolve_asset_path(raw: str, manifest_dir: Path, project_root: Path) -> Path:
    # Preserve Windows absolute paths when the script runs on Windows. On POSIX,
    # treat drive-letter paths as non-resolvable external paths.
    if re.match(r"^[A-Za-z]:[\\/]", raw):
        return Path(PureWindowsPath(raw))
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    cleaned = Path(clean_path(raw))
    local = manifest_dir / cleaned
    if local.exists():
        return local
    return project_root / cleaned


def png_info(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("rb") as handle:
            if handle.read(8) != PNG_SIGNATURE:
                return None
            ihdr_len = struct.unpack(">I", handle.read(4))[0]
            chunk_type = handle.read(4)
            if chunk_type != b"IHDR" or ihdr_len < 13:
                return None
            data = handle.read(ihdr_len)
            width, height, bit_depth, color_type = struct.unpack(">IIBB", data[:10])
            has_alpha = color_type in (4, 6)
            # Check for tRNS before IDAT because indexed/RGB PNGs can have transparency.
            while True:
                length_bytes = handle.read(4)
                if len(length_bytes) != 4:
                    break
                length = struct.unpack(">I", length_bytes)[0]
                ctype = handle.read(4)
                if ctype == b"tRNS":
                    has_alpha = True
                    break
                handle.seek(length + 4, os.SEEK_CUR)
                if ctype in (b"IDAT", b"IEND"):
                    break
            return {
                "width": width,
                "height": height,
                "bit_depth": bit_depth,
                "color_type": color_type,
                "has_alpha": has_alpha,
            }
    except Exception:
        return None


def find_report(project_root: Path, vroid_dir: Path, user_report: str | None) -> Path | None:
    candidates: list[Path] = []
    if user_report:
        candidates.append(Path(user_report))
    candidates.extend([
        project_root / "validacion_custom_items.json",
        vroid_dir / "validacion_custom_items.json",
        project_root / "reports" / "validacion_custom_items.json",
    ])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def failed_count_from_report(data: Any) -> int | None:
    if isinstance(data, dict):
        for key in ("failed", "failures", "failed_count", "error_count"):
            value = data.get(key)
            if isinstance(value, bool):
                return int(value)
            if isinstance(value, int):
                return value
            if isinstance(value, list):
                return len(value)
        for key in ("summary", "totals", "result", "validation"):
            if key in data:
                nested = failed_count_from_report(data[key])
                if nested is not None:
                    return nested
        for key in ("items", "assets", "results", "checks", "custom_items"):
            value = data.get(key)
            if isinstance(value, list):
                return sum(1 for item in value if item_is_failed(item))
    if isinstance(data, list):
        return sum(1 for item in data if item_is_failed(item))
    return None


def item_is_failed(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    if item.get("valid") is False or item.get("passed") is False or item.get("ok") is False:
        return True
    status = str(item.get("status") or item.get("result") or "").lower()
    return status in {"fail", "failed", "invalid", "error", "errors", "broken"}


def vroid_template_folder() -> Path | None:
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        return Path(user_profile) / "AppData" / "LocalLow" / "pixiv" / "VRoid Studio" / "custom_items"
    home = Path.home()
    candidate = home / "AppData" / "LocalLow" / "pixiv" / "VRoid Studio" / "custom_items"
    return candidate


def audit(root: Path, report_path_arg: str | None = None) -> dict[str, Any]:
    project_root, vroid_dir, manifest_path = resolve_project(root)
    report: dict[str, Any] = {
        "project_root": str(project_root),
        "vroid_dir": str(vroid_dir),
        "manifest": str(manifest_path),
        "errors": [],
        "warnings": [],
        "summary": {
            "assets_total": 0,
            "categories": {category: 0 for category in sorted(ALLOWED_CATEGORIES)},
            "png_textures": 0,
            "png_with_alpha": 0,
            "custom_items_referenced": 0,
            "missing_files": 0,
        },
        "assets": [],
    }

    if not vroid_dir.exists():
        add(report, "warnings", f"vroid_modelos folder not found at expected path: {vroid_dir}")

    for script_name in EXPECTED_PIPELINE_SCRIPTS:
        if not (project_root / script_name).exists():
            add(report, "warnings", f"expected pipeline script missing: {script_name}")

    template_dir = vroid_template_folder()
    report["vroid_custom_items_template_dir"] = str(template_dir) if template_dir else None
    if not template_dir or not template_dir.exists():
        add(report, "warnings", "local VRoid Studio custom_items template folder was not found; .vroidcustomitem generation may be blocked")

    manifest = load_manifest(manifest_path, report)
    assets = extract_assets(manifest) if manifest is not None else []
    if manifest is not None and not assets:
        add(report, "warnings", "manifest parsed, but no assets list was found")

    report["summary"]["assets_total"] = len(assets)

    for index, asset in enumerate(assets):
        asset_report: dict[str, Any] = {"index": index, "errors": [], "warnings": [], "files": []}
        if not isinstance(asset, dict):
            asset_report["errors"].append("asset is not an object")
            report["assets"].append(asset_report)
            add(report, "errors", f"asset #{index} is not an object")
            continue

        asset_id = str(asset.get("id") or asset.get("slug") or "").strip()
        asset_name = str(asset.get("name") or asset.get("nombre") or asset_id or f"asset-{index}").strip()
        category = str(asset.get("category") or asset.get("categoria") or "").strip()
        status = str(asset.get("status") or asset.get("estado") or "").strip().lower()
        import_method = str(asset.get("import_method") or asset.get("metodo_importacion") or "").strip().lower()

        asset_report.update({"id": asset_id, "name": asset_name, "category": category, "status": status})

        if not asset_id:
            asset_report["warnings"].append("missing stable id")
        elif not ID_PATTERN.match(asset_id):
            asset_report["warnings"].append("id should use lowercase hyphen-case")

        if not asset_name:
            asset_report["warnings"].append("missing clear name")

        if not category:
            asset_report["errors"].append("missing category")
        elif category not in ALLOWED_CATEGORIES:
            asset_report["errors"].append(f"invalid category: {category}")
        else:
            report["summary"]["categories"][category] += 1

        for field in PATH_FIELDS:
            value = asset.get(field)
            if not isinstance(value, str) or not value.strip():
                continue
            resolved = resolve_asset_path(value, manifest_path.parent, project_root)
            exists = resolved.exists()
            file_info: dict[str, Any] = {"field": field, "path": str(resolved), "exists": exists}
            if not exists:
                report["summary"]["missing_files"] += 1
                message = f"missing referenced file for {asset_name}: {field} -> {value}"
                if status in {"ready", "validated"} or field in {"source_png", "custom_item"}:
                    asset_report["errors"].append(message)
                else:
                    asset_report["warnings"].append(message)
            else:
                suffix = resolved.suffix.lower()
                if field in {"source_png", "texture", "texture_png", "texture_path", "png", "source"}:
                    if suffix != ".png":
                        asset_report["warnings"].append(f"texture field is not a PNG: {field} -> {value}")
                    else:
                        report["summary"]["png_textures"] += 1
                        info = png_info(resolved)
                        file_info["png"] = info
                        if info is None:
                            asset_report["errors"].append(f"invalid PNG file: {value}")
                        elif info.get("has_alpha"):
                            report["summary"]["png_with_alpha"] += 1
                if field in {"custom_item", "custom_item_path"}:
                    report["summary"]["custom_items_referenced"] += 1
                    if suffix != ".vroidcustomitem":
                        asset_report["errors"].append(f"custom item path must end in .vroidcustomitem: {value}")
            asset_report["files"].append(file_info)

        if import_method == "custom_item" and not any(field in asset for field in ("custom_item", "custom_item_path")):
            asset_report["warnings"].append("import_method is custom_item but no custom_item path is documented")

        for message in asset_report["errors"]:
            add(report, "errors", message)
        for message in asset_report["warnings"]:
            add(report, "warnings", message)
        report["assets"].append(asset_report)

    validation_report = find_report(project_root, vroid_dir, report_path_arg)
    if validation_report:
        report["validation_report"] = str(validation_report)
        try:
            validation_data = json.loads(validation_report.read_text(encoding="utf-8"))
            failed = failed_count_from_report(validation_data)
            report["validation_failed"] = failed
            if failed is None:
                add(report, "warnings", "validation report exists but failed count could not be determined")
            elif failed > 0:
                add(report, "errors", f"custom item validation failed count is {failed}")
        except Exception as exc:
            add(report, "errors", f"could not parse validation report: {exc}")
    else:
        report["validation_report"] = None
        if report["summary"]["custom_items_referenced"] > 0:
            add(report, "warnings", "custom items are referenced but validacion_custom_items.json was not found")

    report["ok"] = not report["errors"]
    return report


def print_human(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("VRoid project audit")
    print(f"project_root: {report['project_root']}")
    print(f"manifest: {report['manifest']}")
    print(f"ok: {report['ok']}")
    print(f"assets_total: {summary['assets_total']}")
    print("categories:")
    for category, count in summary["categories"].items():
        print(f"- {category}: {count}")
    print(f"png_textures: {summary['png_textures']}")
    print(f"png_with_alpha: {summary['png_with_alpha']}")
    print(f"custom_items_referenced: {summary['custom_items_referenced']}")
    print(f"missing_files: {summary['missing_files']}")
    if report.get("validation_failed") is not None:
        print(f"validation_failed: {report['validation_failed']}")
    if report["errors"]:
        print("errors:")
        for message in report["errors"]:
            print(f"- {message}")
    if report["warnings"]:
        print("warnings:")
        for message in report["warnings"]:
            print(f"- {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a VRoid-compatible asset project.")
    parser.add_argument("project", nargs="?", default=".", help="Project root or vroid_modelos directory.")
    parser.add_argument("--report", help="Explicit path to validacion_custom_items.json.")
    parser.add_argument("--json", dest="json_output", help="Write full audit JSON to this path.")
    parser.add_argument("--quiet", action="store_true", help="Only write JSON and exit.")
    args = parser.parse_args()

    report = audit(Path(args.project), args.report)

    if args.json_output:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.quiet:
        print_human(report)

    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
