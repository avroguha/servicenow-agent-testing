"""Configuration: everything comes from the .env file (or real environment variables, which win).

The .env format is deliberately simple: KEY=VALUE, '#' comments, optional single/double quotes around the value.
No value is ever hard-coded here - a company run and a home-lab run differ only by their .env and targets.yml.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .util import expand_path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
_QUOTES = ('"', "'")


def parse_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _LINE.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        if len(val) >= 2 and val[0] in _QUOTES and val[-1] == val[0]:
            val = val[1:-1]
        else:
            # strip a trailing inline comment ("value   # note")
            val = re.sub(r"\s+#.*$", "", val)
        out[key] = val
    return out


def _bool(v: str | None, default: bool = False) -> bool:
    if v is None or v == "":
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")


def _int(v: str | None, default: int) -> int:
    try:
        return int(str(v).strip()) if v not in (None, "") else default
    except ValueError:
        return default


def _float(v: str | None, default: float) -> float:
    try:
        return float(str(v).strip()) if v not in (None, "") else default
    except ValueError:
        return default


def _list(v: str | None) -> list[str]:
    if not v:
        return []
    return [x.strip() for x in re.split(r"[,\s]+", v) if x.strip()]


@dataclass
class Settings:
    """Typed view of the .env. Field names mirror the variable names in .env.example (lower-cased)."""
    env_path: Path
    raw: dict[str, str] = field(default_factory=dict)

    # ServiceNow
    sn_instance: str = ""
    sn_user: str = ""
    sn_pass: str = ""
    sn_verify_tls: bool = True
    sn_ui_login: bool = True
    sn_timeout_s: int = 120

    # MID Server the agents connect through
    mid_server_name: str = ""
    mid_host: str = ""
    mid_ws_port: int = 8800
    mid_auto_configure: bool = False
    mid_ws_extension_name: str = "ACC WebSocket Server"

    # ACC API key
    acc_api_key: str = ""
    acc_api_key_name: str = "acc-agent-testing"
    acc_api_key_auto_create: bool = False

    # Agent versions / packages
    agent_version: str = "latest"
    agent_download_dir: Path = PROJECT_ROOT / "dist"
    agent_download: bool = True
    agent_install_mode: str = "package"
    agent_verify_plugin_signature: str = ""   # "" leave the agent default (true) | "false" | "true" - written into acc.yml at install
    plugin_signing_key: str = ""     # PEM private key that signs custom plugin archives (fixtures); empty in lab mode = generated in .state/signing
    plugin_signing_cert: str = ""    # its certificate (PEM); must chain to a root the HOSTS trust (internal CA at the company)
    plugin_signing_ca: str = ""      # the root/intermediate to install on targets when TRUST_SIGNING_CERT_ON_TARGETS (lab: generated root)
    trust_signing_cert_on_targets: bool = False   # lab: install that certificate into each target's OS trust store at install time
    mid_ssh_target: str = ""   # how to copy files onto the MID host: user@host (TARGET_SSH_KEY) or pct:<vmid> (Proxmox container); empty = manual
    mid_home: str = ""         # MID Server installation directory on that host, e.g. /opt/servicenow/mid or C:\ServiceNow\mid

    # Targets
    targets_file: Path = PROJECT_ROOT / "targets.yml"
    target_ssh_key: str = ""
    target_ssh_user: str = "root"
    target_ssh_options: str = ""
    target_os_filter: list[str] = field(default_factory=list)

    # Home lab (Proxmox)
    lab_mode: str = "none"
    pve_host: str = ""
    pve_user: str = "root"
    pve_ssh_key: str = ""
    lab_vmid_base: int = 9520
    lab_os_list: list[str] = field(default_factory=list)
    lab_ct_memory_mb: int = 1024
    lab_ct_cores: int = 2
    lab_ct_disk_gb: int = 8
    lab_bridge: str = "vmbr0"
    lab_storage: str = "local-lvm"
    lab_nameservers: str = "1.1.1.1"
    lab_destroy_after: bool = False
    lab_hostname_prefix: str = "acc"

    # Test tuning
    agent_up_timeout_s: int = 600
    discovery_timeout_s: int = 900
    check_timeout_s: int = 300
    check_filter: list[str] = field(default_factory=list)
    include_custom_checks: bool = True
    include_oob_checks: bool = True
    run_policies: bool = True
    cpu_sample_seconds: int = 60
    cpu_tolerance_pct: float = 5.0
    cleanup_grace_s: int = 120
    uninstall_after: bool = False
    stop_on_install_failure: bool = False

    # Reporting / browser
    results_dir: Path = PROJECT_ROOT / "results"
    browser_headless: bool = True
    browser_screenshots: bool = True
    browser_enabled: bool = True
    report_title: str = "ACC agent qualification"

    @classmethod
    def load(cls, env_path: Path | None = None) -> "Settings":
        env_path = env_path or Path(os.environ.get("ACCTEST_ENV", PROJECT_ROOT / ".env"))
        raw = parse_env_file(env_path)
        # real environment variables override the file (CI / one-off runs); only upper-case names are considered
        for k in [k for k in os.environ if k.isupper() and (k in raw or k.startswith(("SN_", "MID_", "ACC_", "AGENT_", "TARGET", "LAB_", "PVE_", "RESULTS_", "BROWSER_", "CHECK_", "CPU_", "REPORT_")))]:
            raw[k] = os.environ[k]
        g = raw.get
        s = cls(env_path=env_path, raw=raw)
        s.sn_instance = (g("SN_INSTANCE", "") or "").rstrip("/")
        s.sn_user = g("SN_USER", "")
        s.sn_pass = g("SN_PASS", "")
        s.sn_verify_tls = _bool(g("SN_VERIFY_TLS"), True)
        s.sn_ui_login = _bool(g("SN_UI_LOGIN"), True)
        s.sn_timeout_s = _int(g("SN_TIMEOUT_S"), 120)

        s.mid_server_name = g("MID_SERVER_NAME", "")
        s.mid_host = g("MID_HOST", "")
        s.mid_ws_port = _int(g("MID_WS_PORT"), 8800)
        s.mid_auto_configure = _bool(g("MID_AUTO_CONFIGURE"), False)
        s.mid_ws_extension_name = g("MID_WS_EXTENSION_NAME", "ACC WebSocket Server")

        s.acc_api_key = g("ACC_API_KEY", "")
        s.acc_api_key_name = g("ACC_API_KEY_NAME", "acc-agent-testing")
        s.acc_api_key_auto_create = _bool(g("ACC_API_KEY_AUTO_CREATE"), False)

        s.agent_version = g("AGENT_VERSION", "latest") or "latest"
        s.agent_download_dir = expand_path(g("AGENT_DOWNLOAD_DIR", str(PROJECT_ROOT / "dist")))
        s.agent_download = _bool(g("AGENT_DOWNLOAD"), True)
        s.agent_install_mode = (g("AGENT_INSTALL_MODE", "package") or "package").lower()
        s.agent_verify_plugin_signature = (g("AGENT_VERIFY_PLUGIN_SIGNATURE", "") or "").strip().lower()
        s.plugin_signing_key = g("PLUGIN_SIGNING_KEY", "") or ""
        s.plugin_signing_cert = g("PLUGIN_SIGNING_CERT", "") or ""
        s.plugin_signing_ca = g("PLUGIN_SIGNING_CA", "") or ""
        s.trust_signing_cert_on_targets = _bool(g("TRUST_SIGNING_CERT_ON_TARGETS"), False)
        s.mid_ssh_target = (g("MID_SSH_TARGET", "") or "").strip()
        s.mid_home = (g("MID_HOME", "") or "").strip().rstrip("/\\")

        s.targets_file = expand_path(g("TARGETS_FILE", str(PROJECT_ROOT / "targets.yml")))
        s.target_ssh_key = g("TARGET_SSH_KEY", "")
        s.target_ssh_user = g("TARGET_SSH_USER", "root")
        s.target_ssh_options = g("TARGET_SSH_OPTIONS", "")
        s.target_os_filter = _list(g("TARGET_OS_FILTER"))

        s.lab_mode = (g("LAB_MODE", "none") or "none").lower()
        s.pve_host = g("PVE_HOST", "")
        s.pve_user = g("PVE_USER", "root")
        s.pve_ssh_key = g("PVE_SSH_KEY", "")
        s.lab_vmid_base = _int(g("LAB_VMID_BASE"), 9520)
        s.lab_os_list = _list(g("LAB_OS_LIST"))
        s.lab_ct_memory_mb = _int(g("LAB_CT_MEMORY_MB"), 1024)
        s.lab_ct_cores = _int(g("LAB_CT_CORES"), 2)
        s.lab_ct_disk_gb = _int(g("LAB_CT_DISK_GB"), 8)
        s.lab_bridge = g("LAB_BRIDGE", "vmbr0")
        s.lab_storage = g("LAB_STORAGE", "local-lvm")
        s.lab_nameservers = g("LAB_NAMESERVERS", "1.1.1.1")
        s.lab_destroy_after = _bool(g("LAB_DESTROY_AFTER"), False)
        s.lab_hostname_prefix = g("LAB_HOSTNAME_PREFIX", "acc")

        s.agent_up_timeout_s = _int(g("AGENT_UP_TIMEOUT_S"), 600)
        s.discovery_timeout_s = _int(g("DISCOVERY_TIMEOUT_S"), 900)
        s.check_timeout_s = _int(g("CHECK_TIMEOUT_S"), 300)
        s.check_filter = _list(g("CHECK_FILTER"))
        s.include_custom_checks = _bool(g("INCLUDE_CUSTOM_CHECKS"), True)
        s.include_oob_checks = _bool(g("INCLUDE_OOB_CHECKS"), True)
        s.run_policies = _bool(g("RUN_POLICIES"), True)
        s.cpu_sample_seconds = _int(g("CPU_SAMPLE_SECONDS"), 60)
        s.cpu_tolerance_pct = _float(g("CPU_TOLERANCE_PCT"), 5.0)
        s.cleanup_grace_s = _int(g("CLEANUP_GRACE_S"), 120)
        s.uninstall_after = _bool(g("UNINSTALL_AFTER"), False)
        s.stop_on_install_failure = _bool(g("STOP_ON_INSTALL_FAILURE"), False)

        s.results_dir = expand_path(g("RESULTS_DIR", str(PROJECT_ROOT / "results")))
        s.browser_headless = _bool(g("BROWSER_HEADLESS"), True)
        s.browser_screenshots = _bool(g("BROWSER_SCREENSHOTS"), True)
        s.browser_enabled = _bool(g("BROWSER_ENABLED"), True)
        s.report_title = g("REPORT_TITLE", "ACC agent qualification")
        return s

    # ---- helpers -------------------------------------------------------------------------------------------------
    def require(self, *names: str) -> None:
        missing = [n for n in names if not getattr(self, n.lower(), None)]
        if missing:
            raise SystemExit("Missing required settings in %s: %s (see .env.example)"
                             % (self.env_path, ", ".join(n.upper() for n in missing)))

    def backend_url(self) -> str:
        """The MID WebSocket endpoint the agent connects to. The path matters: wss://host:port alone gets a 404 handshake
        ("handshake failed with status 404") and the agent never connects. Pre-flight replaces this with the endpoint
        URL the instance records for the listener when it can read it."""
        return f"wss://{self.mid_host}:{self.mid_ws_port}/ws/events"

    def write_back(self, key: str, value: str) -> None:
        """Persist a generated value (e.g. the API key) into the .env file, replacing the line if present."""
        lines = self.env_path.read_text(encoding="utf-8").splitlines() if self.env_path.exists() else []
        pat = re.compile(rf"^\s*(?:export\s+)?{re.escape(key)}\s*=")
        new = f'{key}="{value}"'
        for i, line in enumerate(lines):
            if pat.match(line):
                lines[i] = new
                break
        else:
            lines.append(new)
        self.env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.raw[key] = value

    def redacted(self) -> dict[str, str]:
        out = {}
        for k, v in sorted(self.raw.items()):
            if re.search(r"(PASS|PASSWORD|SECRET|TOKEN|API_KEY)$", k) and v:
                out[k] = "***"
            else:
                out[k] = v
        return out


# ---- targets.yml --------------------------------------------------------------------------------------------------
@dataclass
class TargetSpec:
    """One server the agent is installed on. Mirrors an entry in targets.yml."""
    name: str
    os: str                      # package key: linux-x86_64 | linux-aarch64 | windows-x86_64 (see agents.py)
    family: str = "linux"        # linux | windows
    host: str = ""               # IP / DNS name reachable from this machine (ssh / winrm). Empty for pct transport.
    transport: str = "ssh"       # ssh | pct | winrm
    user: str = ""
    password: str = ""           # winrm only (or ssh password if no key) - prefer keys
    ssh_key: str = ""
    port: int = 0
    vmid: int = 0                # pct transport: Proxmox container id
    pve_host: str = ""           # pct transport: Proxmox node (defaults to PVE_HOST)
    pkg: str = ""                # deb | rpm | msi | tar (auto-detected from the OS release when empty)
    arch: str = "x86_64"
    labels: dict = field(default_factory=dict)
    distro: str = ""             # filled by probe: ubuntu 24.04, rocky 9.4, windows server 2022 ...
    expected_ci_class: str = ""  # cmdb_ci_linux_server / cmdb_ci_win_server (auto)
    skip: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "TargetSpec":
        known = set(cls.__dataclass_fields__)
        clean = {k: v for k, v in d.items() if k in known}
        t = cls(**clean)
        if not t.family:
            t.family = "windows" if "win" in t.os.lower() else "linux"
        if not t.expected_ci_class:
            t.expected_ci_class = "cmdb_ci_win_server" if t.family == "windows" else "cmdb_ci_linux_server"
        return t

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v not in ("", 0, {}, None, False) or k in ("name", "os")}


def load_targets(settings: Settings) -> list[TargetSpec]:
    p = settings.targets_file
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    items = data.get("targets", []) if isinstance(data, dict) else data
    out = []
    for d in items:
        t = TargetSpec.from_dict(d)
        if not t.user:
            t.user = settings.target_ssh_user
        if not t.ssh_key:
            t.ssh_key = settings.target_ssh_key
        if t.transport == "pct" and not t.pve_host:
            t.pve_host = settings.pve_host
        out.append(t)
    if settings.target_os_filter:
        out = [t for t in out if t.os in settings.target_os_filter or t.name in settings.target_os_filter]
    return out


def save_targets(settings: Settings, targets: list[TargetSpec]) -> None:
    settings.targets_file.write_text(
        "# Generated by `python acctest.py lab provision` - edit freely; regenerate with the same command.\n"
        + yaml.safe_dump({"targets": [t.to_dict() for t in targets]}, sort_keys=False),
        encoding="utf-8",
    )
