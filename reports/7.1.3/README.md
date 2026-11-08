# Agent Client Collector 7.1.3 - qualification result (2026-11-08)

**Agent verdict: SAFE.** No failure in the run is owned by the agent. Every finding is in the environment (instance
content, or a MID Server restart during the test) and is listed with its cause in the report.

Files in this folder (sanitised copies of the lab results - UI screenshots and the lab's Windows host name removed):

| file | what |
|---|---|
| [result.html](result.html) | the full report: verdict, every test on every host, evidence, cause per failure, component inventory, settings |
| [result.md](result.md) | the same full run as Markdown: verdict, targets, findings, every test's status and message, and every component / module / package with its version and the hosts it was seen on |
| [windows-server-2025.md](windows-server-2025.md) | **Windows Server 2025 in full, as Markdown**: all 85 test rows, the performance table and the complete component list (agent, Go, Ruby, OpenSSL, DLLs, 96 gems, plugin content) with versions |
| [result-win2025-performance.html](result-win2025-performance.html), [perf-acc-win2025.csv](perf-acc-win2025.csv), [components-win2025.csv](components-win2025.csv) | the Windows run's HTML report with evidence, its raw performance samples and its component inventory as CSV |
| [components.csv](components.csv) | the component inventory for a security audit (926 rows: agent, Go runtime, embedded Ruby and OpenSSL, shared libraries, gems, plugin content) |
| [result-ubuntu2404-performance.html](result-ubuntu2404-performance.html) | the Ubuntu 24.04 host re-run with the performance sampler: a **Performance** section with the agent's resource usage and host impact per phase |
| [perf-acc-ubuntu2404.csv](perf-acc-ubuntu2404.csv) | the raw performance samples behind it (one row per 5 s interval) |
| [result-rocky9-rerun.html](result-rocky9-rerun.html) | the Rocky 9 host re-run alone after the MID had been restarted under it during the full run - host data collection passes |

## What was tested

Seven hosts, one agent build (7.1.3, build `dd94c9bd`, built 2026-11-03), all connected through one MID Server to a
developer instance on the Brazil release with Agent Client Collector Framework 7.1.3 and Visibility content 2.1.1:

| host | OS | package | result |
|---|---|---|---|
| acc-ubuntu2404 | Ubuntu 24.04 | deb | pass (environment findings only) |
| acc-ubuntu2204 | Ubuntu 22.04 | deb | pass (environment findings only) |
| acc-debian12 | Debian 12 | deb | pass (environment findings only) |
| acc-rocky9 | Rocky Linux 9.4 | rpm | pass on re-run; one discovery result lost to a MID restart in the full run |
| acc-rocky10 | Rocky Linux 10 | rpm | pass (environment findings only) |
| acc-suse156 | SUSE 15.6 | rpm | pass (environment findings only) |
| acc-win2025 | Windows Server 2025 | msi | pass |

Per host: package install, service, configuration, registration through the MID, on-demand host discovery and CI
binding, every applicable shipped check definition run ad hoc, the agent self-test, every published policy evaluated
and its checks run, CPU protection against the configured limit, cleanup (processes, temp files, log, disk), and the
records rendered in the UI. On top of the shipped content, a **signed custom plugin** carrying a POSIX `sh` script and
a PowerShell script (list local users with their groups and admin flag) was deployed as an asset with a check
definition and a policy per OS; the agent fetched it, verified the signature, ran it and returned the output on all
seven hosts, and the output was parsed and verified.

Totals: 319 pass, 25 fail (all environment), 90 warn, 100 skip (checks not applicable to the OS, background checks,
agent-internal check types).

## Components inside the agent (for the security audit)

Read from the installed agent on every host; identical across Linux distributions and Windows except where noted.

| component | version |
|---|---|
| Agent Client Collector | 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03 |
| Go runtime (acc binary) | 1.26.10 |
| Embedded Ruby | 3.3.13 (2026-10-23) - the first agent build carrying the Ruby release that fixes the resolv and Onigmo CVEs; every build from 4.3.2 to 7.1.2 ships Ruby 3.3.2 (2024-05-30) |
| Embedded OpenSSL | 3.5.9 (29 Sep 2026) |
| osquery (delivered as plugin content by the instance) | 5.18.1 |
| libyaml | 0.2.9 (Linux) / libyaml-0-2.dll (Windows) |
| libffi | 8.1.2 |
| zlib | 1.2.13 |
| Ruby gems | 93 in the package; 94 on Linux hosts, 96 on Windows - every name and version in components.csv |

## Performance: what the agent cost the host (Ubuntu 24.04, 2 vCPU, 1 GB)

Sampled on the host every 5 seconds (72 samples) while the agent worked and while it idled. *Agent* is the whole agent
process tree (acc plus the checks and osquery it spawns); CPU is % of one core, *share* is the same CPU as a fraction of
both cores. Disk I/O is what the tree read from and wrote to block devices.

| phase | seconds | agent CPU avg / peak | share of host | agent RSS avg / peak MB | procs / threads / fds (max) | disk read / written MB |
|---|---:|---:|---:|---:|---:|---:|
| discovery (host data collection) | 35 | 2.4% / 16.4% | 1.21% | 58 / 100 | 6 / 22 / 47 | 0.3 / 0.5 |
| checks (every applicable check, ad hoc) | 191 | 0.9% / 10.8% | 0.43% | 48 / 141 | 5 / 22 / 40 | 0.0 / 1.1 |
| policies (policy-driven checks) | 61 | 0.3% / 2.2% | 0.16% | 42 / 42 | 1 / 9 / 18 | 0.0 / 0.2 |
| idle (connected, nothing to do) | 65 | 0.1% / 0.4% | 0.06% | 42 / 42 | 1 / 9 / 19 | 0.0 / 0.0 |
| **all working phases** | **287** | **0.9% / 16.4%** | **0.47%** | **48 / 141** | **6 / 22 / 47** | **0.3 / 1.7** |

What it means:

* **Idle cost** is a single process of 42 MB RSS, 9 threads, 19 open descriptors, averaging 0.1% of one core.
* **Working cost** is small and short: the busiest moment was discovery at 16% of one core for a few seconds, when
  the agent ran osquery and the Ruby discovery modules (up to 6 processes, 22 threads). Memory peaked at 141 MB during
  the checks and returned to 42 MB. Disk I/O over five minutes of work was under 2 MB.
* **Host impact** was not measurable above the noise: host CPU busy averaged 13.7% while the agent worked and 15.5%
  while it idled (-1.8 points), with the agent tree itself at 0.47% of the host's CPU capacity. On this lab the
  target is an LXC container, so the host CPU busy and load figures are those of the physical node (shared with other
  guests), which is why they move independently of the agent; on a VM or bare-metal server they describe that server.
* The CPU protection configured in the agent (5% limit, three strikes) was never approached in the idle sample; the
  short peaks while working are the checks the instance asked for, which is what the protection is designed to govern.

Thresholds for the WARN flag (none hit): agent average CPU while working above 25% of one core, agent RSS peak above
400 MB, host CPU busy increase above 10 points.

## Windows Server 2025: result and performance (4 vCPU, 6 GB)

Run on 2026-11-08 with the performance sampler: **64 pass, 0 fail, 4 warn, 17 skip - agent verdict SAFE, no environment
findings.** The four warnings are informational: one ERROR line in the agent log after start (the first connection
attempt before the service had its certificate store), the shipped *Software Installed Policy* not yet having its
client list calculated by the platform's periodic job, the two lab signing certificates left in `C:\Windows\Temp`
by the test itself, and a UI screenshot on which the CI name could not be confirmed by text. The 17 skips are
background checks (not testable ad hoc), agent-internal check types and policies whose table or filter does not
select a Windows server. Everything else, including the signed custom PowerShell plugin (`acctest_users.ps1` through
its `.cmd` wrapper: 10 local users, 2 administrators), passed. The full list with every message is in
[windows-server-2025.md](windows-server-2025.md).

Performance, sampled every 5 seconds (92 samples). *Agent* is the service `AgentClientCollector` and everything it
spawned (PowerShell check scripts, osquery, Ruby discovery modules); handles stand in for file descriptors and the
processor queue length for load.

| phase | seconds | agent CPU avg / peak | share of host | agent RSS avg / peak MB | procs / threads / handles (max) | disk read / written MB | host CPU busy avg / peak |
|---|---:|---:|---:|---:|---:|---:|---:|
| discovery (host data collection) | 66 | 8.4% / 31.7% | 2.09% | 161 / 264 | 6 / 65 / 1570 | 35.5 / 0.7 | 16.4% / 32.1% |
| checks (every applicable check, ad hoc) | 296 | 6.4% / 47.8% | 1.59% | 102 / 264 | 6 / 65 / 1510 | 27.5 / 0.2 | 10.4% / 32.8% |
| policies (policy-driven checks) | 64 | 4.3% / 43.6% | 1.06% | 78 / 164 | 6 / 49 / 1314 | 3.5 / 0.0 | 6.1% / 25.7% |
| idle (connected, nothing to do) | 65 | 0.8% / 1.6% | 0.19% | 70 / 70 | 1 / 16 / 375 | 0.0 / 0.0 | 5.5% / 18.8% |
| **all working phases** | **426** | **6.4% / 47.8%** | **1.59%** | **107 / 264** | **6 / 65 / 1570** | **66.6 / 0.9** | **10.7% / 32.8%** |

What it means:

* **Idle cost** on Windows is one process of 70 MB working set, 16 threads, 375 handles, under 1% of one core.
* **Working cost is higher than on Linux, as expected from the Windows check content**: the checks run PowerShell and
  osquery processes (up to 6 at once, 65 threads, 1,570 handles), the agent tree peaked at 48% of one core for a few
  seconds and at 264 MB of working set, and read 67 MB from disk over seven minutes (osquery and the software inventory
  reading installed-program metadata). It returned to 70 MB and under 1% once the work was done.
* **Host impact**: host CPU busy averaged 10.7% while the agent worked against 5.5% while it idled, so about
  +5 points on a 4 vCPU VM, of which the agent tree itself accounted for 1.6% of the host's capacity; the rest is the
  work the checks cause elsewhere (WMI provider host, osquery's file reads). Host memory in use rose by up to 118 MB
  during the checks and fell back afterwards. None of the three WARN thresholds (25% average CPU, 400 MB peak RSS,
  10 points host CPU) was reached.
* This VM is a KVM guest on the same node as the Linux containers; the host figures describe the VM itself.

## Environment findings (not the agent's fault)

1. **Visibility content 2.1.1 ships Ruby plugins with Windows line endings** (asset `acc-visibility-modules-common`).
   Five executables have a CRLF shebang, so Linux runs `/usr/bin/env 'ruby\r'` and the check *VISC Browser Extension
   Discovery* exits 127 on every Linux host. The same files reach every agent version; identical on 7.1.2.
2. **The `basic_inventory` module in the `acc-f-modules` asset is broken on Linux**: `basic_inventory.rb` calls
   `getCommonsScriptFullPath` with three arguments while the same asset's `import_commons_scripts.rb` defines it with
   four, so `endpoint_discovery.rb --select=basic_inventory` returns an `ArgumentError` envelope with exit 0. The shipped
   discovery checks do not select that module and pass; only content that does (here the `acctest-custom-os-version`
   fixture) is affected.
3. **One lost discovery result on Rocky 9**: the shared MID Server was restarted by another user seven seconds after
   the agent had sent its result. The agent does not retry results of checks whose interval is under 300 seconds ("will
   not attempt any retries" in its log), so the instance showed *Collection failed*. The re-run with the MID stable
   collected host data normally.

Items 1 and 2 are observations about ServiceNow content; any change to them is ServiceNow's to make - raise a
support case rather than patching the files. See the repository's [NOTICE.md](../../NOTICE.md).

## Reading the report

The report opens with the agent verdict and the *Environment findings* table, then a per-host matrix, the packages,
the component inventory and every test by section with its evidence. Each failure carries a cause pill: *Agent*,
*Instance content*, *Server* or *Instance / MID*. Secrets are redacted; host names and addresses are those of the lab.
