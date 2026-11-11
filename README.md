# acctest - ServiceNow Agent Client Collector release qualification

> **Ownership.** The Agent Client Collector agent, the MID Server and the ACC content are ServiceNow® products, owned by
> ServiceNow, Inc. - proprietary, not open source. This repository contains **no ServiceNow software** and does not
> modify any: it is an independent harness that installs the agent as ServiceNow ships it and reports what it observes.
> It is shared **for use and information only**. Any change to the agent, its content or its behaviour is ServiceNow's
> to make - **contact ServiceNow Support** rather than patching ServiceNow files. Not affiliated with or endorsed by
> ServiceNow. Details in [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).

Every time ServiceNow ships a new Agent Client Collector (ACC) agent, this tool installs it on one server per
operating system, connects the agents **through a MID Server** (never directly to the instance), and proves that the
release is safe for production:

| Area | What is verified |
|---|---|
| Packages | the version the instance offers, every OS package downloaded into `dist/<version>/` with SHA-256 sums, plus the instance's install script; **[dist/README.md](dist/README.md)** lists every version ServiceNow has published with a download page per version (all OS and architecture packages, direct links, signatures) |
| Install | silent install on each target, `acc` service running and enabled, binary reports the version, `acc.yml` points at the MID endpoint with the API key, allow-list on |
| Connectivity | agent registers on the instance **via the configured MID**, status Up, instance sees the expected version, no errors in the agent log |
| Discovery | on-demand host data collection succeeds, a host CI of the right class is bound, name / IP / OS / related data populated |
| Check definitions | every active definition that applies to the target's CI class is run ad hoc on the agent - out-of-box, customized and **custom** ones - and judged on whether the agent executed it (exit 0/1/2 with output = works; command errors, timeouts = fail). The agent self-test is run too |
| Policies | every active published policy is evaluated against the host CI; matching ones must list the agent as a client and each of their check instances is tested on the agent |
| Resources | CPU protection settings read from `acc.yml`; the agent process tree is sampled while idle and must stay within `cpu_percentage_limit` (+ tolerance); **performance metrics** (Linux): a sampler on the host records the agent tree's CPU, RSS, threads, fds, processes and disk I/O and the host's CPU busy %, load and memory through discovery, checks, policies and idle - the report shows them per phase and the working-vs-idle difference as the agent's impact on the host |
| Cleanup | after discovery and checks: no child/zombie/osquery processes, no temp files, no panics, bounded disk footprint; optional uninstall must leave nothing behind |
| UI | headless Chromium logs in and screenshots the agent form, the host CI and the test results (UI-only verification) |

