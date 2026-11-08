"""Resource behaviour of the agent on the target: CPU against the configured threshold, and cleanup after work.

acc.yml (7.x) carries the agent's own CPU protection settings:

    agent_cpu_threshold:
      cpu_percentage_limit: 5        # CPU percentage limit the agent protects itself against
      repeated_high_cpu_num: 3       # consecutive breaches before the agent acts
      monitor_interval_sec: 60
      agent_cpu_threshold_disabled: false
      proxy_cpu_percentage_limit: 80
    max-running-checks: 10

The sampler reads /proc for the agent's process tree (acc + any check child such as osquery/ruby) every few seconds
and reports average and peak CPU as a percentage of ONE core, which is what the agent's own monitor compares with.
"""
from __future__ import annotations

import logging
import re

from .targets import Transport

LOG = logging.getLogger("acctest.resources")

LINUX_SAMPLER = r"""
set +e
DUR=%(dur)d; STEP=%(step)d
MAIN=$(systemctl show -p MainPID --value acc 2>/dev/null); [ -z "$MAIN" ] && MAIN=$(pgrep -o -f 'bin/acc start')
if [ -z "$MAIN" ] || [ "$MAIN" = "0" ]; then echo "ERROR=no acc process"; exit 0; fi
TCK=$(getconf CLK_TCK); NCPU=$(nproc)
tree() { local p=$1; echo $p; for c in $(pgrep -P $p 2>/dev/null); do tree $c; done; }
total_ticks() { local sum=0; for p in $(tree $MAIN); do [ -r /proc/$p/stat ] && { t=$(awk '{print $14+$15}' /proc/$p/stat 2>/dev/null); sum=$((sum+${t:-0})); }; done; echo $sum; }
prev=$(total_ticks); prev_t=$(date +%%s%%N); peak=0; sum=0; n=0; maxprocs=1; children=""
end=$(( $(date +%%s) + DUR ))
while [ $(date +%%s) -lt $end ]; do
  sleep $STEP
  cur=$(total_ticks); cur_t=$(date +%%s%%N)
  dt=$(( (cur_t - prev_t) / 1000000 )); [ $dt -le 0 ] && dt=1
  pct=$(( (cur - prev) * 1000 * 1000 / TCK / dt ))   # tenths of a percent of one core
  prev=$cur; prev_t=$cur_t
  sum=$((sum+pct)); n=$((n+1)); [ $pct -gt $peak ] && peak=$pct
  np=$(tree $MAIN | wc -l); [ $np -gt $maxprocs ] && maxprocs=$np
  for p in $(tree $MAIN); do [ $p != $MAIN ] && children="$children $(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | cut -c1-80 | sed 's/ *$//');"; done
done
avg=$(( n>0 ? sum/n : 0 ))
echo "SAMPLES=$n"; echo "AVG_PCT=$((avg/10)).$((avg%%10))"; echo "PEAK_PCT=$((peak/10)).$((peak%%10))"; echo "NCPU=$NCPU"; echo "MAX_PROCS=$maxprocs"
echo "RSS_KB=$(awk '/VmRSS/ {print $2}' /proc/$MAIN/status)"
echo "THREADS=$(awk '/Threads/ {print $2}' /proc/$MAIN/status)"
echo "CHILDREN=$(echo "$children" | tr ';' '\n' | sed 's/^ *//' | sort -u | tr '\n' ';' | cut -c1-600)"
"""

