"""Install, inspect and remove the ACC agent on a target.

Linux, two modes:
  script  - run the instance's own install script (dist/<version>/install_agent.sh) with ACC_API_KEY / ACC_MID in the
            environment. This is exactly what ServiceNow documents, but the target must reach install.service-now.com.
  package - push the package from dist/ (deb/rpm) and do what the script does after download: install, then
            `acc gateway mid -a <key> -b <url>`, copy the default allow-list, enable + start the `acc` service.
            Works with no internet on the target (company data centres).
Windows: push the MSI and run msiexec with the documented properties (ACC_API_KEY, ACC_MID).

Paths come from the install script: /etc/servicenow/agent-client-collector/acc.yml, binary
/usr/share/servicenow/agent-client-collector/bin/acc, log /var/log/servicenow/agent-client-collector/acc.log,
agent id /var/cache/servicenow/agent-client-collector/agent_now_id. Service name: acc.
"""
from __future__ import annotations

import logging
import shlex
from pathlib import Path

from .agents import AgentCatalog, local_install_script, local_package
from .config import Settings, TargetSpec
from .targets import CmdResult, Transport

LOG = logging.getLogger("acctest.installer")

ACC_NAME = "agent-client-collector"
ACC_CONF = f"/etc/servicenow/{ACC_NAME}/acc.yml"
ACC_BIN = f"/usr/share/servicenow/{ACC_NAME}/bin/acc"
ACC_LOG = f"/var/log/servicenow/{ACC_NAME}/acc.log"
ACC_AGENT_ID = f"/var/cache/servicenow/{ACC_NAME}/agent_now_id"
ACC_ALLOW_LIST = f"/etc/servicenow/{ACC_NAME}/check-allow-list.json"
REMOTE_TMP = "/tmp/acctest"
WIN_TMP = r"C:\Windows\Temp\acctest"
WIN_CONF = r"C:\ProgramData\ServiceNow\agent-client-collector\config\acc.yml"
WIN_LOG = r"C:\ProgramData\ServiceNow\agent-client-collector\log\acc.log"   # the service is 'AgentClientCollector' on Windows


