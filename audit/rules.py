#!/usr/bin/env python3
"""Static indicators used by the DSH source audit.

Rules deliberately represent *signals*, not verdicts.  scanner.py combines
multiple independent signals, executable path context, package lifecycle
metadata and external endpoints before assigning a preliminary risk level.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Pattern


@dataclass(frozen=True)
class Rule:
    rule_id: str
    title: str
    category: str
    base_weight: int
    pattern: Pattern[str]
    max_hits_per_file: int = 4


def rx(
    rule_id: str,
    title: str,
    category: str,
    base_weight: int,
    pattern: str,
    flags: int = re.IGNORECASE | re.MULTILINE,
    max_hits_per_file: int = 4,
) -> Rule:
    return Rule(
        rule_id=rule_id,
        title=title,
        category=category,
        base_weight=base_weight,
        pattern=re.compile(pattern, flags),
        max_hits_per_file=max_hits_per_file,
    )


RULES: tuple[Rule, ...] = (
    # Complete reverse-shell idioms. These are strong enough to stand alone
    # when present in production/install code.
    rx(
        "reverse_shell_dev_tcp",
        "Bash /dev/tcp reverse shell",
        "remote_control",
        100,
        r"(?:bash|sh)\s+-i[^\n]{0,180}(?:/dev/(?:tcp|udp)/|>&\s*/dev/tcp)",
        re.IGNORECASE,
    ),
    rx(
        "reverse_shell_netcat",
        "Netcat shell execution",
        "remote_control",
        100,
        r"\b(?:nc|ncat|netcat)\b[^\n]{0,180}\s-e\s+(?:/bin/)?(?:sh|bash|zsh|cmd(?:\.exe)?|powershell(?:\.exe)?)\b",
    ),
    rx(
        "reverse_shell_python",
        "Python socket/dup2 shell",
        "remote_control",
        100,
        r"socket\.socket\s*\([^)]*\).*?\.connect\s*\([^)]*\).*?os\.dup2\s*\(.*?(?:subprocess\.(?:call|Popen)|os\.(?:system|execv|execl)).{0,180}?(?:/bin/)?(?:sh|bash)",
        re.IGNORECASE | re.DOTALL,
        2,
    ),
    rx(
        "reverse_shell_powershell",
        "PowerShell TCP client command loop",
        "remote_control",
        100,
        r"System\.Net\.Sockets\.TCPClient.{0,1400}?(?:Invoke-Expression|\bIEX\b|cmd\.exe\s*/c)",
        re.IGNORECASE | re.DOTALL,
        2,
    ),
    rx(
        "reverse_shell_perl_ruby_php",
        "Scripting-language reverse shell",
        "remote_control",
        95,
        r"(?:IO::Socket::INET|TCPSocket\.open|fsockopen\s*\()[\s\S]{0,800}?(?:exec\s*\(|system\s*\(|/bin/(?:sh|bash))",
        re.IGNORECASE,
        2,
    ),

    # Sensitive material collection.
    rx(
        "ssh_private_key_read",
        "SSH private-key path access",
        "credential_access",
        55,
        r"(?:\.ssh[/\\](?:id_(?:rsa|dsa|ecdsa|ed25519)|config)|BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY)",
    ),
    rx(
        "cloud_credentials_read",
        "Cloud/package credential-store access",
        "credential_access",
        55,
        r"(?:\.aws[/\\]credentials|\.azure[/\\]|\.config[/\\]gcloud|application_default_credentials\.json|\.npmrc|\.pypirc|\.netrc|NuGet\.Config)",
    ),
    rx(
        "browser_secret_store_read",
        "Browser cookie/password database access",
        "credential_access",
        65,
        r"(?:Chrome|Chromium|Brave|Edge|Firefox)[^\n]{0,160}(?:Cookies|Login Data|logins\.json|key4\.db|Local State)|(?:Cookies|Login Data|logins\.json|key4\.db)[^\n]{0,160}(?:Chrome|Chromium|Brave|Edge|Firefox)",
    ),
    rx(
        "wallet_secret_read",
        "Cryptocurrency wallet/seed material access",
        "credential_access",
        65,
        r"(?:wallet\.dat|keystore[/\\].*UTC--|metamask|phantom|solflare|electrum|exodus|mnemonic|seed[_ -]?phrase|private[_ -]?key)[^\n]{0,180}(?:readFile|open\s*\(|read_to_string|sqlite|cookies?|storage|decrypt)",
    ),
    rx(
        "secret_env_collection",
        "Collection of secret-bearing environment variables",
        "credential_access",
        38,
        r"(?:process\.env|os\.environ|getenv\s*\(|Environment\.GetEnvironmentVariable)[^\n]{0,180}(?:TOKEN|SECRET|PASSWORD|PASSWD|API[_-]?KEY|PRIVATE[_-]?KEY|ACCESS[_-]?KEY|AUTH|COOKIE)",
    ),
    rx(
        "bulk_env_collection",
        "Bulk environment-variable enumeration",
        "credential_access",
        30,
        r"(?:Object\.(?:entries|keys)\s*\(\s*process\.env|dict\s*\(\s*os\.environ|os\.environ\.items\s*\(|Environment\.GetEnvironmentVariables\s*\()",
    ),
    rx(
        "history_collection",
        "Shell/terminal history collection",
        "credential_access",
        45,
        r"(?:\.bash_history|\.zsh_history|ConsoleHost_history\.txt|fish_history|PSReadLine)[^\n]{0,120}(?:read|open|copy|upload|send)",
    ),

    # Exfiltration and suspicious external channels.
    rx(
        "discord_webhook",
        "Discord webhook endpoint",
        "exfiltration",
        70,
        r"https?://(?:canary\.|ptb\.)?discord(?:app)?\.com/api/webhooks/[0-9]{5,}/[A-Za-z0-9._-]{20,}",
        re.IGNORECASE,
    ),
    rx(
        "slack_webhook",
        "Slack incoming webhook endpoint",
        "exfiltration",
        65,
        r"https?://hooks\.slack\.com/services/[A-Za-z0-9/_-]{20,}",
        re.IGNORECASE,
    ),
    rx(
        "telegram_bot_api",
        "Telegram bot API transmission",
        "exfiltration",
        55,
        r"https?://api\.telegram\.org/bot[^\s'\"`/]+/(?:sendMessage|sendDocument|sendPhoto|sendAudio|sendVideo)",
        re.IGNORECASE,
    ),
    rx(
        "webhook_post",
        "Generic webhook POST/upload",
        "exfiltration",
        38,
        r"(?:fetch|axios\.(?:post|put)|requests\.(?:post|put)|httpx\.(?:post|put)|urllib\.request|Invoke-RestMethod|curl\b)[^\n]{0,220}(?:webhook|upload|exfil|collect|telemetry)",
    ),
    rx(
        "sensitive_http_post",
        "Sensitive-looking data sent over HTTP",
        "exfiltration",
        55,
        r"(?:fetch\s*\(|axios\.(?:post|put)\s*\(|requests\.(?:post|put)\s*\(|httpx\.(?:post|put)\s*\()[\s\S]{0,700}?(?:token|secret|password|privateKey|private_key|mnemonic|cookie|authorization|process\.env|os\.environ)",
        re.IGNORECASE,
        3,
    ),
    rx(
        "dns_exfil",
        "Potential DNS-based exfiltration",
        "exfiltration",
        60,
        r"(?:dns\.(?:resolve|lookup)|socket\.gethostbyname|Resolve-DnsName|nslookup)[^\n]{0,260}(?:base64|hex|token|secret|password|key|chunk)",
    ),

    # Remote download, dynamic execution and supply-chain behaviours.
    rx(
        "download_pipe_shell",
        "Remote content piped directly into a shell",
        "remote_execution",
        95,
        r"(?:curl|wget)\b[^\n|;]{0,320}(?:\||;\s*)(?:sudo\s+)?(?:bash|sh|zsh|dash|ksh|powershell|pwsh)\b",
    ),
    rx(
        "powershell_download_exec",
        "PowerShell download-and-execute",
        "remote_execution",
        95,
        r"(?:Invoke-WebRequest|iwr\b|Net\.WebClient|DownloadString|DownloadFile)[\s\S]{0,500}?(?:Invoke-Expression|\bIEX\b|Start-Process|&\s*\$|powershell\s+-enc)",
        re.IGNORECASE,
        3,
    ),
    rx(
        "certutil_bitsadmin_exec",
        "Windows LOLBin download/execute chain",
        "remote_execution",
        90,
        r"(?:certutil\b[^\n]{0,220}-urlcache|bitsadmin\b[^\n]{0,220}/transfer)[\s\S]{0,500}?(?:Start-Process|cmd\s*/c|powershell|\.exe\b)",
        re.IGNORECASE,
        3,
    ),
    rx(
        "download_then_execute",
        "Downloaded artifact subsequently executed",
        "remote_execution",
        75,
        r"(?:download|fetch|axios|get\s*\(|request\s*\(|urllib|requests\.get|httpx\.get)[\s\S]{0,1000}?(?:chmod\s+\+x|child_process\.(?:exec|spawn)|subprocess\.(?:run|Popen|call)|os\.system|Start-Process|execFile)",
        re.IGNORECASE,
        3,
    ),
    rx(
        "remote_dynamic_eval",
        "Remote response passed to dynamic evaluation",
        "remote_execution",
        95,
        r"(?:fetch\s*\(|axios\.|requests\.get|httpx\.get|urllib\.request|DownloadString)[\s\S]{0,900}?(?:\beval\s*\(|new\s+Function\s*\(|\bexec\s*\(|Invoke-Expression|\bIEX\b)",
        re.IGNORECASE,
        3,
    ),
    rx(
        "encoded_dynamic_exec",
        "Encoded/obfuscated payload dynamically executed",
        "obfuscation",
        80,
        r"(?:eval\s*\(|new\s+Function\s*\(|\bexec\s*\()[\s\S]{0,500}?(?:atob\s*\(|Buffer\.from\s*\([^)]*base64|base64\.b64decode|binascii\.unhexlify|FromBase64String|marshal\.loads|zlib\.decompress)",
        re.IGNORECASE,
        4,
    ),
    rx(
        "long_encoded_blob",
        "Large encoded payload embedded in executable source",
        "obfuscation",
        28,
        r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{800,}={0,2}(?![A-Za-z0-9+/=])",
        re.ASCII,
        2,
    ),
    rx(
        "javascript_function_constructor",
        "JavaScript Function constructor",
        "dynamic_execution",
        30,
        r"\b(?:new\s+)?Function\s*\([^)]{0,300}\)",
    ),
    rx(
        "python_pickle_untrusted",
        "Potential untrusted pickle/marshal deserialization",
        "dynamic_execution",
        38,
        r"(?:pickle\.loads?|marshal\.loads?|yaml\.load\s*\()[^\n]{0,220}(?:request|response|socket|download|body|data|input)",
    ),

    # Persistence and system modification.
    rx(
        "authorized_keys_write",
        "SSH authorized_keys modification",
        "persistence",
        90,
        r"authorized_keys[^\n]{0,220}(?:append|write|echo|tee|Add-Content|Set-Content|writeFile)",
    ),
    rx(
        "cron_persistence",
        "Cron persistence installation",
        "persistence",
        65,
        r"(?:crontab\s+-[el]|/etc/(?:cron\.|crontab)|cron\.d)[^\n]{0,300}(?:curl|wget|python|node|bash|sh|@reboot)",
    ),
    rx(
        "systemd_persistence",
        "Systemd service persistence",
        "persistence",
        55,
        r"(?:/etc/systemd/system|systemctl\s+(?:enable|daemon-reload)|WantedBy=multi-user\.target)[\s\S]{0,500}?(?:ExecStart|enable|daemon-reload)",
        re.IGNORECASE,
        3,
    ),
    rx(
        "launch_agent_persistence",
        "macOS LaunchAgent/LaunchDaemon persistence",
        "persistence",
        60,
        r"(?:Library/LaunchAgents|Library/LaunchDaemons|launchctl\s+(?:load|bootstrap)|RunAtLoad)[\s\S]{0,500}?(?:ProgramArguments|launchctl|RunAtLoad)",
        re.IGNORECASE,
        3,
    ),
    rx(
        "windows_run_key",
        "Windows Run/Startup persistence",
        "persistence",
        65,
        r"(?:CurrentVersion\\Run(?:Once)?|Startup\\|schtasks\b[^\n]{0,220}/create)[^\n]{0,260}(?:reg\s+add|Set-ItemProperty|copy|create)",
    ),
    rx(
        "shell_profile_modify",
        "Shell profile/startup-file modification",
        "persistence",
        38,
        r"(?:\.bashrc|\.zshrc|\.profile|config\.fish|Microsoft\.PowerShell_profile\.ps1)[^\n]{0,220}(?:append|write|echo|tee|Add-Content|Set-Content)",
    ),

    # Defence evasion, destructive and monetisation payloads.
    rx(
        "disable_security_controls",
        "Security control disabling/exclusion",
        "defense_evasion",
        90,
        r"(?:Set-MpPreference\b[^\n]{0,220}(?:DisableRealtimeMonitoring|ExclusionPath)|netsh\s+advfirewall\s+set\s+allprofiles\s+state\s+off|systemctl\s+(?:stop|disable)\s+(?:firewalld|ufw|apparmor)|ufw\s+disable)",
    ),
    rx(
        "kill_security_process",
        "Security/monitoring process termination",
        "defense_evasion",
        65,
        r"(?:taskkill|pkill|killall|Stop-Process)[^\n]{0,180}(?:defender|antivirus|crowdstrike|falcon|sentinel|elastic-agent|osquery|sysmon|wireshark|tcpdump)",
    ),
    rx(
        "crypto_miner",
        "Cryptocurrency miner/pool configuration",
        "resource_abuse",
        100,
        r"(?:\bxmrig\b|stratum\+(?:tcp|ssl)://|(?:monero|xmr)[-_ ]?(?:miner|pool)|pool\.(?:supportxmr|minexmr)|cryptonight)",
    ),
    rx(
        "destructive_wipe",
        "Destructive filesystem/disk wipe",
        "destructive_action",
        100,
        r"(?:rm\s+-rf\s+(?:/|~|\$HOME)(?:\s|$)|mkfs\.[a-z0-9]+\s+/dev/|dd\s+if=/dev/(?:zero|urandom)\s+of=/dev/|Remove-Item\s+[^\n]{0,100}-Recurse[^\n]{0,100}-Force[^\n]{0,100}(?:C:\\|\$HOME))",
    ),
    rx(
        "ransom_encrypt_delete",
        "Mass encryption/deletion ransom pattern",
        "destructive_action",
        90,
        r"(?:walk|glob|readdir|find)[\s\S]{0,900}?(?:encrypt|Fernet|AES|ChaCha)[\s\S]{0,900}?(?:unlink|remove|delete|ransom|README_DECRYPT)",
        re.IGNORECASE,
        2,
    ),

    # Surveillance and privacy-sensitive capabilities.
    rx(
        "keyboard_capture",
        "Keyboard capture/hook capability",
        "surveillance",
        55,
        r"(?:pynput\.keyboard\.Listener|keyboard\.(?:on_press|hook)|SetWindowsHookEx\s*\([^\n]{0,100}WH_KEYBOARD|CGEventTapCreate[^\n]{0,160}kCGEventKeyDown|iohook\.(?:on|start))",
    ),
    rx(
        "screen_capture",
        "Screen capture capability",
        "surveillance",
        38,
        r"(?:pyautogui\.screenshot|ImageGrab\.grab|mss\s*\(|desktopCapturer\.getSources|getDisplayMedia\s*\(|screencapture\s+-|BitBlt\s*\()",
    ),
    rx(
        "clipboard_capture",
        "Clipboard read/monitor capability",
        "surveillance",
        32,
        r"(?:clipboard\.(?:readText|read|readSync)|pyperclip\.paste|Get-Clipboard|UIPasteboard\.general\.string|navigator\.clipboard\.readText)",
    ),
    rx(
        "microphone_capture",
        "Microphone/audio capture capability",
        "surveillance",
        32,
        r"(?:getUserMedia\s*\([^)]*audio|MediaRecorder\s*\(|pyaudio\.PyAudio|sounddevice\.(?:rec|InputStream)|arecord\b)",
    ),

    # Unauthenticated command execution / unsafe boundaries.
    rx(
        "http_input_to_shell_js",
        "HTTP request parameter passed to shell execution",
        "command_injection",
        80,
        r"(?:req\.(?:query|body|params)|request\.(?:args|form|json)|ctx\.(?:query|request\.body))[\s\S]{0,500}?(?:child_process\.(?:exec|spawn)|\bexec\s*\(|subprocess\.(?:run|Popen|call)|os\.system)",
        re.IGNORECASE,
        4,
    ),
    rx(
        "websocket_input_to_shell",
        "Socket/WebSocket message passed to command execution",
        "command_injection",
        80,
        r"(?:socket|websocket|ws)\.(?:on|recv|receive)[\s\S]{0,600}?(?:child_process\.(?:exec|spawn)|subprocess\.(?:run|Popen|call)|os\.system|Process\.Start)",
        re.IGNORECASE,
        3,
    ),
    rx(
        "python_shell_true",
        "Python subprocess with shell=True",
        "command_execution",
        32,
        r"subprocess\.(?:run|Popen|call|check_output|check_call)\s*\([^\n]{0,500}?shell\s*=\s*True",
    ),
    rx(
        "node_shell_exec",
        "Node.js shell command execution",
        "command_execution",
        22,
        r"(?:child_process\.)?(?:exec|execSync)\s*\(",
    ),
    rx(
        "generic_shell_spawn",
        "Explicit shell process spawn",
        "command_execution",
        32,
        r"(?:spawn|Popen|Process\.Start|Command::new)\s*\([^\n]{0,120}?(?:/bin/(?:sh|bash)|cmd(?:\.exe)?|powershell(?:\.exe)?|pwsh)",
    ),
    rx(
        "process_injection",
        "Process injection/memory manipulation",
        "defense_evasion",
        90,
        r"(?:VirtualAllocEx|WriteProcessMemory|CreateRemoteThread|NtCreateThreadEx|ptrace\s*\(|process_vm_writev)",
    ),

    # Transport/update weaknesses that matter when coupled with privileged code.
    rx(
        "tls_verification_disabled",
        "TLS certificate verification disabled",
        "insecure_transport",
        28,
        r"(?:verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED[^\n]{0,40}[=:]\s*['\"]?0|CURLOPT_SSL_VERIFYPEER[^\n]{0,50}(?:0|false)|ServerCertificateValidationCallback[^\n]{0,120}=>\s*true)",
    ),
    rx(
        "unsigned_self_update",
        "Self-update/downloader without visible integrity check",
        "supply_chain",
        40,
        r"(?:self[-_ ]?update|auto[-_ ]?update|downloadLatest|latestRelease)[\s\S]{0,700}?(?:writeFile|rename|chmod|execFile|spawn|Start-Process|replace)",
        re.IGNORECASE,
        3,
    ),
    rx(
        "package_manager_global_install",
        "Runtime global package installation",
        "supply_chain",
        28,
        r"(?:npm|pnpm|yarn)\s+(?:install|add)\s+(?:-g|--global)|pip\s+install[^\n]{0,120}(?:--user|--target|git\+https)|cargo\s+install",
    ),
)


# Paths considered executable or security-relevant.  Documentation and test
# paths are retained only as low-priority context, preventing example payloads
# from being reported as production backdoors.
SOURCE_EXTENSIONS = {
    ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts",
    ".py", ".pyw", ".sh", ".bash", ".zsh", ".fish", ".ps1", ".psm1",
    ".bat", ".cmd", ".rb", ".php", ".pl", ".lua", ".go", ".rs",
    ".java", ".kt", ".kts", ".scala", ".cs", ".c", ".cc", ".cpp",
    ".cxx", ".h", ".hpp", ".swift", ".sol", ".ex", ".exs", ".clj",
    ".cljs", ".groovy", ".r", ".dart", ".vb", ".vbs", ".fs", ".fsx",
    ".toml", ".yaml", ".yml", ".json", ".ini", ".cfg", ".conf",
    ".properties", ".xml", ".gradle", ".mk", ".make", ".dockerfile",
}

IMPORTANT_BASENAMES = {
    "package.json", "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
    "cargo.toml", "go.mod", "gemfile", "composer.json", "dockerfile",
    "makefile", "justfile", "taskfile.yml", "taskfile.yaml", "manifest.json",
    "plugin.json", "dsh.json", "cordis.patch.yml", "cordis.patch.yaml",
    "install.sh", "install.ps1", "install.bat", "bootstrap.sh", "postinstall.js",
    "preinstall.js", "entrypoint.sh", "entrypoint.ps1", "deno.json", "bunfig.toml",
}

SKIP_DIR_PARTS = {
    ".git", "node_modules", ".pnpm", ".yarn", "vendor", "third_party",
    "third-party", "target", "coverage", ".next", ".nuxt", ".cache",
    "__pycache__", ".venv", "venv", "site-packages", "pods", "deriveddata",
}

DOC_PARTS = {"docs", "doc", "documentation", "examples", "example", "samples", "sample"}
TEST_PARTS = {"test", "tests", "spec", "specs", "fixtures", "fixture", "mocks", "mock"}
GENERATED_PARTS = {"dist", "build", "out", "generated", "bundle", "bundles", "min", "release"}
SOURCE_DIR_PARTS = {"src", "lib", "app", "server", "client", "host", "plugin", "plugins", "scripts", "bin", "cmd", "internal", "packages"}
DSH_PATH_KEYWORDS = ("dsh", "deepseek", "harness", "cordis", "plugin", "skill")