LINUX_CLEANUP = r"""
set +e
MAIN=$(systemctl show -p MainPID --value acc 2>/dev/null)
echo "SERVICE=$(systemctl is-active acc)"
echo "CHILD_PROCS=$(pgrep -P ${MAIN:-0} 2>/dev/null | wc -l)"
echo "CHILD_CMDS=$(for p in $(pgrep -P ${MAIN:-0} 2>/dev/null); do tr '\0' ' ' < /proc/$p/cmdline | cut -c1-100; echo -n ';'; done)"
echo "ZOMBIES=$(ps -eo stat,ppid | awk -v m=${MAIN:-0} '$1 ~ /Z/ && $2==m' | wc -l)"
echo "OSQUERY_PROCS=$(pgrep -c -f osquery 2>/dev/null || echo 0)"
echo "TMP_FILES=$(find /tmp /var/tmp -maxdepth 1 \( -iname '*acc*' -o -iname '*sensu*' -o -iname '*osquery*' -o -iname '*servicenow*' -o -iname 'agent-client-collector*' \) ! -name acctest ! -name .osquery 2>/dev/null | tr '\n' ';')"
echo "TMP_SHM=$(find /dev/shm -maxdepth 1 \( -iname '*acc*' -o -iname '*osquery*' \) 2>/dev/null | tr '\n' ';')"
echo "CACHE_DU_KB=$(du -sk /var/cache/servicenow/agent-client-collector 2>/dev/null | cut -f1)"
echo "CACHE_TMP=$(find /var/cache/servicenow/agent-client-collector -maxdepth 2 -type d \( -iname 'tmp*' -o -iname '*temp*' \) 2>/dev/null | tr '\n' ';')"
echo "LOG_KB=$(du -sk /var/log/servicenow/agent-client-collector 2>/dev/null | cut -f1)"
echo "OPEN_FILES=$(ls /proc/${MAIN:-0}/fd 2>/dev/null | wc -l)"
echo "LOG_ERRORS=$(grep -c '\[ERROR\]' /var/log/servicenow/agent-client-collector/acc.log 2>/dev/null)"
echo "LOG_PANICS=$(grep -ci 'panic\|fatal' /var/log/servicenow/agent-client-collector/acc.log 2>/dev/null)"
echo "RESTARTS=$(journalctl -u acc --no-pager -o cat 2>/dev/null | grep -c 'Started\|Scheduled restart')"
"""

LINUX_PLUGINS = r"""
set +e
CACHE=/var/cache/servicenow/agent-client-collector
echo "PLUGIN_DIRS=$(find $CACHE -maxdepth 1 -mindepth 1 -type d ! -name osquery ! -name config-files 2>/dev/null | wc -l)"
echo "SCRIPTS=$(find $CACHE -type f \( -name '*.rb' -o -name '*.sh' -o -name '*.py' \) 2>/dev/null | wc -l)"
# scripts whose first line (shebang) ends in CR: executed directly they fail with "/usr/bin/env: 'ruby\r': No such file"
crlf=""
for f in $(find $CACHE -type f \( -name '*.rb' -o -name '*.sh' -o -name '*.py' \) 2>/dev/null); do
  if head -c 2 "$f" | grep -q '#!' && head -n 1 "$f" | grep -q $'\r'; then crlf="$crlf${f#$CACHE/};"; fi
done
echo "CRLF_SHEBANG=$crlf"
echo "NOEXEC=$(find $CACHE -type f -name '*.rb' -path '*/bin/*' ! -perm -u+x 2>/dev/null | wc -l)"
"""

