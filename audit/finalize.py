#!/usr/bin/env python3
"""Second-stage review of preliminary DSH findings.

This script never executes repository content.  It retrieves only the exact
source files referenced by preliminary evidence at each repository's pinned
commit, verifies line context, applies conservative intent-aware verdict rules,
and writes the final Chinese Markdown report plus an exact 2,000-row coverage
CSV.  Security/CTF/malware-analysis projects are not labelled malicious solely
because they contain offensive primitives; their findings are retained as risk
where the executable capability remains relevant.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

EXPECTED_ROWS = 2000
MAX_SOURCE_BYTES = 5_000_000
FETCH_WORKERS = 12
RETRIES = 5

SEVERITY = {
    "confirmed_malicious": 5,
    "high_risk": 4,
    "medium_risk": 3,
    "low_risk": 2,
    "no_reportable_risk": 1,
    "unresolved": 0,
}
LABEL = {
    "confirmed_malicious": "确认存在恶意/后门行为",
    "high_risk": "高风险",
    "medium_risk": "中风险",
    "low_risk": "低风险",
    "no_reportable_risk": "未发现可报告风险",
    "unresolved": "未解决（覆盖受限）",
}

STRONG_MALICIOUS_TITLES = {
    "Reverse-shell implementation",
    "Cryptocurrency mining payload",
    "Destructive filesystem behaviour",
    "Credential/secret collection with exfiltration channel",
    "Remote-access persistence through authorized_keys",
    "Defence evasion combined with remote execution",
}
HIGH_RISK_TITLES = {
    "Secret access and outbound transmission coexist",
    "Surveillance capability with outbound channel",
    "Install-time remote download or execution",
    "Remote code dynamically evaluated",
    "Remote download-and-execute path",
    "Persistence combined with remote payload retrieval",
    "Defence-evasion or process-injection capability",
    "Network input reaches shell execution",
}
MEDIUM_RISK_TITLES = {
    "System persistence or startup-file modification",
    "Sensitive credential/wallet data access",
    "Privacy-sensitive capture capability",
    "Unverified transport or update path",
    "Unsafe dynamic or shell execution primitive",
    "Suspicious npm lifecycle hook",
}

OFFENSIVE_CONTEXT_RE = re.compile(
    r"\b(?:security|cybersecurity|audit|auditor|pentest|penetration|red[ -]?team|"
    r"malware|reverse[ -]?shell|exploit|vulnerability|ctf|capture the flag|"
    r"honeypot|sandbox|forensic|incident response|threat|yara|antivirus|"
    r"credential scanner|secret scanner|backdoor detector|research)\b|"
    r"(?:安全|审计|渗透|红队|恶意软件|漏洞|逆向|取证|蜜罐|威胁|检测|研究)",
    re.IGNORECASE,
)
EXPECTED_CAPABILITY_HINTS: dict[str, re.Pattern[str]] = {
    "surveillance": re.compile(
        r"(?:screen|screenshot|clipboard|keyboard|microphone|voice|audio|computer use|"
        r"desktop control|remote desktop|录屏|截图|剪贴板|键盘|麦克风|语音|电脑控制|远程桌面)",
        re.IGNORECASE,
    ),
    "credential_access": re.compile(
        r"(?:credential|secret|token|wallet|password|browser cookie|key manager|"
        r"凭据|密钥|令牌|钱包|密码|浏览器.*cookie)",
        re.IGNORECASE,
    ),
    "command_execution": re.compile(
        r"(?:terminal|shell|command|automation|devops|remote control|executor|"
        r"终端|命令|自动化|运维|远程控制|执行器)",
        re.IGNORECASE,
    ),
    "persistence": re.compile(
        r"(?:startup|service|daemon|autostart|install agent|开机|服务|守护进程|自启动)",
        re.IGNORECASE,
    ),
}

CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SPACE_RE = re.compile(r"\s+")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SOURCE_STATUS_OK = {"scanned", "scanned_no_source_candidates"}
PARTIAL_OR_FAILURE = {
    "scanned_partial",
    "source_read_failed",
    "tree_read_failed",
    "clone_timeout",
    "network_error",
    "clone_failed",
    "unavailable",
    "invalid_repository_url",
    "internal_error",
    "scan_result_missing",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean(value: object, limit: int = 12_000) -> str:
    text = CONTROL_RE.sub("", str(value or ""))
    if len(text) > limit:
        text = text[: limit - 22] + " …[truncated]"
    return text


def md(value: object, limit: int = 3000) -> str:
    return clean(value, limit).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def fenced(value: object) -> str:
    text = clean(value, 20_000).replace("````", "` ` ` `")
    return f"````text\n{text}\n````"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_key(repo: str, commit: str, path: str) -> tuple[str, str, str]:
    return repo, commit, path


def raw_url(repo: str, commit: str, path: str) -> str:
    encoded_path = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    return f"https://raw.githubusercontent.com/{repo}/{commit}/{encoded_path}"


def blob_url(repo: str, commit: str, path: str, start: int, end: int) -> str:
    encoded_path = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    return f"https://github.com/{repo}/blob/{commit}/{encoded_path}#L{start}-L{end}"


def fetch_source(key: tuple[str, str, str]) -> dict[str, Any]:
    repo, commit, path = key
    result: dict[str, Any] = {
        "repo": repo,
        "commit": commit,
        "path": path,
        "ok": False,
        "status": None,
        "error": None,
        "text": None,
        "sha256": None,
        "bytes": 0,
    }
    if not REPO_RE.fullmatch(repo) or not re.fullmatch(r"[0-9a-fA-F]{7,64}", commit or ""):
        result["error"] = "invalid repository or commit"
        return result
    url = raw_url(repo, commit, path)
    last_error = "unknown fetch error"
    for attempt in range(1, RETRIES + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "dsh-static-audit-finalizer/1.0",
                    "Accept": "text/plain, application/octet-stream;q=0.9, */*;q=0.1",
                },
            )
            with urllib.request.urlopen(request, timeout=90) as response:
                status = getattr(response, "status", 200)
                size_header = response.headers.get("Content-Length")
                if size_header and int(size_header) > MAX_SOURCE_BYTES:
                    raise ValueError(f"source file exceeds {MAX_SOURCE_BYTES} byte review cap")
                data = response.read(MAX_SOURCE_BYTES + 1)
            if len(data) > MAX_SOURCE_BYTES:
                raise ValueError(f"source file exceeds {MAX_SOURCE_BYTES} byte review cap")
            if b"\x00" in data[:8192] and not data.startswith((b"\xff\xfe", b"\xfe\xff")):
                raise ValueError("source evidence resolved to a binary file")
            if data.startswith(b"\xff\xfe"):
                text = data.decode("utf-16-le", errors="replace")
            elif data.startswith(b"\xfe\xff"):
                text = data.decode("utf-16-be", errors="replace")
            else:
                text = data.decode("utf-8", errors="replace")
            result.update(
                {
                    "ok": True,
                    "status": status,
                    "text": text,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "bytes": len(data),
                }
            )
            return result
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code in {400, 401, 403, 404, 410}:
                break
        except Exception as exc:  # noqa: BLE001
            last_error = clean(exc, 500)
        if attempt < RETRIES:
            time.sleep(min(2**attempt, 16))
    result["error"] = last_error
    return result


def normalise_match(value: object) -> str:
    return SPACE_RE.sub(" ", clean(value, 2000)).strip().casefold()


def review_evidence(
    evidence: dict[str, Any],
    source: dict[str, Any] | None,
    repo: str,
    commit: str,
) -> dict[str, Any]:
    reviewed = dict(evidence)
    line = max(1, int(evidence.get("line") or 1))
    reviewed["source_retrieved"] = bool(source and source.get("ok"))
    reviewed["source_error"] = None if reviewed["source_retrieved"] else clean((source or {}).get("error"), 500)
    reviewed["verified"] = False
    reviewed["verification"] = "source_unavailable"
    reviewed["review_context"] = clean(evidence.get("snippet"), 12_000)
    reviewed["context_start_line"] = max(1, line - 3)
    reviewed["context_end_line"] = line + 3
    reviewed["source_url"] = blob_url(
        repo,
        commit,
        clean(evidence.get("path"), 1000),
        reviewed["context_start_line"],
        reviewed["context_end_line"],
    )
    if not source or not source.get("ok") or not isinstance(source.get("text"), str):
        return reviewed

    text = source["text"]
    lines = text.splitlines() or [""]
    if line > len(lines):
        reviewed["verification"] = "reported_line_out_of_range"
        return reviewed
    start = max(1, line - 18)
    end = min(len(lines), line + 18)
    rendered = [f"{number:>6} | {clean(lines[number - 1], 900)}" for number in range(start, end + 1)]
    reviewed["review_context"] = "\n".join(rendered)
    reviewed["context_start_line"] = start
    reviewed["context_end_line"] = end
    reviewed["source_url"] = blob_url(repo, commit, clean(evidence.get("path"), 1000), start, end)
    reviewed["source_file_sha256"] = source.get("sha256")

    probe = normalise_match(evidence.get("match"))
    local = normalise_match("\n".join(lines[max(0, line - 8) : min(len(lines), line + 8)]))
    if not probe:
        reviewed["verified"] = True
        reviewed["verification"] = "source_and_line_retrieved"
    else:
        # Scanner matches can span many lines and are truncated to 500 chars.
        # Comparing the first meaningful token sequence is resilient to that
        # truncation while still proving the evidence is present at the commit.
        probe_parts = [part for part in re.split(r"\s+", probe) if len(part) >= 3]
        distinctive = " ".join(probe_parts[:8])
        if probe in local or (distinctive and distinctive in local):
            reviewed["verified"] = True
            reviewed["verification"] = "match_verified_at_pinned_commit"
        else:
            rule_id = clean(evidence.get("rule_id"), 200)
            source_line = normalise_match(lines[line - 1])
            if source_line and (source_line in probe or any(token in source_line for token in probe_parts[:4])):
                reviewed["verified"] = True
                reviewed["verification"] = "reported_source_line_verified"
            elif rule_id == "npm_lifecycle_script" and clean(evidence.get("lifecycle_key"), 50) in lines[line - 1]:
                reviewed["verified"] = True
                reviewed["verification"] = "npm_lifecycle_entry_verified"
            else:
                reviewed["verification"] = "context_retrieved_match_not_reconfirmed"
    return reviewed


def repo_is_offensive_context(item: dict[str, Any]) -> bool:
    haystack = " ".join(
        clean(item.get(field), 5000)
        for field in ("name", "repo_full_name", "description")
    )
    return bool(OFFENSIVE_CONTEXT_RE.search(haystack))


def declared_capability(item: dict[str, Any], categories: set[str]) -> bool:
    description = " ".join(clean(item.get(field), 5000) for field in ("name", "description"))
    for category in categories:
        pattern = EXPECTED_CAPABILITY_HINTS.get(category)
        if pattern and pattern.search(description):
            return True
    return False


def evidence_categories(finding: dict[str, Any]) -> set[str]:
    return {clean(value.get("category"), 100) for value in finding.get("evidence") or []}


def finalise_finding(item: dict[str, Any], finding: dict[str, Any]) -> dict[str, Any] | None:
    title = clean(finding.get("title"), 500)
    reviewed_evidence = finding.get("evidence") or []
    verified = [value for value in reviewed_evidence if value.get("verified")]
    production = [
        value
        for value in reviewed_evidence
        if value.get("path_role") not in {"docs", "test"} and not value.get("comment_only")
    ]
    verified_production = [value for value in verified if value in production]
    preliminary = clean(finding.get("verdict"), 100)
    categories = evidence_categories(finding)
    offensive_context = repo_is_offensive_context(item)
    capability_declared = declared_capability(item, categories)

    if not production:
        return None

    final_verdict: str
    confidence: str
    rationale = clean(finding.get("reason"), 3000)

    if title in STRONG_MALICIOUS_TITLES:
        if verified_production and not offensive_context:
            final_verdict = "confirmed_malicious"
            confidence = "high"
        else:
            final_verdict = "high_risk"
            confidence = "medium" if verified_production else "low"
            if offensive_context:
                rationale += " 仓库描述具有安全研究/审计/CTF语境，因此不单凭攻击原语推断作者恶意意图，但可执行能力仍属高风险。"
            elif not verified_production:
                rationale += " 第二阶段未能重新取回或精确复核全部源码证据，故不升级为确认恶意。"
    elif title in HIGH_RISK_TITLES or preliminary == "high_risk":
        final_verdict = "high_risk" if verified_production else "medium_risk"
        confidence = "high" if verified_production else "low"
    elif title in MEDIUM_RISK_TITLES or preliminary == "medium_risk":
        final_verdict = "medium_risk"
        confidence = "medium" if verified_production else "low"
        if capability_declared:
            rationale += " 该能力与仓库描述的公开功能相符，未发现隐藏意图证据；仍因权限/数据边界敏感而列为风险。"
    else:
        # Low-confidence findings are kept only if the evidence was recovered
        # at the pinned commit, or if independent production signals coexist.
        rule_ids = {clean(value.get("rule_id"), 200) for value in production}
        if verified_production and (len(rule_ids) >= 2 or any(value.get("rule_id") == "npm_lifecycle_script" for value in verified_production)):
            final_verdict = "low_risk"
            confidence = "low"
        else:
            return None

    reviewed = dict(finding)
    reviewed["final_verdict"] = final_verdict
    reviewed["final_confidence"] = confidence
    reviewed["final_reason"] = rationale
    reviewed["offensive_research_context"] = offensive_context
    reviewed["declared_capability"] = capability_declared
    reviewed["verified_evidence_count"] = len(verified_production)
    reviewed["production_evidence_count"] = len(production)
    reviewed["evidence"] = reviewed_evidence
    return reviewed


def highest_verdict(findings: list[dict[str, Any]], status: str) -> str:
    if findings:
        return max((value["final_verdict"] for value in findings), key=lambda value: SEVERITY[value])
    if status in PARTIAL_OR_FAILURE:
        return "unresolved"
    return "no_reportable_risk"


def evidence_sort_key(value: dict[str, Any]) -> tuple[int, int, str, int]:
    return (
        0 if value.get("verified") else 1,
        -int(value.get("effective_weight") or 0),
        clean(value.get("path"), 1000),
        int(value.get("line") or 0),
    )


def dedupe_findings(findings: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, str, tuple[str, ...]]] = set()
    for finding in sorted(
        findings,
        key=lambda value: (-SEVERITY[value["final_verdict"]], clean(value.get("title"), 500)),
    ):
        evidence_ids = tuple(sorted(clean(v.get("evidence_id"), 100) for v in finding.get("evidence") or []))
        key = (finding["final_verdict"], clean(finding.get("title"), 500), evidence_ids)
        if key in seen:
            continue
        seen.add(key)
        output.append(finding)
    return output


def write_coverage(path: Path, rows: list[dict[str, Any]]) -> None:
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
            note_parts = [clean(value, 500) for value in item.get("errors") or []]
            if item.get("status") == "scanned_partial":
                note_parts.append("静态读取受文件数/字节/大文件上限影响")
            writer.writerow(
                {
                    "row": item.get("row"),
                    "name": item.get("name"),
                    "url": item.get("url"),
                    "repo_full_name": item.get("repo_full_name"),
                    "star": item.get("star", 0),
                    "fork": item.get("fork", 0),
                    "scan_status": item.get("status"),
                    "final_verdict": item.get("final_verdict"),
                    "final_finding_count": len(item.get("final_findings") or []),
                    "commit": item.get("commit"),
                    "branch": item.get("branch"),
                    "candidate_files": item.get("candidate_files", 0),
                    "scanned_files": item.get("scanned_files", 0),
                    "scanned_bytes": item.get("scanned_bytes", 0),
                    "skipped_large": item.get("skipped_large", 0),
                    "blob_errors": item.get("blob_errors", 0),
                    "candidate_cap_reached": item.get("candidate_cap_reached", False),
                    "byte_cap_reached": item.get("byte_cap_reached", False),
                    "reviewed_evidence_files": item.get("reviewed_evidence_files", 0),
                    "review_fetch_failures": item.get("review_fetch_failures", 0),
                    "note": "; ".join(part for part in note_parts if part),
                }
            )


def report_repo(item: dict[str, Any]) -> list[str]:
    lines = [
        f"### CSV 第 {int(item['row'])} 行：{md(item.get('repo_full_name') or item.get('name'))}",
        "",
        f"- 仓库：{md(item.get('url'))}",
        f"- 固定提交：`{md(item.get('commit') or '无')}`",
        f"- 最终结论：**{LABEL[item['final_verdict']]}**",
        f"- 扫描覆盖：`{md(item.get('status'))}`；读取 {int(item.get('scanned_files', 0))} 个文件、{int(item.get('scanned_bytes', 0)):,} 字节",
    ]
    if item.get("description"):
        lines.append(f"- 仓库描述：{md(item.get('description'), 1600)}")
    lines.append("")

    for index, finding in enumerate(item.get("final_findings") or [], start=1):
        lines.extend(
            [
                f"#### {index}. {md(finding.get('title'))}",
                "",
                f"- 结论：`{md(finding.get('final_verdict'))}`；置信度：`{md(finding.get('final_confidence'))}`",
                f"- 原因：{md(finding.get('final_reason'), 4000)}",
                f"- 第二阶段源码复核：{int(finding.get('verified_evidence_count', 0))}/{int(finding.get('production_evidence_count', 0))} 条生产证据在固定提交中重新确认。",
                "",
            ]
        )
        evidence_values = sorted(finding.get("evidence") or [], key=evidence_sort_key)
        # Keep every independent rule/path while preventing repeated matches in
        # the same file from exploding the report.
        emitted: set[tuple[str, str]] = set()
        emitted_count = 0
        for evidence in evidence_values:
            key = (clean(evidence.get("path"), 1000), clean(evidence.get("rule_id"), 200))
            if key in emitted:
                continue
            emitted.add(key)
            emitted_count += 1
            verification = clean(evidence.get("verification"), 300)
            line = int(evidence.get("line") or 0)
            lines.extend(
                [
                    f"**证据 {emitted_count}：`{md(evidence.get('path'))}:{line}` — 规则 `{md(evidence.get('rule_id'))}`**",
                    "",
                    f"- 复核状态：`{md(verification)}`",
                    f"- 固定源码：{md(evidence.get('source_url'))}",
                    "",
                    fenced(evidence.get("review_context") or evidence.get("snippet")),
                    "",
                ]
            )
            if emitted_count >= 10:
                break
    return lines


def build_report(rows: list[dict[str, Any]], source_summary: dict[str, Any], review_meta: dict[str, Any]) -> str:
    verdict_counts = Counter(item["final_verdict"] for item in rows)
    status_counts = Counter(item.get("status", "unknown") for item in rows)
    reportable = [item for item in rows if item["final_verdict"] in {"confirmed_malicious", "high_risk", "medium_risk", "low_risk"}]
    unresolved = [item for item in rows if item["final_verdict"] == "unresolved"]
    lines: list[str] = [
        "# DSH 插件源码安全审计报告：CSV 第 1–2000 行",
        "",
        f"> 完成时间：`{now()}`。本报告覆盖 CSV 数据行 1–2000，所有目标均在附录和覆盖 CSV 中逐行记账。",
        "",
        "## 一、结论摘要",
        "",
        "| 最终结论 | 数量 |",
        "|---|---:|",
        f"| 确认存在恶意/后门行为 | {verdict_counts.get('confirmed_malicious', 0)} |",
        f"| 高风险 | {verdict_counts.get('high_risk', 0)} |",
        f"| 中风险 | {verdict_counts.get('medium_risk', 0)} |",
        f"| 低风险 | {verdict_counts.get('low_risk', 0)} |",
        f"| 未发现可报告风险 | {verdict_counts.get('no_reportable_risk', 0)} |",
        f"| 未解决（仓库不可用或读取受限） | {verdict_counts.get('unresolved', 0)} |",
        f"| **总计** | **{len(rows)}** |",
        "",
        "这里的“确认恶意/后门”要求生产或安装路径中出现可复核的强恶意行为链，例如反向 Shell、凭据收集并外传、挖矿、破坏性擦除、远程载荷加持久化、关闭安全控制后执行远程代码。仅有通用 Shell 调用、屏幕/剪贴板能力或外部域名，不会被单独判为恶意。",
        "",
        "## 二、范围、快照与方法",
        "",
        f"- 原 CSV SHA-256：`{md((source_summary.get('target_meta') or {}).get('reproduced_csv_sha256'))}`。",
        f"- 注册表固定提交：`{md((source_summary.get('target_meta') or {}).get('source_commit'))}`。",
        f"- 初筛结果：{int(source_summary.get('received_result_count', 0))}/2000 行；聚合校验错误：{len(source_summary.get('validation_errors') or [])}。",
        f"- 第二阶段请求的唯一证据文件：{review_meta.get('requested_source_files', 0)}；成功读取：{review_meta.get('retrieved_source_files', 0)}；失败：{review_meta.get('failed_source_files', 0)}。",
        "- 审计过程只做浅克隆、Git blob/Raw 文件读取和静态分析；未安装依赖、未运行构建、未导入模块、未执行插件脚本。",
        "- 第一阶段检测反向 Shell、安装期下载执行、凭据/钱包/浏览器数据访问及外传、持久化、挖矿、破坏性行为、键盘/屏幕/剪贴板/麦克风采集、禁用 TLS、安全控制规避、网络输入到 Shell 等。",
        "- 第二阶段按每个仓库扫描时的 commit 重新读取证据文件，扩大上下文并验证行号；安全研究、审计、CTF、恶意软件分析类仓库不会仅因包含攻击原语而被定性为作者恶意，但可执行危险能力仍列入风险。",
        "",
        "## 三、确认存在恶意或后门行为的插件",
        "",
    ]
    malicious = [item for item in reportable if item["final_verdict"] == "confirmed_malicious"]
    if not malicious:
        lines.extend(["在当前静态证据和复核标准下，没有条目达到“确认恶意/后门”的门槛。", ""])
    else:
        for item in malicious:
            lines.extend(report_repo(item))

    for heading, verdict in (
        ("## 四、高风险插件", "high_risk"),
        ("## 五、中风险插件", "medium_risk"),
        ("## 六、低风险插件", "low_risk"),
    ):
        values = [item for item in reportable if item["final_verdict"] == verdict]
        lines.extend([heading, ""])
        if not values:
            lines.extend(["本级别没有条目。", ""])
        else:
            for item in values:
                lines.extend(report_repo(item))

    lines.extend(["## 七、未解决的覆盖缺口", ""])
    if not unresolved:
        lines.extend(["没有仓库因不可用、克隆失败或读取上限而留下未解决结论。", ""])
    else:
        lines.extend(
            [
                "以下仓库已经计入 2000 个目标，但无法据现有静态证据宣称安全。它们可能已删除、改名、网络不可达，或源码规模触发读取上限。",
                "",
                "| CSV 行 | 仓库 | 状态 | 已读文件 | 限制/错误 |",
                "|---:|---|---|---:|---|",
            ]
        )
        for item in unresolved:
            notes = [clean(value, 500) for value in item.get("errors") or []]
            if item.get("candidate_cap_reached"):
                notes.append("候选文件数达到上限")
            if item.get("byte_cap_reached"):
                notes.append("读取字节达到上限")
            if item.get("skipped_large"):
                notes.append(f"跳过超限大文件 {item.get('skipped_large')} 个")
            lines.append(
                f"| {int(item['row'])} | {md(item.get('repo_full_name') or item.get('url'))} | "
                f"`{md(item.get('status'))}` | {int(item.get('scanned_files', 0))} | {md('; '.join(notes))} |"
            )
        lines.append("")

    lines.extend(
        [
            "## 八、完整覆盖清单（2000/2000）",
            "",
            "| CSV 行 | 仓库 | 扫描状态 | 最终结论 | 固定提交 | 已读文件 |",
            "|---:|---|---|---|---|---:|",
        ]
    )
    for item in rows:
        lines.append(
            f"| {int(item['row'])} | {md(item.get('repo_full_name') or item.get('url'))} | "
            f"`{md(item.get('status'))}` | `{md(item.get('final_verdict'))}` | "
            f"`{md((item.get('commit') or '')[:12])}` | {int(item.get('scanned_files', 0))} |"
        )

    lines.extend(
        [
            "",
            "## 九、限制与正确解读",
            "",
            "- “未发现可报告风险”表示在本次固定提交、已读取文件和规则范围内没有形成可报告证据，不等于数学意义上的绝对安全。",
            "- 报告审计的是公开 GitHub 默认分支快照；不覆盖已删除历史、私有分支、恶意发布包与仓库源码不一致、运行期服务器返回不同载荷等供应链情形。",
            "- 静态数据流判断无法完全替代沙箱动态分析。涉及远程更新、外部 API、浏览器/桌面权限、Shell 和敏感数据访问的插件，即使功能公开，也应在隔离环境和最小权限下使用。",
            "- 所有外部内容均按不可信文本处理；报告中的代码块只是证据展示，不应直接执行。",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-results", required=True)
    parser.add_argument("--source-summary", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    all_results_path = Path(args.all_results)
    source_summary_path = Path(args.source_summary)
    rows = json.loads(all_results_path.read_text(encoding="utf-8"))
    source_summary = json.loads(source_summary_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != EXPECTED_ROWS:
        raise RuntimeError(f"expected {EXPECTED_ROWS} scan rows, got {len(rows) if isinstance(rows, list) else 'invalid'}")
    if [int(item.get("row", 0)) for item in rows] != list(range(1, EXPECTED_ROWS + 1)):
        raise RuntimeError("scan rows are not exactly 1..2000 in order")
    if source_summary.get("received_result_count") != EXPECTED_ROWS or source_summary.get("validation_errors"):
        raise RuntimeError("preliminary aggregate did not pass exact coverage validation")

    requests: set[tuple[str, str, str]] = set()
    for item in rows:
        repo = clean(item.get("repo_full_name"), 500)
        commit = clean(item.get("commit"), 100)
        if not repo or not commit:
            continue
        for finding in item.get("findings") or []:
            for evidence in finding.get("evidence") or []:
                path = clean(evidence.get("path"), 1500)
                if path:
                    requests.add(source_key(repo, commit, path))

    fetched: dict[tuple[str, str, str], dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=FETCH_WORKERS) as executor:
        future_map = {executor.submit(fetch_source, key): key for key in sorted(requests)}
        done = 0
        for future in concurrent.futures.as_completed(future_map):
            key = future_map[future]
            try:
                fetched[key] = future.result()
            except Exception as exc:  # noqa: BLE001
                fetched[key] = {
                    "repo": key[0], "commit": key[1], "path": key[2], "ok": False,
                    "error": clean(exc, 500), "text": None, "bytes": 0,
                }
            done += 1
            if done % 50 == 0 or done == len(requests):
                print(f"source review {done}/{len(requests)}", flush=True)

    final_rows: list[dict[str, Any]] = []
    fetch_failure_rows = 0
    for item in rows:
        repo = clean(item.get("repo_full_name"), 500)
        commit = clean(item.get("commit"), 100)
        reviewed_files: set[tuple[str, str, str]] = set()
        failed_files: set[tuple[str, str, str]] = set()
        reviewed_findings: list[dict[str, Any]] = []
        for finding in item.get("findings") or []:
            reviewed_finding = dict(finding)
            reviewed_evidence: list[dict[str, Any]] = []
            for evidence in finding.get("evidence") or []:
                path = clean(evidence.get("path"), 1500)
                key = source_key(repo, commit, path)
                source = fetched.get(key)
                reviewed = review_evidence(evidence, source, repo, commit)
                reviewed_evidence.append(reviewed)
                if source and source.get("ok"):
                    reviewed_files.add(key)
                else:
                    failed_files.add(key)
            reviewed_finding["evidence"] = reviewed_evidence
            final = finalise_finding(item, reviewed_finding)
            if final:
                reviewed_findings.append(final)
        reviewed_findings = dedupe_findings(reviewed_findings)
        enriched = dict(item)
        enriched["final_findings"] = reviewed_findings
        enriched["reviewed_evidence_files"] = len(reviewed_files)
        enriched["review_fetch_failures"] = len(failed_files)
        enriched["final_verdict"] = highest_verdict(reviewed_findings, clean(item.get("status"), 100))
        if failed_files:
            fetch_failure_rows += 1
        final_rows.append(enriched)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "dsh_plugins_security_audit_1_2000_final.md"
    coverage_path = output_dir / "dsh_plugins_security_audit_1_2000_coverage.csv"
    findings_path = output_dir / "dsh_plugins_security_audit_1_2000_findings.json"
    results_path = output_dir / "dsh_plugins_security_audit_1_2000_reviewed_results.json"
    summary_path = output_dir / "dsh_plugins_security_audit_1_2000_summary.json"
    source_review_path = output_dir / "dsh_plugins_security_audit_1_2000_source_review.json"

    review_meta = {
        "requested_source_files": len(requests),
        "retrieved_source_files": sum(1 for value in fetched.values() if value.get("ok")),
        "failed_source_files": sum(1 for value in fetched.values() if not value.get("ok")),
        "rows_with_review_fetch_failure": fetch_failure_rows,
        "generated_at": now(),
    }
    report_path.write_text(build_report(final_rows, source_summary, review_meta), encoding="utf-8")
    write_coverage(coverage_path, final_rows)
    findings = [
        item
        for item in final_rows
        if item["final_verdict"] in {"confirmed_malicious", "high_risk", "medium_risk", "low_risk"}
    ]
    findings_path.write_text(json.dumps(findings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    results_path.write_text(json.dumps(final_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Keep only metadata/errors, never duplicate complete source content into the artifact.
    source_review = {
        "meta": review_meta,
        "files": [
            {key: value for key, value in source.items() if key != "text"}
            for source in sorted(fetched.values(), key=lambda value: (value["repo"], value["commit"], value["path"]))
        ],
    }
    source_review_path.write_text(json.dumps(source_review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    verdict_counts = Counter(item["final_verdict"] for item in final_rows)
    status_counts = Counter(item.get("status", "unknown") for item in final_rows)
    summary = {
        "target_count": len(final_rows),
        "rows": [1, 2000],
        "verdict_counts": dict(verdict_counts),
        "status_counts": dict(status_counts),
        "reportable_repository_count": len(findings),
        "review_meta": review_meta,
        "preliminary_summary_sha256": sha256(source_summary_path),
        "all_results_sha256": sha256(all_results_path),
        "artifacts": {
            path.name: {"size": path.stat().st_size, "sha256": sha256(path)}
            for path in (report_path, coverage_path, findings_path, results_path, source_review_path)
        },
        "generated_at": now(),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Final hard gates: no missing rows, unique URLs, exact coverage CSV.
    if len({clean(item.get("url"), 1000).rstrip("/").casefold() for item in final_rows}) != EXPECTED_ROWS:
        raise RuntimeError("final rows do not contain 2000 unique URLs")
    with coverage_path.open("r", encoding="utf-8-sig", newline="") as handle:
        coverage_rows = list(csv.DictReader(handle))
    if len(coverage_rows) != EXPECTED_ROWS or [int(item["row"]) for item in coverage_rows] != list(range(1, EXPECTED_ROWS + 1)):
        raise RuntimeError("final coverage CSV failed 1..2000 validation")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"finalizer failed: {clean(exc, 1000)}", file=sys.stderr)
        raise
