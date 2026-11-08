"""Performance metrics: what the agent costs the host while it actually works.

A small POSIX-sh sampler is started on the Linux target before discovery and stopped after the idle CPU sample. Every
STEP seconds it appends one CSV row of raw counters - host CPU ticks (busy / total across all cores), load average,
memory, and for the agent's whole process tree (acc + the checks and osquery it spawns) the CPU ticks, RSS, threads, open
file descriptors, process count and disk bytes read / written. The runner marks the phase boundaries (connect, discovery,
checks, policies, inventory, idle); `analyze` turns the counters into per-phase numbers:

    agent CPU        % of one core (avg / peak) and its share of the whole host (avg)
    agent memory     RSS of the tree, avg / peak MB; threads, processes, fds at their peak
    agent disk       bytes read / written by the tree during the phase
    host             CPU busy % avg / peak, load1 peak, memory-used change - and the difference between the working
                     phases (discovery + checks + policies) and the idle phase = the agent's impact on the host

Everything is read from /proc; nothing is installed on the target and the sampler removes itself. /proc/<pid>/io needs
root (or the agent's own user) - without it the disk columns stay 0 and the result says so.

Windows targets get the same CSV from a PowerShell sampler (raw performance counters + Win32_Process of the service's
process tree); there "fds" are handles and "load1" is the processor queue length.
"""
from __future__ import annotations

import csv
import io
import time

from .resources import parse_kv

PERF_DIR = "/tmp/acctest-perf"
LOAD_PHASES = ("discovery", "checks", "policies")

_SAMPLER_SH = r"""#!/bin/sh
# acctest performance sampler: one CSV row of raw counters every STEP seconds (see acctest/perf.py)
STEP=$1; OUT=$2
tree() { echo $1; for c in $(pgrep -P $1 2>/dev/null); do tree $c; done; }
while :; do
  MAIN=$(systemctl show -p MainPID --value acc 2>/dev/null)
  if [ -z "$MAIN" ] || [ "$MAIN" = 0 ]; then MAIN=$(pgrep -o -f 'bin/acc start' 2>/dev/null); fi
  read -r _ u n s i w q sq st _ < /proc/stat
  total=$((u+n+s+i+w+q+sq+st)); idle=$((i+w))
  load=$(cut -d' ' -f1 /proc/loadavg)
  memt=$(awk '/MemTotal/ {print $2}' /proc/meminfo); mema=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
  at=0; rss=0; th=0; fd=0; np=0; rb=0; wb=0; io=0
  if [ -n "$MAIN" ]; then
    for p in $(tree $MAIN); do
      [ -r /proc/$p/stat ] || continue
      np=$((np+1))
      t=$(awk '{print $14+$15}' /proc/$p/stat 2>/dev/null); at=$((at+${t:-0}))
      r=$(awk '/VmRSS/ {print $2}' /proc/$p/status 2>/dev/null); rss=$((rss+${r:-0}))
      h=$(awk '/Threads/ {print $2}' /proc/$p/status 2>/dev/null); th=$((th+${h:-0}))
      f=$(ls /proc/$p/fd 2>/dev/null | wc -l); fd=$((fd+f))
      if [ -r /proc/$p/io ]; then
        io=1
        b=$(awk '/^read_bytes/ {print $2}' /proc/$p/io 2>/dev/null); rb=$((rb+${b:-0}))
        b=$(awk '/^write_bytes/ {print $2}' /proc/$p/io 2>/dev/null); wb=$((wb+${b:-0}))
      fi
    done
  fi
  echo "$(date +%s),$total,$idle,$load,$memt,$mema,$at,$rss,$th,$fd,$np,$rb,$wb,$io" >> "$OUT"
  sleep $STEP
done
"""