The result is `results/<version>/result.html` (self-contained, offline, light/dark): what was tested, the status of
each item, and for every failure exactly what failed with the evidence (command output, record values, log lines) -
plus `result.md`, the same report as Markdown (verdict, targets, findings, performance, every component with its
version, every test's status and message) for a repository, a wiki or a ticket.
`results/index.html` lists all versions tested so far.

Nothing in this repository is specific to one company or one lab. Everything environment-specific lives in two
git-ignored files: `.env` (instance, MID, credentials, lab) and `targets.yml` (the servers).

## Published results

`results/` is git-ignored (it holds the lab's addresses and UI screenshots), so each qualification that is worth keeping is
copied, sanitised, into `reports/<version>/` with a Markdown summary: **[reports/7.1.3/](reports/7.1.3/README.md)** -
agent 7.1.3 on six Linux distributions and Windows Server 2025, verdict SAFE, with the component inventory for the
security audit, performance metrics for Ubuntu 24.04 and Windows Server 2025, the full run and the Windows run as
Markdown (`result.md`, `windows-server-2025.md`), and the environment findings explained.

## Agent downloads

**[dist/README.md](dist/README.md)** is the index of every agent version on ServiceNow's download server (47 as of
2026-11-11, 2.5.0 to 7.1.3) with a page per version - `dist/<version>.md` - listing every package that exists for it:
Ubuntu / Debian x86_64 `.deb`, Ubuntu ARM64 `.deb`, RHEL-family and SUSE `.rpm`, Windows x64 `.msi`, macOS Intel and
Apple silicon `.pkg`, each with its direct link, size, date on the server, signature file and the SHA-256 of the
packages this harness downloaded. Each page also has a **change log** (summarised from ServiceNow's release notes on the
Store, kept in `dist/changelog.json`, with the full text linked) and the index says which **server and desktop** systems
ServiceNow supports - the same packages serve both. The packages themselves stay on `install.service-now.com`; nothing
is mirrored here.
`python acctest.py downloads` rebuilds the pages by asking the server what exists (HEAD per file - the server has no
index) and reads the Store listing; `--no-probe` re-renders from `dist/packages.json`. When the Store has a version with
no summary yet, or its notes changed since the summary was written, the command says so: add or revise the entry in
`dist/changelog.json` in your own words and render again.

## Requirements

* Python 3.11+ (3.12 used), `pip install -r requirements.txt` (pinned; every version older than 72 h when pinned)
* `python -m playwright install chromium` once (only for the UI section; set `BROWSER_ENABLED=false` to skip it)
* OpenSSH client on the PATH (Linux targets); WinRM reachable for Windows targets
* An instance with the **Agent Client Collector Framework** store app installed and a MID Server that is Up and
  validated. The tool creates the MID WebSocket listener and an API key itself when allowed (`MID_AUTO_CONFIGURE`,
  `ACC_API_KEY_AUTO_CREATE`), otherwise it expects them to exist.

## Set up

```bash
cp .env.example .env            # fill in - every key is documented in the file
cp targets.example.yml targets.yml
python acctest.py env check     # shows the effective settings (secrets redacted) and what is missing
python acctest.py preflight     # instance, ACC app, MID listener, API key, plugin cache, targets
python acctest.py versions      # agent version offered by the instance and the OS packages that exist
```

### Company

The ServiceNow admin gives you: instance URL, a user (ACC admin + MID read, no SSO, or SSO with a local account),
the MID Server name and the host name the agents will connect to, and the ACC API key. Put them in `.env`
(`MID_AUTO_CONFIGURE=false`, `ACC_API_KEY=<key>`). Ask for one server per OS type `versions` lists and describe
them in `targets.yml` (`transport: ssh` with a key, or `transport: winrm`). Targets do not need internet access:
the default install mode pushes the package from `dist/` and configures the agent locally.

### Home lab (Proxmox)

`.env` with `LAB_MODE=proxmox`, the node address/key and `LAB_OS_LIST`; then

```bash
python acctest.py lab provision   # one LXC container per OS, prerequisites installed, targets.yml written
python acctest.py lab status
python acctest.py lab destroy     # when done (or LAB_DESTROY_AFTER=true)
```

Containers use DHCP and are reached with `pct exec` through the node - no SSH inside them is needed.

### Custom content on an instance that has none (lab)

`python acctest.py fixtures create --filter "nameSTARTSWITHacc-"` creates a custom check definition
(`acctest-custom-os-version`, an osquery query the default allow-list already permits) and a custom policy
(`acctest-custom-policy`, published for the CIs matching the filter), so the custom-definition and policy paths of the
run are exercised. `fixtures delete` removes them. The company instance has its own custom content; the fixtures are
not needed there.

## Run

```bash
python acctest.py run                         # AGENT_VERSION from .env (default: latest the instance offers)
python acctest.py run --version 7.1.3         # a specific version (must exist on install.service-now.com)
python acctest.py run --mode script           # install with the instance's install script instead of the package
python acctest.py run --targets rhel9-app01   # a subset of targets.yml
python acctest.py run --skip-install          # re-test agents that are already installed
python acctest.py report 7.1.3                # re-render result.html from result.json
python acctest.py uninstall                   # remove the agent from the targets
python acctest.py versions --published        # every agent version that exists on the download server (HEAD probe)
python acctest.py downloads                   # dist/README.md + dist/<version>.md: every published version, every OS package link
python acctest.py runtimes --version 7.1.3 --version 7.1.2   # embedded Ruby / OpenSSL / gems per version, read from the deb
```

Exit code 0 = pass or warnings only, 1 = at least one failure. Logs go to `results/logs/`.

### Reading a failure: whose fault is it?

Every failure in `result.html` carries a **cause** so the reader does not have to work it out from the evidence:

| cause | meaning | changes with the agent version? |
|---|---|---|
| **Agent** | the package itself: binary, service unit, embedded Ruby/OpenSSL, CPU behaviour | yes |
| **Instance content** | check content delivered from the instance through the MID: plugin assets, check definitions, allow-lists | **no** - the same files reach every agent version until the content app is fixed |
| **Server** | the server under test: a missing tool in PATH, sudoers, file modes, network | no |
| **Instance / MID** | the instance or MID Server: stale plugin cache (ACC-1500), listener, API, a MID restart while a result was in flight | no |

Two attributions that are easy to misread, both seen on the 2026-11-08 qualification run:

* **"Host data collected" fails with `Collection failed` on one host while every other host passes.** The agent sends a
  discovery result exactly once - "interval for check is less than 300 seconds, will not attempt any retries" in its log -
  so a MID that restarts in the seconds after the send loses the result. The tool compares the MID's `started` time with the
  moment it requested the collection and attributes a later start to *Instance / MID*; a `websocket: close 1006` plus
  `connection refused ... wss://` in the agent log says the same. Re-run that host once the MID is stable.
* **A check exits 0 but its output is an error envelope** (`{"<module>":{"error_backtrace":..., "error_msg":...}}`). That is
  `endpoint_discovery.rb` reporting that one of its modules crashed. It is *Instance content*: the Ruby that crashed came
  from the content app, not from the agent. The fixture `acctest-custom-os-version` (which reuses the shipped
  `basic_inventory` module) fails this way on Visibility content 2.1.1 - see the known behaviours below.

The report opens with the **Agent verdict**: SAFE when no failure is owned by the agent (or left unattributed), NOT SAFE
otherwise. Failures owned by the server, the instance content or the MID are listed apart as *Environment findings*; they
do not fail the qualification, and `run` exits 0 on a SAFE verdict even when such findings exist. A failure the evidence
cannot attribute counts against the agent on purpose - read it. `report <version>` attributes causes retroactively for a
`result.json` written before this existed.

The report also carries the **component inventory** for the security team (`components.csv` beside it): the agent
version, the Go toolchain, the embedded Ruby and OpenSSL, every shared library and gem the package ships, and the plugin
assets and osquery version the instance delivered - read from the package before installing and again on every host
after installing.

### Performance metrics: what the agent costs the host

On every Linux target a POSIX-sh sampler (`acctest/perf.py`, written to `/tmp/acctest-perf/` and removed afterwards) runs from
the moment the agent is connected until the idle CPU sample is over. Every `PERF_STEP_S` seconds it records raw counters
from `/proc`: host CPU ticks, load average, memory, and for the agent's whole process tree (`acc` plus the checks and
osquery it spawns) CPU ticks, RSS, threads, open file descriptors, process count and bytes read / written. The runner
marks the phase boundaries, so the **Performance** section of the report shows, per target and per phase (connect,
discovery, checks, policies, inventory, idle, plus "all working phases" and "whole window"):

