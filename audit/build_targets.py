#!/usr/bin/env python3
"""Reproduce the exact CSV snapshot and emit immutable audit targets.

The source registry is pinned to the commit used to generate
`github_dsh_plugins_deduplicated.csv`.  The script recreates the CSV with the
same canonicalisation, deduplication and ordering logic, verifies its SHA-256,
and then emits rows 1..2000 (or one fixed-size chunk).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

SOURCE_COMMIT = "4591632cbf97aba66f2b2b81f778f976ab2c3e49"
SOURCE_URL = (
    "https://raw.githubusercontent.com/zp-home/dsh-recommend/"
    f"{SOURCE_COMMIT}/data/registry.json"
)
EXPECTED_SOURCE_COUNT = 7195
EXPECTED_CSV_SHA256 = "5852f4f8aa21582096b445f969609cb68b83fbb8e009c7dab3dfd89266afd5b7"
AUDIT_LIMIT = 2000
CSV_FIELDS = ["name", "url", "description", "star", "fork"]
REPO_RE = re.compile(r"^https://github\.com/([^/]+)/([^/]+?)/?$", re.I)


def canonical_url(value: object) -> str:
    url = str(value or "").strip()
    url = re.sub(r"^http://github\.com/", "https://github.com/", url, flags=re.I)
    url = re.sub(r"\.git/?$", "", url, flags=re.I)
    return url.rstrip("/").lower()


def display_url(value: object) -> str:
    url = str(value or "").strip()
    url = re.sub(r"^http://github\.com/", "https://github.com/", url, flags=re.I)
    url = re.sub(r"\.git/?$", "", url, flags=re.I)
    return url.rstrip("/")


def nonnegative_int(value: object) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError, OverflowError):
        return 0


def fetch_json(url: str, attempts: int = 6) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "dsh-static-audit/1.0",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = response.read()
            parsed = json.loads(payload.decode("utf-8"))
            if not isinstance(parsed, dict):
                raise ValueError("registry root is not an object")
            return parsed
        except Exception as exc:  # noqa: BLE001 - retry boundary
            last_error = exc
            if attempt < attempts:
                time.sleep(min(2**attempt, 20))
    raise RuntimeError(f"failed to fetch pinned registry: {last_error}")


def reproduce_rows(payload: dict[str, Any]) -> list[dict[str, object]]:
    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        raise ValueError("registry does not contain a plugins array")
    if len(plugins) != EXPECTED_SOURCE_COUNT:
        raise ValueError(
            f"pinned registry count changed: expected {EXPECTED_SOURCE_COUNT}, got {len(plugins)}"
        )

    by_url: dict[str, dict[str, object]] = {}
    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue
        name = str(plugin.get("name") or "").strip()
        url = display_url(plugin.get("url"))
        key = canonical_url(url)
        if not name or not key:
            continue
        row: dict[str, object] = {
            "name": name,
            "url": url,
            "description": str(plugin.get("description") or "").strip(),
            "star": nonnegative_int(plugin.get("stars", plugin.get("star", 0))),
            "fork": nonnegative_int(plugin.get("forks", plugin.get("fork", 0))),
        }
        existing = by_url.get(key)
        if existing is None:
            by_url[key] = row
            continue
        existing["star"] = max(int(existing["star"]), int(row["star"]))
        existing["fork"] = max(int(existing["fork"]), int(row["fork"]))
        if len(str(row["description"])) > len(str(existing["description"])):
            existing["description"] = row["description"]
        if len(str(row["name"])) > len(str(existing["name"])):
            existing["name"] = row["name"]

    rows = sorted(
        by_url.values(),
        key=lambda row: (
            -int(row["star"]),
            -int(row["fork"]),
            str(row["name"]).casefold(),
            str(row["url"]).casefold(),
        ),
    )
    if len(rows) != EXPECTED_SOURCE_COUNT:
        raise ValueError(
            f"deduplicated row count mismatch: expected {EXPECTED_SOURCE_COUNT}, got {len(rows)}"
        )
    return rows


def csv_bytes(rows: list[dict[str, object]]) -> bytes:
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return b"\xef\xbb\xbf" + text.getvalue().encode("utf-8")


def repo_full_name(url: str) -> str | None:
    match = REPO_RE.match(url)
    if not match:
        return None
    owner, repo = match.groups()
    repo = re.sub(r"\.git$", "", repo, flags=re.I)
    if not owner or not repo:
        return None
    return f"{owner}/{repo}"


def target_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    targets: list[dict[str, object]] = []
    for index, row in enumerate(rows[:AUDIT_LIMIT], start=1):
        full_name = repo_full_name(str(row["url"]))
        targets.append(
            {
                "row": index,
                **row,
                "repo_full_name": full_name,
                "target_id": f"{index:04d}",
            }
        )
    if len(targets) != AUDIT_LIMIT:
        raise ValueError(f"expected {AUDIT_LIMIT} targets, got {len(targets)}")
    if len({canonical_url(item["url"]) for item in targets}) != AUDIT_LIMIT:
        raise ValueError("target list contains duplicate repository URLs")
    return targets


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="target JSON output path")
    parser.add_argument("--meta-output", help="optional target metadata output path")
    parser.add_argument("--chunk-index", type=int)
    parser.add_argument("--chunk-size", type=int, default=50)
    args = parser.parse_args()

    if args.chunk_index is not None and args.chunk_index < 0:
        parser.error("--chunk-index must be non-negative")
    if args.chunk_size <= 0:
        parser.error("--chunk-size must be positive")

    payload = fetch_json(SOURCE_URL)
    rows = reproduce_rows(payload)
    digest = hashlib.sha256(csv_bytes(rows)).hexdigest()
    if digest != EXPECTED_CSV_SHA256:
        raise RuntimeError(
            "reproduced CSV hash mismatch; refusing to audit a moving or altered target set: "
            f"expected {EXPECTED_CSV_SHA256}, got {digest}"
        )

    targets = target_rows(rows)
    full_manifest_bytes = (
        json.dumps(targets, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    manifest_sha = hashlib.sha256(full_manifest_bytes).hexdigest()

    selected = targets
    chunk_start = 1
    chunk_end = AUDIT_LIMIT
    if args.chunk_index is not None:
        start = args.chunk_index * args.chunk_size
        end = min(start + args.chunk_size, AUDIT_LIMIT)
        selected = targets[start:end]
        chunk_start = start + 1
        chunk_end = end
        if start >= AUDIT_LIMIT:
            raise RuntimeError(f"chunk {args.chunk_index} starts beyond row {AUDIT_LIMIT}")

    write_json(Path(args.output), selected)
    meta = {
        "source_commit": SOURCE_COMMIT,
        "source_url": SOURCE_URL,
        "source_generated_at": payload.get("meta", {}).get("generatedAt"),
        "source_raw_fetched_at": payload.get("meta", {}).get("rawFetchedAt"),
        "reproduced_csv_sha256": digest,
        "expected_csv_sha256": EXPECTED_CSV_SHA256,
        "full_target_manifest_sha256": manifest_sha,
        "audit_rows": [1, AUDIT_LIMIT],
        "selected_rows": [chunk_start, chunk_end],
        "selected_count": len(selected),
        "chunk_index": args.chunk_index,
        "chunk_size": args.chunk_size,
    }
    if args.meta_output:
        write_json(Path(args.meta_output), meta)
    print(json.dumps(meta, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"target builder failed: {exc}", file=sys.stderr)
        raise