_START = """set +e
pkill -f __DIR__/sampler.sh 2>/dev/null
rm -rf __DIR__; mkdir -p __DIR__
cat > __DIR__/sampler.sh <<'ACCTEST_SAMPLER_EOF'
__SCRIPT__
ACCTEST_SAMPLER_EOF
chmod +x __DIR__/sampler.sh
: > __DIR__/samples.csv
nohup setsid __DIR__/sampler.sh __STEP__ __DIR__/samples.csv > __DIR__/sampler.log 2>&1 < /dev/null &
echo "PID=$!"
echo "T0=$(date +%s)"
echo "TCK=$(getconf CLK_TCK 2>/dev/null || echo 100)"
echo "NCPU=$(nproc 2>/dev/null || echo 1)"
sleep 1
echo "ALIVE=$(pgrep -f __DIR__/sampler.sh | wc -l)"
"""

_STOP = """set +e
pkill -f __DIR__/sampler.sh 2>/dev/null; sleep 1
echo "T1=$(date +%s)"
echo "LOG=$(tail -c 300 __DIR__/sampler.log 2>/dev/null | tr '\\n' ' ')"
echo "---CSV---"
cat __DIR__/samples.csv 2>/dev/null
rm -rf __DIR__
"""

COLUMNS = ("t", "host_total", "host_idle", "load1", "mem_total_kb", "mem_avail_kb", "agent_ticks", "agent_rss_kb",
           "agent_threads", "agent_fds", "agent_procs", "agent_read_bytes", "agent_write_bytes", "io_readable")

# ---- Windows: the same CSV from PowerShell -----------------------------------------------------------------------------
# Host CPU comes from the raw performance counters (Win32_PerfRawData_PerfOS_Processor _Total: PercentProcessorTime is the
# cumulative IDLE time in 100 ns units, Timestamp_Sys100NS the clock), scaled to 1/100 s "ticks" so the analyzer's
# delta arithmetic is identical to Linux. "load1" is the processor queue length (Windows has no load average) and "fds"
# are handle counts. Process CPU is KernelModeTime + UserModeTime (100 ns units) of the service's process tree.
WIN_PERF_DIR = r"C:\Windows\Temp\acctest-perf"

_WIN_SAMPLER_PS1 = r"""param([int]$Step, [string]$Out)
# acctest performance sampler (Windows): one CSV row of raw counters every STEP seconds (see acctest/perf.py)
$ErrorActionPreference = 'SilentlyContinue'
$ncpu = [Environment]::ProcessorCount
while ($true) {
  $t = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
  $cpu = Get-CimInstance Win32_PerfRawData_PerfOS_Processor -Filter "Name='_Total'"
  $total = [int64]($cpu.Timestamp_Sys100NS / 100000)   # _Total's PercentProcessorTime is per-processor idle, so no ncpu factor
  $idle = [int64]($cpu.PercentProcessorTime / 100000)
  $q = (Get-CimInstance Win32_PerfRawData_PerfOS_System).ProcessorQueueLength
  $os = Get-CimInstance Win32_OperatingSystem
  $memt = $os.TotalVisibleMemorySize; $mema = $os.FreePhysicalMemory
  $main = (Get-CimInstance Win32_Service -Filter "Name='AgentClientCollector'").ProcessId
  $procs = Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, KernelModeTime, UserModeTime, WorkingSetSize, ThreadCount, HandleCount, ReadTransferCount, WriteTransferCount
  $tree = @()
  if ($main) {
    $queue = @([int]$main)
    while ($queue.Count -gt 0) {
      $p = $queue[0]; $queue = @($queue | Select-Object -Skip 1); $tree += $p
      $queue += @($procs | Where-Object { $_.ParentProcessId -eq $p } | ForEach-Object { [int]$_.ProcessId })
    }
  }
  $at = [int64]0; $rss = [int64]0; $th = 0; $fd = 0; $np = 0; $rb = [int64]0; $wb = [int64]0
  foreach ($p in ($procs | Where-Object { $tree -contains [int]$_.ProcessId })) {
    $np++; $at += [int64](($p.KernelModeTime + $p.UserModeTime) / 100000); $rss += [int64]($p.WorkingSetSize / 1024)
    $th += $p.ThreadCount; $fd += $p.HandleCount; $rb += [int64]$p.ReadTransferCount; $wb += [int64]$p.WriteTransferCount
  }
  Add-Content -Path $Out -Encoding ascii -Value "$t,$total,$idle,$q,$memt,$mema,$at,$rss,$th,$fd,$np,$rb,$wb,1"
  Start-Sleep -Seconds $Step
}
"""

