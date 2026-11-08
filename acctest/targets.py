"""Target servers and how to reach them.

Three transports, one interface:
  ssh   - Linux over OpenSSH (key auth). Scripts are sent on stdin (`bash -s`), never quoted into the command line.
  pct   - a Proxmox LXC container reached through the node (`ssh node 'pct exec <vmid> -- bash -s'`). No SSH inside
          the container is needed; files travel with scp to the node and `pct push`.
  winrm - Windows over WinRM (pywinrm). Files are uploaded in base64 chunks through PowerShell.

Every transport returns a CmdResult(rc, out, err) and never raises for a non-zero exit code.
"""
from __future__ import annotations

import base64
import logging
import shlex
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path

from .config import PROJECT_ROOT, Settings, TargetSpec
from .util import expand_path

LOG = logging.getLogger("acctest.targets")
STATE_DIR = PROJECT_ROOT / ".state"
CR, LF = chr(13), chr(10)


@dataclass
class CmdResult:
    rc: int
    out: str
    err: str = ""

    @property
    def ok(self) -> bool:
        return self.rc == 0

    def text(self, limit: int = 4000) -> str:
        t = (self.out or "") + (("\n[stderr] " + self.err) if self.err and self.err.strip() else "")
        return t if len(t) <= limit else t[:limit] + f"\n... ({len(t) - limit} more chars)"


class Transport:
    family = "linux"

    def run(self, script: str, timeout: int = 300) -> CmdResult:  # pragma: no cover - interface
        raise NotImplementedError

    def put(self, local: Path, remote: str, timeout: int = 600) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def describe(self) -> str:  # pragma: no cover - interface
        return self.__class__.__name__


def _ssh_base(key: str, port: int = 0, extra: str = "") -> list[str]:
    STATE_DIR.mkdir(exist_ok=True)
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "StrictHostKeyChecking=accept-new",
           "-o", f"UserKnownHostsFile={STATE_DIR / 'known_hosts'}", "-o", "ServerAliveInterval=30"]
    if key:
        cmd += ["-i", str(expand_path(key))]
    if port:
        cmd += ["-p", str(port)]
    if extra:
        cmd += shlex.split(extra)
    return cmd


def _scp_base(key: str, port: int = 0, extra: str = "") -> list[str]:
    STATE_DIR.mkdir(exist_ok=True)
    cmd = ["scp", "-q", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "StrictHostKeyChecking=accept-new",
           "-o", f"UserKnownHostsFile={STATE_DIR / 'known_hosts'}"]
    if key:
        cmd += ["-i", str(expand_path(key))]
    if port:
        cmd += ["-P", str(port)]
    if extra:
        cmd += shlex.split(extra)
    return cmd