| column | meaning |
|---|---|
| Agent CPU avg / peak | the agent tree, in % of one core |
| Share of host | the same CPU as a fraction of all cores on the host |
| Agent RSS avg / peak | resident memory of the tree, MB |
| Procs / threads / fds | peak process count, threads and open descriptors of the tree |
| Disk read / written | bytes the tree read from / wrote to block devices during the phase (needs root to read `/proc/<pid>/io`) |
| Host CPU busy avg / peak | the whole machine, everything included |
| Load1 max, Host memory used Δ | host load average peak and the change in used memory over the phase |

The **impact** line under each table is the host's CPU busy % while the agent worked minus while it idled, and the agent
tree's own average share of the host's capacity while working. The test row *Agent resource usage and host impact
while working* is PASS or WARN only (the budget is yours): WARN when the agent's average CPU while working exceeds
`PERF_CPU_AVG_WARN_PCT` (25% of one core), its RSS peak exceeds `PERF_RSS_PEAK_WARN_MB` (400 MB), or the host CPU busy
increase exceeds `PERF_HOST_IMPACT_WARN_PCT` (10 points). Raw per-interval samples are written to `perf-<target>.csv`
next to the report. Windows targets are sampled the same way by a PowerShell script started through WMI (so it outlives the SSH session);
there handles stand in for fds and the processor queue length for the load average. On an LXC container the host CPU busy and load figures are the physical
node's (shared with every other guest), so read the agent's own CPU and *share of host* there; on a VM or bare metal they
describe that server. Worked examples with numbers (Ubuntu 24.04 and Windows Server 2025) are in [reports/7.1.3/README.md](reports/7.1.3/README.md).

