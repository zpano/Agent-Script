#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlparse

MAX_FILE_BYTES = 1_200_000
MAX_SELECTED_BYTES = 32 * 1024 * 1024
MAX_SELECTED_FILES = 5000
MAX_FALLBACK_FILES = 350
MAX_EVIDENCE_PER_FEATURE_FILE = 2
MAX_EVIDENCE_PER_REPO = 36

TEXT_EXTENSIONS = {
    ".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx",
    ".py", ".pyw", ".rb", ".php", ".go", ".rs", ".java", ".kt", ".kts",
    ".cs", ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh", ".swift",
    ".lua", ".pl", ".pm", ".r", ".sh", ".bash", ".zsh", ".fish", ".ps1",
    ".psm1", ".bat", ".cmd", ".vbs", ".vue", ".svelte", ".html", ".htm",
    ".json", ".json5", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".xml", ".gradle", ".properties", ".tf", ".hcl", ".sql", ".graphql",
    ".proto", ".ex", ".exs", ".erl", ".hrl", ".clj", ".cljs", ".scala",
    ".dart", ".sol", ".move", ".cairo", ".nix", ".mk", ".dockerfile",
}
SPECIAL_NAMES = {
    "package.json", "pyproject.toml", "setup.py", "setup.cfg", "tox.ini",
    "cargo.toml", "go.mod", "go.sum", "makefile", "gnumakefile", "dockerfile",
    "compose.yml", "compose.yaml", "docker-compose.yml", "docker-compose.yaml",
    "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle",
    "gemfile", "rakefile", "procfile", "manifest.json", "plugin.json",
    "dsh.json", "cordis.patch.yml", "cordis.patch.yaml", "requirements.txt",
    "security.md", "install.md", "installation.md", "readme.md", "readme",
}
EXCLUDED_DIRS = {
    ".git", "node_modules", ".pnpm", ".yarn", ".venv", "venv", "env",
    "vendor", "third_party", "third-party", "thirdparty", "external", "deps",
    "bower_components", ".tox", ".mypy_cache", ".pytest_cache", "__pycache__",
    ".next", ".nuxt", ".cache", "coverage", ".gradle", ".idea",
}
LOW_CONTEXT_DIRS = {
    "test", "tests", "testing", "spec", "specs", "fixtures", "fixture",
    "examples", "example", "samples", "sample", "docs", "doc", "demo",
    "demos", "benchmark", "benchmarks", "poc", "pocs", "research",
}
LOCK_OR_GENERATED = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb",
    "cargo.lock", "poetry.lock", "uv.lock", "composer.lock", "gemfile.lock",
}
BINARY_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".dat", ".jar", ".class",
    ".wasm", ".node", ".msi", ".apk", ".ipa", ".deb", ".rpm", ".pkg",
}
SAFE_HOST_SUFFIXES = (
    "github.com", "githubusercontent.com", "npmjs.org", "npmjs.com", "pypi.org",
    "pythonhosted.org", "crates.io", "rustup.rs", "nodejs.org", "microsoft.com",
    "googleapis.com", "deepseek.com", "deepseek.ai", "localhost", "127.0.0.1",
)
KNOWN_EXFIL_HOST_FRAGMENTS = (
    "discord.com/api/webhooks", "discordapp.com/api/webhooks", "api.telegram.org/bot",
    "webhook.site", "requestbin", "pipedream.net", "beeceptor.com", "hookbin.com",
    "interact.sh", "oastify.com", "burpcollaborator.net", "ngrok.io", "ngrok-free.app",
)


@dataclass(frozen=True)
class FeatureDef:
    feature: str
    label_zh: str
    patterns: tuple[re.Pattern[str], ...]


def cre(pattern: str, flags: int = re.I | re.M) -> re.Pattern[str]:
    return re.compile(pattern, flags)