class Installer:
    def __init__(self, target: TargetSpec, tr: Transport, facts: dict, settings: Settings, catalog: AgentCatalog):
        self.t, self.tr, self.facts, self.s, self.cat = target, tr, facts, settings, catalog
        self.windows = target.family == "windows"

    # ---- install -------------------------------------------------------------------------------------------------
    def install(self, api_key: str, backend_url: str, mode: str = "package") -> CmdResult:
        if self.windows:
            return self._install_windows(api_key, backend_url)
        if mode == "script":
            return self._install_linux_script(api_key, backend_url)
        return self._install_linux_package(api_key, backend_url)

    def _install_linux_script(self, api_key: str, backend_url: str) -> CmdResult:
        script = local_install_script(self.s.agent_download_dir, self.cat.version)
        if not script:
            return CmdResult(2, "", f"install script for {self.cat.version} not found in {self.s.agent_download_dir}")
        self.tr.run(f"mkdir -p {REMOTE_TMP}", 60)
        self.tr.put(script, f"{REMOTE_TMP}/install_agent.sh")
        body = (f"export ACC_API_KEY={shlex.quote(api_key)}\nexport ACC_MID={shlex.quote(backend_url)}\n"
                f"cd {REMOTE_TMP} && bash {REMOTE_TMP}/install_agent.sh 2>&1\n")
        return self.tr.run(body, 1200)

    def _install_linux_package(self, api_key: str, backend_url: str) -> CmdResult:
        pkg = local_package(self.s.agent_download_dir, self.cat.version, self.t.os)
        if not pkg:
            return CmdResult(2, "", f"no package for {self.t.os} {self.cat.version} in {self.s.agent_download_dir} - run `download` first")
        self.tr.run(f"mkdir -p {REMOTE_TMP}", 60)
        LOG.info("  pushing %s (%d MB) to %s", pkg.name, pkg.stat().st_size // (1 << 20), self.t.name)
        self.tr.put(pkg, f"{REMOTE_TMP}/{pkg.name}")
        cert = self._signing_cert()
        if cert:
            self.tr.put(cert, f"{REMOTE_TMP}/plugin-signing.cer")
        if pkg.suffix == ".deb":
            inst = f"export DEBIAN_FRONTEND=noninteractive; dpkg -i {REMOTE_TMP}/{pkg.name} || (apt-get -qq -y -f install && dpkg -i {REMOTE_TMP}/{pkg.name})"
        else:
            inst = (f"if command -v zypper >/dev/null; then zypper -n --no-gpg-checks install -y {REMOTE_TMP}/{pkg.name}; "
                    f"elif command -v dnf >/dev/null; then dnf -y --nogpgcheck install {REMOTE_TMP}/{pkg.name}; "
                    f"elif command -v yum >/dev/null; then yum -y --nogpgcheck install {REMOTE_TMP}/{pkg.name}; "
                    f"else rpm -Uvh --nosignature {REMOTE_TMP}/{pkg.name}; fi")
        body = f"""set -e
{inst}
if [ -f {ACC_CONF}.example ] && [ ! -f {ACC_CONF} ]; then cp {ACC_CONF}.example {ACC_CONF}; fi
{ACC_BIN} gateway mid -a {shlex.quote(api_key)} -b {shlex.quote(backend_url)} --randomize-backend-urls=false
if [ -f {ACC_ALLOW_LIST}.default ] && [ ! -f {ACC_ALLOW_LIST} ]; then cp -p {ACC_ALLOW_LIST}.default {ACC_ALLOW_LIST}; fi
{self._sig_lines_linux()}
{self._trust_lines_linux()}
# the service runs as servicenow; a config written by root with the example's 0600 mode is unreadable to it (FATAL open acc.yml: permission denied)
id servicenow >/dev/null 2>&1 && chown servicenow:servicenow {ACC_CONF} {ACC_ALLOW_LIST} 2>/dev/null || true
systemctl enable acc >/dev/null 2>&1 || true
systemctl restart acc
for i in $(seq 1 20); do systemctl is-active --quiet acc && break; sleep 2; done
echo "service: $(systemctl is-active acc)"
"""
        return self.tr.run(body, 900)

    def container_accommodation(self) -> str:
        """Unprivileged LXC containers (the home lab) cannot honour the rpm unit's CPUSchedulingPolicy= and systemd 254+
        then refuses to start the service (status 214/SETSCHEDULER). A real server is unaffected; in a container a
        drop-in clears the two directives. Returns a note when it had to act, '' otherwise."""
        if self.windows or (self.facts.get("CONTAINER") or "") != "lxc":
            return ""
        r = self.tr.run("systemctl is-active acc >/dev/null 2>&1 && echo active || (journalctl -u acc --no-pager -n 20 2>/dev/null | grep -c SETSCHEDULER)", 60)
        if r.out.strip() == "active" or r.out.strip() in ("", "0"):
            return ""
        self.tr.run("""mkdir -p /etc/systemd/system/acc.service.d
printf '[Service]\\nCPUSchedulingPolicy=\\nCPUSchedulingPriority=\\n' > /etc/systemd/system/acc.service.d/acctest-lxc.conf
systemctl daemon-reload; systemctl reset-failed acc 2>/dev/null; systemctl restart acc
for i in $(seq 1 20); do systemctl is-active --quiet acc && break; sleep 2; done
systemctl is-active acc""", 120)
        return ("the acc unit sets CPUSchedulingPolicy=/CPUSchedulingPriority=, which an unprivileged LXC container cannot apply "
                "(systemd: 214/SETSCHEDULER) - a drop-in cleared them for this lab container; real servers are not affected")

    def _sig_lines_linux(self) -> str:
        """verify-plugin-signature in acc.yml, when AGENT_VERIFY_PLUGIN_SIGNATURE asks for it. The agent default (true)
        rejects every plugin without a ServiceNow signature - including a customer's own scripts."""
        v = self.s.agent_verify_plugin_signature
        if v not in ("true", "false"):
            return ""
        return (f"if grep -qE '^\\s*#?\\s*verify-plugin-signature:' {ACC_CONF}; then "
                f"sed -i -E 's|^\\s*#?\\s*verify-plugin-signature:.*|verify-plugin-signature: {v}|' {ACC_CONF}; "
                f"else printf '\\nverify-plugin-signature: {v}\\n' >> {ACC_CONF}; fi")

    def _signing_cert(self):
        """The plugin-signing certificate to trust on the target, when TRUST_SIGNING_CERT_ON_TARGETS is on (lab)."""
        if not self.s.trust_signing_cert_on_targets:
            return None
        from . import fixtures
        try:
            return fixtures.trust_anchor(self.s)
        except Exception as e:  # openssl missing etc. - the run goes on without it
            LOG.warning("could not obtain the plugin-signing certificate: %s", e)
            return None

    def _trust_lines_linux(self) -> str:
        """Install the signing certificate as a trust anchor (the agent validates plugin signers against the OS store).
        The file is pushed to REMOTE_TMP by install() beforehand."""
        if not self._signing_cert():
            return ""
        src = f"{REMOTE_TMP}/plugin-signing.cer"
        return (f"if [ -f {src} ]; then "
                f"if [ -d /usr/local/share/ca-certificates ]; then cp {src} /usr/local/share/ca-certificates/acctest-plugin-signing.crt && update-ca-certificates >/dev/null 2>&1; "
                f"elif [ -d /etc/pki/ca-trust/source/anchors ]; then cp {src} /etc/pki/ca-trust/source/anchors/acctest-plugin-signing.crt && update-ca-trust; "
                f"elif [ -d /etc/pki/trust/anchors ]; then cp {src} /etc/pki/trust/anchors/acctest-plugin-signing.crt && update-ca-certificates >/dev/null 2>&1; fi; "
                f"echo 'plugin-signing certificate trusted'; fi")

    def _trust_lines_windows(self) -> str:
        if not self._signing_cert():
            return ""
        return (f"if (Test-Path '{WIN_TMP}\\plugin-signing.cer') {{ Import-Certificate -FilePath '{WIN_TMP}\\plugin-signing.cer' -CertStoreLocation Cert:\\LocalMachine\\Root | Out-Null; "
                f"'plugin-signing certificate trusted' }}; ")

    def _sig_lines_windows(self) -> str:
        v = self.s.agent_verify_plugin_signature
        if v not in ("true", "false"):
            return ""
        return (f"$c = Get-Content '{WIN_CONF}' -Raw; "
                f"if ($c -match '(?m)^\\s*#?\\s*verify-plugin-signature:') {{ $c = [regex]::Replace($c, '(?m)^\\s*#?\\s*verify-plugin-signature:.*$', 'verify-plugin-signature: {v}') }} "
                f"else {{ $c += \"`r`nverify-plugin-signature: {v}`r`n\" }}; "
                f"Set-Content -Path '{WIN_CONF}' -Value $c -Encoding ascii; Restart-Service AgentClientCollector; Start-Sleep 5; ")

    def _install_windows(self, api_key: str, backend_url: str) -> CmdResult:
        pkg = local_package(self.s.agent_download_dir, self.cat.version, self.t.os)
        if not pkg:
            return CmdResult(2, "", f"no MSI for {self.t.os} {self.cat.version} in {self.s.agent_download_dir}")
        self.tr.run(f"New-Item -ItemType Directory -Force -Path '{WIN_TMP}' | Out-Null", 60)
        LOG.info("  uploading %s (%d MB) to %s", pkg.name, pkg.stat().st_size // (1 << 20), self.t.name)
        self.tr.put(pkg, f"{WIN_TMP}\\{pkg.name}")
        cert = self._signing_cert()
        if cert:
            self.tr.put(cert, f"{WIN_TMP}\\plugin-signing.cer")
        ps = (self._trust_lines_windows() + f"$p = Start-Process msiexec.exe -ArgumentList '/i \"{WIN_TMP}\\{pkg.name}\" /quiet /qn /norestart "
              f"ACC_API_KEY={api_key} ACC_MID=\"{backend_url}\" /l*v \"{WIN_TMP}\\install.log\"' -Wait -PassThru; "
              f"\"msiexec exit code: $($p.ExitCode)\"; Start-Sleep 5; "
              # 1638 = this product version is already installed (a re-run on a host that has it): not a failure
              f"if ($p.ExitCode -eq 1638) {{ 'already installed at this version - kept' }} "
              f"elseif ($p.ExitCode -ne 0) {{ Get-Content '{WIN_TMP}\\install.log' -Tail 60; exit $p.ExitCode }}; "
              + self._sig_lines_windows() + "Get-Service AgentClientCollector | Format-List Name,Status")
        return self.tr.run(ps, 1200)

    # ---- inspect -------------------------------------------------------------------------------------------------
    def status(self) -> dict:
        """Service state, version, agent id and config as the target sees them."""
        if self.windows:
            r = self.tr.run(
                "$s = Get-Service AgentClientCollector -ErrorAction SilentlyContinue; \"SERVICE=$(if($s){$s.Status}else{'missing'})\"; "
                f"$cfg = '{WIN_CONF}'; \"CONF=$(Test-Path $cfg)\"; "
                "$bin = Get-ChildItem 'C:\\Program Files\\ServiceNow\\agent-client-collector\\bin\\acc.exe' -ErrorAction SilentlyContinue; "
                "if ($bin) { \"VERSION=$(& $bin.FullName version 2>&1 | Select-Object -First 1)\" }; "
                "$pid_ = (Get-Process acc -ErrorAction SilentlyContinue | Select-Object -First 1).Id; \"PID=$pid_\"", 120)
        else:
            r = self.tr.run(f"""
echo "SERVICE=$(systemctl is-active acc 2>/dev/null || echo missing)"
echo "ENABLED=$(systemctl is-enabled acc 2>/dev/null)"
echo "CONF=$( [ -f {ACC_CONF} ] && echo yes || echo no)"
echo "AGENT_ID=$(cat {ACC_AGENT_ID} 2>/dev/null)"
echo "VERSION=$({ACC_BIN} version 2>/dev/null | head -1)"
echo "PID=$(systemctl show -p MainPID --value acc 2>/dev/null)"
echo "PKG=$( (dpkg-query -W -f='${{Version}}' {ACC_NAME} 2>/dev/null) || (rpm -q --qf '%{{VERSION}}-%{{RELEASE}}' {ACC_NAME} 2>/dev/null) )"
echo "LOG_LINES=$(wc -l < {ACC_LOG} 2>/dev/null)"
""", 120)
        facts: dict = {"_rc": r.rc}
        for line in (r.out or "").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                facts[k.strip()] = v.strip()
        return facts

    def read_config(self) -> str:
        if self.windows:
            return self.tr.run(f"Get-Content '{WIN_CONF}' -ErrorAction SilentlyContinue", 60).out
        return self.tr.run(f"cat {ACC_CONF} 2>/dev/null", 60).out

    def tail_log(self, lines: int = 80) -> str:
        if self.windows:
            return self.tr.run(f"Get-Content '{WIN_LOG}' -Tail {lines} -ErrorAction SilentlyContinue", 60).out
        return self.tr.run(f"tail -n {lines} {ACC_LOG} 2>/dev/null", 60).out

    # ---- remove --------------------------------------------------------------------------------------------------
    def uninstall(self) -> CmdResult:
        if self.windows:
            pkg = local_package(self.s.agent_download_dir, self.cat.version, self.t.os)
            name = pkg.name if pkg else "agent-client-collector.msi"
            return self.tr.run(f"$p = Start-Process msiexec.exe -ArgumentList '/x \"{WIN_TMP}\\{name}\" /quiet /qn /norestart' -Wait -PassThru; "
                               "\"msiexec exit code: $($p.ExitCode)\"; Get-Service AgentClientCollector -ErrorAction SilentlyContinue", 900)
        script = local_install_script(self.s.agent_download_dir, self.cat.version)
        if script:
            self.tr.run(f"mkdir -p {REMOTE_TMP}", 60)
            self.tr.put(script, f"{REMOTE_TMP}/install_agent.sh")
            return self.tr.run(f"cd {REMOTE_TMP} && bash {REMOTE_TMP}/install_agent.sh --remove 2>&1; "
                               f"systemctl is-active acc 2>/dev/null; rm -rf {REMOTE_TMP}", 900)
        return self.tr.run(f"systemctl stop acc 2>/dev/null; (dpkg -r {ACC_NAME} 2>/dev/null || rpm -e {ACC_NAME} 2>/dev/null); "
                           f"systemctl is-active acc 2>/dev/null; rm -rf {REMOTE_TMP}", 900)

    def leftovers(self) -> dict:
        """What is left on the host after an uninstall (should be nothing but logs/config, per ServiceNow's prerm)."""
        if self.windows:
            r = self.tr.run("\"SERVICE=$(if(Get-Service AgentClientCollector -ErrorAction SilentlyContinue){'present'}else{'absent'})\"; "
                            "\"DIR=$(Test-Path 'C:\\Program Files\\ServiceNow\\agent-client-collector')\"; "
                            "\"PROC=$((Get-Process acc -ErrorAction SilentlyContinue | Measure-Object).Count)\"", 60)
        else:
            r = self.tr.run(f"""
echo "SERVICE=$(systemctl list-unit-files acc.service 2>/dev/null | grep -c '^acc.service')"
echo "BIN=$( [ -e {ACC_BIN} ] && echo present || echo absent)"
echo "CONF_DIR=$( [ -d /etc/servicenow/{ACC_NAME} ] && echo present || echo absent)"
echo "CACHE_DIR=$( [ -d /var/cache/servicenow/{ACC_NAME} ] && echo present || echo absent)"
echo "PROC=$(pgrep -c -f '{ACC_NAME}|/bin/acc' 2>/dev/null || echo 0)"
echo "PKG=$( (dpkg-query -W {ACC_NAME} >/dev/null 2>&1 || rpm -q {ACC_NAME} >/dev/null 2>&1) && echo present || echo absent)"
""", 60)
        facts: dict = {}
        for line in (r.out or "").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                facts[k.strip()] = v.strip()
        return facts