WINDOWS_SAMPLER = r"""
$dur = %(dur)d; $step = %(step)d
$svc = Get-CimInstance Win32_Service -Filter "Name='AgentClientCollector'"
if (-not $svc -or -not $svc.ProcessId) { "ERROR=no acc service process"; exit 0 }
$main = [int]$svc.ProcessId
function Tree($p) { $p; Get-CimInstance Win32_Process -Filter "ParentProcessId=$p" | ForEach-Object { Tree $_.ProcessId } }
$ncpu = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
$peak = 0; $sum = 0; $n = 0; $maxprocs = 1
$prev = (Tree $main | ForEach-Object { (Get-Process -Id $_ -ErrorAction SilentlyContinue).TotalProcessorTime.TotalMilliseconds } | Measure-Object -Sum).Sum
$t0 = Get-Date
$end = (Get-Date).AddSeconds($dur)
while ((Get-Date) -lt $end) {
  Start-Sleep -Seconds $step
  $ids = Tree $main
  $cur = ($ids | ForEach-Object { (Get-Process -Id $_ -ErrorAction SilentlyContinue).TotalProcessorTime.TotalMilliseconds } | Measure-Object -Sum).Sum
  $t1 = Get-Date; $dt = ($t1 - $t0).TotalMilliseconds; $t0 = $t1
  $pct = [int](($cur - $prev) * 100 / $dt); $prev = $cur
  $sum += $pct; $n++; if ($pct -gt $peak) { $peak = $pct }
  if ($ids.Count -gt $maxprocs) { $maxprocs = $ids.Count }
}
"SAMPLES=$n"; "AVG_PCT=$([int]($sum / [Math]::Max($n,1)))"; "PEAK_PCT=$peak"; "NCPU=$ncpu"; "MAX_PROCS=$maxprocs"
"RSS_KB=$([int]((Get-Process -Id $main).WorkingSet64 / 1KB))"; "THREADS=$((Get-Process -Id $main).Threads.Count)"
"""

WINDOWS_CLEANUP = r"""
$svc = Get-CimInstance Win32_Service -Filter "Name='AgentClientCollector'"
"SERVICE=$($svc.State)"
$main = [int]$svc.ProcessId
$kids = Get-CimInstance Win32_Process -Filter "ParentProcessId=$main"
"CHILD_PROCS=$(($kids | Measure-Object).Count)"
"CHILD_CMDS=$(($kids | ForEach-Object { $_.CommandLine }) -join ';')"
"OSQUERY_PROCS=$((Get-Process osqueryi,osqueryd -ErrorAction SilentlyContinue | Measure-Object).Count)"
"TMP_FILES=$((Get-ChildItem $env:TEMP,C:\Windows\Temp -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'acc|sensu|osquery|servicenow' -and $_.Name -notmatch '^acctest$|^ACC_Logs$' } | ForEach-Object { $_.FullName }) -join ';')"
$log = 'C:\ProgramData\ServiceNow\agent-client-collector\log\acc.log'
"LOG_ERRORS=$(if (Test-Path $log) { (Select-String -Path $log -Pattern '\[ERROR\]' | Measure-Object).Count } else { 0 })"
"LOG_PANICS=$(if (Test-Path $log) { (Select-String -Path $log -Pattern 'panic|fatal' | Measure-Object).Count } else { 0 })"
"""


def parse_kv(out: str) -> dict:
    facts: dict = {}
    for line in (out or "").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            facts[k.strip()] = v.strip()
    return facts


def cpu_limits(acc_yml: str) -> dict:
    """The CPU protection settings from acc.yml text (defaults applied when missing)."""
    def num(key: str, default: float) -> float:
        m = re.search(rf"^\s*{re.escape(key)}\s*:\s*([0-9.]+)", acc_yml, re.M)
        return float(m.group(1)) if m else default

    disabled = bool(re.search(r"^\s*agent_cpu_threshold_disabled\s*:\s*true", acc_yml, re.M))
    return {"cpu_percentage_limit": num("cpu_percentage_limit", 5), "repeated_high_cpu_num": num("repeated_high_cpu_num", 3),
            "monitor_interval_sec": num("monitor_interval_sec", 60), "proxy_cpu_percentage_limit": num("proxy_cpu_percentage_limit", 80),
            "max_running_checks": num("max-running-checks", 10), "disabled": disabled,
            "present": "agent_cpu_threshold" in acc_yml}


def sample_cpu(tr: Transport, family: str, duration: int, step: int = 5) -> dict:
    script = (WINDOWS_SAMPLER if family == "windows" else LINUX_SAMPLER) % {"dur": duration, "step": step}
    r = tr.run(script, timeout=duration + 120)
    facts = parse_kv(r.out)
    facts["_rc"] = r.rc
    if r.err.strip():
        facts["_err"] = r.err.strip()[-500:]
    return facts