### Which version fixes a Ruby / OpenSSL CVE?

The agent embeds its own Ruby and OpenSSL. Upgrading the ACC Framework app on the instance changes nothing on the servers
(ServiceNow KB1710136); only a newer **agent build** does. `runtimes` reads the embedded versions out of the packages in
`dist/` without installing anything, so the question "which agent carries Ruby >= x.y.z" is answered from the downloads;
the summary card of `result.html` shows the same for the version qualified. Read 2026-11-08 from the download server:

| agent | embedded Ruby | embedded OpenSSL |
|---|---|---|
| 7.1.3 (2026-11-04) | **3.3.13** (2026-10-23) | 3.5.9 |
| 7.1.2, 7.1.1 | 3.3.2 (2024-05-30) | 3.4.7 |
| 7.0.4, 6.6.x | 3.3.2 | 3.4.6 |
| 6.5.1 … 4.3.2 | 3.3.2 | 3.4.5 … 3.3.2 |
| 3.5.5 | 3.2.2 (2023) | - |

So every build from 4.3.2 to 7.1.2 shares one Ruby from May 2024; 7.1.3 is the first with the October 2026 Ruby fixes
(resolv 0.3.2, Onigmo regexp CVEs). Re-run `runtimes` for newer builds rather than trusting this table.

## What ends up where

```
dist/<version>/install_agent.sh            the instance's install script for that version
dist/<version>/<os-key>/<package>          agent packages (+ signature zip) as served by install.service-now.com
dist/<version>/manifest.json               sizes and SHA-256 of everything above
dist/README.md, dist/<version>.md          download pages: every published version, every OS/arch package (committed)
dist/packages.json                         the probed catalog the pages are rendered from (committed)
results/<version>/result.html|result.json  the report and its data
results/<version>/screenshots/             UI screenshots referenced by the report
results/index.html                         all versions tested
```

## How it works (for whoever maintains it)

* `acctest/snow.py` - REST client. Server-side JavaScript runs through a run-once `sys_trigger` whose output is read
  back from `syslog` (the only way to call scoped script includes such as the ACC setup without a UI session).
* `acctest/agents.py` - reads the agent version (`sn_agent.agent_version`) and the OS map (`AgentScripts` script
  include) from the instance and builds the public package URLs; downloads into `dist/`.
* `acctest/downloads.py` - the download pages: probes the server for every published version and package, keeps
  the SHA-256 of the packages downloaded locally, renders `dist/README.md` and `dist/<version>.md`.
* `acctest/mid.py` - ACC listener (`AgentNowSetup.setupExt`), API key (`mid_webserver_api_key_credentials`, value
  generated by the platform and read through `AgentSingleLineInstallerCommands`), plugin cache state and MID restart.
* `acctest/targets.py` - transports (ssh / pct / winrm); scripts travel on stdin, never quoted into command lines.
* `acctest/installer.py` - install (package or script mode), status, config, log, uninstall, leftovers.
* `acctest/discovery.py`, `acctest/checks.py`, `acctest/resources.py` - the verifications.
* `acctest/runner.py` - the order of events and every pass/fail decision; `acctest/report.py` renders the HTML.
* `tests/test_offline.py` - unit tests that need neither an instance nor a lab (`python -m unittest discover -s tests`).

### Custom plugins: how a script of your own reaches the agent, and why it must be signed

The fixtures include a real custom plugin, `acctest/fixture_plugin/` (a shell script and a PowerShell script that list
local users with their groups and admin status), delivered exactly the way a customer's own content is:

1. The scripts are packed as `bin/<script>` (0755, LF line endings) plus `allow_list/<name>.json` into `<asset>.tar.gz`.
   The allow-list entry for a command without arguments is `{"exec": "x.sh", "args": [""], "skip_arguments": true}`
   (an empty `args` list is rejected: "args cannot be empty").
2. That archive is **signed**: the outer `<asset>.tar.gz` holds `<asset>.sig` (base64 of an RSA PKCS#1 v1.5 SHA-256
   signature over the inner archive) and the inner `<asset>.tar.gz`. ACC 7.x agents verify every plugin they fetch
   (`verify-plugin-signature`, default true) and refuse one without a signature they can validate - **so a customer's
   custom scripts stop running on 7.x agents unless they are signed** (or verification is switched off, which the tool
   does not do).