_WIN_START = r"""$ErrorActionPreference = 'SilentlyContinue'
$d = '__DIR__'
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like '*acctest-perf\sampler.ps1*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Remove-Item -Recurse -Force $d; New-Item -ItemType Directory -Force $d | Out-Null
Set-Content -Path "$d\sampler.ps1" -Encoding ascii -Value @'
__SCRIPT__
'@
New-Item -ItemType File -Force "$d\samples.csv" | Out-Null
# a child of the SSH session dies with the session - WMI's Win32_Process.Create spawns it outside, under WmiPrvSE
$cmd = "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$d\sampler.ps1`" __STEP__ `"$d\samples.csv`""
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd }
$p = @{ Id = $r.ProcessId }
"PID=$($p.Id)"
"T0=$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())"
"TCK=100"
"NCPU=$([Environment]::ProcessorCount)"
Start-Sleep -Seconds 2
"ALIVE=$(@(Get-Process -Id $p.Id -ErrorAction SilentlyContinue).Count)"
"""

_WIN_STOP = r"""$ErrorActionPreference = 'SilentlyContinue'
$d = '__DIR__'
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like '*acctest-perf\sampler.ps1*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 1
"T1=$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())"
"LOG="
"---CSV---"
Get-Content "$d\samples.csv"
Remove-Item -Recurse -Force $d
"""


def start_script(step: int, family: str = "linux") -> str:
    if family == "windows":
        return _WIN_START.replace("__SCRIPT__", _WIN_SAMPLER_PS1.rstrip("\n")).replace("__DIR__", WIN_PERF_DIR).replace("__STEP__", str(int(step)))
    return _START.replace("__SCRIPT__", _SAMPLER_SH.rstrip("\n")).replace("__DIR__", PERF_DIR).replace("__STEP__", str(int(step)))


def stop_script(family: str = "linux") -> str:
    if family == "windows":
        return _WIN_STOP.replace("__DIR__", WIN_PERF_DIR)
    return _STOP.replace("__DIR__", PERF_DIR)


def parse_rows(csv_text: str) -> list[dict]:
    rows = []
    for rec in csv.reader(io.StringIO(csv_text.strip())):
        if len(rec) < 13:
            continue
        try:
            r = {k: float(v) for k, v in zip(COLUMNS, rec + ["1"] * (len(COLUMNS) - len(rec)))}
        except ValueError:
            continue
        rows.append(r)
    rows.sort(key=lambda r: r["t"])
    return rows


def intervals(rows: list[dict], tck: int, ncpu: int) -> list[dict]:
    """Per-interval metrics from consecutive raw rows. Counters of a child that exited between two samples disappear
    from the tree sum, so deltas are clamped at 0 (the agent's own counters never go backwards)."""
    out = []
    for a, b in zip(rows, rows[1:]):
        dt = b["t"] - a["t"]
        if dt <= 0:
            continue
        d_total = max(b["host_total"] - a["host_total"], 0.0)
        d_idle = max(b["host_idle"] - a["host_idle"], 0.0)
        host_busy = (d_total - d_idle) / d_total * 100 if d_total > 0 else 0.0
        agent_cpu = max(b["agent_ticks"] - a["agent_ticks"], 0.0) / tck / dt * 100       # % of one core
        out.append({
            "t": b["t"], "dt": dt,
            "agent_cpu": agent_cpu, "agent_share": agent_cpu / max(ncpu, 1),
            "agent_rss_mb": b["agent_rss_kb"] / 1024, "agent_threads": b["agent_threads"], "agent_fds": b["agent_fds"], "agent_procs": b["agent_procs"],
            "agent_read_mb": max(b["agent_read_bytes"] - a["agent_read_bytes"], 0.0) / (1 << 20),
            "agent_write_mb": max(b["agent_write_bytes"] - a["agent_write_bytes"], 0.0) / (1 << 20),
            "host_busy": max(min(host_busy, 100.0), 0.0), "load1": b["load1"],
            "host_mem_used_mb": (b["mem_total_kb"] - b["mem_avail_kb"]) / 1024,
            "io_readable": bool(b.get("io_readable", 1)),
        })
    return out