def plugin_state(tr: Transport, family: str) -> dict:
    """Plugin scripts the MID delivered to the agent: how many, and which ones cannot execute on Linux."""
    if family == "windows":
        return {"_rc": 0, "PLUGIN_DIRS": "", "CRLF_SHEBANG": ""}
    r = tr.run(LINUX_PLUGINS, timeout=180)
    facts = parse_kv(r.out)
    facts["_rc"] = r.rc
    return facts


def cleanup_state(tr: Transport, family: str) -> dict:
    r = tr.run(WINDOWS_CLEANUP if family == "windows" else LINUX_CLEANUP, timeout=180)
    facts = parse_kv(r.out)
    facts["_rc"] = r.rc
    return facts


# ---- component inventory (what is actually installed on the host) ---------------------------------------------------
LINUX_INVENTORY = r"""
set +e
B=/usr/share/servicenow/agent-client-collector
C=/var/cache/servicenow/agent-client-collector
echo "ACC_VERSION=$($B/bin/acc version 2>/dev/null | head -1)"
echo "PKG=$( (dpkg-query -W -f='${Version}' agent-client-collector 2>/dev/null) || (rpm -q --qf '%{VERSION}-%{RELEASE}' agent-client-collector 2>/dev/null) )"
echo "RUBY=$($B/embedded/bin/ruby -v 2>/dev/null)"
if [ -x $B/embedded/bin/openssl ]; then echo "OPENSSL=$($B/embedded/bin/openssl version 2>/dev/null)"; fi
echo "OPENSSL_LIB=$(ls $B/embedded/lib/libcrypto.so.* 2>/dev/null | head -1 | sed 's/.*libcrypto.so.//')"
echo "RUBY_OPENSSL=$($B/embedded/bin/ruby -ropenssl -e 'puts OpenSSL::OPENSSL_LIBRARY_VERSION' 2>/dev/null)"
for q in $C/osquery/bin/osqueryi $C/osquery/bin/osqueryd; do [ -x "$q" ] && echo "OSQUERY=$($q --version 2>/dev/null | head -1)" && break; done
echo "GO=$(grep -a -o -m1 -E 'go1\.[0-9]+(\.[0-9]+)?' $B/bin/acc 2>/dev/null | head -1)"
for so in $B/embedded/lib/lib*.so.*[0-9]; do n=$(basename $so); echo "LIB $n"; done 2>/dev/null | sort -u
$B/embedded/bin/gem list --local 2>/dev/null | sed -n 's/^\([A-Za-z0-9_.-]*\) (\(.*\))$/GEM \1 \2/p'
for d in $(find $C -maxdepth 1 -mindepth 1 -type d ! -name config-files 2>/dev/null); do echo "ASSET $(basename $d) $(find $d -type f | wc -l) files, $(du -sk $d | cut -f1) KB"; done
"""

