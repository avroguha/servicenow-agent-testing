# Agent Client Collector 7.1.3 - qualification result (2026-11-08)

**Agent verdict: SAFE.** No failure in the run is owned by the agent. Every finding is in the environment (instance
content, or a MID Server restart during the test) and is listed with its cause in the report.

Files in this folder (sanitised copies of the lab results - UI screenshots and the lab's Windows host name removed):

| file | what |
|---|---|
| [result.html](result.html) | the full report: verdict, every test on every host, evidence, cause per failure, component inventory, settings |
| [components.csv](components.csv) | the component inventory for a security audit (926 rows: agent, Go runtime, embedded Ruby and OpenSSL, shared libraries, gems, plugin content) |
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