FEATURE_DEFS: tuple[FeatureDef, ...] = (
    FeatureDef("reverse_shell", "反向 Shell / 远程交互式命令通道", (
        cre(r"/dev/tcp/[A-Za-z0-9_.:-]+/\d+"),
        cre(r"\b(?:nc|ncat|netcat)\b[^\n]{0,220}\s(?:-e|--exec)\s+(?:/bin/)?(?:sh|bash|zsh|cmd(?:\.exe)?|powershell(?:\.exe)?)"),
        cre(r"\bbash\s+-i\b[^\n]{0,220}(?:/dev/tcp|>&|0>&1)"),
        cre(r"System\.Net\.Sockets\.TCPClient[\s\S]{0,900}(?:Invoke-Expression|\biex\b|GetStream\s*\()"),
        cre(r"socket\.socket\s*\([\s\S]{0,700}(?:os\.dup2|dup2\s*\()[\s\S]{0,500}(?:/bin/(?:sh|bash)|subprocess\.(?:call|Popen))"),
    )),
    FeatureDef("remote_exec", "下载远程内容后直接执行", (
        cre(r"\b(?:curl|wget)\b[^\n]{0,500}(?:\||&&|;)\s*(?:sudo\s+)?(?:sh|bash|zsh|dash|python\d*|node|deno|bun|pwsh|powershell)\b"),
        cre(r"(?:Invoke-WebRequest|Invoke-RestMethod|\biwr\b|\birm\b)[^\n]{0,600}(?:\||;)\s*(?:Invoke-Expression|\biex\b)"),
        cre(r"(?:Invoke-Expression|\biex\b)\s*\(?\s*\(?\s*(?:New-Object\s+Net\.WebClient|\[[^\]]*WebClient[^\]]*\])[^\n]{0,500}DownloadString", re.I | re.M),
        cre(r"\b(?:eval|exec)\s*\(\s*(?:await\s+)?(?:fetch\s*\(|requests\.(?:get|post)\s*\(|urllib\.request\.urlopen\s*\()", re.I | re.M),
        cre(r"new\s+Function\s*\(\s*(?:await\s+)?\(?\s*(?:fetch\s*\(|[^\n]{0,120}\.text\s*\()", re.I | re.M),
    )),
    FeatureDef("obfuscated_exec", "混淆/编码载荷解码后动态执行", (
        cre(r"(?:eval|exec|new\s+Function)\s*\([^\n]{0,500}(?:atob\s*\(|b64decode\s*\(|fromCharCode\s*\(|zlib\.decompress|gzip\.decompress|marshal\.loads)"),
        cre(r"(?:atob\s*\(|b64decode\s*\(|zlib\.decompress|gzip\.decompress|marshal\.loads)[\s\S]{0,700}(?:eval\s*\(|exec\s*\(|new\s+Function)"),
        cre(r"powershell(?:\.exe)?[^\n]{0,250}\s-(?:enc|encodedcommand)\s+[A-Za-z0-9+/=]{40,}"),
        cre(r"Buffer\.from\s*\([^\n]{0,300}['\"]base64['\"][^\n]{0,500}(?:eval|Function|vm\.runIn)"),
    )),
    FeatureDef("dynamic_exec", "动态执行系统命令或代码", (
        cre(r"\bchild_process\.(?:exec|execSync|spawn|spawnSync|fork)\s*\("),
        cre(r"\bsubprocess\.(?:Popen|run|call|check_output|check_call)\s*\("),
        cre(r"\bos\.(?:system|popen)\s*\("),
        cre(r"\b(?:eval|exec)\s*\("),
        cre(r"\bnew\s+Function\s*\("),
        cre(r"\bvm\.(?:runInNewContext|runInThisContext|runInContext|compileFunction)\s*\("),
        cre(r"\bProcess\.Start\s*\("),
        cre(r"\bRuntime\.getRuntime\(\)\.exec\s*\("),
        cre(r"\bCommand::new\s*\("),
    )),
    FeatureDef("credential_access", "读取 SSH、云凭据、浏览器凭据或钱包材料", (
        cre(r"(?:~|HOME|USERPROFILE|homedir\s*\(\))[^\n]{0,180}\.ssh[/\\](?:id_rsa|id_ed25519|id_ecdsa|config|known_hosts)"),
        cre(r"\.aws[/\\](?:credentials|config)"),
        cre(r"\.azure[/\\](?:accessTokens\.json|azureProfile\.json|msal_token_cache)"),
        cre(r"\.config[/\\]gcloud[/\\](?:credentials|application_default_credentials\.json)"),
        cre(r"(?:\.npmrc|\.pypirc|\.git-credentials|hosts\.yml|credentials\.json)"),
        cre(r"(?:Chrome|Chromium|Brave|Edge|Firefox)[^\n]{0,220}(?:Login Data|Cookies|logins\.json|key4\.db|places\.sqlite)"),
        cre(r"(?:wallet\.dat|keystore[/\\]|mnemonic|seed[_ -]?phrase|private[_ -]?key)[^\n]{0,220}(?:readFile|read_text|open\s*\(|fs\.)"),
        cre(r"(?:Login Data|Cookies|logins\.json|key4\.db|wallet\.dat)[^\n]{0,220}(?:readFile|read_text|open\s*\(|sqlite)"),
    )),
    FeatureDef("secret_env", "读取高价值密钥环境变量", (
        cre(r"(?:process\.env\.|os\.(?:getenv|environ\[)|std::env::var\s*\()[^\n]{0,120}(?:GITHUB_TOKEN|GH_TOKEN|NPM_TOKEN|AWS_SECRET_ACCESS_KEY|PRIVATE_KEY|MNEMONIC|SEED_PHRASE|DATABASE_URL|OPENAI_API_KEY|DEEPSEEK_API_KEY)"),
    )),
    FeatureDef("network_send", "向网络端点发送数据", (
        cre(r"\brequests\.(?:post|put|patch)\s*\("),
        cre(r"\b(?:axios|got)\.(?:post|put|patch)\s*\("),
        cre(r"\bfetch\s*\([^\n]{0,500}method\s*:\s*['\"](?:POST|PUT|PATCH)['\"]"),
        cre(r"\b(?:http|https)\.request\s*\("),
        cre(r"\b(?:curl|wget)\b[^\n]{0,400}(?:--data|-d\s|--upload-file|-T\s|--form|-F\s)"),
        cre(r"\bWebClient\.(?:UploadString|UploadData|UploadFile)\s*\("),
        cre(r"\bnet/http\b[\s\S]{0,600}(?:NewRequest|PostForm|Client\.Do)"),
    )),
    FeatureDef("known_exfil_endpoint", "使用常见外传/Webhook 接收端点", tuple(cre(re.escape(fragment)) for fragment in KNOWN_EXFIL_HOST_FRAGMENTS)),
    FeatureDef("input_capture", "键盘输入/全局按键采集", (
        cre(r"\bpynput\.keyboard\b|from\s+pynput\s+import\s+keyboard"),
        cre(r"\bkeyboard\.(?:hook|on_press|on_release|record)\s*\("),
        cre(r"SetWindowsHookEx(?:A|W)?\s*\([^\n]{0,200}WH_KEYBOARD"),
        cre(r"CGEventTapCreate\s*\("),
        cre(r"RegisterRawInputDevices\s*\("),
    )),
    FeatureDef("screen_capture", "屏幕截图/屏幕录制", (
        cre(r"\b(?:pyautogui|pyscreeze)\.screenshot\s*\("),
        cre(r"\bImageGrab\.grab\s*\("),
        cre(r"\b(?:screencapture|gnome-screenshot|scrot)\b"),
        cre(r"\bdesktopCapturer\.getSources\s*\("),
        cre(r"\bGetDC\s*\([^\n]{0,100}\bBitBlt\s*\("),
    )),
    FeatureDef("clipboard_capture", "读取剪贴板内容", (
        cre(r"\b(?:pyperclip|clipboard)\.paste\s*\("),
        cre(r"\bnavigator\.clipboard\.readText\s*\("),
        cre(r"\b(?:pbpaste|xclip\s+-o|xsel\s+--clipboard\s+--output)\b"),
        cre(r"\bGetClipboardData\s*\("),
    )),
    FeatureDef("camera_mic_capture", "摄像头/麦克风采集", (
        cre(r"\bgetUserMedia\s*\("),
        cre(r"\bMediaRecorder\s*\("),
        cre(r"\bcv2\.VideoCapture\s*\("),
        cre(r"\b(?:pyaudio|sounddevice)\b"),
    )),
    FeatureDef("persistence", "建立系统启动项、计划任务或服务持久化", (
        cre(r"\bcrontab\s+(?:-|/)|/etc/(?:cron\.|crontab)"),
        cre(r"\bsystemctl\s+(?:enable|reenable)\b|/etc/systemd/system/"),
        cre(r"\blaunchctl\s+(?:load|bootstrap|enable)\b|LaunchAgents|LaunchDaemons"),
        cre(r"CurrentVersion[/\\]Run(?:Once)?|HKCU[/\\].*[/\\]Run(?:Once)?"),
        cre(r"(?:Startup|Autostart)[/\\][^\n]{0,240}(?:copy|write|create|ln\s+-s)"),
        cre(r"(?:\.bashrc|\.zshrc|\.profile|config\.fish)[^\n]{0,220}(?:append|write|>>|Add-Content)"),
        cre(r"\bschtasks\b[^\n]{0,300}/create\b"),
    )),
    FeatureDef("security_disable", "关闭安全软件、防火墙或系统防护", (
        cre(r"Set-MpPreference[^\n]{0,240}DisableRealtimeMonitoring\s+\$?true"),
        cre(r"Add-MpPreference[^\n]{0,240}ExclusionPath"),
        cre(r"\bnetsh\b[^\n]{0,260}firewall[^\n]{0,260}(?:off|disable)"),
        cre(r"\b(?:ufw\s+disable|setenforce\s+0|systemctl\s+(?:stop|disable)\s+(?:firewalld|clamav|apparmor))\b"),
        cre(r"\b(?:sc|net)\s+(?:stop|config)\s+(?:WinDefend|Sense|WdNisSvc)\b"),
    )),
    FeatureDef("miner", "加密货币挖矿程序或矿池连接", (
        cre(r"\b(?:xmrig|xmr-stak|minerd|cpuminer|cgminer|bfgminer)\b"),
        cre(r"stratum\+(?:tcp|ssl)://"),
        cre(r"(?:supportxmr|nanopool|minexmr|2miners|f2pool|nicehash)[^\s'\"]*"),
        cre(r"\b(?:cryptonight|randomx)\b[^\n]{0,200}(?:mine|mining|pool)"),
    )),
    FeatureDef("destructive", "破坏性删除、加密或勒索行为", (
        cre(r"\brm\s+-rf\s+(?:/|/\*|~|\$HOME)\b"),
        cre(r"\b(?:del|erase)\s+/[sqf]+\s+[A-Za-z]:\\\*"),
        cre(r"\b(?:format|mkfs\.[a-z0-9]+)\s+(?:/dev/|[A-Za-z]:)"),
        cre(r"(?:ransom|decrypt[_ -]?key|pay\s+(?:bitcoin|btc)|files\s+have\s+been\s+encrypted)"),
        cre(r"(?:Fernet|AES|ChaCha20)[\s\S]{0,900}(?:rglob|walk\s*\(|glob\s*\()[\s\S]{0,900}(?:unlink|remove|rename)"),
    )),
    FeatureDef("download", "从网络下载文件/载荷", (
        cre(r"\b(?:curl|wget)\b[^\n]{0,500}(?:https?://|ftp://)"),
        cre(r"\b(?:requests\.get|urllib\.request\.urlretrieve|DownloadFile|download_file|fetch)\s*\("),
        cre(r"\bhttps?\.get\s*\("),
    )),
    FeatureDef("binary_execute", "下载或释放本机二进制后执行", (
        cre(r"(?:curl|wget|DownloadFile|urlretrieve)[\s\S]{0,900}(?:\.exe|\.dll|\.so|\.dylib|\.bin|\.msi)[\s\S]{0,900}(?:chmod\s+\+x|Process\.Start|subprocess|child_process|Start-Process|&\s*\$)"),
        cre(r"(?:writeFile|open\s*\([^\n]{0,180}['\"]wb['\"])[\s\S]{0,800}(?:base64|Buffer\.from)[\s\S]{0,800}(?:chmod|exec|spawn|Popen|Process\.Start)"),
    )),
    FeatureDef("sensitive_collection", "批量收集主机、文件或账户信息", (
        cre(r"(?:os\.walk|rglob|glob\.glob|walkDir|WalkDir)[^\n]{0,300}(?:\.ssh|\.aws|wallet|cookie|history|credential|token|secret)"),
        cre(r"\b(?:whoami|systeminfo|ipconfig\s+/all|ifconfig|uname\s+-a|dscl\s+\.\s+list)\b"),
        cre(r"(?:process\.env|os\.environ)[\s\S]{0,500}(?:JSON\.stringify|json\.dumps|requests\.post|fetch\s*\()"),
    )),
    FeatureDef("inbound_command_surface", "网络请求/Socket 输入进入命令执行面", (
        cre(r"(?:req\.(?:body|query|params)|request\.(?:json|args|form)|socket\.on\s*\(\s*['\"]data|websocket[^\n]{0,120}(?:recv|message)|await\s+receive_text)[\s\S]{0,1400}(?:child_process\.(?:exec|spawn)|subprocess\.(?:Popen|run)|os\.system|Process\.Start|Command::new)"),
        cre(r"(?:child_process\.(?:exec|spawn)|subprocess\.(?:Popen|run)|os\.system|Process\.Start|Command::new)[\s\S]{0,1400}(?:req\.(?:body|query|params)|request\.(?:json|args|form)|socket\.on\s*\(\s*['\"]data|websocket[^\n]{0,120}(?:recv|message))"),
    )),
    FeatureDef("workflow_danger", "高风险 CI 触发/权限或远程脚本执行", (
        cre(r"\bpull_request_target\s*:"),
        cre(r"\bpermissions\s*:\s*write-all\b"),
        cre(r"\bpermissions\s*:[\s\S]{0,500}(?:contents|actions|packages|id-token)\s*:\s*write[\s\S]{0,900}\b(?:pull_request_target|issue_comment|workflow_run)\b"),
        cre(r"\brun\s*:\s*[|>]?[^\n]*\n(?:[^\n]*\n){0,8}[^\n]*(?:curl|wget)[^\n]*(?:\||&&|;)\s*(?:bash|sh|pwsh|powershell)"),
    )),
    FeatureDef("anti_analysis", "反调试、虚拟机检测或隐藏执行", (
        cre(r"\b(?:IsDebuggerPresent|CheckRemoteDebuggerPresent|ptrace\s*\(|sys\.gettrace\s*\()"),
        cre(r"(?:VirtualBox|VMware|QEMU|Sandboxie)[\s\S]{0,500}(?:detect|exit|terminate|abort)"),
        cre(r"\b(?:attrib\s+\+h|SetFileAttributes[^\n]{0,160}HIDDEN|chflags\s+hidden)\b"),
    )),
)
FEATURE_LABELS = {item.feature: item.label_zh for item in FEATURE_DEFS}
REMOTE_EXEC_PATTERNS = FEATURE_DEFS[1].patterns

