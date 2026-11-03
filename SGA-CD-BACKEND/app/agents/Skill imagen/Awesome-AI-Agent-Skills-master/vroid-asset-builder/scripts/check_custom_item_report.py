#!/usr/bin/env python3
"""Validate a VRoid custom item validation report.

The script accepts several report shapes, but the preferred report contains a
numeric top-level field named "failed". It exits with code 0 only when the
number of failed items is exactly zero.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

FAIL_KEYS = ("failed", "failures", "failed_count", "error_count", "errors")
PASS_STATUS = {"ok", "valid", "passed", "pass", "ready", "success", "validated"}
FAIL_STATUS = {"fail", "failed", "invalid", "error", "errors", "broken"}


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    if isinstance(value, list):
        return len(value)
    return None


def find_failed_count(data: Any) -> tuple[int | None, list[str]]:
    """Return a failed count and short details extracted from a flexible report."""
    details: list[str] = []

    if isinstance(data, dict):
        for key in FAIL_KEYS:
            if key in data:
                count = _as_int(data[key])
                if count is not None:
                    return count, details

        for container_key in ("summary", "totals", "result", "validation"):
            if container_key in data:
                count, nested_details = find_failed_count(data[container_key])
                details.extend(nested_details)
                if count is not None:
                    return count, details

        for list_key in ("items", "assets", "results", "checks", "custom_items"):
            value = data.get(list_key)
            if isinstance(value, list):
                failed = 0
                for item in value:
                    is_failed, label = item_failed(item)
                    if is_failed:
                        failed += 1
                        if label:
                            details.append(label)
                return failed, details

    if isinstance(data, list):
        failed = 0
        for item in data:
            is_failed, label = item_failed(item)
            if is_failed:
                failed += 1
                if label:
                    details.append(label)
        return failed, details

    return None, details


def item_failed(item: Any) -> tuple[bool, str | None]:
    if not isinstance(item, dict):
        return False, None

    label = str(item.get("name") or item.get("id") or item.get("path") or item.get("file") or "unnamed item")

    if item.get("valid") is False or item.get("passed") is False or item.get("ok") is False:
        return True, label

    for key in ("status", "result", "state"):
        value = item.get(key)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in FAIL_STATUS:
                return True, label
            if lowered in PASS_STATUS:
                return False, None

    for key in FAIL_KEYS:
        if key in item:
            count = _as_int(item[key])
            if count and count > 0:
                return True, label

    return False, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check validacion_custom_items.json and require failed: 0.")
    parser.add_argument("report", nargs="?", default="validacion_custom_items.json", help="Path to validation report JSON.")
    parser.add_argument("--max-details", type=int, default=20, help="Maximum failed item details to print.")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"ERROR: report not found: {report_path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: could not parse JSON report {report_path}: {exc}", file=sys.stderr)
        return 1

    failed, details = find_failed_count(data)
    if failed is None:
        print("ERROR: could not determine failed count from report.", file=sys.stderr)
        return 1

    print(f"report: {report_path}")
    print(f"failed: {failed}")
    if details:
        print("failed_items:")
        for label in details[: args.max_details]:
            print(f"- {label}")
        if len(details) > args.max_details:
            print(f"- ... {len(details) - args.max_details} more")

    if failed == 0:
        print("status: passed")
        return 0

    print("status: failed")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
