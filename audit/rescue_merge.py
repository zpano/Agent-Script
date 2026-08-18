#!/usr/bin/env python3
"""Merge expanded-limit retry results into the exact 1..2000 audit set."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED = 2000
STATUS_RANK = {
    "scanned": 8,
    "scanned_no_source_candidates": 8,
    "scanned_partial": 7,
    "source_read_failed": 4,
    "tree_read_failed": 3,
    "unavailable": 2,
    "invalid_repository_url": 2,
    "clone_timeout": 1,
    "network_error": 1,
    "clone_failed": 1,
    "internal_error": 0,
    "scan_result_missing": 0,
}
RETRY_STATUSES = {
    "scanned_partial",
    "source_read_failed",
    "tree_read_failed",
    "clone_timeout",
    "network_error",
    "clone_failed",
    "internal_error",
    "scan_result_missing",
    "unavailable",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl_files(root: Path) -> tuple[dict[int, dict[str, Any]], list[str]]:
    values: dict[int, dict[str, Any]] = {}
    errors: list[str] = []
    for path in sorted(root.glob("**/results.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                    row = int(value["row"])
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{path}:{line_number}: {exc}")
                    continue
                if row in values:
                    errors.append(f"duplicate rescue result row {row}")
                    continue
                values[row] = value
    return values, errors


def quality(value: dict[str, Any]) -> tuple[int, int, int, int, int]:
    return (
        STATUS_RANK.get(str(value.get("status")), -1),
        int(value.get("scanned_files") or 0),
        int(value.get("scanned_bytes") or 0),
        -int(value.get("blob_errors") or 0),
        -int(value.get("skipped_large") or 0),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", required=True)
    parser.add_argument("--rescue-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary-output", required=True)
    args = parser.parse_args()

    original = read_json(Path(args.original))
    if not isinstance(original, list) or len(original) != EXPECTED:
        raise RuntimeError("original result set is not exactly 2000 rows")
    if [int(v.get("row", 0)) for v in original] != list(range(1, EXPECTED + 1)):
        raise RuntimeError("original result rows are not exactly 1..2000")

    rescue, errors = read_jsonl_files(Path(args.rescue_dir))
    expected_retry_rows = {
        int(value["row"])
        for value in original
        if str(value.get("status")) in RETRY_STATUSES
    }
    unexpected = sorted(set(rescue) - expected_retry_rows)
    if unexpected:
        errors.append(f"unexpected rescue rows: {unexpected[:50]}")

    merged: list[dict[str, Any]] = []
    replaced: list[int] = []
    retained: list[int] = []
    for old in original:
        row = int(old["row"])
        new = rescue.get(row)
        if new is not None and quality(new) > quality(old):
            # Keep immutable CSV identity even if a remote repository redirects.
            for field in ("row", "target_id", "name", "url", "repo_full_name", "description", "star", "fork"):
                new[field] = old.get(field)
            merged.append(new)
            replaced.append(row)
        else:
            merged.append(old)
            if new is not None:
                retained.append(row)

    if len(merged) != EXPECTED or [int(v["row"]) for v in merged] != list(range(1, EXPECTED + 1)):
        raise RuntimeError("merged rescue set lost exact 1..2000 ordering")
    if len({str(v.get("url", "")).rstrip("/").casefold() for v in merged}) != EXPECTED:
        raise RuntimeError("merged rescue set does not contain 2000 unique URLs")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    missing_rescue_rows = sorted(expected_retry_rows - set(rescue))
    summary = {
        "target_count": EXPECTED,
        "retry_target_count": len(expected_retry_rows),
        "rescue_result_count": len(rescue),
        "replaced_count": len(replaced),
        "replaced_rows": replaced,
        "retained_original_count": len(retained),
        "retained_rows": retained,
        "missing_rescue_result_count": len(missing_rescue_rows),
        "missing_rescue_rows": missing_rescue_rows,
        "validation_errors": errors,
        "status_counts_before": dict(Counter(str(v.get("status")) for v in original)),
        "status_counts_after": dict(Counter(str(v.get("status")) for v in merged)),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "generated_at": now(),
    }
    summary_path = Path(args.summary_output)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    # Missing retry artifacts are a hard failure; an unavailable repository that
    # was actually retried remains a valid, explicitly unresolved result.
    if errors or missing_rescue_rows:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
