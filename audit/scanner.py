#!/usr/bin/env python3
"""Read-only static scanner for public DSH plugin repositories.

Security properties:
- never checks out or executes repository files;
- never runs package managers, build systems, hooks, submodules or LFS smudges;
- shallow partial-clones only GitHub HTTPS repositories;
- reads selected blobs through `git cat-file` with strict byte/time caps;
- accounts for every target, including unavailable and partially scanned repos.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import select
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlsplit

from rules import (
    DOC_PARTS,
    DSH_PATH_KEYWORDS,
    GENERATED_PARTS,
    IMPORTANT_BASENAMES,
    RULES,
    SKIP_DIR_PARTS,
    SOURCE_DIR_PARTS,
    SOURCE_EXTENSIONS,
    TEST_PARTS,
)

SCANNER_VERSION = "2026-08-19.2"
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
URL_RE = re.compile(r"https?://[^\s\"'`<>\]\[(){}]{4,500}", re.IGNORECASE)
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
COMMENT_PREFIXES = ("#", "//", "/*", "*", "<!--", ";", "--")
LIFECYCLE_KEYS = {"preinstall", "install", "postinstall", "prepublish", "prepare"}
SUSPICIOUS_SCRIPT_RE = re.compile(
    r"(?:curl|wget|Invoke-WebRequest|iwr\b|DownloadString|powershell|pwsh|certutil|bitsadmin|"
    r"child_process|\beval\b|\bexec\b|node\s+-e|python\s+-c|bash\s+-c|sh\s+-c|chmod\s+\+x)",
    re.IGNORECASE,
)
URL_INTEGRITY_RE = re.compile(r"(?:sha(?:256|512)|checksum|integrity|sig(?:nature)?|gpg|cosign)", re.IGNORECASE)

ALLOWLIST_SUFFIXES = (
    "github.com",
    "githubusercontent.com",
    "githubassets.com",
    "npmjs.org",
    "npmjs.com",
    "npmmirror.com",
    "jsdelivr.net",
    "unpkg.com",
    "pypi.org",
    "pythonhosted.org",
    "docker.com",
    "docker.io",
    "ghcr.io",
    "deepseek.com",
    "deepseek.ai",
    "openai.com",
    "anthropic.com",
    "googleapis.com",
    "google.com",
    "microsoft.com",
    "azure.com",
    "cloudflare.com",
    "localhost",
)
WEBHOOK_HOSTS = {
    "discord.com",
    "discordapp.com",
    "canary.discord.com",
    "ptb.discord.com",
    "hooks.slack.com",
    "api.telegram.org",
}


class ScanError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize(value: object, limit: int = 4000) -> str:
    text = str(value or "")
    text = ANSI_RE.sub("", text)
    text = CONTROL_RE.sub("", text)
    if len(text) > limit:
        text = text[: limit - 20] + " …[truncated]"
    return text


def safe_error(value: object) -> str:
    text = sanitize(value, 1200)
    # Do not persist accidental credentials embedded in URLs/errors.
    text = re.sub(r"https://[^/@\s]+@github\.com/", "https://github.com/", text, flags=re.I)
    text = re.sub(r"(?i)(token|authorization|password)=([^\s&]+)", r"\1=[redacted]", text)
    return text


def clean_git_env(home: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ASKPASS": "/bin/false",
            "GCM_INTERACTIVE": "Never",
            "GIT_LFS_SKIP_SMUDGE": "1",
            "LC_ALL": "C.UTF-8",
        }
    )
    env.pop("GIT_CONFIG_GLOBAL", None)
    return env


def run_command(
    command: list[str],
    *,
    cwd: Path | None,
    env: dict[str, str],
    timeout: int,
    max_output: int = 2_000_000,
) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if len(completed.stdout) > max_output:
        completed.stdout = completed.stdout[:max_output]
    if len(completed.stderr) > max_output:
        completed.stderr = completed.stderr[:max_output]
    return completed


def git_command(repo: Path, env: dict[str, str], args: list[str], timeout: int = 60) -> bytes:
    command = [
        "git",
        "-c",
        "core.hooksPath=/dev/null",
        "-c",
        "protocol.file.allow=never",
        "-c",
        "filter.lfs.smudge=",
        "-c",
        "filter.lfs.required=false",
        *args,
    ]
    completed = run_command(command, cwd=repo, env=env, timeout=timeout, max_output=40_000_000)
    if completed.returncode != 0:
        raise ScanError(safe_error(completed.stderr.decode("utf-8", errors="replace")))
    return completed.stdout


def clone_repository(full_name: str, destination: Path, env: dict[str, str], timeout: int) -> None:
    if not REPO_RE.fullmatch(full_name):
        raise ScanError("invalid GitHub owner/repository path")
    url = f"https://github.com/{full_name}.git"
    command = [
        "git",
        "-c",
        "core.hooksPath=/dev/null",
        "-c",
        "protocol.file.allow=never",
        "-c",
        "filter.lfs.smudge=",
        "-c",
        "filter.lfs.required=false",
        "-c",
        "http.followRedirects=initial",
        "clone",
        "--quiet",
        "--depth=1",
        "--filter=blob:none",
        "--no-checkout",
        "--single-branch",
        "--no-tags",
        url,
        str(destination),
    ]
    completed = run_command(command, cwd=None, env=env, timeout=timeout, max_output=250_000)
    if completed.returncode != 0:
        message = safe_error(completed.stderr.decode("utf-8", errors="replace"))
        raise ScanError(message or f"git clone exited {completed.returncode}")


def parse_tree(raw: bytes) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            prefix, path_raw = record.split(b"\t", 1)
            parts = prefix.split()
            if len(parts) != 3 or parts[1] != b"blob":
                continue
            oid = parts[2].decode("ascii")
            path = path_raw.decode("utf-8", errors="surrogateescape")
        except Exception:
            continue
        items.append((path, oid))
    return items


def path_parts(path: str) -> tuple[str, ...]:
    return tuple(part.casefold() for part in PurePosixPath(path).parts)


def path_role(path: str) -> str:
    parts = path_parts(path)
    base = parts[-1] if parts else ""
    if base in IMPORTANT_BASENAMES or base == "package.json" or parts[:2] == (".github", "workflows"):
        return "manifest"
    if any(part in TEST_PARTS for part in parts):
        return "test"
    if any(part in DOC_PARTS for part in parts):
        return "docs"
    if any(part in GENERATED_PARTS for part in parts):
        return "generated"
    if any(part in SOURCE_DIR_PARTS for part in parts):
        return "source"
    return "other"


def path_is_candidate(path: str) -> bool:
    parts = path_parts(path)
    if not parts or any(part in SKIP_DIR_PARTS for part in parts[:-1]):
        return False
    if len(path) > 800:
        return False
    base = parts[-1]
    suffix = PurePosixPath(base).suffix.casefold()
    if base in IMPORTANT_BASENAMES or base == "package.json":
        return True
    if len(parts) >= 3 and parts[0] == ".github" and parts[1] == "workflows":
        return suffix in {".yml", ".yaml"}
    return suffix in SOURCE_EXTENSIONS


def candidate_priority(path: str) -> tuple[int, int, str]:
    role = path_role(path)
    lowered = path.casefold()
    dsh_specific = any(keyword in lowered for keyword in DSH_PATH_KEYWORDS)
    base = PurePosixPath(path).name.casefold()
    if role == "manifest":
        level = 0
    elif dsh_specific:
        level = 1
    elif role == "source":
        level = 2
    elif role == "generated":
        level = 3
    elif role == "other":
        level = 4
    elif role == "test":
        level = 6
    else:
        level = 7
    # Installation/entry scripts are favoured inside each class.
    script_bias = 0 if any(token in base for token in ("install", "setup", "bootstrap", "entry", "main", "index")) else 1
    return level, script_bias, lowered


class BlobBatchReader:
    """Read Git blobs without checking out the repository."""

    def __init__(self, repo: Path, env: dict[str, str], object_timeout: int = 40) -> None:
        self.repo = repo
        self.env = env
        self.object_timeout = object_timeout
        self.process: subprocess.Popen[bytes] | None = None
        self._start()

    def _start(self) -> None:
        self.close()
        command = [
            "git",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "protocol.file.allow=never",
            "cat-file",
            "--batch",
        ]
        self.process = subprocess.Popen(
            command,
            cwd=str(self.repo),
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

    def close(self) -> None:
        if self.process is not None:
            try:
                self.process.kill()
            except ProcessLookupError:
                pass
            try:
                self.process.wait(timeout=2)
            except Exception:
                pass
        self.process = None

    def _wait_readable(self) -> None:
        assert self.process is not None and self.process.stdout is not None
        ready, _, _ = select.select([self.process.stdout], [], [], self.object_timeout)
        if not ready:
            raise TimeoutError("timed out reading Git blob")

    def _readline(self) -> bytes:
        self._wait_readable()
        assert self.process is not None and self.process.stdout is not None
        line = self.process.stdout.readline()
        if not line:
            raise EOFError("git cat-file ended unexpectedly")
        return line

    def _read_exact(self, size: int) -> bytes:
        assert self.process is not None and self.process.stdout is not None
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            self._wait_readable()
            chunk = os.read(self.process.stdout.fileno(), min(remaining, 262_144))
            if not chunk:
                raise EOFError("git cat-file ended inside blob")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    def read(self, oid: str, scan_limit: int, hard_limit: int) -> tuple[bytes | None, int, str | None]:
        try:
            assert self.process is not None and self.process.stdin is not None
            self.process.stdin.write(oid.encode("ascii") + b"\n")
            self.process.stdin.flush()
            header = self._readline().strip().split()
            if len(header) == 2 and header[1] == b"missing":
                return None, 0, "missing blob"
            if len(header) != 3 or header[1] != b"blob":
                return None, 0, "unexpected blob header"
            size = int(header[2])
            if size > hard_limit:
                # Killing avoids draining a maliciously huge source-looking blob.
                self._start()
                return None, size, "hard size limit"
            content = self._read_exact(size)
            terminator = self._read_exact(1)
            if terminator != b"\n":
                self._start()
                return None, size, "invalid blob terminator"
            if size > scan_limit:
                return None, size, "scan size limit"
            return content, size, None
        except Exception as exc:  # noqa: BLE001
            self._start()
            return None, 0, safe_error(exc)

    def __enter__(self) -> "BlobBatchReader":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def decode_source(content: bytes) -> str | None:
    sample = content[:8192]
    if b"\x00" in sample and not content.startswith((b"\xff\xfe", b"\xfe\xff")):
        return None
    if content.startswith(b"\xff\xfe"):
        return content.decode("utf-16-le", errors="replace")
    if content.startswith(b"\xfe\xff"):
        return content.decode("utf-16-be", errors="replace")
    return content.decode("utf-8", errors="replace")


def is_comment_only(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith(COMMENT_PREFIXES)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def make_snippet(lines: list[str], hit_line: int, radius: int = 3) -> str:
    start = max(1, hit_line - radius)
    end = min(len(lines), hit_line + radius)
    rendered: list[str] = []
    for number in range(start, end + 1):
        value = sanitize(lines[number - 1], 600)
        rendered.append(f"{number:>6} | {value}")
    return "\n".join(rendered)


def extract_urls(text: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for match in URL_RE.finditer(text):
        value = sanitize(match.group(0).rstrip(".,;:"), 500)
        if value not in seen:
            seen.add(value)
            values.append(value)
        if len(values) >= 80:
            break
    return values


def hostname(url: str) -> str | None:
    try:
        value = (urlsplit(url).hostname or "").casefold().rstrip(".")
        return value or None
    except Exception:
        return None


def is_allowlisted_host(host: str | None) -> bool:
    if not host:
        return False
    if host in {"127.0.0.1", "0.0.0.0", "::1"}:
        return True
    return any(host == suffix or host.endswith("." + suffix) for suffix in ALLOWLIST_SUFFIXES)


def is_ip_literal(host: str | None) -> bool:
    if not host:
        return False
    return bool(re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host) or ":" in host)


def context_multiplier(role: str, comment_only: bool) -> float:
    multipliers = {
        "manifest": 1.20,
        "source": 1.00,
        "generated": 0.90,
        "other": 0.85,
        "test": 0.25,
        "docs": 0.10,
    }
    value = multipliers.get(role, 0.80)
    if comment_only:
        value *= 0.25
    return value


def evidence_id(row: int, path: str, rule_id: str, line: int, ordinal: int) -> str:
    seed = f"{row}\0{path}\0{rule_id}\0{line}\0{ordinal}".encode("utf-8", errors="replace")
    return hashlib.sha256(seed).hexdigest()[:16]


def scan_text(row: int, path: str, text: str) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    role = path_role(path)
    lines = text.splitlines() or [""]
    indicators: list[dict[str, Any]] = []
    lifecycle: list[dict[str, Any]] = []
    urls = extract_urls(text)

    for rule in RULES:
        hits = 0
        for match in rule.pattern.finditer(text):
            hit_line = line_number(text, match.start())
            source_line = lines[hit_line - 1] if hit_line <= len(lines) else ""
            comment = is_comment_only(source_line)
            multiplier = context_multiplier(role, comment)
            effective_weight = round(rule.base_weight * multiplier)
            if effective_weight < 8:
                continue
            hits += 1
            indicator = {
                "evidence_id": evidence_id(row, path, rule.rule_id, hit_line, hits),
                "rule_id": rule.rule_id,
                "title": rule.title,
                "category": rule.category,
                "base_weight": rule.base_weight,
                "effective_weight": effective_weight,
                "path": sanitize(path, 900),
                "path_role": role,
                "line": hit_line,
                "comment_only": comment,
                "match": sanitize(match.group(0), 500),
                "snippet": make_snippet(lines, hit_line),
            }
            indicators.append(indicator)
            if hits >= rule.max_hits_per_file:
                break

    # Parse npm lifecycle scripts explicitly; JSON regex matches alone cannot
    # reliably distinguish a harmless metadata string from an install hook.
    if PurePosixPath(path).name.casefold() == "package.json":
        try:
            package = json.loads(text)
        except Exception:
            package = None
        if isinstance(package, dict) and isinstance(package.get("scripts"), dict):
            scripts = package["scripts"]
            for key in sorted(LIFECYCLE_KEYS):
                value = scripts.get(key)
                if not isinstance(value, str) or not value.strip():
                    continue
                location = next(
                    (index for index, line in enumerate(lines, 1) if f'"{key}"' in line),
                    1,
                )
                suspicious = bool(SUSPICIOUS_SCRIPT_RE.search(value))
                item = {
                    "evidence_id": evidence_id(row, path, f"npm_{key}", location, 1),
                    "rule_id": "npm_lifecycle_script",
                    "title": f"npm lifecycle script: {key}",
                    "category": "supply_chain",
                    "base_weight": 42 if suspicious else 18,
                    "effective_weight": 50 if suspicious else 20,
                    "path": sanitize(path, 900),
                    "path_role": "manifest",
                    "line": location,
                    "comment_only": False,
                    "match": sanitize(value, 500),
                    "snippet": make_snippet(lines, location),
                    "lifecycle_key": key,
                    "suspicious_command": suspicious,
                }
                lifecycle.append(item)
                indicators.append(item)

    return indicators, urls, lifecycle


def production_indicators(indicators: list[dict[str, Any]], minimum_weight: int = 1) -> list[dict[str, Any]]:
    return [
        item
        for item in indicators
        if item.get("path_role") not in {"docs", "test"}
        and not item.get("comment_only")
        and int(item.get("effective_weight", 0)) >= minimum_weight
    ]


def ids(items: Iterable[dict[str, Any]]) -> set[str]:
    return {str(item.get("rule_id")) for item in items}


def categories(items: Iterable[dict[str, Any]]) -> set[str]:
    return {str(item.get("category")) for item in items}


def select_evidence(
    indicators: list[dict[str, Any]],
    *,
    rule_ids: set[str] | None = None,
    category_names: set[str] | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in sorted(indicators, key=lambda value: -int(value.get("effective_weight", 0))):
        if rule_ids and str(item.get("rule_id")) not in rule_ids:
            if not category_names or str(item.get("category")) not in category_names:
                continue
        elif category_names and not rule_ids and str(item.get("category")) not in category_names:
            continue
        key = str(item.get("evidence_id"))
        if key in seen:
            continue
        seen.add(key)
        chosen.append(item)
        if len(chosen) >= limit:
            break
    return chosen


def add_finding(
    findings: list[dict[str, Any]],
    verdict: str,
    confidence: str,
    title: str,
    reason: str,
    evidence: list[dict[str, Any]],
) -> None:
    if not evidence:
        return
    signature = (verdict, title, tuple(item["evidence_id"] for item in evidence))
    for existing in findings:
        existing_signature = (
            existing["verdict"],
            existing["title"],
            tuple(item["evidence_id"] for item in existing["evidence"]),
        )
        if existing_signature == signature:
            return
    findings.append(
        {
            "verdict": verdict,
            "confidence": confidence,
            "title": title,
            "reason": reason,
            "evidence": evidence,
        }
    )


def evaluate_repository(
    indicators: list[dict[str, Any]],
    external_urls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    prod = production_indicators(indicators)
    prod_ids = ids(prod)
    prod_categories = categories(prod)
    findings: list[dict[str, Any]] = []
    suspicious_external = [
        item
        for item in external_urls
        if item.get("classification") in {"webhook", "external_ip", "unknown_external"}
    ]
    webhook_present = any(item.get("classification") == "webhook" for item in external_urls)

    reverse_ids = {
        "reverse_shell_dev_tcp",
        "reverse_shell_netcat",
        "reverse_shell_python",
        "reverse_shell_powershell",
        "reverse_shell_perl_ruby_php",
    }
    direct_reverse = prod_ids & reverse_ids
    if direct_reverse:
        add_finding(
            findings,
            "malicious",
            "high",
            "Reverse-shell implementation",
            "Production or install-time code contains a complete reverse-shell idiom that opens remote command execution.",
            select_evidence(prod, rule_ids=direct_reverse, limit=6),
        )

    if "crypto_miner" in prod_ids:
        add_finding(
            findings,
            "malicious",
            "high",
            "Cryptocurrency mining payload",
            "Executable code or configuration invokes a miner or mining-pool protocol; this is unrelated to normal DSH plugin operation.",
            select_evidence(prod, rule_ids={"crypto_miner"}, limit=6),
        )

    destructive_ids = prod_ids & {"destructive_wipe", "ransom_encrypt_delete"}
    if destructive_ids:
        add_finding(
            findings,
            "malicious",
            "high",
            "Destructive filesystem behaviour",
            "Production code contains disk/filesystem wiping or mass encryption/deletion logic with destructive impact.",
            select_evidence(prod, rule_ids=destructive_ids, limit=8),
        )

    credential_ids = {
        "ssh_private_key_read",
        "cloud_credentials_read",
        "browser_secret_store_read",
        "wallet_secret_read",
        "secret_env_collection",
        "bulk_env_collection",
        "history_collection",
    }
    exfil_ids = {
        "discord_webhook",
        "slack_webhook",
        "telegram_bot_api",
        "webhook_post",
        "sensitive_http_post",
        "dns_exfil",
    }
    credential_hits = prod_ids & credential_ids
    exfil_hits = prod_ids & exfil_ids
    same_file_chain = False
    if credential_hits and exfil_hits:
        credential_files = {item["path"] for item in prod if item["rule_id"] in credential_hits}
        exfil_files = {item["path"] for item in prod if item["rule_id"] in exfil_hits}
        same_file_chain = bool(credential_files & exfil_files)
    if credential_hits and exfil_hits and (same_file_chain or webhook_present):
        add_finding(
            findings,
            "malicious",
            "high" if same_file_chain else "medium",
            "Credential/secret collection with exfiltration channel",
            "The repository combines access to credentials, wallet/browser secrets or bulk secret-bearing environment data with an outbound upload/webhook mechanism.",
            select_evidence(prod, rule_ids=credential_hits | exfil_hits, limit=10),
        )
    elif credential_hits and exfil_hits:
        add_finding(
            findings,
            "high_risk",
            "medium",
            "Secret access and outbound transmission coexist",
            "Sensitive-data collection and an outbound transmission mechanism are both present, but the static scan could not prove a same-file data-flow chain.",
            select_evidence(prod, rule_ids=credential_hits | exfil_hits, limit=10),
        )

    surveillance_ids = prod_ids & {"keyboard_capture", "screen_capture", "clipboard_capture", "microphone_capture"}
    if surveillance_ids and (exfil_hits or suspicious_external):
        add_finding(
            findings,
            "high_risk",
            "high" if webhook_present else "medium",
            "Surveillance capability with outbound channel",
            "Keyboard, screen, clipboard or microphone capture is combined with an external communication channel and can expose user data.",
            select_evidence(prod, rule_ids=surveillance_ids | exfil_hits, limit=10),
        )

    lifecycle = [item for item in prod if item.get("rule_id") == "npm_lifecycle_script"]
    dangerous_remote = prod_ids & {
        "download_pipe_shell",
        "powershell_download_exec",
        "certutil_bitsadmin_exec",
        "download_then_execute",
        "remote_dynamic_eval",
        "encoded_dynamic_exec",
    }
    lifecycle_files = {item["path"] for item in lifecycle if item.get("suspicious_command")}
    remote_files = {item["path"] for item in prod if item["rule_id"] in dangerous_remote}
    if lifecycle_files and dangerous_remote and (lifecycle_files & remote_files or any(item.get("path_role") == "manifest" for item in prod if item["rule_id"] in dangerous_remote)):
        add_finding(
            findings,
            "high_risk",
            "high",
            "Install-time remote download or execution",
            "An npm lifecycle hook invokes download, shell, encoded or dynamic execution logic, so code can run automatically during installation.",
            select_evidence(prod, rule_ids=dangerous_remote | {"npm_lifecycle_script"}, limit=10),
        )
    elif "remote_dynamic_eval" in prod_ids:
        add_finding(
            findings,
            "high_risk",
            "high",
            "Remote code dynamically evaluated",
            "A network response is passed to eval/exec/Function/PowerShell IEX, bypassing normal source review and update integrity.",
            select_evidence(prod, rule_ids={"remote_dynamic_eval"}, limit=8),
        )
    elif dangerous_remote:
        add_finding(
            findings,
            "high_risk",
            "medium",
            "Remote download-and-execute path",
            "Production code downloads content and executes it, or evaluates an encoded payload; integrity and provenance require manual verification.",
            select_evidence(prod, rule_ids=dangerous_remote, limit=10),
        )

    persistence_ids = prod_ids & {
        "authorized_keys_write",
        "cron_persistence",
        "systemd_persistence",
        "launch_agent_persistence",
        "windows_run_key",
        "shell_profile_modify",
    }
    if "authorized_keys_write" in persistence_ids and (dangerous_remote or suspicious_external):
        add_finding(
            findings,
            "malicious",
            "high",
            "Remote-access persistence through authorized_keys",
            "Code modifies SSH authorized_keys while also obtaining remote content or contacting an external endpoint, enabling durable unauthorized access.",
            select_evidence(prod, rule_ids=persistence_ids | dangerous_remote, limit=10),
        )
    elif persistence_ids and dangerous_remote:
        add_finding(
            findings,
            "high_risk",
            "high",
            "Persistence combined with remote payload retrieval",
            "The plugin installs startup persistence and also downloads or dynamically executes remote content.",
            select_evidence(prod, rule_ids=persistence_ids | dangerous_remote, limit=10),
        )
    elif persistence_ids:
        add_finding(
            findings,
            "medium_risk",
            "medium",
            "System persistence or startup-file modification",
            "The repository modifies startup services, scheduled tasks, shell profiles or SSH authorization and therefore has persistence capability.",
            select_evidence(prod, rule_ids=persistence_ids, limit=8),
        )

    defense_ids = prod_ids & {"disable_security_controls", "kill_security_process", "process_injection"}
    if defense_ids and dangerous_remote:
        add_finding(
            findings,
            "malicious",
            "high",
            "Defence evasion combined with remote execution",
            "The code disables or evades host protections and also retrieves/executes remote code, a strong malicious chain.",
            select_evidence(prod, rule_ids=defense_ids | dangerous_remote, limit=10),
        )
    elif defense_ids:
        add_finding(
            findings,
            "high_risk",
            "high",
            "Defence-evasion or process-injection capability",
            "The repository disables host security controls, terminates monitoring tools, or manipulates another process.",
            select_evidence(prod, rule_ids=defense_ids, limit=8),
        )

    command_injection_ids = prod_ids & {"http_input_to_shell_js", "websocket_input_to_shell"}
    if command_injection_ids:
        add_finding(
            findings,
            "high_risk",
            "high",
            "Network input reaches shell execution",
            "HTTP/WebSocket request data is passed to an operating-system command primitive, potentially exposing an unauthenticated remote command channel.",
            select_evidence(prod, rule_ids=command_injection_ids, limit=8),
        )

    if credential_hits and not exfil_hits:
        add_finding(
            findings,
            "medium_risk",
            "medium",
            "Sensitive credential/wallet data access",
            "Production code reads credential stores, browser secrets, wallet material, shell history or secret-bearing environment variables; the intended data boundary needs review.",
            select_evidence(prod, rule_ids=credential_hits, limit=8),
        )

    if surveillance_ids and not (exfil_hits or suspicious_external):
        add_finding(
            findings,
            "medium_risk",
            "medium",
            "Privacy-sensitive capture capability",
            "The plugin can capture keyboard, screen, clipboard or microphone data. No exfiltration chain was proven, but the capability is privacy-sensitive.",
            select_evidence(prod, rule_ids=surveillance_ids, limit=8),
        )

    transport_ids = prod_ids & {"tls_verification_disabled", "unsigned_self_update"}
    if transport_ids:
        add_finding(
            findings,
            "medium_risk",
            "medium",
            "Unverified transport or update path",
            "TLS verification is disabled or a self-update path downloads/replaces executable content without a visible signature/checksum gate.",
            select_evidence(prod, rule_ids=transport_ids, limit=8),
        )

    generic_exec_ids = prod_ids & {"python_shell_true", "generic_shell_spawn", "encoded_dynamic_exec", "python_pickle_untrusted"}
    if generic_exec_ids and not dangerous_remote and not command_injection_ids:
        add_finding(
            findings,
            "medium_risk",
            "low",
            "Unsafe dynamic or shell execution primitive",
            "Production code uses shell=True, explicit shell spawning, encoded evaluation or potentially untrusted deserialization. Static evidence does not by itself prove exploitation.",
            select_evidence(prod, rule_ids=generic_exec_ids, limit=8),
        )

    suspicious_lifecycle = [item for item in lifecycle if item.get("suspicious_command")]
    if suspicious_lifecycle and not dangerous_remote:
        add_finding(
            findings,
            "medium_risk",
            "medium",
            "Suspicious npm lifecycle hook",
            "A preinstall/install/postinstall/prepare hook invokes shell, downloader or dynamic-execution tooling and runs automatically during package installation.",
            suspicious_lifecycle[:8],
        )

    # Deduplicate overlapping findings: a malicious finding subsumes lower-risk
    # findings carrying the same evidence/category chain.
    severity_rank = {"malicious": 4, "high_risk": 3, "medium_risk": 2, "low_risk": 1}
    findings.sort(key=lambda item: (-severity_rank[item["verdict"]], item["title"]))
    kept: list[dict[str, Any]] = []
    covered_evidence: set[str] = set()
    for finding in findings:
        evidence_set = {item["evidence_id"] for item in finding["evidence"]}
        if evidence_set and evidence_set <= covered_evidence and kept:
            continue
        kept.append(finding)
        covered_evidence.update(evidence_set)
    return kept[:8]


def overall_verdict(findings: list[dict[str, Any]]) -> str:
    order = {"malicious": 4, "high_risk": 3, "medium_risk": 2, "low_risk": 1, "no_flag": 0}
    if not findings:
        return "no_flag"
    return max((item["verdict"] for item in findings), key=lambda value: order[value])


def classify_external_urls(urls_by_path: dict[str, list[str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for path, urls in urls_by_path.items():
        for url in urls:
            host = hostname(url)
            key = (path, url)
            if key in seen:
                continue
            seen.add(key)
            if host in WEBHOOK_HOSTS:
                classification = "webhook"
            elif is_ip_literal(host) and host not in {"127.0.0.1", "0.0.0.0", "::1"}:
                classification = "external_ip"
            elif is_allowlisted_host(host):
                classification = "allowlisted"
            elif host:
                classification = "unknown_external"
            else:
                classification = "invalid"
            output.append(
                {
                    "path": sanitize(path, 900),
                    "url": sanitize(url, 500),
                    "host": sanitize(host or "", 300),
                    "classification": classification,
                }
            )
            if len(output) >= 160:
                return output
    return output


def classify_clone_failure(message: str) -> str:
    lowered = message.casefold()
    if any(token in lowered for token in ("repository not found", "not found", "404", "does not exist")):
        return "unavailable"
    if "timed out" in lowered or "timeout" in lowered:
        return "clone_timeout"
    if any(token in lowered for token in ("could not resolve host", "connection reset", "failed to connect", "http 5")):
        return "network_error"
    return "clone_failed"


def scan_target(
    target: dict[str, Any],
    *,
    clone_timeout: int,
    max_files: int,
    max_total_bytes: int,
    max_file_bytes: int,
    hard_file_bytes: int,
) -> dict[str, Any]:
    started = time.monotonic()
    row = int(target.get("row", 0))
    full_name = target.get("repo_full_name")
    base: dict[str, Any] = {
        "scanner_version": SCANNER_VERSION,
        "row": row,
        "target_id": target.get("target_id"),
        "name": sanitize(target.get("name"), 500),
        "url": sanitize(target.get("url"), 900),
        "repo_full_name": sanitize(full_name, 500) if full_name else None,
        "description": sanitize(target.get("description"), 2000),
        "star": int(target.get("star", 0)),
        "fork": int(target.get("fork", 0)),
        "status": "internal_error",
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
        "errors": [],
        "external_urls": [],
        "indicators": [],
        "findings": [],
        "preliminary_verdict": "unresolved",
        "started_at": utc_now(),
        "finished_at": None,
        "elapsed_seconds": None,
    }
    if not isinstance(full_name, str) or not REPO_RE.fullmatch(full_name):
        base["status"] = "invalid_repository_url"
        base["errors"] = ["CSV URL could not be converted to owner/repository"]
        base["finished_at"] = utc_now()
        base["elapsed_seconds"] = round(time.monotonic() - started, 3)
        return base

    with tempfile.TemporaryDirectory(prefix=f"dsh-audit-{row:04d}-") as temporary:
        root = Path(temporary)
        home = root / "home"
        home.mkdir()
        env = clean_git_env(home)
        repo = root / "repo"
        try:
            clone_repository(full_name, repo, env, clone_timeout)
        except subprocess.TimeoutExpired:
            base["status"] = "clone_timeout"
            base["errors"] = [f"clone exceeded {clone_timeout} seconds"]
            base["finished_at"] = utc_now()
            base["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return base
        except Exception as exc:  # noqa: BLE001
            message = safe_error(exc)
            base["status"] = classify_clone_failure(message)
            base["errors"] = [message]
            base["finished_at"] = utc_now()
            base["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return base

        try:
            base["commit"] = git_command(repo, env, ["rev-parse", "HEAD"], 20).decode("ascii").strip()
            try:
                base["branch"] = sanitize(
                    git_command(repo, env, ["symbolic-ref", "--short", "HEAD"], 20)
                    .decode("utf-8", errors="replace")
                    .strip(),
                    300,
                )
            except Exception:
                base["branch"] = None
            tree = parse_tree(git_command(repo, env, ["ls-tree", "-r", "-z", "--full-tree", "HEAD"], 90))
        except Exception as exc:  # noqa: BLE001
            base["status"] = "tree_read_failed"
            base["errors"] = [safe_error(exc)]
            base["finished_at"] = utc_now()
            base["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return base

        base["tree_paths"] = len(tree)
        candidates = [(path, oid) for path, oid in tree if path_is_candidate(path)]
        candidates.sort(key=lambda pair: candidate_priority(pair[0]))
        base["candidate_files"] = len(candidates)
        if len(candidates) > max_files:
            base["candidate_cap_reached"] = True
            candidates = candidates[:max_files]
        base["selected_files"] = len(candidates)

        all_indicators: list[dict[str, Any]] = []
        urls_by_path: dict[str, list[str]] = {}
        indicator_limit = 240
        scanned_bytes = 0
        with BlobBatchReader(repo, env) as reader:
            for path, oid in candidates:
                if scanned_bytes >= max_total_bytes:
                    base["byte_cap_reached"] = True
                    break
                content, declared_size, error = reader.read(oid, max_file_bytes, hard_file_bytes)
                if error:
                    if "size limit" in error:
                        base["skipped_large"] += 1
                    else:
                        base["blob_errors"] += 1
                    continue
                if content is None:
                    continue
                text = decode_source(content)
                if text is None:
                    base["skipped_binary"] += 1
                    continue
                scanned_bytes += len(content)
                base["scanned_files"] += 1
                indicators, urls, _ = scan_text(row, path, text)
                if urls:
                    urls_by_path[path] = urls
                if indicators and len(all_indicators) < indicator_limit:
                    remaining = indicator_limit - len(all_indicators)
                    all_indicators.extend(indicators[:remaining])
                    if len(indicators) > remaining:
                        base["indicator_cap_reached"] = True
                elif indicators:
                    base["indicator_cap_reached"] = True

        base["scanned_bytes"] = scanned_bytes
        external_urls = classify_external_urls(urls_by_path)
        findings = evaluate_repository(all_indicators, external_urls)
        base["external_urls"] = external_urls
        base["indicators"] = all_indicators
        base["findings"] = findings
        base["preliminary_verdict"] = overall_verdict(findings)

        partial = bool(
            base["candidate_cap_reached"]
            or base["byte_cap_reached"]
            or base["blob_errors"]
            or base["skipped_large"]
        )
        if base["scanned_files"] == 0 and base["candidate_files"] == 0:
            base["status"] = "scanned_no_source_candidates"
        elif base["scanned_files"] == 0:
            base["status"] = "source_read_failed"
        elif partial:
            base["status"] = "scanned_partial"
        else:
            base["status"] = "scanned"

    base["finished_at"] = utc_now()
    base["elapsed_seconds"] = round(time.monotonic() - started, 3)
    return base


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--clone-timeout", type=int, default=90)
    parser.add_argument("--max-files", type=int, default=3500)
    parser.add_argument("--max-total-bytes", type=int, default=45_000_000)
    parser.add_argument("--max-file-bytes", type=int, default=1_800_000)
    parser.add_argument("--hard-file-bytes", type=int, default=12_000_000)
    args = parser.parse_args()

    targets = json.loads(Path(args.targets).read_text(encoding="utf-8"))
    if not isinstance(targets, list) or not targets:
        raise RuntimeError("targets file is empty or invalid")
    rows = [int(item["row"]) for item in targets]
    if len(rows) != len(set(rows)):
        raise RuntimeError("duplicate target row in chunk")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[int, dict[str, Any]] = {}
    lock = threading.Lock()
    completed_count = 0

    def task(target: dict[str, Any]) -> dict[str, Any]:
        try:
            return scan_target(
                target,
                clone_timeout=args.clone_timeout,
                max_files=args.max_files,
                max_total_bytes=args.max_total_bytes,
                max_file_bytes=args.max_file_bytes,
                hard_file_bytes=args.hard_file_bytes,
            )
        except Exception as exc:  # noqa: BLE001
            return {
                "scanner_version": SCANNER_VERSION,
                "row": int(target.get("row", 0)),
                "target_id": target.get("target_id"),
                "name": sanitize(target.get("name"), 500),
                "url": sanitize(target.get("url"), 900),
                "repo_full_name": sanitize(target.get("repo_full_name"), 500),
                "description": sanitize(target.get("description"), 2000),
                "star": int(target.get("star", 0)),
                "fork": int(target.get("fork", 0)),
                "status": "internal_error",
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
                "errors": [safe_error(exc)],
                "external_urls": [],
                "indicators": [],
                "findings": [],
                "preliminary_verdict": "unresolved",
                "started_at": utc_now(),
                "finished_at": utc_now(),
                "elapsed_seconds": 0,
            }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {executor.submit(task, target): target for target in targets}
        for future in concurrent.futures.as_completed(future_map):
            result = future.result()
            results[int(result["row"])] = result
            with lock:
                completed_count += 1
                if completed_count % 10 == 0 or completed_count == len(targets):
                    counts = Counter(item["status"] for item in results.values())
                    print(
                        f"progress {completed_count}/{len(targets)}; "
                        + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())),
                        flush=True,
                    )

    missing = sorted(set(rows) - set(results))
    if missing:
        raise RuntimeError(f"scanner did not return rows: {missing}")

    ordered = [results[row] for row in sorted(results)]
    results_path = output_dir / "results.jsonl"
    with results_path.open("w", encoding="utf-8") as handle:
        for result in ordered:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "scanner_version": SCANNER_VERSION,
        "rows": [min(rows), max(rows)],
        "target_count": len(targets),
        "result_count": len(ordered),
        "status_counts": dict(Counter(item["status"] for item in ordered)),
        "preliminary_verdict_counts": dict(Counter(item["preliminary_verdict"] for item in ordered)),
        "flagged_count": sum(item["preliminary_verdict"] not in {"no_flag", "unresolved"} for item in ordered),
        "results_sha256": hashlib.sha256(results_path.read_bytes()).hexdigest(),
        "finished_at": utc_now(),
    }
    write_json(output_dir / "chunk_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"scanner failed: {safe_error(exc)}", file=sys.stderr)
        raise