REDACTIONS: tuple[re.Pattern[str], ...] = (
    cre(r"(?i)(authorization\s*[:=]\s*['\"]?bearer\s+)[A-Za-z0-9._~+/=-]{12,}"),
    cre(r"(?i)((?:token|secret|password|passwd|private[_-]?key|api[_-]?key)\s*[:=]\s*['\"])[^'\"\s]{8,}"),
    cre(r"https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9._-]+"),
    cre(r"https://api\.telegram\.org/bot\d+:[A-Za-z0-9_-]+"),
    cre(r"\b(?:ghp|github_pat|sk|xox[baprs]|AKIA)[A-Za-z0-9_-]{12,}\b"),
)


def redact(text: str) -> str:
    out = text
    for pat in REDACTIONS:
        if pat.groups:
            out = pat.sub(lambda m: (m.group(1) if m.lastindex else "") + "<REDACTED>", out)
        else:
            out = pat.sub("<REDACTED>", out)
    return out


def run_command(cmd: list[str], *, cwd: Path | None = None, timeout: int = 120, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env.update({"GIT_TERMINAL_PROMPT": "0", "GIT_LFS_SKIP_SMUDGE": "1", "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C.UTF-8"})
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False, env=env)


def is_low_context(path: str) -> bool:
    parts = {p.casefold() for p in PurePosixPath(path).parts[:-1]}
    return bool(parts & LOW_CONTEXT_DIRS)