def _run(cmd: list[str], timeout: int, stdin_text: str | None = None) -> CmdResult:
    """Run a local command. The script goes in as BYTES: in text mode Windows turns every line feed into CR LF and
    bash on the target then fails with a CR syntax error on the first line."""
    LOG.debug("exec: %s", " ".join(cmd[:6]) + (" ..." if len(cmd) > 6 else ""))
    data = stdin_text.replace(CR + LF, LF).encode("utf-8") if stdin_text is not None else None
    try:
        cp = subprocess.run(cmd, input=data, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else ""
        return CmdResult(124, out, f"timeout after {timeout}s")
    except FileNotFoundError as e:
        return CmdResult(127, "", f"{cmd[0]} not found on this machine: {e}")
    err = cp.stderr.decode("utf-8", "replace")
    # ssh's own chatter is not the target's stderr: host-key notices and OpenSSH 10's post-quantum warning banner
    err = LF.join(l for l in err.splitlines() if not (l.startswith("** ") or l.startswith("Warning: Permanently added")))
    return CmdResult(cp.returncode, cp.stdout.decode("utf-8", "replace"), err)


class SSHTransport(Transport):
    def __init__(self, host: str, user: str, key: str, port: int = 0, options: str = ""):
        self.host, self.user, self.key, self.port, self.options = host, user, key, port, options

    def describe(self) -> str:
        return f"ssh {self.user}@{self.host}"

    def run(self, script: str, timeout: int = 300) -> CmdResult:
        # The whole script travels on stdin: no quoting problems, any length.
        cmd = _ssh_base(self.key, self.port, self.options) + [f"{self.user}@{self.host}", "bash -s"]
        return _run(cmd, timeout, script if script.endswith(LF) else script + LF)

    def put(self, local: Path, remote: str, timeout: int = 600) -> None:
        cmd = _scp_base(self.key, self.port, self.options) + [str(local), f"{self.user}@{self.host}:{remote}"]
        r = _run(cmd, timeout)
        if not r.ok:
            raise RuntimeError(f"scp to {self.host} failed: {r.err.strip() or r.out.strip()}")


class PctTransport(Transport):
    """A Proxmox container reached through its node. `pct exec` passes stdin through, so `bash -s` works."""

    def __init__(self, pve_host: str, pve_user: str, pve_key: str, vmid: int):
        self.pve_host, self.pve_user, self.pve_key, self.vmid = pve_host, pve_user, pve_key, vmid

    def describe(self) -> str:
        return f"pct {self.vmid} via {self.pve_user}@{self.pve_host}"

    def _node(self, remote_cmd: str, timeout: int, stdin_text: str | None = None) -> CmdResult:
        cmd = _ssh_base(self.pve_key) + [f"{self.pve_user}@{self.pve_host}", remote_cmd]
        return _run(cmd, timeout, stdin_text)

    def run(self, script: str, timeout: int = 300) -> CmdResult:
        return self._node(f"pct exec {self.vmid} -- bash -s", timeout, script if script.endswith(LF) else script + LF)

    def put(self, local: Path, remote: str, timeout: int = 600) -> None:
        tmp = f"/tmp/acctest-{uuid.uuid4().hex[:8]}-{local.name}"
        cmd = _scp_base(self.pve_key) + [str(local), f"{self.pve_user}@{self.pve_host}:{tmp}"]
        r = _run(cmd, timeout)
        if not r.ok:
            raise RuntimeError(f"scp to node {self.pve_host} failed: {r.err.strip()}")
        r = self._node(f"pct push {self.vmid} {tmp} {remote} && rm -f {tmp}", timeout)
        if not r.ok:
            raise RuntimeError(f"pct push into {self.vmid} failed: {r.err.strip() or r.out.strip()}")

    def node_run(self, remote_cmd: str, timeout: int = 300) -> CmdResult:
        return self._node(remote_cmd, timeout)


class WinRMTransport(Transport):
    """Windows over WinRM. Needs `pip install pywinrm`; the user must be a local administrator."""
    family = "windows"

    def __init__(self, host: str, user: str, password: str, port: int = 5985, use_ssl: bool = False,
                 transport: str = "ntlm"):
        self.host, self.user, self.password, self.port, self.use_ssl, self.transport = host, user, password, port, use_ssl, transport
        self._session = None

    def describe(self) -> str:
        return f"winrm {self.user}@{self.host}:{self.port}"

    def _s(self):
        if self._session is None:
            import winrm  # type: ignore
            scheme = "https" if self.use_ssl else "http"
            self._session = winrm.Session(f"{scheme}://{self.host}:{self.port}/wsman", auth=(self.user, self.password),
                                          transport=self.transport, server_cert_validation="ignore",
                                          read_timeout_sec=600, operation_timeout_sec=540)
        return self._session

    def run(self, script: str, timeout: int = 300) -> CmdResult:
        try:
            r = self._s().run_ps(script)
        except Exception as e:  # connection problems
            return CmdResult(255, "", f"winrm error: {e}")
        return CmdResult(r.status_code, r.std_out.decode("utf-8", "replace"), r.std_err.decode("utf-8", "replace"))

    def put(self, local: Path, remote: str, timeout: int = 1800) -> None:
        data = local.read_bytes()
        chunk = 512 * 1024
        first = True
        for i in range(0, len(data), chunk):
            b64 = base64.b64encode(data[i:i + chunk]).decode()
            mode = "Create" if first else "Append"
            ps = (f"$b=[Convert]::FromBase64String('{b64}'); "
                  f"$f=[System.IO.File]::Open('{remote}', [System.IO.FileMode]::{mode}); "
                  f"$f.Write($b,0,$b.Length); $f.Close()")
            r = self.run(ps, timeout)
            if not r.ok:
                raise RuntimeError(f"winrm upload failed at offset {i}: {r.err.strip()}")
            first = False


def _clean_clixml(err: str) -> str:
    """PowerShell over a non-console host serialises stderr as CLIXML (progress records such as 'Preparing modules for
    first use' included). Keep only the error strings."""
    if "CLIXML" not in err and "<Objs" not in err:
        return err
    import html as _html
    import re as _re
    msgs = _re.findall(r'<S S="Error">(.*?)</S>', err, _re.S)
    return LF.join(_html.unescape(m).replace("_x000D__x000A_", LF).strip() for m in msgs if m.strip())


class WinSSHTransport(Transport):
    """Windows over OpenSSH (Windows Server 2019+ ships it; common where WinRM is closed). The script travels on stdin
    to `powershell -Command -`, so quoting and length are no concern. The account must be a local administrator."""
    family = "windows"

    def __init__(self, host: str, user: str, key: str, port: int = 0, options: str = ""):
        self.host, self.user, self.key, self.port, self.options = host, user, key, port, options

    def describe(self) -> str:
        return f"ssh(windows) {self.user}@{self.host}"

    def run(self, script: str, timeout: int = 300) -> CmdResult:
        # -EncodedCommand carries the whole script in the command line: `-Command -` (stdin) silently drops output of
        # some multi-statement scripts (a `$x = Get-Date` followed by a loop produced nothing). The command line is
        # limited to ~32k characters, so very long scripts (the base64 upload chunks) still go over stdin as one statement.
        enc = base64.b64encode(script.encode("utf-16-le")).decode()
        if len(enc) < 28000:
            cmd = _ssh_base(self.key, self.port, self.options) + [f"{self.user}@{self.host}",
                                                                    f"powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand {enc}"]
            r = _run(cmd, timeout)
        else:
            cmd = _ssh_base(self.key, self.port, self.options) + [f"{self.user}@{self.host}",
                                                                    "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command -"]
            body = script.replace(CR + LF, LF).replace(LF, CR + LF)
            r = _run(cmd, timeout, body if body.endswith(LF) else body + CR + LF)
        return CmdResult(r.rc, r.out, _clean_clixml(r.err))

    def put(self, local: Path, remote: str, timeout: int = 1800) -> None:
        # scp first (Windows OpenSSH ships scp); fall back to base64 chunks through the shell when it is missing
        cmd = _scp_base(self.key, self.port, self.options) + [str(local), f"{self.user}@{self.host}:{remote}"]
        r = _run(cmd, timeout)
        if r.ok:
            return
        LOG.info("  scp to %s failed (%s) - uploading through PowerShell instead", self.host, (r.err or r.out).strip()[:80])
        data = local.read_bytes()
        chunk = 512 * 1024
        first = True
        for i in range(0, len(data), chunk):
            b64 = base64.b64encode(data[i:i + chunk]).decode()
            mode = "Create" if first else "Append"
            ps = (f"$b=[Convert]::FromBase64String('{b64}'); $f=[System.IO.File]::Open('{remote}', [System.IO.FileMode]::{mode}); "
                  f"$f.Write($b,0,$b.Length); $f.Close()")
            rr = self.run(ps, timeout)
            if not rr.ok:
                raise RuntimeError(f"upload to {self.host} failed at offset {i}: {rr.err.strip()[:200]}")
            first = False


def make_transport(t: TargetSpec, settings: Settings) -> Transport:
    if t.transport == "pct":
        return PctTransport(t.pve_host or settings.pve_host, settings.pve_user, settings.pve_ssh_key, int(t.vmid))
    if t.transport == "winrm":
        return WinRMTransport(t.host, t.user, t.password, t.port or 5985, use_ssl=bool(t.labels.get("winrm_ssl")),
                              transport=t.labels.get("winrm_transport", "ntlm"))
    if t.family == "windows":   # transport ssh on a Windows target = OpenSSH with PowerShell
        return WinSSHTransport(t.host, t.user or "Administrator", t.ssh_key or settings.target_ssh_key, t.port, settings.target_ssh_options)
    return SSHTransport(t.host, t.user or settings.target_ssh_user, t.ssh_key or settings.target_ssh_key, t.port,
                        settings.target_ssh_options)


# ---- probing ------------------------------------------------------------------------------------------------------
LINUX_PROBE = r"""
set +e
. /etc/os-release 2>/dev/null
echo "ID=$ID"; echo "ID_LIKE=$ID_LIKE"; echo "VERSION_ID=$VERSION_ID"; echo "PRETTY=$PRETTY_NAME"
echo "ARCH=$(uname -m)"; echo "HOST=$(hostname)"; echo "FQDN=$(hostname -f 2>/dev/null)"
echo "IP=$(hostname -I 2>/dev/null | awk '{print $1}')"
echo "KERNEL=$(uname -r)"; echo "NPROC=$(nproc 2>/dev/null)"; echo "MEM_MB=$(awk '/MemTotal/ {printf "%d", $2/1024}' /proc/meminfo)"
echo "USER=$(id -un)"; echo "SUDO=$(command -v sudo)"; echo "CURL=$(command -v curl)"; echo "WGET=$(command -v wget)"
echo "GPG=$(command -v gpg)"; echo "DPKG=$(command -v dpkg)"; echo "RPM=$(command -v rpm)"; echo "SYSTEMCTL=$(command -v systemctl)"
echo "SERIAL=$(cat /sys/class/dmi/id/product_serial 2>/dev/null)"
echo "UUID=$(cat /sys/class/dmi/id/product_uuid 2>/dev/null)"
echo "CONTAINER=$(systemd-detect-virt -c 2>/dev/null)"
echo "ACC_INSTALLED=$( (command -v /usr/share/servicenow/agent-client-collector/bin/acc >/dev/null && echo yes) || echo no)"
"""

WINDOWS_PROBE = r"""
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
"ID=windows"; "VERSION_ID=$($os.Version)"; "PRETTY=$($os.Caption)"; "ARCH=$($env:PROCESSOR_ARCHITECTURE)"
"HOST=$($env:COMPUTERNAME)"; "FQDN=$([System.Net.Dns]::GetHostByName($env:COMPUTERNAME).HostName)"
"IP=$((Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' } | Select-Object -First 1).IPAddress)"
"NPROC=$($cs.NumberOfLogicalProcessors)"; "MEM_MB=$([int]($cs.TotalPhysicalMemory/1MB))"
"USER=$($env:USERNAME)"
"ACC_INSTALLED=$(if (Get-Service -Name AgentClientCollector -ErrorAction SilentlyContinue) { 'yes' } else { 'no' })"
"""


def probe(tr: Transport, family: str) -> dict:
    """Return the target's OS facts as a dict (ID, VERSION_ID, ARCH, HOST, ...)."""
    r = tr.run(WINDOWS_PROBE if family == "windows" else LINUX_PROBE, timeout=120)
    facts: dict = {"_rc": r.rc, "_err": r.err.strip()}
    for line in (r.out or "").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            facts[k.strip()] = v.strip().strip('"')
    return facts


def pkg_kind(facts: dict) -> str:
    """deb | rpm | msi from probe facts, mirroring the instance install script's distro logic."""
    osid = (facts.get("ID") or "").lower()
    like = (facts.get("ID_LIKE") or "").lower()
    if osid == "windows":
        return "msi"
    if osid in ("ubuntu", "debian") or "debian" in like or "ubuntu" in like:
        return "deb"
    if osid in ("rhel", "centos", "redhat", "sles", "amzn", "ol", "rocky", "almalinux", "fedora", "opensuse-leap",
                "opensuse", "sled") or "rhel" in like or "centos" in like or "suse" in like or "fedora" in like:
        return "rpm"
    return ""


def distro_label(facts: dict) -> str:
    return facts.get("PRETTY") or f"{facts.get('ID', '?')} {facts.get('VERSION_ID', '')}".strip()