3. The signing certificate reaches the agents as a zip the MID Server serves from
   `<MID home>/agent/static/cert/customer/` (`fixtures create` copies it there when `MID_SSH_TARGET`/`MID_HOME` are set,
   otherwise it names the file and the directory). The agent fetches it the first time a verification fails and keeps it
   under `cert/customer/`. An agent never refetches a zip of a name it already has, so a re-issued certificate needs a
   new zip name (the tool names the zip after the certificate's fingerprint).
4. The certificate must chain to a root the **host** trusts: the agent validates the signer against the OS trust store
   ("x509: certificate signed by unknown authority" otherwise). At the company that is the internal CA, so sign with a
   code-signing certificate it issued (`PLUGIN_SIGNING_KEY` / `PLUGIN_SIGNING_CERT`). In the lab the tool generates a
   root CA plus a code-signing leaf under `.state/signing/` and, with `TRUST_SIGNING_CERT_ON_TARGETS=true`, installs
   the root on each target at install time. The root must carry no extended key usage: RHEL and SUSE build their TLS
   bundle with p11-kit, which drops anchors that lack the serverAuth purpose, and Go programs such as the agent read
   only that bundle - a self-signed code-signing certificate is trusted on Debian/Ubuntu alone.
5. The asset record (`sn_agent_asset`, os/platform/arch = all) cannot be inserted over REST without its attachment, so
   the tool inserts it from a run-once script with workflow off, attaches the file, then activates it. Check definitions
   reference it through `sn_agent_asset_name`, and a check group (`sn_agent_check_group.ci_type`) pins each definition to
   its CI class so the Linux script is never offered to a Windows agent.

On Windows the check command is a `.cmd` wrapper (`acctest_users.cmd`) that starts the `.ps1` next to it: `cmd`/`exec`
resolve `.cmd` through PATH, PowerShell needs a full path. The report verifies the scripts' output (header marker, one
JSON object per user, footer count, the built-in administrator present), not just the exit code.

### Windows targets