def path_priority(path: str) -> int | None:
    pp = PurePosixPath(path)
    parts = [p.casefold() for p in pp.parts]
    if any(part in EXCLUDED_DIRS for part in parts[:-1]):
        return None
    name = pp.name.casefold()
    suffix = pp.suffix.casefold()
    if name in LOCK_OR_GENERATED or name.endswith(".map") or name.endswith(".min.js") or name.endswith(".min.css"):
        return None
    if name in {"readme.md", "readme", "security.md", "install.md", "installation.md"}:
        return 5
    if name in SPECIAL_NAMES or path.startswith(".github/workflows/"):
        return 0
    if suffix not in TEXT_EXTENSIONS:
        return None
    if suffix in {".sh", ".bash", ".zsh", ".fish", ".ps1", ".psm1", ".bat", ".cmd", ".vbs"}:
        return 0
    if any(part in {"scripts", "script", "bin", "hooks", "install", "installer", ".github"} for part in parts[:-1]):
        return 1
    if any(part in {"src", "lib", "app", "server", "client", "packages", "plugin", "plugins", "cmd"} for part in parts[:-1]):
        return 2
    if is_low_context(path):
        return 4
    return 3


def parse_ls_tree(raw: bytes) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            left, path_b = record.split(b"\t", 1)
            pieces = left.split()
            if len(pieces) != 4 or pieces[1] != b"blob":
                continue
            size = None if pieces[3] == b"-" else int(pieces[3])
            entries.append({"mode": pieces[0].decode(), "oid": pieces[2].decode(), "size": size, "path": path_b.decode("utf-8", errors="surrogateescape")})
        except Exception:
            continue
    return entries


