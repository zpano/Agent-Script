#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--count", type=int, default=2000)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()

    raw = args.registry.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        raise SystemExit("registry does not contain a plugins array")

    by_url: dict[str, dict[str, Any]] = {}
    duplicate_count = 0
    invalid_count = 0
    for plugin in plugins:
        if not isinstance(plugin, dict):
            invalid_count += 1
            continue
        name = str(plugin.get("name") or "").strip()
        url = display_url(plugin.get("url"))
        key = canonical_url(url)
        if not name or not key:
            invalid_count += 1
            continue
        row = {
            "name": name,
            "url": url,
            "description": str(plugin.get("description") or "").strip(),
            "star": nonnegative_int(plugin.get("stars", plugin.get("star", 0))),
            "fork": nonnegative_int(plugin.get("forks", plugin.get("fork", 0))),
        }
        old = by_url.get(key)
        if old is None:
            by_url[key] = row
        else:
            duplicate_count += 1
            old["star"] = max(int(old["star"]), int(row["star"]))
            old["fork"] = max(int(old["fork"]), int(row["fork"]))
            if len(str(row["description"])) > len(str(old["description"])):
                old["description"] = row["description"]
            if len(str(row["name"])) > len(str(old["name"])):
                old["name"] = row["name"]

    rows = sorted(
        by_url.values(),
        key=lambda row: (
            -int(row["star"]),
            -int(row["fork"]),
            str(row["name"]).casefold(),
            str(row["url"]).casefold(),
        ),
    )
    if len(rows) < args.count:
        raise SystemExit(f"only {len(rows)} deduplicated repositories; need {args.count}")

    selected = [{"index": index, **row} for index, row in enumerate(rows[: args.count], start=1)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    serialized = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in selected)
    args.output.write_text(serialized, encoding="utf-8")

    declared = payload.get("meta", {}).get("counts", {}).get("topicRepos")
    manifest = {
        "scope": "CSV data rows 1-2000 (header excluded)",
        "source_url": args.source_url,
        "source_commit": args.source_commit,
        "source_generated_at": payload.get("meta", {}).get("generatedAt"),
        "source_raw_fetched_at": payload.get("meta", {}).get("rawFetchedAt"),
        "source_registry_sha256": hashlib.sha256(raw).hexdigest(),
        "source_declared_count": declared,
        "source_plugins_array_count": len(plugins),
        "deduplicated_count": len(rows),
        "target_count": len(selected),
        "target_jsonl_sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
        "duplicate_input_count": duplicate_count,
        "invalid_input_count": invalid_count,
        "deduplication_key": "canonical GitHub repository URL",
        "sort": "star desc, fork desc, name case-insensitive asc, url case-insensitive asc",
    }
    if declared is not None and int(declared) != len(plugins):
        raise SystemExit(f"declared count {declared} != plugins array count {len(plugins)}")
    if len(rows) != 7195:
        raise SystemExit(f"expected 7195 deduplicated rows for pinned snapshot; got {len(rows)}")
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