The Windows service is **`AgentClientCollector`** (not `acc`); files live under `C:\Program Files\ServiceNow\agent-client-collector`
(binary, embedded Ruby) and `C:\ProgramData\ServiceNow\agent-client-collector` (`config\acc.yml`, `log\acc.log`, `cache\`).
Targets can be reached over WinRM (`transport: winrm`, NTLM) or over OpenSSH with PowerShell as the shell
(`transport: ssh`, `family: windows`, key auth for an administrator) - both are implemented; the lab uses SSH.
`msiexec` exit 1638 (this version already installed) is treated as success.

### Host access the agent needs for a self-upgrade (Linux)

Read from the upgrade plugins the agent runs (`acc-f-commons/bin/linux_upgrade_checks.rb`, `linux_run_upgrade.rb`).
The agent runs as the unprivileged `servicenow` user, so an upgrade started from the instance ("Upgrade agent") works
only when that user can `sudo` five commands, with the arguments the instance sends, **without a password and without a
TTY** (the agent has neither). Before touching anything the plugin runs `sudo -l <command>` for each; one refusal aborts
the upgrade. The package arrives from the MID into `/var/cache/servicenow/agent-client-collector/upgrade/...`, so the
install rule needs a wildcard for that path:

| step | command the plugin runs with `sudo` |
|---|---|
| stop the service | `systemctl stop acc` |
| install the new package | `dpkg -i /var/cache/servicenow/agent-client-collector/upgrade/*.deb` or `rpm -U .../upgrade/*.rpm` (zypper/yum on the distros that use them) |
| reload systemd | `systemctl daemon-reload` (a failure here is only a warning) |
| start the service | `systemctl start acc` |
| detach the upgrade from the service being replaced | `systemd-run ...` (the agent spawns the upgrade outside its own cgroup so stopping `acc` does not kill it) |

Beyond upgrades, discovery content asks for `sudo` on `dmidecode` (serial numbers), `ss` (TCP connections to
processes) and `osqueryi` (running processes with elevated detail); without them those fields stay empty and the
self-test reports `SudoSSCommandAccessTest` as failed, nothing else breaks. `sudo` itself must be installed (minimal
RHEL-family images ship without it) and `Defaults requiretty` must not apply to `servicenow`. Keep the rules to exact
paths and NOPASSWD, in `/etc/sudoers.d/`, and check them with `sudo -l -U servicenow`.

### Known behaviours of the platform the tool handles

* **Visibility content 2.1.1 ships Ruby plugins with Windows line endings.** The `acc-visibility-modules-common` asset
  (inner tarball `agent-client-collector-visibility-content-2.1.0-rc.2-...`, built 2026-09-25) has CRLF in all 44 Ruby
  files; five are executables with a shebang, so Linux runs `/usr/bin/env 'ruby\r'` and fails with exit 127
  ("VISC Browser Extension Discovery"). The content is the same for every agent version - the report marks it
  *Instance content*. The `Resources > plugins` test scans the delivered plugins for this on every run.
* **Visibility content 2.1.1's `basic_inventory` module is broken on Linux.** In the `acc-f-modules` asset,
  `bin/basic_inventory.rb` calls `getCommonsScriptFullPath(cache, script, log_level)` with three arguments while the same
  asset's `bin/import_commons_scripts.rb` defines it with four (`..., logFile`), so
  `endpoint_discovery.rb --select=basic_inventory` returns an `ArgumentError` envelope with exit 0 on every Linux host and
  every agent version (verified on 7.1.2 and 7.1.3, six distributions). The shipped discovery checks do not select that
  module (`check-discovery-basic` and `Enhanced Discovery` pass), so it only bites content that does - such as the
  `acctest-custom-os-version` fixture, which the report now marks *Instance content*.
* **ACC-1500 "hash of the file does not match"** on discovery: the MID keeps the hash of each plugin asset it serves
  from the time it started; after the ACC app is installed or upgraded the MID must be restarted. Pre-flight detects
  assets newer than the MID start and (with `MID_AUTO_CONFIGURE=true`) syncs + restarts the MID; the discovery step
  retries once after the same remedy.
* The Linux install script needs `curl`, `gpg` and `unzip` on the target (signature validation); `lab provision`
  installs them. For your own servers make sure they are present or use `--mode package`.
* The agent's discovery and self-test lean on host tools: `which` (discovery on minimal RHEL-family images fails with
  "No such file or directory - which"), `sudo` + `ss` (self-test `SudoSSCommandAccessTest`), `ifconfig` (logged as an
  error on hosts without net-tools). The lab provisioning installs them; the report shows each as a finding on servers
  that lack them, which is exactly what a production rollout needs to know.
* The agent runs as the `servicenow` user and ServiceNow expects a sudoers entry for it (self-test
  `SudoSSCommandAccessTest`, osquery as sudo for serial numbers). Neither the package nor the install script creates
  it; the report flags the missing entry on every server. Add it the way your ACC admin prescribes.
* Plugin scripts arrive from the MID with the Visibility content; the Resources section scans them for Windows line
  endings in the shebang (`'ruby
': No such file or directory`, exit 127) - a content defect, not a server problem.
* Ad-hoc "Test check" needs the *discovered host CI* (class per check group, default `cmdb_ci_computer`), so checks
  and policies run only after discovery succeeded.
* The API key value cannot be chosen: the platform generates it on insert. The generated key is written back into
  `.env` so later runs reuse it.

## Limitations (today)

* Windows targets: the WinRM transport and the MSI install/uninstall are implemented but have not been exercised -
  there is no Windows server in the home lab. Expect to adjust `installer.py` paths on the first Windows run.
* macOS packages are catalogued and downloaded but no installer exists for them.
* Policies that select CIs by script or by group are reported as "not evaluated"; table + filter policies are
  evaluated against the host CI on the instance.
* In unprivileged LXC containers (the home lab) the rpm's systemd unit cannot apply `CPUSchedulingPolicy=` and the
  service never starts (214/SETSCHEDULER, seen on openSUSE 15.6); the tool adds a drop-in that clears the directive
  in containers only and reports it. Real servers are unaffected.
* Agents are left installed after a run unless `UNINSTALL_AFTER=true` (so the ACC admin can look at them).

## Safety

* `.env`, `targets.yml`, `dist/` and `results/` are git-ignored. `tests/test_offline.py` fails if a committed file
  contains an instance name, a lab address or a key. Review `git status` before every commit anyway.
* The tool never changes anything on the instance beyond: the MID listener extension records, an API key record,
  ad-hoc check test requests and discovery requests (all also available as buttons in the ACC UI) and, when allowed,
  a MID restart. It never touches policies or check definitions.
