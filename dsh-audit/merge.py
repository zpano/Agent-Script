#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

FINDING_CLASSES = ("SUSPECTED_MALICIOUS", "HIGH_RISK", "MEDIUM_RISK")
INCOMPLETE_CLASSES = ("SOURCE_UNAVAILABLE", "SOURCE_INCOMPLETE", "INCOMPLETE_REVIEW", "PIPELINE_MISSING")
CLASS_ZH = {
    "SUSPECTED_MALICIOUS": "疑似恶意",
    "HIGH_RISK": "高风险",
    "MEDIUM_RISK": "中风险",
    "LOW_REVIEW": "低置信度复核项",
    "NO_HIGH_CONFIDENCE_SIGNAL": "未发现高置信度恶意信号",
    "INCOMPLETE_REVIEW": "审计不完整",
    "SOURCE_UNAVAILABLE": "源码不可获取",
    "SOURCE_INCOMPLETE": "源码处理失败/不完整",
    "PIPELINE_MISSING": "扫描分片缺失",
}
SEVERITY_PREFIX = {"SUSPECTED_MALICIOUS": "M", "HIGH_RISK": "H", "MEDIUM_RISK": "R"}
LANG_BY_EXT = {
    ".py": "python", ".pyw": "python", ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".jsx": "jsx", ".ts": "typescript", ".tsx": "tsx", ".sh": "bash", ".bash": "bash", ".zsh": "bash",
    ".fish": "fish", ".ps1": "powershell", ".psm1": "powershell", ".bat": "bat", ".cmd": "bat",
    ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php", ".java": "java", ".kt": "kotlin",
    ".cs": "csharp", ".c": "c", ".h": "c", ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp",
    ".swift": "swift", ".lua": "lua", ".json": "json", ".json5": "json", ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml", ".xml": "xml", ".html": "html", ".vue": "vue", ".svelte": "svelte",
    ".sol": "solidity", ".move": "move", ".cairo": "cairo",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception as exc:
                raise SystemExit(f"invalid JSONL {path}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise SystemExit(f"non-object JSONL row {path}:{line_number}")
            rows.append(row)
    return rows


def load_targets(path: Path) -> list[dict[str, Any]]:
    rows = load_jsonl(path)
    indexes = [int(row["index"]) for row in rows]
    urls = [str(row["url"]).rstrip("/").casefold() for row in rows]
    if len(rows) != 2000:
        raise SystemExit(f"target count must be 2000, got {len(rows)}")
    if indexes != list(range(1, 2001)):
        raise SystemExit("target indexes are not exactly 1..2000")
    if len(set(urls)) != 2000:
        raise SystemExit("target URLs are not unique")
    return rows


def result_fallback(target: dict[str, Any], classification: str, error: str) -> dict[str, Any]:
    return {
        **target, "fetch_status": "unknown", "scan_status": "not_scanned", "commit_sha": None,
        "classification": classification, "confidence": "low",
        "reasons": [{"code": "PIPELINE_COVERAGE_GAP", "title": "扫描分片未产出结果", "detail": error, "features": []}],
        "evidence": [], "features": [], "unusual_urls": [], "coverage": {}, "error": error, "elapsed_seconds": 0,
    }


def report_header(manifest: dict[str, Any], stats: dict[str, Any], coverage_hash: str) -> str:
    generated = datetime.now(timezone.utc).isoformat()
    class_counts = stats["classification_counts"]
    scan_counts = stats["scan_status_counts"]
    fetch_counts = stats["fetch_status_counts"]
    return f"""# DSH 插件源码安全审计报告：CSV 第 1–2000 项

> **结论口径**：本报告是针对固定源码快照的只读静态审计。`未发现高置信度恶意信号` 不等同于绝对安全；`疑似恶意` 表示代码行为链高度不符合普通插件预期，但最终定性仍应结合作者说明、发布包、运行流量与历史提交复核。

## 1. 范围与完整性

- CSV 范围：数据行 **1–2000**，不含表头。
- 目标仓库数：**{manifest.get('target_count', 2000)}**。
- 目标清单 SHA-256：`{manifest.get('target_jsonl_sha256')}`。
- 清单来源：固定到 `zp-home/dsh-recommend` 提交 `{manifest.get('source_commit')}` 的 `data/registry.json`。
- 原始 Registry SHA-256：`{manifest.get('source_registry_sha256')}`。
- Registry 生成时间：`{manifest.get('source_generated_at')}`。
- 审计报告生成时间：`{generated}`。
- 覆盖清单 SHA-256：`{coverage_hash}`。
- 完整逐项结果见同包中的 `dsh_plugins_1_2000_coverage.csv`，严格包含 2000 行且按 CSV 序号排列。

## 2. 统计结果

| 分类 | 数量 |
|---|---:|
| 疑似恶意 | {class_counts.get('SUSPECTED_MALICIOUS', 0)} |
| 高风险 | {class_counts.get('HIGH_RISK', 0)} |
| 中风险 | {class_counts.get('MEDIUM_RISK', 0)} |
| 低置信度复核项 | {class_counts.get('LOW_REVIEW', 0)} |
| 未发现高置信度恶意信号 | {class_counts.get('NO_HIGH_CONFIDENCE_SIGNAL', 0)} |
| 审计不完整 | {class_counts.get('INCOMPLETE_REVIEW', 0)} |
| 源码不可获取 | {class_counts.get('SOURCE_UNAVAILABLE', 0)} |
| 源码处理失败/分片缺失 | {class_counts.get('SOURCE_INCOMPLETE', 0) + class_counts.get('PIPELINE_MISSING', 0)} |

| 覆盖状态 | 数量 |
|---|---:|
| 源码获取成功 | {fetch_counts.get('ok', 0)} |
| 源码获取失败/超时/未知 | {sum(v for k, v in fetch_counts.items() if k != 'ok')} |
| 完整扫描 | {scan_counts.get('complete', 0)} |
| 部分扫描 | {scan_counts.get('partial', 0)} |
| 未扫描 | {scan_counts.get('not_scanned', 0)} |

## 3. 审计方法

本轮没有运行任何插件、安装脚本或仓库二进制。每个仓库以只读浅克隆获取当时默认分支 HEAD，并记录提交 SHA；随后枚举 Git 树，读取 package/构建清单、安装钩子、CI 工作流、脚本和主流源码文件。扫描重点包括：

- 反向 Shell、远程命令入口、下载后执行与混淆动态执行；
- 安装期 `preinstall/install/postinstall/prepare` 远程载荷执行；
- SSH、云凭据、浏览器登录数据、钱包材料的读取与网络外传组合；
- 键盘、屏幕、剪贴板、摄像头或麦克风采集及外传；
- cron/systemd/launchd/注册表启动项等持久化；
- 关闭 Defender、防火墙、SELinux/AppArmor 等防护；
- 挖矿、破坏性删除、批量加密或勒索行为；
- 高权限 CI 触发面、二进制载荷和未经验证的远程安装链。

单独出现 `child_process`、`subprocess`、`eval`、Webhook 或截图 API 并不会自动判为恶意；分类优先依据**生产路径中的行为组合、安装时机、数据源与网络汇、隐藏性和持久化**。测试、示例和文档中的攻击样例会降低置信度。

## 4. 局限

- 本轮不执行插件，因此无法观察运行时动态下载、服务端下发内容、DNS/流量、时间炸弹或环境触发分支。
- 未对仓库携带的 EXE/DLL/SO/WASM/JAR 做完整反编译；相关仓库会在风险或不完整项中标注。
- 只审计记录的 HEAD，不代表 npm/PyPI/Release 历史版本或已删除提交完全一致。
- 不对所有传递依赖逐包审计；安装脚本和锁文件之外的第三方供应链风险需另行核查。
- 大型仓库受单文件、总文件数和总文本字节上限保护；任何截断都会标记为 `部分扫描/审计不完整`，不会被写成“安全”。

"""


def language_for(path: str) -> str:
    return LANG_BY_EXT.get(PurePosixPath(path).suffix.casefold(), "text")


def render_findings(results: list[dict[str, Any]], classification: str) -> str:
    items = [row for row in results if row.get("classification") == classification]
    section = {"SUSPECTED_MALICIOUS": "5. 疑似恶意插件", "HIGH_RISK": "6. 高风险插件", "MEDIUM_RISK": "7. 中风险插件"}[classification]
    if not items:
        return f"## {section}\n\n本轮没有仓库达到该分类阈值。\n\n"
    prefix = SEVERITY_PREFIX[classification]
    lines = [f"## {section}", ""]
    for ordinal, row in enumerate(items, start=1):
        fid = f"{prefix}-{ordinal:03d}"
        coverage = row.get("coverage") or {}
        lines.extend([
            f"### {fid} · `{row.get('name')}`", "",
            f"- CSV 序号：**{row.get('index')}**",
            f"- 仓库：{row.get('url')}",
            f"- 审计提交：`{row.get('commit_sha') or '无法获取'}`",
            f"- 结论：**{CLASS_ZH.get(classification, classification)}**；置信度 `{row.get('confidence', 'unknown')}`",
            f"- 源码覆盖：`{row.get('scan_status')}`；仓库文件 {coverage.get('total_repository_files', 0)}，候选文本 {coverage.get('candidate_text_files', 0)}，实际扫描 {coverage.get('files_scanned', 0)}，扫描字节 {coverage.get('bytes_scanned', 0)}",
            "", "#### 原因", "",
        ])
        reasons = row.get("reasons") or []
        if reasons:
            for idx, reason in enumerate(reasons, start=1):
                lines.append(f"{idx}. **{reason.get('title')}**（`{reason.get('code')}`）：{reason.get('detail')}")
        else:
            lines.append("1. 扫描器给出风险分类，但未返回结构化原因；需查看原始 findings JSON。")
        lines.extend(["", "#### 证据代码", ""])
        evidence = row.get("evidence") or []
        if not evidence:
            lines.extend(["未能生成可安全展示的源码片段；该项依据组合信号或二进制/覆盖元数据，需直接检查对应提交。", ""])
        for ev_index, ev in enumerate(evidence, start=1):
            path = str(ev.get("path") or "unknown")
            line_start = ev.get("line_start") or ev.get("line") or "?"
            line_end = ev.get("line_end") or line_start
            label = ev.get("label") or ev.get("feature")
            lines.extend([
                f"**证据 {ev_index}：{label}** — `{path}:{line_start}-{line_end}`", "",
                f"```{language_for(path)}", str(ev.get("snippet") or "").replace("```", "` ` `"), "```", "",
            ])
        if row.get("unusual_urls"):
            lines.append("可疑/非常规端点（已截断，需结合源码确认）：")
            for url in row["unusual_urls"][:10]:
                lines.append(f"- `{url}`")
            lines.append("")
        if row.get("error"):
            lines.extend([f"> 覆盖提示：`{row.get('error')}`", ""])
    return "\n".join(lines) + "\n"


def render_incomplete(results: list[dict[str, Any]]) -> str:
    incomplete = [row for row in results if row.get("classification") in INCOMPLETE_CLASSES or row.get("scan_status") in {"partial", "not_scanned"}]
    lines = ["## 8. 源码不可用或审计不完整项", ""]
    if not incomplete:
        return "\n".join(lines + ["全部 2000 个目标均完成了受限静态扫描。", ""])
    lines.extend([
        "这些仓库仍计入 2000 项覆盖，但**不能据此判定安全**。完整字段和误差原因见覆盖 CSV。", "",
        "| CSV 序号 | 仓库 | 分类 | 获取 | 扫描 | 原因 |", "|---:|---|---|---|---|---|",
    ])
    for row in incomplete:
        error = str(row.get("error") or "").replace("|", "\\|").replace("\n", " ")
        if len(error) > 260:
            error = error[:257] + "..."
        lines.append(f"| {row.get('index')} | {row.get('url')} | {CLASS_ZH.get(str(row.get('classification')), row.get('classification'))} | {row.get('fetch_status')} | {row.get('scan_status')} | {error or '文件/字节上限导致部分覆盖'} |")
    return "\n".join(lines + [""])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    targets = load_targets(args.targets)
    target_by_index = {int(row["index"]): row for row in targets}
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result_files = sorted(args.results_root.rglob("*.jsonl"))
    by_index: dict[int, dict[str, Any]] = {}
    duplicate_result_indexes: list[int] = []
    invalid_result_rows = 0
    for result_file in result_files:
        for row in load_jsonl(result_file):
            try:
                index = int(row["index"])
            except Exception:
                invalid_result_rows += 1
                continue
            if index not in target_by_index:
                invalid_result_rows += 1
                continue
            if index in by_index:
                duplicate_result_indexes.append(index)
                old = by_index[index]
                old_score = (old.get("fetch_status") == "ok", old.get("scan_status") == "complete")
                new_score = (row.get("fetch_status") == "ok", row.get("scan_status") == "complete")
                if new_score > old_score:
                    by_index[index] = row
            else:
                by_index[index] = row

    results: list[dict[str, Any]] = []
    missing_indexes: list[int] = []
    for index in range(1, 2001):
        row = by_index.get(index)
        if row is None:
            missing_indexes.append(index)
            row = result_fallback(target_by_index[index], "PIPELINE_MISSING", "对应扫描分片没有产出记录")
        results.append(row)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    coverage_path = args.output_dir / "dsh_plugins_1_2000_coverage.csv"
    fields = [
        "index", "name", "url", "description", "star", "fork", "commit_sha", "fetch_status", "scan_status",
        "classification", "confidence", "total_repository_files", "candidate_text_files", "selected_files",
        "selected_declared_bytes", "files_scanned", "bytes_scanned", "skipped_oversize_files", "omitted_due_cap",
        "missing_blob_files", "binary_payload_count", "features", "reason_codes", "error", "elapsed_seconds",
    ]
    with coverage_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in results:
            coverage = row.get("coverage") or {}
            writer.writerow({
                "index": row.get("index"), "name": row.get("name"), "url": row.get("url"), "description": row.get("description"),
                "star": row.get("star"), "fork": row.get("fork"), "commit_sha": row.get("commit_sha"),
                "fetch_status": row.get("fetch_status"), "scan_status": row.get("scan_status"), "classification": row.get("classification"),
                "confidence": row.get("confidence"), "total_repository_files": coverage.get("total_repository_files"),
                "candidate_text_files": coverage.get("candidate_text_files"), "selected_files": coverage.get("selected_files"),
                "selected_declared_bytes": coverage.get("selected_declared_bytes"), "files_scanned": coverage.get("files_scanned"),
                "bytes_scanned": coverage.get("bytes_scanned"), "skipped_oversize_files": coverage.get("skipped_oversize_files"),
                "omitted_due_cap": coverage.get("omitted_due_cap"), "missing_blob_files": coverage.get("missing_blob_files"),
                "binary_payload_count": coverage.get("binary_payload_count"), "features": ";".join(row.get("features") or []),
                "reason_codes": ";".join(str(reason.get("code")) for reason in (row.get("reasons") or [])),
                "error": row.get("error"), "elapsed_seconds": row.get("elapsed_seconds"),
            })

    class_counts = Counter(str(row.get("classification")) for row in results)
    fetch_counts = Counter(str(row.get("fetch_status")) for row in results)
    scan_counts = Counter(str(row.get("scan_status")) for row in results)
    stats = {
        "target_count": 2000, "result_files": len(result_files), "raw_result_count": len(by_index),
        "missing_indexes": missing_indexes, "duplicate_result_indexes": sorted(set(duplicate_result_indexes)),
        "invalid_result_rows": invalid_result_rows, "classification_counts": dict(sorted(class_counts.items())),
        "fetch_status_counts": dict(sorted(fetch_counts.items())), "scan_status_counts": dict(sorted(scan_counts.items())),
        "finding_count": sum(class_counts.get(c, 0) for c in FINDING_CLASSES),
    }
    findings = [row for row in results if row.get("classification") in FINDING_CLASSES]
    findings_path = args.output_dir / "dsh_plugins_1_2000_findings.json"
    findings_path.write_text(json.dumps({"manifest": manifest, "stats": stats, "findings": findings}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    all_results_path = args.output_dir / "dsh_plugins_1_2000_results.jsonl"
    all_results_path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in results), encoding="utf-8")

    coverage_hash = sha256(coverage_path)
    report = report_header(manifest, stats, coverage_hash)
    report += render_findings(results, "SUSPECTED_MALICIOUS")
    report += render_findings(results, "HIGH_RISK")
    report += render_findings(results, "MEDIUM_RISK")
    report += render_incomplete(results)
    report += """
## 9. 处置建议

- **疑似恶意**：不要安装或运行；先隔离仓库/发布包，核对作者账户与提交历史，撤销可能暴露的令牌，并在沙箱中进行动态网络与文件行为分析。
- **高风险**：安装前逐条确认功能必要性、用户授权、认证边界、下载内容哈希/签名及最小权限；默认不应在主力环境运行。
- **中风险**：重点检查命令参数是否可被模型输出或网络输入控制、Webhook 发送内容、CI 权限以及远程安装链的固定版本与完整性校验。
- **审计不完整**：不得视作通过；应补抓源码、拆分大型仓库，或对二进制和历史发布包做单独审计。

## 10. 文件说明

- `dsh_plugins_1_2000_security_audit.md`：本报告，仅详细展开疑似恶意、高风险和中风险项。
- `dsh_plugins_1_2000_coverage.csv`：2000 个仓库逐项覆盖清单，无省略。
- `dsh_plugins_1_2000_findings.json`：报告发现的机器可读版本。
- `dsh_plugins_1_2000_results.jsonl`：全部 2000 项的结构化原始结果。
- `dsh_plugins_1_2000_manifest.json`：不可变目标清单与输出哈希。

"""
    report_path = args.output_dir / "dsh_plugins_1_2000_security_audit.md"
    report_path.write_text(report, encoding="utf-8")

    final_manifest = {
        **manifest, "generated_at": datetime.now(timezone.utc).isoformat(), "stats": stats,
        "outputs": {
            report_path.name: {"sha256": sha256(report_path), "bytes": report_path.stat().st_size},
            coverage_path.name: {"sha256": sha256(coverage_path), "bytes": coverage_path.stat().st_size},
            findings_path.name: {"sha256": sha256(findings_path), "bytes": findings_path.stat().st_size},
            all_results_path.name: {"sha256": sha256(all_results_path), "bytes": all_results_path.stat().st_size},
        },
    }
    manifest_path = args.output_dir / "dsh_plugins_1_2000_manifest.json"
    manifest_path.write_text(json.dumps(final_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    done_path = args.output_dir / "DONE.json"
    done_path.write_text(json.dumps({"success": True, "generated_at": final_manifest["generated_at"], "target_count": 2000, "coverage_rows": 2000, "stats": stats, "manifest_sha256": sha256(manifest_path)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with coverage_path.open("r", encoding="utf-8-sig", newline="") as handle:
        coverage_rows = list(csv.DictReader(handle))
    if len(coverage_rows) != 2000:
        raise SystemExit(f"coverage CSV has {len(coverage_rows)} rows, expected 2000")
    if [int(row["index"]) for row in coverage_rows] != list(range(1, 2001)):
        raise SystemExit("coverage CSV indexes are not exactly 1..2000")
    if len({row["url"].rstrip("/").casefold() for row in coverage_rows}) != 2000:
        raise SystemExit("coverage CSV contains duplicate URLs")
    if report_path.stat().st_size < 1000:
        raise SystemExit("report unexpectedly small")
    print(json.dumps({"stats": stats, "outputs": final_manifest["outputs"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