def _avg(xs):
    return sum(xs) / len(xs) if xs else 0.0


def summarize(ivs: list[dict]) -> dict:
    if not ivs:
        return {"samples": 0, "duration_s": 0}
    return {
        "samples": len(ivs), "duration_s": round(sum(i["dt"] for i in ivs)),
        "agent_cpu_avg": round(_avg([i["agent_cpu"] for i in ivs]), 1), "agent_cpu_peak": round(max(i["agent_cpu"] for i in ivs), 1),
        "agent_share_avg": round(_avg([i["agent_share"] for i in ivs]), 2),
        "agent_rss_avg_mb": round(_avg([i["agent_rss_mb"] for i in ivs])), "agent_rss_peak_mb": round(max(i["agent_rss_mb"] for i in ivs)),
        "agent_threads_max": int(max(i["agent_threads"] for i in ivs)), "agent_fds_max": int(max(i["agent_fds"] for i in ivs)),
        "agent_procs_max": int(max(i["agent_procs"] for i in ivs)),
        "agent_read_mb": round(sum(i["agent_read_mb"] for i in ivs), 1), "agent_write_mb": round(sum(i["agent_write_mb"] for i in ivs), 1),
        "host_busy_avg": round(_avg([i["host_busy"] for i in ivs]), 1), "host_busy_peak": round(max(i["host_busy"] for i in ivs), 1),
        "load1_max": round(max(i["load1"] for i in ivs), 2),
        "host_mem_used_start_mb": round(ivs[0]["host_mem_used_mb"]), "host_mem_used_max_mb": round(max(i["host_mem_used_mb"] for i in ivs)),
        "host_mem_delta_mb": round(max(i["host_mem_used_mb"] for i in ivs) - ivs[0]["host_mem_used_mb"]),
    }


def analyze(csv_text: str, marks: list[tuple[str, float]], tck: int = 100, ncpu: int = 1, t_end: float | None = None) -> dict:
    """Phase-by-phase and overall metrics. `marks` = [(label, host epoch), ...] in order; a phase runs from its mark to
    the next mark (the last one to t_end). An interval belongs to the phase its END time falls into."""
    rows = parse_rows(csv_text)
    ivs = intervals(rows, tck, ncpu)
    marks = sorted(marks, key=lambda m: m[1])
    end = t_end if t_end is not None else (rows[-1]["t"] if rows else 0)
    phases = []
    for k, (label, t0) in enumerate(marks):
        t1 = marks[k + 1][1] if k + 1 < len(marks) else end + 1
        sel = [i for i in ivs if t0 < i["t"] <= t1]
        phases.append({"phase": label, "start": t0, "end": t1, **summarize(sel)})
    overall = summarize(ivs)
    load = [i for i in ivs if any(p["phase"] in LOAD_PHASES and p["start"] < i["t"] <= p["end"] for p in phases)]
    idle = [i for i in ivs if any(p["phase"] == "idle" and p["start"] < i["t"] <= p["end"] for p in phases)]
    impact = {
        "load": summarize(load), "idle": summarize(idle),
        "host_busy_delta": round(_avg([i["host_busy"] for i in load]) - _avg([i["host_busy"] for i in idle]), 1) if load and idle else None,
        "agent_share_load_avg": round(_avg([i["agent_share"] for i in load]), 2) if load else None,
    }
    return {"ncpu": ncpu, "tck": tck, "samples": len(rows), "io_readable": all(i["io_readable"] for i in ivs) if ivs else False,
            "phases": phases, "overall": overall, "impact": impact,
            "series": [{k: (round(v, 2) if isinstance(v, float) else v) for k, v in i.items() if k != "io_readable"} for i in ivs]}