WINDOWS_INVENTORY = r"""
$ErrorActionPreference = 'SilentlyContinue'
$svc = Get-CimInstance Win32_Service -Filter "Name='AgentClientCollector'"
$exe = if ($svc) { ($svc.PathName -replace '^"([^"]+)".*','$1') } else { 'C:\Program Files\ServiceNow\agent-client-collector\bin\acc.exe' }
$base = Split-Path (Split-Path $exe -Parent) -Parent
"BASE=$base"
"ACC_VERSION=$(& $exe version 2>$null | Select-Object -First 1)"
$p = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' | Where-Object { $_.DisplayName -like 'Agent Client Collector*' } | Select-Object -First 1
"PKG=$($p.DisplayVersion)"
$ruby = Join-Path $base 'embedded\bin\ruby.exe'
if (Test-Path $ruby) { "RUBY=$(& $ruby -v 2>$null)"; "RUBY_OPENSSL=$(& $ruby -ropenssl -e 'puts OpenSSL::OPENSSL_LIBRARY_VERSION' 2>$null)" }
Get-ChildItem (Join-Path $base 'embedded\bin') -Filter '*.dll' | Where-Object { $_.Name -match 'ssl|crypto' } | ForEach-Object { "LIB $($_.Name) $($_.VersionInfo.FileVersion)" }
Get-ChildItem (Join-Path $base 'embedded\bin') -Filter '*.dll' | Where-Object { $_.Name -notmatch 'ssl|crypto' } | ForEach-Object { "LIB $($_.Name) $($_.VersionInfo.FileVersion)" }
$gem = Join-Path $base 'embedded\bin\gem.cmd'
if (Test-Path $gem) { & $gem list --local 2>$null | ForEach-Object { if ($_ -match '^([A-Za-z0-9_.-]+) \((.*)\)$') { "GEM $($matches[1]) $($matches[2])" } } }
$cache = 'C:\ProgramData\ServiceNow\agent-client-collector\cache'
$osq = Get-ChildItem $cache -Recurse -Filter osqueryi.exe | Select-Object -First 1
if ($osq) { "OSQUERY=$(& $osq.FullName --version 2>$null | Select-Object -First 1)" }
Get-ChildItem $cache -Directory | Where-Object { $_.Name -ne 'config-files' } | ForEach-Object { $n = (Get-ChildItem $_.FullName -Recurse -File | Measure-Object).Count; "ASSET $($_.Name) $n files" }
"GO=$(Select-String -Path $exe -Pattern 'go1\.[0-9]+(\.[0-9]+)?' -Encoding ascii | Select-Object -First 1 | ForEach-Object { $_.Matches[0].Value })"
"""


def inventory(tr: Transport, family: str) -> dict:
    """Component versions as installed on the target: {facts: {...}, components: [{component, version, kind, source}]}.
    This is the on-host truth (what a scanner would see); runtimes.inspect_deb is the same view read from the package."""
    r = tr.run(WINDOWS_INVENTORY if family == "windows" else LINUX_INVENTORY, timeout=300)
    facts: dict = {"_rc": r.rc}
    comps: list[dict] = []
    for line in (r.out or "").splitlines():
        line = line.rstrip()
        if line.startswith("GEM "):
            parts = line.split(" ", 2)
            if len(parts) == 3:
                comps.append({"component": f"gem {parts[1]}", "version": parts[2].replace("default: ", ""), "kind": "Ruby gem", "source": "embedded ruby"})
        elif line.startswith("LIB "):
            parts = line.split(" ", 2)
            comps.append({"component": parts[1], "version": parts[2] if len(parts) > 2 else "", "kind": "shared library", "source": "embedded/lib"})
        elif line.startswith("ASSET "):
            parts = line.split(" ", 2)
            comps.append({"component": f"plugin asset {parts[1]}", "version": parts[2] if len(parts) > 2 else "", "kind": "plugin content (from the instance)", "source": "agent cache"})
        elif "=" in line:
            k, v = line.split("=", 1)
            facts[k.strip()] = v.strip()
    if facts.get("ACC_VERSION"):
        comps.insert(0, {"component": "Agent Client Collector", "version": facts["ACC_VERSION"], "kind": "agent", "source": facts.get("PKG", "")})
    if facts.get("GO"):
        comps.insert(1, {"component": "Go runtime (acc binary)", "version": facts["GO"], "kind": "compiler/runtime", "source": "bin/acc"})
    if facts.get("RUBY"):
        comps.insert(2, {"component": "Ruby (embedded)", "version": facts["RUBY"], "kind": "interpreter", "source": "embedded/bin/ruby"})
    ossl = facts.get("RUBY_OPENSSL") or facts.get("OPENSSL") or (("OpenSSL " + facts["OPENSSL_LIB"]) if facts.get("OPENSSL_LIB") else "")
    if ossl:
        comps.insert(3, {"component": "OpenSSL (embedded)", "version": ossl, "kind": "crypto library", "source": "embedded/lib"})
    if facts.get("OSQUERY"):
        comps.insert(4, {"component": "osquery (plugin asset)", "version": facts["OSQUERY"], "kind": "tool (from the instance)", "source": "agent cache"})
    return {"facts": facts, "components": comps, "_err": r.err.strip()[-400:]}


