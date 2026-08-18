#!/usr/bin/env python3
"""Validate all 2000 scan results and create preliminary audit artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED_TARGETS = 2000
VERDICT_ORDER = {"malicious": 4, "high_risk": 3, "medium_risk": 2, "low_risk": 1, "no_flag": 0, "unresolved": -1}
VERDICT_LABEL = {
    "malicious": "自动初筛：疑似恶意",
    "high_risk": "自动初筛：高风险",
    "medium_risk": "自动初筛：中风险",
    "low_risk": "自动初筛：低置信风险",
    "no_flag": "未命中报告级规则",
    "unresolved": "未完成判定",
}
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean(value: object, limit: int = 5000) -> str:
    text = CONTROL_RE.sub("", str(value or ""))
    if len(text) > limit:
        text = text[: limit - 20] + " …[truncated]"
    return text


def md(value: object) -> str:
    text = clean(value, 3000)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def code_block(value: object) -> str:
    text = clean(value, 9000).replace("````", "` ` ` `")
    return f"````text\n{text}\n````"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_results(root: Path) -> tuple[dict[int, dict[str, Any]], list[str]]:
    results: dict[int, dict[str, Any]] = {}
    errors: list[str] = []
    files = sorted(root.glob("**/results.jsonl"))
    if not files:
        errors.append("no chunk results.jsonl files were downloaded")
    for path in files:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                    row = int(item["row"])
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{path}:{line_number}: invalid JSON/result: {exc}")
                    continue
                if row in results:
                    errors.append(f"duplicate result for row {row}: {path}")
                    continue
                results[row] = item
    return results, errors


def unresolved_result(target: dict[str, Any], status: str, error: str) -> dict[str, Any]:
    return {
        **target,
        "status": status,
        "preliminary_verdict": "unresolved",
        "commit": None,
        "branch": None,
        "tree_paths": 0,
        "candidate_files": 0,
        "selected_files": 0,
        "scanned_files": 0,
        "scanned_bytes": 0,
        "skipped_binary": 0,
        "skipped_large": 0,
        "blob_errors": 0,
        "candidate_cap_reached": False,
        "byte_cap_reached": False,
        "indicator_cap_reached": False,
        "errors": [error],
        "external_urls": [],
        "indicators": [],
        "findings": [],
    }


def write_coverage(path: Path, ordered: list[dict[str, Any]]) -> None:
    fields = [
        "row",
        "name",
        "url",
        "repo_full_name",
        "star",
        "fork",
        "status",
        "preliminary_verdict",
        "commit",
        "branch",
        "tree_paths",
        "candidate_files",
        "selected_files",
        "scanned_files",
        "scanned_bytes",
        "skipped_binary",
        "skipped_large",
        "blob_errors",
        "candidate_cap_reached",
        "byte_cap_reached",
        "indicator_cap_reached",
        "finding_count",
        "error",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for item in ordered:
            writer.writerow(
                {
                    "row": item.get("row"),
                    "name": item.get("name"),
                    "url": item.get("url"),
                    "repo_full_name": item.get("repo_full_name"),
                    "star": item.get("star", 0),
                    "fork": item.get("fork", 0),
                    "status": item.get("status"),
                    "preliminary_verdict": item.get("preliminary_verdict"),
                    "commit": item.get("commit"),
                    "branch": item.get("branch"),
                    "tree_paths": item.get("tree_paths", 0),
                    "candidate_files": item.get("candidate_files", 0),
                    "selected_files": item.get("selected_files", 0),
                    "scanned_files": item.get("scanned_files", 0),
                    "scanned_bytes": item.get("scanned_bytes", 0),
                    "skipped_binary": item.get("skipped_binary", 0),
                    "skipped_large": item.get("skipped_large", 0),
                    "blob_errors": item.get("blob_errors", 0),
                    "candidate_cap_reached": item.get("candidate_cap_reached", False),
                    "byte_cap_reached": item.get("byte_cap_reached", False),
                    "indicator_cap_reached": item.get("indicator_cap_reached", False),
                    "finding_count": len(item.get("findings") or []),
                    "error": "; ".join(clean(value, 800) for value in (item.get("errors") or [])),
                }
            )


def report_section_for_repo(item: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    verdict = item.get("preliminary_verdict", "unresolved")
    lines.append(f"### CSV 第 {item['row']} 行：{md(item.get('repo_full_name') or item.get('name'))}")
    lines.append("")
    lines.append(
        f"- 仓库：{md(item.get('url'))}\n"
        f"- 初筛级别：**{VERDICT_LABEL.get(verdict, md(verdict))}**\n"
        f"- 扫描状态：`{md(item.get('status'))}`\n"
        f"- 固定提交：`{md(item.get('commit') or '无')}`\n"
        f"- 已读取：{int(item.get('scanned_files', 0))} 个源码/配置文件，"
        f"{int(item.get('scanned_bytes', 0)):,} 字节"
    )
    description = clean(item.get("description"), 1200)
    if description:
        lines.append(f"- CSV 描述：{md(description)}")
    lines.append("")

    for index, finding in enumerate(item.get("findings") or [], start=1):
        lines.append(f"#### {index}. {md(finding.get('title'))}")
        lines.append("")
        lines.append(f"- 判定：`{md(finding.get('verdict'))}`；置信度：`{md(finding.get('confidence'))}`")
        lines.append(f"- 原因：{md(finding.get('reason'))}")
        lines.append("")
        for evidence in finding.get("evidence") or []:
            lines.append(
                f"**证据 `{md(evidence.get('path'))}:{int(evidence.get('line', 0))}` "
                f"（规则 `{md(evidence.get('rule_id'))}`）**"
            )
            lines.append("")
            lines.append(code_block(evidence.get("snippet")))
            lines.append("")

    notable_urls = [
        value
        for value in (item.get("external_urls") or [])
        if value.get("classification") in {"webhook", "external_ip", "unknown_external"}
    ][:8]
    if notable_urls:
        lines.append("**相关外部端点（仅作上下文，不单独构成恶意结论）**")
        lines.append("")
        for value in notable_urls:
            lines.append(
                f"- `{md(value.get('classification'))}` — `{md(value.get('host'))}` — "
                f"`{md(value.get('path'))}`"
            )
        lines.append("")
    return lines


def build_report(
    ordered: list[dict[str, Any]],
    target_meta: dict[str, Any],
    validation_errors: list[str],
) -> str:
    status_counts = Counter(item.get("status", "unknown") for item in ordered)
    verdict_counts = Counter(item.get("preliminary_verdict", "unresolved") for item in ordered)
    flagged = [
        item
        for item in ordered
        if item.get("preliminary_verdict") in {"malicious", "high_risk", "medium_risk", "low_risk"}
    ]
    unresolved = [item for item in ordered if item.get("preliminary_verdict") == "unresolved"]
    partial = [item for item in ordered if item.get("status") == "scanned_partial"]

    lines: list[str] = [
        "# DSH 插件源码安全审计：CSV 第 1–2000 行（自动静态初筛报告）",
        "",
        "> 本文件是第一阶段的只读静态扫描结果，供后续逐项人工复核使用。",
        "> 扫描器没有安装、构建或运行任何插件，也没有执行仓库脚本。",
        "",
        "## 1. 范围与不可变性",
        "",
        f"- CSV 范围：第 1–2000 个数据行，共 **{len(ordered)}** 个目标。",
        f"- 数据源提交：`{md(target_meta.get('source_commit'))}`。",
        f"- 原 CSV SHA-256：`{md(target_meta.get('reproduced_csv_sha256'))}`。",
        f"- 前 2000 行目标清单 SHA-256：`{md(target_meta.get('full_target_manifest_sha256'))}`。",
        f"- 扫描结果生成时间：`{utc_now()}`。",
        "",
        "## 2. 覆盖与初筛统计",
        "",
        "| 项目 | 数量 |",
        "|---|---:|",
        f"| 目标总数 | {len(ordered)} |",
        f"| 完整静态读取（scanned） | {status_counts.get('scanned', 0)} |",
        f"| 部分读取（scanned_partial） | {status_counts.get('scanned_partial', 0)} |",
        f"| 无源码候选 | {status_counts.get('scanned_no_source_candidates', 0)} |",
        f"| 仓库不可用 | {status_counts.get('unavailable', 0)} |",
        f"| 克隆超时/网络/其他失败 | {sum(value for key, value in status_counts.items() if key not in {'scanned', 'scanned_partial', 'scanned_no_source_candidates', 'unavailable'})} |",
        f"| 自动初筛疑似恶意 | {verdict_counts.get('malicious', 0)} |",
        f"| 自动初筛高风险 | {verdict_counts.get('high_risk', 0)} |",
        f"| 自动初筛中风险 | {verdict_counts.get('medium_risk', 0)} |",
        f"| 自动初筛低置信风险 | {verdict_counts.get('low_risk', 0)} |",
        f"| 未命中报告级规则 | {verdict_counts.get('no_flag', 0)} |",
        f"| 尚未完成判定 | {verdict_counts.get('unresolved', 0)} |",
        "",
        "扫描规则覆盖反向 Shell、凭据/钱包/浏览器数据读取与外传、安装期下载执行、远程动态执行、持久化、关闭安全控制、挖矿、破坏性行为、键盘/屏幕/剪贴板采集、网络输入到 Shell、禁用 TLS 校验和无完整性自更新。规则命中只是证据候选，最终结论需要结合完整文件、调用路径和插件声明人工复核。",
        "",
    ]

    for verdict in ("malicious", "high_risk", "medium_risk", "low_risk"):
        repos = [item for item in flagged if item.get("preliminary_verdict") == verdict]
        lines.extend([f"## 3.{VERDICT_ORDER[verdict]} {VERDICT_LABEL[verdict]}（{len(repos)}）", ""])
        if not repos:
            lines.extend(["本级别没有候选项。", ""])
        else:
            for item in repos:
                lines.extend(report_section_for_repo(item))

    lines.extend(["## 4. 未完全读取或无法访问的目标", ""])
    if not partial and not unresolved:
        lines.extend(["没有未解决的覆盖缺口。", ""])
    else:
        lines.extend([
            "这些条目已计入 2000 个目标，但不能据此宣称安全。最终人工报告应重新拉取或扩大读取上限。",
            "",
            "| CSV 行 | 仓库 | 状态 | 已读文件 | 错误/限制 |",
            "|---:|---|---|---:|---|",
        ])
        for item in sorted({value["row"]: value for value in partial + unresolved}.values(), key=lambda value: value["row"]):
            error = "; ".join(clean(value, 500) for value in (item.get("errors") or []))
            limits = []
            if item.get("candidate_cap_reached"):
                limits.append("候选文件上限")
            if item.get("byte_cap_reached"):
                limits.append("读取字节上限")
            if item.get("skipped_large"):
                limits.append(f"大文件跳过 {item.get('skipped_large')}")
            detail = "; ".join(limits + ([error] if error else []))
            lines.append(
                f"| {item['row']} | {md(item.get('repo_full_name') or item.get('url'))} | "
                f"`{md(item.get('status'))}` | {int(item.get('scanned_files', 0))} | {md(detail)} |"
            )
        lines.append("")

    lines.extend([
        "## 5. 全部 2000 个目标的覆盖清单",
        "",
        "| CSV 行 | 仓库 | 扫描状态 | 自动初筛 | 固定提交 | 已读文件 |",
        "|---:|---|---|---|---|---:|",
    ])
    for item in ordered:
        lines.append(
            f"| {item['row']} | {md(item.get('repo_full_name') or item.get('url'))} | "
            f"`{md(item.get('status'))}` | `{md(item.get('preliminary_verdict'))}` | "
            f"`{md((item.get('commit') or '')[:12])}` | {int(item.get('scanned_files', 0))} |"
        )

    lines.extend([
        "",
        "## 6. 方法限制",
        "",
        "- 只审计每个仓库扫描时默认分支的最新浅克隆提交，不覆盖私有分支、已删除历史或发布包与仓库源码不一致的情况。",
        "- 静态规则可发现明确恶意链和危险能力，但不能证明所有无命中仓库绝对安全，也可能把测试样例、管理工具或声明功能误报为风险。",
        "- `scanned_partial`、不可访问、超时和源码读取失败条目必须在最终报告前再次处理。",
        "- 外部域名出现本身不等于外传；报告将其保留为人工判断上下文。",
        "",
    ])
    if validation_errors:
        lines.extend(["## 7. 汇总校验错误", ""])
        for error in validation_errors:
            lines.append(f"- {md(error)}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", required=True)
    parser.add_argument("--target-meta", required=True)
    parser.add_argument("--artifacts-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    targets = read_json(Path(args.targets))
    target_meta = read_json(Path(args.target_meta))
    if not isinstance(targets, list) or len(targets) != EXPECTED_TARGETS:
        raise RuntimeError(f"expected {EXPECTED_TARGETS} targets, got {len(targets) if isinstance(targets, list) else 'invalid'}")
    target_by_row = {int(item["row"]): item for item in targets}
    if set(target_by_row) != set(range(1, EXPECTED_TARGETS + 1)):
        raise RuntimeError("target rows are not exactly 1..2000")

    results, validation_errors = read_results(Path(args.artifacts_dir))
    ordered: list[dict[str, Any]] = []
    for row in range(1, EXPECTED_TARGETS + 1):
        item = results.get(row)
        if item is None:
            validation_errors.append(f"missing scan result for row {row}")
            item = unresolved_result(target_by_row[row], "scan_result_missing", "chunk result missing")
        else:
            # Protect immutable identity fields from scanner/output corruption.
            target = target_by_row[row]
            for field in ("name", "url", "repo_full_name", "description", "star", "fork", "target_id"):
                item[field] = target.get(field)
        ordered.append(item)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    coverage_path = output_dir / "dsh_plugins_audit_1_2000_coverage.csv"
    report_path = output_dir / "dsh_plugins_audit_1_2000_preliminary.md"
    findings_path = output_dir / "dsh_plugins_audit_1_2000_preliminary_findings.json"
    all_results_path = output_dir / "dsh_plugins_audit_1_2000_all_results.json"
    summary_path = output_dir / "dsh_plugins_audit_1_2000_summary.json"

    write_coverage(coverage_path, ordered)
    flagged = [
        item
        for item in ordered
        if item.get("preliminary_verdict") in {"malicious", "high_risk", "medium_risk", "low_risk"}
    ]
    findings_path.write_text(json.dumps(flagged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    all_results_path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(build_report(ordered, target_meta, validation_errors), encoding="utf-8")

    status_counts = Counter(item.get("status", "unknown") for item in ordered)
    verdict_counts = Counter(item.get("preliminary_verdict", "unresolved") for item in ordered)
    summary = {
        "target_count": len(ordered),
        "received_result_count": len(results),
        "status_counts": dict(status_counts),
        "preliminary_verdict_counts": dict(verdict_counts),
        "flagged_repositories": len(flagged),
        "validation_errors": validation_errors,
        "target_meta": target_meta,
        "artifacts": {
            path.name: {
                "size": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in (coverage_path, report_path, findings_path, all_results_path)
        },
        "generated_at": utc_now(),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))

    if validation_errors:
        print("coverage validation failed", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
