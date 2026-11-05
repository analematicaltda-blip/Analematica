#!/usr/bin/env python3
"""Run the canonical VRoid asset pipeline from a project root.

This script is intentionally conservative. It refuses to run missing steps, stops
on the first failure unless --continue-on-error is used, and treats Custom Item
validation as a hard quality gate.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PIPELINE = [
    ("generate base textures", ["{python}", "crear_modelos_vroid.py"]),
    ("generate custom items", ["{python}", "crear_vroidcustomitem.py", "--batch"]),
    ("validate custom items", ["{python}", "validar_custom_items_vroid.py"]),
    ("check validation report", ["{python}", "{check_report}", "validacion_custom_items.json"]),
    ("create final formats", ["{python}", "crear_formatos_vroid.py"]),
]
REQUIRED_FILES = [
    "crear_modelos_vroid.py",
    "crear_vroidcustomitem.py",
    "validar_custom_items_vroid.py",
    "crear_formatos_vroid.py",
]


def expand(command: list[str], project_root: Path, python_cmd: str, check_report: Path, replace_all: bool) -> list[str]:
    expanded = [part.format(python=python_cmd, check_report=str(check_report)) for part in command]
    if "crear_vroidcustomitem.py" in expanded and replace_all:
        expanded.append("--replace-all-transferables")
    return expanded


def print_command(label: str, command: list[str]) -> None:
    print(f"\n== {label} ==")
    print(" ".join(command))


def run_step(label: str, command: list[str], cwd: Path, dry_run: bool) -> int:
    print_command(label, command)
    if dry_run:
        return 0
    completed = subprocess.run(command, cwd=str(cwd), text=True)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the canonical VRoid project pipeline.")
    parser.add_argument("project", nargs="?", default=".", help="Project root containing the pipeline scripts.")
    parser.add_argument("--python", default=sys.executable, help="Python executable to use for project scripts.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running them.")
    parser.add_argument("--replace-all-transferables", action="store_true", help="Pass this flag to crear_vroidcustomitem.py.")
    parser.add_argument("--skip-package", action="store_true", help="Skip generar_pack_vroid.bat.")
    parser.add_argument("--continue-on-error", action="store_true", help="Continue after a failed command and return failure at the end.")
    args = parser.parse_args()

    project_root = Path(args.project).resolve()
    if not project_root.exists():
        print(f"ERROR: project root not found: {project_root}", file=sys.stderr)
        return 1

    missing = [name for name in REQUIRED_FILES if not (project_root / name).exists()]
    if missing:
        print("ERROR: required pipeline files are missing:", file=sys.stderr)
        for name in missing:
            print(f"- {name}", file=sys.stderr)
        print("Use --dry-run only after adding the expected scripts, or run individual available steps manually.", file=sys.stderr)
        return 1

    check_report = Path(__file__).resolve().with_name("check_custom_item_report.py")
    failed = False

    for label, template in PIPELINE:
        command = expand(template, project_root, args.python, check_report, args.replace_all_transferables)
        code = run_step(label, command, project_root, args.dry_run)
        if code != 0:
            failed = True
            print(f"ERROR: step failed with exit code {code}: {label}", file=sys.stderr)
            if not args.continue_on_error:
                return code

    package_bat = project_root / "generar_pack_vroid.bat"
    if not args.skip_package:
        if package_bat.exists():
            if os.name == "nt":
                code = run_step("package final pack", ["cmd", "/c", str(package_bat.name)], project_root, args.dry_run)
                if code != 0:
                    failed = True
                    if not args.continue_on_error:
                        return code
            else:
                print("\n== package final pack ==")
                print("skipped: generar_pack_vroid.bat exists but this is not Windows; run it in cmd.exe or provide a cross-platform pack script")
        else:
            print("\n== package final pack ==")
            print("skipped: generar_pack_vroid.bat not found")

    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