def describe(a: dict, cpu_limit: float | None = None) -> str:
    """One readable sentence for the test row."""
    if not a.get("samples"):
        return "no samples"
    L, I = a["impact"]["load"], a["impact"]["idle"]
    parts = []
    if L.get("samples"):
        parts.append(f"while working (discovery + checks + policies, {L['duration_s']}s): agent avg {L['agent_cpu_avg']:g}% / peak {L['agent_cpu_peak']:g}% of one core "
                     f"= {L['agent_share_avg']:g}% of the host's {a['ncpu']} cores; RSS avg {L['agent_rss_avg_mb']} / peak {L['agent_rss_peak_mb']} MB; "
                     f"up to {L['agent_procs_max']} processes, {L['agent_threads_max']} threads, {L['agent_fds_max']} fds; "
                     f"disk read {L['agent_read_mb']:g} MB / written {L['agent_write_mb']:g} MB" + ("" if a.get("io_readable") else " (io counters not readable)")
                     + f"; host CPU busy avg {L['host_busy_avg']:g}% (peak {L['host_busy_peak']:g}%), load1 max {L['load1_max']:g}, host memory used {L['host_mem_delta_mb']:+d} MB")
    if I.get("samples"):
        parts.append(f"idle ({I['duration_s']}s): agent avg {I['agent_cpu_avg']:g}% of one core, RSS {I['agent_rss_avg_mb']} MB; host CPU busy avg {I['host_busy_avg']:g}%")
    if a["impact"].get("host_busy_delta") is not None:
        parts.append(f"host impact: CPU busy {a['impact']['host_busy_delta']:+g} points working vs idle")
    return "; ".join(parts)


class PerfSession:
    """Start the sampler on one target, mark phases from the runner's clock, stop and analyze."""

    def __init__(self, tr, step: int = 5, family: str = "linux"):
        self.tr = tr
        self.family = family
        self.step = max(int(step), 2)
        self.offset = 0.0           # host epoch - local epoch
        self.marks: list[tuple[str, float]] = []
        self.meta: dict = {}

    def start(self) -> str:
        r = self.tr.run(start_script(self.step, self.family), timeout=180)
        kv = parse_kv(r.out)
        if r.rc != 0 or not kv.get("T0") or not kv.get("PID") or kv.get("ALIVE", "0") in ("", "0"):
            return f"sampler did not start (rc {r.rc}, alive {kv.get('ALIVE', '?')}): {(r.err or r.out).strip()[-300:]}"
        self.meta = kv
        self.offset = float(kv["T0"]) - time.time()
        self.marks = [("connect", float(kv["T0"]))]
        return ""

    def mark(self, label: str) -> None:
        self.marks.append((label, time.time() + self.offset))

    def stop(self) -> dict:
        r = self.tr.run(stop_script(self.family), timeout=180)
        head, _, body = r.out.partition("---CSV---")
        kv = parse_kv(head)
        t_end = float(kv["T1"]) if kv.get("T1", "").isdigit() else time.time() + self.offset
        a = analyze(body, self.marks, tck=int(self.meta.get("TCK") or 100), ncpu=int(self.meta.get("NCPU") or 1), t_end=t_end)
        a["marks"] = [{"phase": l, "t": round(t)} for l, t in self.marks]
        a["step_s"] = self.step
        if kv.get("LOG"):
            a["sampler_log"] = kv["LOG"][-300:]
        return a