def select_entries(entries: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates: list[tuple[int, int, str, dict[str, Any]]] = []
    skipped_oversize = 0
    binary_payloads: list[dict[str, Any]] = []
    binary_count = 0
    for entry in entries:
        path = str(entry["path"])
        suffix = PurePosixPath(path).suffix.casefold()
        if suffix in BINARY_EXTENSIONS:
            binary_count += 1
            if len(binary_payloads) < 50:
                binary_payloads.append({"path": path, "size": entry.get("size"), "mode": entry.get("mode")})
        prio = path_priority(path)
        if prio is None:
            continue
        size = entry.get("size")
        if size is None or size > MAX_FILE_BYTES:
            skipped_oversize += 1
            continue
        candidates.append((prio, int(size), path.casefold(), entry))
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    selected: list[dict[str, Any]] = []
    total = 0
    omitted_due_cap = 0
    for _, size, _, entry in candidates:
        if len(selected) >= MAX_SELECTED_FILES or total + size > MAX_SELECTED_BYTES:
            omitted_due_cap += 1
            continue
        selected.append(entry)
        total += size
    return selected, {"candidate_text_files": len(candidates), "selected_files": len(selected), "selected_declared_bytes": total, "skipped_oversize_files": skipped_oversize, "omitted_due_cap": omitted_due_cap, "binary_payload_count": binary_count, "binary_payload_samples": binary_payloads}


def parse_cat_file_output(raw: bytes, requested_oids: list[str]) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    pos = 0
    for expected in requested_oids:
        nl = raw.find(b"\n", pos)
        if nl < 0:
            raise ValueError("truncated cat-file header")
        header = raw[pos:nl].decode("ascii", errors="replace")
        pos = nl + 1
        if header.endswith(" missing"):
            continue
        parts = header.split()
        if len(parts) != 3 or parts[1] != "blob":
            raise ValueError(f"unexpected cat-file header: {header!r}")
        oid, _, size_s = parts
        size = int(size_s)
        if pos + size > len(raw):
            raise ValueError("truncated cat-file body")
        body = raw[pos:pos + size]
        pos += size
        if pos < len(raw) and raw[pos:pos + 1] == b"\n":
            pos += 1
        result[expected] = body
        if oid != expected:
            result[oid] = body
    return result


def read_selected_blobs(repo_dir: Path, selected: list[dict[str, Any]]) -> tuple[dict[str, bytes], dict[str, Any]]:
    unique_oids: list[str] = []
    seen: set[str] = set()
    for entry in selected:
        oid = str(entry["oid"])
        if oid not in seen:
            seen.add(oid)
            unique_oids.append(oid)
    if not unique_oids:
        return {}, {"method": "none", "error": None, "fallback_files": 0}
    try:
        proc = run_command(["git", "cat-file", "--batch"], cwd=repo_dir, timeout=420, input_bytes=("\n".join(unique_oids) + "\n").encode("ascii"))
        if proc.returncode == 0:
            return parse_cat_file_output(proc.stdout, unique_oids), {"method": "git-cat-file-batch", "error": None, "stderr": proc.stderr.decode("utf-8", errors="replace")[-1200:], "fallback_files": 0}
        batch_error = proc.stderr.decode("utf-8", errors="replace")[-1600:]
    except Exception as exc:
        batch_error = f"{type(exc).__name__}: {exc}"
    contents: dict[str, bytes] = {}
    fallback_count = 0
    for entry in selected[:MAX_FALLBACK_FILES]:
        path = str(entry["path"])
        oid = str(entry["oid"])
        if oid in contents:
            continue
        try:
            proc = run_command(["git", "show", f"HEAD:{path}"], cwd=repo_dir, timeout=25)
            if proc.returncode == 0:
                contents[oid] = proc.stdout
                fallback_count += 1
        except Exception:
            continue
    return contents, {"method": "git-show-fallback", "error": batch_error, "fallback_files": fallback_count}


def looks_text(data: bytes) -> bool:
    if not data:
        return True
    sample = data[:8192]
    if b"\x00" in sample:
        return False
    control = sum(1 for b in sample if b < 9 or (13 < b < 32))
    return control / max(1, len(sample)) < 0.08


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def evidence_from_match(path: str, text: str, match: re.Match[str], feature: str) -> dict[str, Any]:
    line_no = line_number(text, match.start())
    lines = text.splitlines()
    start = max(1, line_no - 2)
    end = min(len(lines), line_no + 2)
    snippet_lines = []
    for number in range(start, end + 1):
        value = lines[number - 1]
        if len(value) > 420:
            value = value[:417] + "..."
        snippet_lines.append(f"{number:>5}: {value}")
    return {"feature": feature, "label": FEATURE_LABELS.get(feature, feature), "path": path, "line": line_no, "line_start": start, "line_end": end, "snippet": redact("\n".join(snippet_lines)), "low_context": is_low_context(path)}


def add_manual_evidence(evidence: list[dict[str, Any]], *, feature: str, path: str, line: int, snippet: str, detail: str | None = None) -> None:
    evidence.append({"feature": feature, "label": FEATURE_LABELS.get(feature, feature), "path": path, "line": line, "line_start": line, "line_end": line, "snippet": redact(snippet[:1600]), "low_context": is_low_context(path), "detail": detail})


def extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s'\"<>`)\]}]+", text, flags=re.I)
    unique: list[str] = []
    seen: set[str] = set()
    for url in urls:
        clean = url.rstrip(".,;:")
        if clean not in seen:
            seen.add(clean)
            unique.append(clean)
        if len(unique) >= 80:
            break
    return unique


def url_is_unusual(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").casefold()
    except Exception:
        return False
    if not host:
        return False
    if any(host == suffix or host.endswith("." + suffix) for suffix in SAFE_HOST_SUFFIXES):
        return False
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
        return True
    return any(fragment.split("/")[0] in host for fragment in KNOWN_EXFIL_HOST_FRAGMENTS)


def scan_text_file(path: str, text: str) -> tuple[set[str], list[dict[str, Any]], list[str]]:
    features: set[str] = set()
    evidence: list[dict[str, Any]] = []
    unusual_urls = [url for url in extract_urls(text) if url_is_unusual(url)]
    for definition in FEATURE_DEFS:
        feature_hits = 0
        for pattern in definition.patterns:
            for match in pattern.finditer(text):
                features.add(definition.feature)
                if feature_hits < MAX_EVIDENCE_PER_FEATURE_FILE:
                    evidence.append(evidence_from_match(path, text, match, definition.feature))
                    feature_hits += 1
                if feature_hits >= MAX_EVIDENCE_PER_FEATURE_FILE:
                    break
            if feature_hits >= MAX_EVIDENCE_PER_FEATURE_FILE:
                break
    if PurePosixPath(path).name.casefold() == "package.json":
        try:
            package = json.loads(text)
            scripts = package.get("scripts") if isinstance(package, dict) else None
            if isinstance(scripts, dict):
                for script_name in ("preinstall", "install", "postinstall", "prepare", "prepublish", "prepublishOnly"):
                    value = scripts.get(script_name)
                    if not isinstance(value, str) or not value.strip():
                        continue
                    features.add("install_lifecycle")
                    line = max(1, text[: text.find(value)].count("\n") + 1) if value in text else 1
                    add_manual_evidence(evidence, feature="install_lifecycle", path=path, line=line, snippet=f'{script_name}: {value}', detail="package manager lifecycle hook")
                    if any(p.search(value) for p in REMOTE_EXEC_PATTERNS):
                        features.add("install_remote_exec")
                        add_manual_evidence(evidence, feature="install_remote_exec", path=path, line=line, snippet=f'{script_name}: {value}', detail="install-time remote content execution")
                    if re.search(r"(?:curl|wget|DownloadFile|urlretrieve).{0,500}(?:\.exe|\.dll|\.so|\.dylib|\.bin|\.msi).{0,500}(?:chmod|exec|spawn|start|&)", value, re.I):
                        features.add("install_binary_exec")
        except Exception:
            pass
    if path.startswith(".github/workflows/") and "workflow_danger" in features and re.search(r"\bsecrets\.[A-Za-z0-9_]+", text):
        features.add("privileged_pr_workflow")
    return features, evidence, unusual_urls


def choose_evidence(evidence: list[dict[str, Any]], features: Iterable[str], limit: int = 14) -> list[dict[str, Any]]:
    wanted = set(features)
    selected = [item for item in evidence if item.get("feature") in wanted]
    selected.sort(key=lambda item: (bool(item.get("low_context")), str(item.get("path")), int(item.get("line") or 0)))
    unique: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int]] = set()
    for item in selected:
        key = (str(item.get("feature")), str(item.get("path")), int(item.get("line") or 0))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
        if len(unique) >= limit:
            break
    return unique