# ---- environment prerequisites (so a later failure is blamed on the right party) ---------------------------------------
LINUX_ENV = r"""
set +e
for t in which ss dmidecode sudo awk tar gzip curl gpg unzip systemctl ps; do printf 'TOOL %s %s\n' "$t" "$(command -v $t 2>/dev/null || echo MISSING)"; done
echo "SUDO_RULES=$( (sudo -n -l -U servicenow 2>/dev/null || true) | grep -c -E '^\s+\(' )"
echo "SUDO_REQUIRETTY=$(grep -rhs -E '^\s*Defaults\s+requiretty' /etc/sudoers /etc/sudoers.d 2>/dev/null | wc -l)"
echo "DISK_VAR_MB=$(df -Pm /var 2>/dev/null | awk 'NR==2 {print $4}')"
echo "DISK_TMP_MB=$(df -Pm /tmp 2>/dev/null | awk 'NR==2 {print $4}')"
echo "MEM_FREE_MB=$(awk '/MemAvailable/ {printf "%d", $2/1024}' /proc/meminfo)"
echo "NPROC=$(nproc 2>/dev/null)"
echo "SELINUX=$(getenforce 2>/dev/null)"
echo "FIREWALL=$( (command -v ufw >/dev/null && ufw status 2>/dev/null | head -1) || (command -v firewall-cmd >/dev/null && firewall-cmd --state 2>/dev/null) || echo none)"
echo "PROXY=${https_proxy:-${HTTPS_PROXY:-none}}"
echo "CONTAINER=$(systemd-detect-virt -c 2>/dev/null)"
"""

WINDOWS_ENV = r"""
$ErrorActionPreference = 'SilentlyContinue'
"PS_VERSION=$($PSVersionTable.PSVersion)"
"IS_ADMIN=$(([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))"
"EXEC_POLICY=$(Get-ExecutionPolicy -Scope LocalMachine)"
"DISK_C_MB=$([int]((Get-PSDrive C).Free / 1MB))"
"MEM_FREE_MB=$([int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB))"
"NPROC=$((Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors)"
"DOTNET=$((Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full').Release)"
"FIREWALL=$((Get-NetFirewallProfile | Where-Object Enabled | Select-Object -ExpandProperty Name) -join ',')"
"DEFENDER=$((Get-MpComputerStatus).RealTimeProtectionEnabled)"
"PROXY=$((Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings').ProxyServer)"
"TOOL powershell $((Get-Command powershell.exe).Source)"
"TOOL msiexec $((Get-Command msiexec.exe).Source)"
"""


def environment(tr: Transport, family: str) -> dict:
    """Prerequisites of the host, read before anything is installed: {facts, tools: {name: path|MISSING}}."""
    r = tr.run(WINDOWS_ENV if family == "windows" else LINUX_ENV, timeout=120)
    facts: dict = {"_rc": r.rc}
    tools: dict = {}
    for line in (r.out or "").splitlines():
        line = line.rstrip()
        if line.startswith("TOOL "):
            parts = line.split(" ", 2)
            tools[parts[1]] = parts[2] if len(parts) > 2 else "MISSING"
        elif "=" in line:
            k, v = line.split("=", 1)
            facts[k.strip()] = v.strip()
    return {"facts": facts, "tools": tools, "_err": r.err.strip()[-300:]}


# tools the shipped content reaches for; missing ones degrade specific checks (named here) rather than the agent
LINUX_TOOL_IMPACT = {
    "which": "discovery (endpoint_discovery.rb) fails with 'fatal error in check' on minimal images",
    "ss": "TCP connection discovery (tcp_connections.rb) returns nothing; self-test SudoSSCommandAccessTest fails",
    "dmidecode": "serial number / hardware fields stay empty",
    "sudo": "no elevation at all: serial numbers, sudo osquery, agent self-upgrade",
    "ps": "running process discovery degrades",
}
