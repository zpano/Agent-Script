#!/usr/bin/env python3
"""Strict postfilter for the reviewed DSH audit report.

The first two stages intentionally favour recall.  This stage removes common
configuration patterns that are not independently risky, especially a plugin
reading its own API key before calling a model provider.  It never creates new
findings; it can only drop or downgrade already reviewed evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import finalize

EXPECTED = 2000
SENSITIVE_STORE_RULES = {
    "ssh_private_key_read",
    "cloud_credentials_read",
    "browser_secret_store_read",
    "wallet_secret_read",
    "bulk_env_collection",
    "history_collection",
}
STRONG_EXFIL_RULES = {
    "discord_webhook",
    "slack_webhook",
    "telegram_bot_api",
    "dns_exfil",
}
GENERIC_API_SECRET_RULES = {"secret_env_collection"}
GENERIC_HTTP_RULES = {"sensitive_http_post", "webhook_post"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_rule_ids(finding: dict[str, Any]) -> set[str]:
    return {str(value.get("rule_id") or "") for value in finding.get("evidence") or []}


def suspicious_endpoint(item: dict[str, Any]) -> bool:
    return any(
        value.get("classification") in {"webhook", "external_ip", "unknown_external"}
        for value in item.get("external_urls") or []
    )


def strict_finding(item: dict[str, Any], finding: dict[str, Any]) -> dict[str, Any] | None:
    title = str(finding.get("title") or "")
    rules = evidence_rule_ids(finding)
    verified = int(finding.get("verified_evidence_count") or 0)

    # Reading a named API key from the environment is ordinary configuration.
    # Without bulk enumeration, a sensitive store, or an outbound exfiltration
    # primitive, it is not a reportable credential-access finding.
    if title == "Sensitive credential/wallet data access" and rules <= GENERIC_API_SECRET_RULES:
        return None

    credential_exfil_titles = {
        "Credential/secret collection with exfiltration channel",
        "Secret access and outbound transmission coexist",
    }
    if title in credential_exfil_titles:
        has_sensitive_store = bool(rules & SENSITIVE_STORE_RULES)
        has_strong_exfil = bool(rules & STRONG_EXFIL_RULES)
        only_generic = rules <= (GENERIC_API_SECRET_RULES | GENERIC_HTTP_RULES | {"npm_lifecycle_script"})
        endpoint = suspicious_endpoint(item)
        if only_generic and not endpoint:
            return None
        if not has_sensitive_store and not has_strong_exfil:
            # A named API key plus an unknown endpoint may be a custom provider.
            # Retain it as a boundary risk, never as confirmed malicious.
            value = dict(finding)
            value["final_verdict"] = "medium_risk"
            value["final_confidence"] = "low" if verified == 0 else "medium"
            value["final_reason"] = (
                str(value.get("final_reason") or "")
                + " 严格复核未发现浏览器/钱包/SSH/云凭据库、批量环境变量或明确 Webhook/DNS 外传证据；"
                  "该项仅保留为自定义外部端点的数据边界风险，不认定为后门。"
            )
            return value

    # A single explicit shell primitive used by an openly declared terminal or
    # automation plugin is a capability risk, but lower than hidden execution.
    if title == "Unsafe dynamic or shell execution primitive" and finding.get("declared_capability"):
        value = dict(finding)
        value["final_verdict"] = "low_risk"
        value["final_confidence"] = "low"
        value["final_reason"] = (
            str(value.get("final_reason") or "")
            + " 仓库公开声明终端/命令/自动化功能，未见网络输入直达 Shell 或远程载荷链；按权限风险保留为低风险。"
        )
        return value

    # Any confirmed-malicious label must retain at least one source-retrieved,
    # verified production evidence item after the second stage.
    if finding.get("final_verdict") == "confirmed_malicious" and verified < 1:
        value = dict(finding)
        value["final_verdict"] = "high_risk"
        value["final_confidence"] = "low"
        value["final_reason"] = str(value.get("final_reason") or "") + " 固定提交证据未能重新确认，因此降为高风险。"
        return value

    return finding


def minimal_row_from_coverage(row: dict[str, str]) -> dict[str, Any]:
    status = row.get("scan_status") or "unknown"
    verdict = row.get("final_verdict") or "no_reportable_risk"
    return {
        "row": int(row["row"]),
        "name": row.get("name") or "",
        "url": row.get("url") or "",
        "repo_full_name": row.get("repo_full_name") or "",
        "star": int(row.get("star") or 0),
        "fork": int(row.get("fork") or 0),
        "status": status,
        "final_verdict": verdict,
        "final_findings": [],
        "commit": row.get("commit") or None,
        "branch": row.get("branch") or None,
        "candidate_files": int(row.get("candidate_files") or 0),
        "scanned_files": int(row.get("scanned_files") or 0),
        "scanned_bytes": int(row.get("scanned_bytes") or 0),
        "skipped_large": int(row.get("skipped_large") or 0),
        "blob_errors": int(row.get("blob_errors") or 0),
        "candidate_cap_reached": str(row.get("candidate_cap_reached") or "").casefold() == "true",
        "byte_cap_reached": str(row.get("byte_cap_reached") or "").casefold() == "true",
        "reviewed_evidence_files": int(row.get("reviewed_evidence_files") or 0),
        "review_fetch_failures": int(row.get("review_fetch_failures") or 0),
        "errors": [row.get("note")] if row.get("note") else [],
    }


def write_strict_coverage(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "row", "name", "url", "repo_full_name", "star", "fork", "scan_status",
        "final_verdict", "final_finding_count", "commit", "branch", "candidate_files",
        "scanned_files", "scanned_bytes", "skipped_large", "blob_errors",
        "candidate_cap_reached", "byte_cap_reached", "reviewed_evidence_files",
        "review_fetch_failures", "note",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for item in rows:
            writer.writerow(
                {
                    "row": item["row"],
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "repo_full_name": item.get("repo_full_name", ""),
                    "star": item.get("star", 0),
                    "fork": item.get("fork", 0),
                    "scan_status": item.get("status", ""),
                    "final_verdict": item.get("final_verdict", ""),
                    "final_finding_count": len(item.get("final_findings") or []),
                    "commit": item.get("commit") or "",
                    "branch": item.get("branch") or "",
                    "candidate_files": item.get("candidate_files", 0),
                    "scanned_files": item.get("scanned_files", 0),
                    "scanned_bytes": item.get("scanned_bytes", 0),
                    "skipped_large": item.get("skipped_large", 0),
                    "blob_errors": item.get("blob_errors", 0),
                    "candidate_cap_reached": item.get("candidate_cap_reached", False),
                    "byte_cap_reached": item.get("byte_cap_reached", False),
                    "reviewed_evidence_files": item.get("reviewed_evidence_files", 0),
                    "review_fetch_failures": item.get("review_fetch_failures", 0),
                    "note": "; ".join(str(value) for value in item.get("errors") or [] if value),
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--findings", required=True)
    parser.add_argument("--coverage", required=True)
    parser.add_argument("--review-summary", required=True)
    parser.add_argument("--source-summary", required=True)
    parser.add_argument("--source-review", required=True)
    parser.add_argument("--rescue-summary", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    findings = json.loads(Path(args.findings).read_text(encoding="utf-8"))
    review_summary = json.loads(Path(args.review_summary).read_text(encoding="utf-8"))
    source_summary = json.loads(Path(args.source_summary).read_text(encoding="utf-8"))
    source_review = json.loads(Path(args.source_review).read_text(encoding="utf-8"))
    rescue_summary = json.loads(Path(args.rescue_summary).read_text(encoding="utf-8"))
    with Path(args.coverage).open("r", encoding="utf-8-sig", newline="") as handle:
        coverage = list(csv.DictReader(handle))
    if len(coverage) != EXPECTED or [int(value["row"]) for value in coverage] != list(range(1, EXPECTED + 1)):
        raise RuntimeError("input coverage is not exactly rows 1..2000")

    by_row: dict[int, dict[str, Any]] = {int(value["row"]): value for value in findings}
    rows: list[dict[str, Any]] = []
    removed_findings = 0
    downgraded_findings = 0
    for raw in coverage:
        row_number = int(raw["row"])
        item = by_row.get(row_number)
        if item is None:
            item = minimal_row_from_coverage(raw)
        else:
            old_findings = item.get("final_findings") or []
            strict: list[dict[str, Any]] = []
            for finding in old_findings:
                value = strict_finding(item, finding)
                if value is None:
                    removed_findings += 1
                    continue
                if value.get("final_verdict") != finding.get("final_verdict"):
                    downgraded_findings += 1
                strict.append(value)
            item["final_findings"] = finalize.dedupe_findings(strict)
            item["final_verdict"] = finalize.highest_verdict(item["final_findings"], str(item.get("status") or ""))
        rows.append(item)

    if len(rows) != EXPECTED or [int(value["row"]) for value in rows] != list(range(1, EXPECTED + 1)):
        raise RuntimeError("strict rows lost exact 1..2000 accounting")
    if len({str(value.get("url", "")).rstrip("/").casefold() for value in rows}) != EXPECTED:
        raise RuntimeError("strict rows do not contain 2000 unique URLs")

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / "dsh_plugins_security_audit_1_2000_final.md"
    coverage_path = output / "dsh_plugins_security_audit_1_2000_coverage.csv"
    findings_path = output / "dsh_plugins_security_audit_1_2000_findings.json"
    summary_path = output / "dsh_plugins_security_audit_1_2000_summary.json"
    source_review_path = output / "dsh_plugins_security_audit_1_2000_source_review.json"
    rescue_path = output / "dsh_plugins_audit_1_2000_rescue_summary.json"

    review_meta = dict((source_review.get("meta") or {}))
    review_meta.update(
        {
            "strict_postfilter_removed_findings": removed_findings,
            "strict_postfilter_downgraded_findings": downgraded_findings,
            "rescue_applied": True,
        }
    )
    report = finalize.build_report(rows, source_summary, review_meta)
    needle = "- 第二阶段按每个仓库扫描时的 commit 重新读取证据文件，扩大上下文并验证行号；安全研究、审计、CTF、恶意软件分析类仓库不会仅因包含攻击原语而被定性为作者恶意，但可执行危险能力仍列入风险。\n"
    addition = (
        needle
        + f"- 扩大上限补救：重扫 {rescue_summary.get('retry_target_count', 0)} 个部分读取/失败/不可用目标，"
          f"取得 {rescue_summary.get('rescue_result_count', 0)} 份结果，替换 {rescue_summary.get('replaced_count', 0)} 份较差首轮结果；"
          f"缺失重扫结果 {rescue_summary.get('missing_rescue_result_count', 0)}。\n"
        + f"- 严格误报抑制：移除 {removed_findings} 条仅由正常 API Key 配置等形成的候选，"
          f"另有 {downgraded_findings} 条因证据链不足而降级。\n"
    )
    report = report.replace(needle, addition, 1)
    report_path.write_text(report, encoding="utf-8")
    write_strict_coverage(coverage_path, rows)
    reportable = [
        value for value in rows
        if value["final_verdict"] in {"confirmed_malicious", "high_risk", "medium_risk", "low_risk"}
    ]
    findings_path.write_text(json.dumps(reportable, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    source_review_path.write_text(json.dumps(source_review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rescue_path.write_text(json.dumps(rescue_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    verdict_counts = Counter(value["final_verdict"] for value in rows)
    status_counts = Counter(str(value.get("status")) for value in rows)
    summary = {
        "target_count": EXPECTED,
        "rows": [1, 2000],
        "verdict_counts": dict(verdict_counts),
        "status_counts": dict(status_counts),
        "reportable_repository_count": len(reportable),
        "strict_postfilter": {
            "removed_findings": removed_findings,
            "downgraded_findings": downgraded_findings,
            "normal_named_api_key_reads_are_not_reportable_alone": True,
        },
        "review_meta": review_meta,
        "rescue_pass": {
            "retry_target_count": rescue_summary.get("retry_target_count", 0),
            "rescue_result_count": rescue_summary.get("rescue_result_count", 0),
            "replaced_count": rescue_summary.get("replaced_count", 0),
            "missing_rescue_result_count": rescue_summary.get("missing_rescue_result_count", 0),
            "validation_errors": rescue_summary.get("validation_errors", []),
            "status_counts_before": rescue_summary.get("status_counts_before", {}),
            "status_counts_after": rescue_summary.get("status_counts_after", {}),
        },
        "upstream_review_summary_sha256": hashlib.sha256(Path(args.review_summary).read_bytes()).hexdigest(),
        "artifacts": {},
        "generated_at": now(),
    }
    for path in (report_path, coverage_path, findings_path, source_review_path, rescue_path):
        summary["artifacts"][path.name] = {"size": path.stat().st_size, "sha256": sha(path)}
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with coverage_path.open("r", encoding="utf-8-sig", newline="") as handle:
        check = list(csv.DictReader(handle))
    if len(check) != EXPECTED or [int(value["row"]) for value in check] != list(range(1, EXPECTED + 1)):
        raise RuntimeError("strict final coverage failed 1..2000 validation")
    if rescue_summary.get("missing_rescue_result_count") != 0 or rescue_summary.get("validation_errors"):
        raise RuntimeError("rescue coverage validation failed")
    if sum(verdict_counts.values()) != EXPECTED:
        raise RuntimeError("strict verdict counts do not sum to 2000")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