def classify_repo(target: dict[str, Any], file_features: dict[str, set[str]], evidence: list[dict[str, Any]], unusual_urls: list[str], selection_meta: dict[str, Any], read_meta: dict[str, Any]) -> tuple[str, str, list[dict[str, Any]], list[dict[str, Any]]]:
    prod_features: set[str] = set()
    all_features: set[str] = set()
    for path, feats in file_features.items():
        all_features |= feats
        if not is_low_context(path):
            prod_features |= feats
    malicious_reasons: list[dict[str, Any]] = []
    high_reasons: list[dict[str, Any]] = []
    medium_reasons: list[dict[str, Any]] = []

    def reason(bucket: list[dict[str, Any]], code: str, title: str, detail: str, feats: list[str]) -> None:
        bucket.append({"code": code, "title": title, "detail": detail, "features": feats})

    for path, feats in file_features.items():
        if is_low_context(path):
            continue
        if {"credential_access", "network_send"} <= feats:
            if "known_exfil_endpoint" in feats or unusual_urls or "obfuscated_exec" in feats:
                reason(malicious_reasons, "CREDENTIAL_EXFILTRATION", "凭据材料读取与网络外传出现在同一生产代码路径", f"{path} 同时读取 SSH/云/浏览器/钱包凭据并向外发送；这不是普通插件功能应默认具备的组合。", ["credential_access", "network_send", "known_exfil_endpoint"])
            else:
                reason(high_reasons, "CREDENTIAL_NETWORK_COMBINATION", "凭据读取与网络发送组合", f"{path} 同时包含高价值凭据读取和网络发送，需要人工确认数据流与目的端点。", ["credential_access", "network_send"])
        capture = feats & {"input_capture", "screen_capture", "clipboard_capture", "camera_mic_capture"}
        if capture and "network_send" in feats:
            if "known_exfil_endpoint" in feats or "obfuscated_exec" in feats or "persistence" in feats:
                reason(malicious_reasons, "SURVEILLANCE_EXFILTRATION", "用户输入/屏幕/剪贴板采集并外传", f"{path} 在同一路径采集用户数据并发送至网络，且伴随隐藏端点、混淆或持久化信号。", sorted(capture | {"network_send"}))
            else:
                reason(high_reasons, "CAPTURE_NETWORK_COMBINATION", "敏感采集与网络发送组合", f"{path} 同时采集输入、屏幕、剪贴板或音视频并发送网络数据；即便是远程控制类插件也需要显式授权和边界核查。", sorted(capture | {"network_send"}))
        if "reverse_shell" in feats:
            if feats & {"persistence", "obfuscated_exec", "known_exfil_endpoint", "install_lifecycle"}:
                reason(malicious_reasons, "HIDDEN_REVERSE_SHELL", "反向 Shell 与隐藏执行/持久化组合", f"{path} 含反向 Shell，并与持久化、安装期执行、混淆或可疑端点共同出现。", ["reverse_shell", "persistence", "obfuscated_exec", "known_exfil_endpoint", "install_lifecycle"])
            else:
                reason(high_reasons, "REVERSE_SHELL", "生产代码包含反向 Shell 能力", f"{path} 可建立远程交互式命令通道；若非明确的远程终端产品能力，应按后门处置。", ["reverse_shell"])
        if "persistence" in feats and feats & {"remote_exec", "obfuscated_exec", "binary_execute"}:
            reason(malicious_reasons, "PERSISTENT_REMOTE_PAYLOAD", "持久化与远程/混淆载荷执行组合", f"{path} 同时建立开机持久化并执行远程或混淆载荷。", ["persistence", "remote_exec", "obfuscated_exec", "binary_execute"])
        if "security_disable" in feats and feats & {"remote_exec", "download", "binary_execute", "persistence"}:
            reason(malicious_reasons, "DEFENSE_EVASION_PAYLOAD", "关闭安全防护并部署/执行载荷", f"{path} 关闭系统防护，同时下载、执行或持久化代码。", ["security_disable", "remote_exec", "download", "binary_execute", "persistence"])
        if "destructive" in feats and feats & {"remote_exec", "inbound_command_surface", "obfuscated_exec"}:
            reason(malicious_reasons, "REMOTE_DESTRUCTIVE_ACTION", "远程可触发的破坏/勒索行为", f"{path} 将破坏性操作与远程输入或混淆执行面组合。", ["destructive", "remote_exec", "inbound_command_surface", "obfuscated_exec"])

    if "miner" in prod_features:
        repo_text = (str(target.get("name", "")) + " " + str(target.get("description", ""))).casefold()
        if not re.search(r"\b(?:miner|mining|xmrig|crypto mine)\b", repo_text):
            reason(malicious_reasons, "HIDDEN_MINER", "插件生产代码包含未声明的挖矿行为", "仓库名称和描述未声明挖矿用途，但生产代码命中矿工/矿池协议。", ["miner"])
        else:
            reason(high_reasons, "DECLARED_MINER", "插件包含挖矿能力", "仓库文本可能声明了挖矿用途，但该行为仍会消耗用户资源，安装前必须明确授权。", ["miner"])
    if "security_disable" in prod_features and not any(r["code"] == "DEFENSE_EVASION_PAYLOAD" for r in malicious_reasons):
        reason(high_reasons, "SECURITY_DISABLE", "修改或关闭系统安全防护", "生产代码命中关闭 Defender、防火墙、SELinux/AppArmor 等行为。", ["security_disable"])
    if "destructive" in prod_features and not any(r["code"] == "REMOTE_DESTRUCTIVE_ACTION" for r in malicious_reasons):
        reason(high_reasons, "DESTRUCTIVE_OPERATION", "包含高破坏性文件或磁盘操作", "生产代码包含递归删除、磁盘格式化或批量加密/勒索特征。", ["destructive"])
    if "install_remote_exec" in all_features:
        reason(high_reasons, "INSTALL_REMOTE_EXEC", "安装阶段下载并直接执行远程代码", "package manager 生命周期钩子在安装/准备阶段执行远程内容，供应链风险高。", ["install_lifecycle", "install_remote_exec", "remote_exec"])
    if "install_binary_exec" in all_features:
        reason(high_reasons, "INSTALL_BINARY_EXEC", "安装阶段下载并执行本机二进制", "安装钩子获取本机可执行载荷后启动，缺少签名或哈希验证时风险高。", ["install_lifecycle", "install_binary_exec", "binary_execute"])
    if "remote_exec" in prod_features and "install_remote_exec" not in all_features:
        reason(high_reasons, "REMOTE_CODE_EXEC", "运行时下载并执行远程代码", "生产代码直接执行网络响应或 curl/wget 管道脚本，远端内容变化可绕过仓库审计。", ["remote_exec"])
    if "obfuscated_exec" in prod_features:
        reason(high_reasons, "OBFUSCATED_EXEC", "解码混淆载荷后动态执行", "生产代码将 Base64/压缩/字符数组等载荷解码后交给 eval/exec/Function/PowerShell。", ["obfuscated_exec"])
    if "binary_execute" in prod_features:
        reason(high_reasons, "BINARY_DOWNLOAD_EXEC", "下载/释放二进制后执行", "生产代码获取或释放 EXE/DLL/SO 等本机载荷并启动，需核验哈希、签名和来源。", ["binary_execute", "download"])
    if "persistence" in prod_features and not any(r["code"] == "PERSISTENT_REMOTE_PAYLOAD" for r in malicious_reasons):
        reason(high_reasons, "PERSISTENCE", "建立系统级持久化", "生产代码修改计划任务、服务、启动项或 shell 配置，使插件跨重启运行。", ["persistence"])
    if "credential_access" in prod_features and not any(r["code"] in {"CREDENTIAL_EXFILTRATION", "CREDENTIAL_NETWORK_COMBINATION"} for r in malicious_reasons + high_reasons):
        reason(high_reasons, "CREDENTIAL_ACCESS", "读取高价值凭据或钱包材料", "生产代码访问 SSH、云凭据、浏览器登录数据或钱包密钥；需要证明最小权限与本地使用边界。", ["credential_access"])
    capture_prod = prod_features & {"input_capture", "screen_capture", "clipboard_capture", "camera_mic_capture"}
    if capture_prod and not any(r["code"] in {"SURVEILLANCE_EXFILTRATION", "CAPTURE_NETWORK_COMBINATION"} for r in malicious_reasons + high_reasons):
        reason(high_reasons, "SENSITIVE_CAPTURE", "采集键盘、屏幕、剪贴板或音视频", "生产代码可捕获高敏感用户数据；必须核查显式授权、存储和网络发送边界。", sorted(capture_prod))
    if "inbound_command_surface" in prod_features:
        reason(high_reasons, "NETWORK_COMMAND_SURFACE", "网络输入可进入系统命令执行面", "生产代码把 HTTP/WebSocket/Socket 输入连接到系统命令执行 API；若缺少强认证，可能形成远程代码执行后门。", ["inbound_command_surface", "dynamic_exec"])
    if "workflow_danger" in all_features or "privileged_pr_workflow" in all_features:
        reason(medium_reasons, "CI_SUPPLY_CHAIN", "CI 工作流存在高权限触发或远程脚本执行", "命中 pull_request_target、write-all/写权限与外部输入组合，或 CI 中 curl/wget 管道执行。", ["workflow_danger", "privileged_pr_workflow"])
    if "dynamic_exec" in prod_features and not any(r["code"] in {"NETWORK_COMMAND_SURFACE", "REMOTE_CODE_EXEC", "OBFUSCATED_EXEC"} for r in high_reasons):
        if prod_features & {"download", "network_send", "secret_env", "sensitive_collection"}:
            reason(medium_reasons, "DYNAMIC_EXEC_WITH_NETWORK_OR_SECRETS", "动态命令执行与网络/密钥访问共同出现", "插件可能有合理的工具执行功能，但组合扩大了命令注入和数据泄露后果。", ["dynamic_exec", "download", "network_send", "secret_env", "sensitive_collection"])
        else:
            reason(medium_reasons, "DYNAMIC_EXEC", "生产代码具有任意命令/代码执行能力", "命中 child_process/subprocess/os.system/eval 等；需确认参数是否完全由可信边界控制。", ["dynamic_exec"])
    if "known_exfil_endpoint" in prod_features and "network_send" in prod_features and not any(r["code"] in {"CREDENTIAL_EXFILTRATION", "SURVEILLANCE_EXFILTRATION"} for r in malicious_reasons):
        reason(medium_reasons, "WEBHOOK_DATA_FLOW", "向 Webhook/机器人端点发送数据", "生产代码向 Discord/Telegram/通用 Webhook 等端点发送数据，需要核查发送内容及用户授权。", ["known_exfil_endpoint", "network_send"])
    if "anti_analysis" in prod_features:
        reason(medium_reasons, "ANTI_ANALYSIS", "包含反调试、沙箱/虚拟机检测或隐藏文件行为", "此类行为可能用于兼容性，也可能用于规避分析；需结合调用链复核。", ["anti_analysis"])
    if selection_meta.get("binary_payload_count", 0) and prod_features & {"download", "dynamic_exec", "install_lifecycle"}:
        reason(medium_reasons, "BINARY_PAYLOAD_PRESENT", "仓库携带本机二进制且存在执行/安装路径", "静态源代码旁存在 EXE/DLL/SO/WASM 等载荷；本轮未反编译二进制，需要单独校验哈希和签名。", ["binary_execute", "dynamic_exec", "install_lifecycle"])

    def dedup(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        seen_codes: set[str] = set()
        for item in items:
            if item["code"] not in seen_codes:
                seen_codes.add(item["code"])
                out.append(item)
        return out

    malicious_reasons, high_reasons, medium_reasons = dedup(malicious_reasons), dedup(high_reasons), dedup(medium_reasons)
    if malicious_reasons:
        classification = "SUSPECTED_MALICIOUS"
        confidence = "high" if any(r["code"] in {"CREDENTIAL_EXFILTRATION", "SURVEILLANCE_EXFILTRATION", "DEFENSE_EVASION_PAYLOAD", "PERSISTENT_REMOTE_PAYLOAD"} for r in malicious_reasons) else "medium"
        reasons = malicious_reasons + high_reasons + medium_reasons
    elif high_reasons:
        classification, confidence, reasons = "HIGH_RISK", "medium", high_reasons + medium_reasons
    elif medium_reasons:
        classification, confidence, reasons = "MEDIUM_RISK", "medium", medium_reasons
    elif all_features:
        classification, confidence = "LOW_REVIEW", "low"
        reasons = [{"code": "LOW_CONTEXT_OR_WEAK_SIGNAL", "title": "仅发现低上下文或弱信号", "detail": "命中项主要位于文档、测试、示例或缺少危险组合，未达到报告风险阈值。", "features": sorted(all_features)}]
    else:
        classification, confidence, reasons = "NO_HIGH_CONFIDENCE_SIGNAL", "low", []
    important_features: list[str] = []
    for item in reasons:
        important_features.extend(item.get("features", []))
    return classification, confidence, reasons, choose_evidence(evidence, important_features, limit=16)


def clone_repo(url: str, repo_dir: Path) -> tuple[bool, str | None, str]:
    clone_url = url.rstrip("/") + ".git"
    try:
        proc = run_command(["git", "-c", "protocol.version=2", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout", "--no-tags", "--single-branch", clone_url, str(repo_dir)], timeout=150)
        first_error = proc.stderr.decode("utf-8", errors="replace")[-1800:]
        if proc.returncode == 0:
            sha_proc = run_command(["git", "rev-parse", "HEAD"], cwd=repo_dir, timeout=20)
            return True, sha_proc.stdout.decode().strip() if sha_proc.returncode == 0 else None, first_error
    except Exception as exc:
        first_error = f"{type(exc).__name__}: {exc}"
    shutil.rmtree(repo_dir, ignore_errors=True)
    try:
        proc2 = run_command(["git", "clone", "--depth", "1", "--no-checkout", "--no-tags", "--single-branch", clone_url, str(repo_dir)], timeout=180)
    except Exception as exc:
        return False, None, f"partial clone failed: {first_error}; fallback exception: {type(exc).__name__}: {exc}"
    if proc2.returncode != 0:
        return False, None, f"partial clone failed: {first_error}; fallback failed: {proc2.stderr.decode('utf-8', errors='replace')[-1800:]}"
    sha_proc = run_command(["git", "rev-parse", "HEAD"], cwd=repo_dir, timeout=20)
    return True, sha_proc.stdout.decode().strip() if sha_proc.returncode == 0 else None, proc2.stderr.decode("utf-8", errors="replace")[-1800:]


def scan_repository(target: dict[str, Any], workspace: Path) -> dict[str, Any]:
    started = time.monotonic()
    result: dict[str, Any] = {**target, "fetch_status": "pending", "scan_status": "pending", "commit_sha": None, "classification": "UNAVAILABLE", "confidence": "low", "reasons": [], "evidence": [], "features": [], "unusual_urls": [], "coverage": {}, "error": None}
    repo_dir = workspace / f"repo-{target.get('index')}"
    try:
        ok, sha, clone_note = clone_repo(str(target.get("url") or ""), repo_dir)
        if not ok:
            result.update({"fetch_status": "failed", "scan_status": "not_scanned", "classification": "SOURCE_UNAVAILABLE", "error": clone_note})
            return result
        result["fetch_status"] = "ok"
        result["commit_sha"] = sha
        tree_proc = run_command(["git", "-c", "core.quotePath=false", "ls-tree", "-r", "-l", "-z", "HEAD"], cwd=repo_dir, timeout=180)
        if tree_proc.returncode != 0:
            result.update({"scan_status": "not_scanned", "classification": "SOURCE_INCOMPLETE", "error": "git ls-tree failed: " + tree_proc.stderr.decode("utf-8", errors="replace")[-1800:]})
            return result
        entries = parse_ls_tree(tree_proc.stdout)
        selected, selection_meta = select_entries(entries)
        blobs, read_meta = read_selected_blobs(repo_dir, selected)
        file_features: dict[str, set[str]] = {}
        evidence: list[dict[str, Any]] = []
        unusual_urls: list[str] = []
        files_scanned = bytes_scanned = decode_failures = missing_blob_files = 0
        for entry in selected:
            data = blobs.get(str(entry["oid"]))
            path = str(entry["path"])
            if data is None:
                missing_blob_files += 1
                continue
            if not looks_text(data):
                decode_failures += 1
                continue
            text = data.decode("utf-8", errors="replace")
            files_scanned += 1
            bytes_scanned += len(data)
            feats, file_evidence, urls = scan_text_file(path, text)
            if feats:
                file_features[path] = feats
            if len(evidence) < MAX_EVIDENCE_PER_REPO * 3:
                evidence.extend(file_evidence[: max(0, MAX_EVIDENCE_PER_REPO * 3 - len(evidence))])
            unusual_urls.extend(urls)
        selection_meta.update({"total_repository_files": len(entries), "files_scanned": files_scanned, "bytes_scanned": bytes_scanned, "missing_blob_files": missing_blob_files, "decode_or_binary_skips": decode_failures, "read_method": read_meta.get("method"), "read_error": read_meta.get("error"), "fallback_files": read_meta.get("fallback_files", 0)})
        incomplete = bool(selection_meta.get("omitted_due_cap") or selection_meta.get("skipped_oversize_files") or missing_blob_files or read_meta.get("error"))
        result["scan_status"] = "partial" if incomplete else "complete"
        if files_scanned == 0 and selected:
            result.update({"scan_status": "not_scanned", "classification": "SOURCE_INCOMPLETE", "coverage": selection_meta, "error": f"unable to read selected blobs: {read_meta.get('error')}"})
            return result
        classification, confidence, reasons, chosen = classify_repo(target, file_features, evidence, sorted(set(unusual_urls))[:40], selection_meta, read_meta)
        if incomplete and classification == "NO_HIGH_CONFIDENCE_SIGNAL":
            classification = "INCOMPLETE_REVIEW"
            reasons = [{"code": "PARTIAL_SOURCE_COVERAGE", "title": "源码覆盖不完整，不能下无风险结论", "detail": "仓库因单文件大小、总文件/字节上限或对象读取失败而部分扫描；已审计部分未发现高置信度恶意链，但剩余内容仍需复核。", "features": []}]
        result.update({"classification": classification, "confidence": confidence, "reasons": reasons, "evidence": chosen, "features": sorted(set().union(*file_features.values())) if file_features else [], "unusual_urls": sorted(set(unusual_urls))[:40], "coverage": selection_meta, "error": read_meta.get("error") if incomplete else None})
        return result
    except subprocess.TimeoutExpired as exc:
        result.update({"fetch_status": "timeout" if result["fetch_status"] == "pending" else result["fetch_status"], "scan_status": "not_scanned", "classification": "SOURCE_INCOMPLETE", "error": f"timeout: {exc}"})
        return result
    except Exception as exc:
        result.update({"fetch_status": "failed" if result["fetch_status"] == "pending" else result["fetch_status"], "scan_status": "not_scanned", "classification": "SOURCE_INCOMPLETE", "error": f"{type(exc).__name__}: {exc}"})
        return result
    finally:
        result["elapsed_seconds"] = round(time.monotonic() - started, 3)
        shutil.rmtree(repo_dir, ignore_errors=True)


def load_targets(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--shards", type=int, required=True)
    args = parser.parse_args()
    if args.shard < 0 or args.shard >= args.shards:
        raise SystemExit("invalid shard")
    assigned = [row for row in load_targets(args.targets) if (int(row["index"]) - 1) % args.shards == args.shard]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"dsh-audit-{args.shard}-") as tmp, args.output.open("w", encoding="utf-8") as out:
        workspace = Path(tmp)
        for target in assigned:
            result = scan_repository(target, workspace)
            out.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
            out.flush()
            print(f"[{target['index']:04d}] {target['url']} -> {result['classification']} ({result.get('elapsed_seconds', 0)}s)", flush=True)
    actual = sum(1 for line in args.output.read_text(encoding="utf-8").splitlines() if line.strip())
    if actual != len(assigned):
        raise SystemExit(f"shard coverage mismatch: expected {len(assigned)}, got {actual}")


if __name__ == "__main__":
    main()
