# Agent Client Collector - all published versions

Every agent version on ServiceNow's download server and the packages that exist for it, found by asking the server file by file (there is no index). Probed 2026-11-11; base URL `https://install.service-now.com/glide/distribution/builds/package/app-signed/`. Open a version for the direct links, sizes, signatures and SHA-256 sums. The packages are ServiceNow's and are not mirrored here (see [NOTICE.md](../NOTICE.md)).

Regenerate with `python acctest.py downloads` (re-probes the server) or `python acctest.py downloads --no-probe` (re-renders from `packages.json`).

## Package types

| Column | File | Covers |
|---|---|---|
| Ubuntu x86_64 | `agent-client-collector-<version>-ubuntu-1804_amd64.deb` | every Ubuntu release (the install script picks this build for Ubuntu 18.04 and later and falls back to it for older ones); it also installs on other Debian-family distributions |
| Debian x86_64 | `agent-client-collector-<version>-debian-9_amd64.deb` | every Debian release - the install script picks this build for Debian whatever the version (it is built on Debian 9) |
| Debian 8 | `agent-client-collector-<version>-debian-8_amd64.deb` | Debian 8 only; published for the 2.x releases and 3.0.0, dropped afterwards |
| Ubuntu ARM64 | `agent-client-collector-<version>-ubuntu-2204_arm64.deb` | Ubuntu 22.04 and later on ARM64 (the install script refuses older Ubuntu on ARM); published since 6.5.1 |
| RPM x86_64 | `agent-client-collector-<version>-x86_64.rpm` | RHEL, CentOS, Rocky, AlmaLinux, Oracle Linux, Amazon Linux, SLES and openSUSE (the install script accepts any distribution whose ID_LIKE says rhel or centos); published since 3.3.1. There is no ARM64 rpm |
| Windows x64 | `agent-client-collector-<version>-windows-x64.msi` | Windows Server and Windows desktops (the Store lists Windows 10 Enterprise and Windows 11 Pro/Enterprise), 64-bit Intel/AMD only. There is no Windows ARM64 build |
| macOS Intel | `agent-client-collector-<version>-macos_x64.pkg` | macOS on Intel Macs (desktops and laptops); published since 2.9.0 |
| macOS ARM64 | `agent-client-collector-<version>-macos_arm64.pkg` | macOS on Apple silicon (M-series) Macs; published since 3.1.0 |

## Server or desktop

The same packages install on servers and on desktops or laptops - there is no separate desktop build. ServiceNow's Store listing describes the Framework as suitable for on-premises servers, VMs, cloud instances and end-user desktops and laptops, and lists these systems for version 7.1.3 (fetched 2026-11-11 from the [Store listing](https://store.servicenow.com/store/app/bc09636e1be06a50a85b16db234bcbd1)):

**x86_64**

- Linux
  - Red Hat Enterprise Linux - 7, 8, 9, 10, Rocky Linux - 10, Oracle Linux - OL 7, 8, 9, 10
  - CentOS 7, CentOS Stream 8 and 9
  - SLES 12, 15
  - Ubuntu 18.04, 20.04, 22.04 LTS and 24.04 LTS
  - Debian 9, 10, 11, 12 and 13
  - Amazon Linux 2, Amazon Linux 2023
- Microsoft Windows
  - Windows Server 2012, 2012r2, 2016, 2019, 2022, 2025
  - Windows 10 Enterprise Edition
  - Windows 11 Professional and Enterprise
- MacOS (x86_64 only)
  - 10.15 - Catalina
  - 11 - Big Sur
  - 12 - Monterey
  - 13 - Ventura
  - 14 - Sonoma
  - 15 - Sequoia
  - 26 - Tahoe
  - 27 - Golden Gate

**ARM64**

- MacOS
  - 12 - Monterey
  - 13 - Ventura
  - 14 - Sonoma
  - 15 - Sequoia
  - 26 - Tahoe
- Linux
  - Ubuntu 22.04 LTS

Limits that matter for desktops and laptops:

- There is no Windows build for ARM. The only ARM64 Linux build is for Ubuntu 22.04 or later. Apple silicon Macs are supported.
- The Monitoring (ACC-M) and Log Analytics (ACC-L) apps that run on the agent are supported on server operating systems only.
- The listing says the Framework does not support Virtual Desktop Infrastructure, while the 7.0.4 release notes announce official support for non-persistent VDI. Check with ServiceNow before relying on either.

## acc.yml changes across versions

Read from the Ubuntu x86_64 package of 47 versions. Only versions whose shipped `acc.yml`, default allow-list or service unit differ from the version before are listed; each version page has its full default table.

What matters when upgrading:

- **An upgrade keeps your acc.yml and your allow-list.** The deb ships `acc.yml.example` and `check-allow-list.json.default`; the install script copies them to `acc.yml` and `check-allow-list.json` only when no `acc.yml` exists yet, and otherwise prints "Keeping old ... configuration file" (read from the 7.1.3 install script). A default changed below therefore reaches a host only through a fresh install or your own edit - compare your files with the table of the version you install.
- **TLS to the MID is not verified by default, in every version.** The template has always set the skip-verification flag to true. To verify the MID's certificate set `insecure-skip-tls-verify: false` and point `trusted-ca-file` at the CA that signed it.
- **3.1.0 renamed `skip-tls-verify` to `insecure-skip-tls-verify`.** A file written by 3.0.x or older that sets `skip-tls-verify: false` should be changed to the new name; whether newer agents still read the old name was not tested here.
- **3.3.1 turned Auto MID Selection off by default** (`enable-auto-mid-selection: false`); the agent then uses `backend-url` in the order given. Older files keep `true`.
- **3.5.2 cut the default allow-list from 77 commands to 10** (the discovery modules plus `acc`, `osqueryi`, `read-file.rb` and the restart and upgrade helpers). The old monitoring scripts (check-*, metrics-*) are allowed through the allow-lists that come with each ACC plugin instead; `allow-list-global-only`, documented since the same version, turns those off. A host installed before 3.5.2 and upgraded since still has the long list.
- **5.0.0 put the MID-less keys in the template** (`connect-without-mid: false`, `instance-url`, `registration-key`); they were only documented since 3.1.0.
- **The template has not changed since 6.0.0** (`pac-file` documented). Between 6.0.0 and 7.1.3 only the allow-list (6.4.0, 7.1.1) and the service unit (6.1.0 to 6.4.0) changed.
- **rpm installs differ.** The rpm ships neither template (the install script says so), so on RHEL-family and SUSE hosts `acc.yml` is written by the agent's own `acc gateway mid` command and has no `allow-list:` line - every command is allowed unless you add one. This matches what the qualification runs found on Rocky and openSUSE.

**[2.6.0](2.6.0.md)** (from 2.5.0)

- systemd unit: `Service.Environment` `AGENT_ROOT=/usr/share | AGENT_CACHE_ROOT=/var/cache | AGENT_CONFIG_ROOT=/etc | AGENT_LOG_ROOT=/var/log | AGENT_RUN_ROOT=/var/run` -> `AGENT_ROOT=/usr/share | AGENT_CACHE_ROOT=/var/cache | AGENT_CONFIG_ROOT=/etc | AGENT_LOG_ROOT=/var/log | AGENT_RUN_ROOT=/var/run | RUBYOPT=-Eutf-8`

**[2.7.0](2.7.0.md)** (from 2.6.0)

- acc.yml: new key `check-commands-prefer-installed` documented (commented out, example `false`)
- acc.yml: key `disable-api` removed (was set to `true`)
- allow-list: 6 command(s) added: `file_systems.rb`, `network_adapters.rb`, `running_processes.rb`, `serial_numbers.rb`, `storage_devices.rb`, `tcp_connections.rb`
- allow-list: now accepts any arguments for `endpoint_discovery.rb`

**[3.0.0](3.0.0.md)** (from 2.10.1)

- acc.yml: `agent_cpu_threshold.proxy_cpu_percentage_limit` default `15` -> `80`

**[3.1.0](3.1.0.md)** (from 3.0.0)

> The TLS flag was renamed in this version: an existing acc.yml that sets `skip-tls-verify` should use `insecure-skip-tls-verify` from now on.

- acc.yml: new key `connect-without-mid` documented (commented out, example `true`)
- acc.yml: new key `insecure-skip-tls-verify` set to `true`
- acc.yml: new key `instance-url` documented (commented out, example `""`)
- acc.yml: new key `registration-key` documented (commented out, example `""`)
- acc.yml: key `skip-tls-verify` removed (was set to `true`)
- allow-list: no longer accepts any arguments for `endpoint_discovery.rb`
- allow-list: `endpoint_discovery.rb` arguments are now matched as regular expressions

**[3.2.0](3.2.0.md)** (from 3.1.0)

- allow-list: `endpoint_discovery.rb` - 2 allowed argument pattern(s) added: `(--log-level|--l)=(FATAL|ERROR|WARN|INFO|DEBUG)`, `(--select|--s)=((basic_inventory|data_collection|tcp_connections|running_processes|cloud),?)+`; 3 removed: `(--select|-s)=((basic_inventory|data_collection|tcp_connections|running_processes|cloud),?)+`, `(FATAL|ERROR|WARN|INFO|DEBUG)`, `--log-level|-l`

**[3.3.1](3.3.1.md)** (from 3.2.0)

> Auto MID Selection is off by default from this version; hosts installed earlier keep it on unless their acc.yml is edited.

- acc.yml: `enable-auto-mid-selection` default `true` -> `false`

**[3.4.0](3.4.0.md)** (from 3.3.1)

- allow-list: `endpoint_discovery.rb` - 6 allowed argument pattern(s) added: `((basic_inventory|data_collection|tcp_connections|running_processes|cloud),?)+`, `(FATAL|ERROR|WARN|INFO|DEBUG)`, `--log-level=(FATAL|ERROR|WARN|INFO|DEBUG)`, `--select=((basic_inventory|data_collection|tcp_connections|running_processes|cloud),?)+`, `-l`, `-s`; 2 removed: `(--log-level|--l)=(FATAL|ERROR|WARN|INFO|DEBUG)`, `(--select|--s)=((basic_inventory|data_collection|tcp_connections|running_processes|cloud),?)+`

**[3.5.2](3.5.2.md)** (from 3.4.1)

> The default allow-list now covers only the discovery modules; monitoring checks are allowed by the plugins' own allow-lists. The install script copies the default only on a fresh install, so a host upgraded from an older version keeps its old, longer check-allow-list.json.

- acc.yml: new key `allow-list-global-only` documented (commented out, example `false`)
- acc.yml: new key `disable-assets` documented (commented out, example `false`)
- allow-list: 3 command(s) added: `basic_inventory.rb`, `data_collection.rb`, `runUpgrade.rb`
- allow-list: 70 command(s) removed: `check-cpu.rb`, `check-disk-usage.rb`, `check-head-redirect.rb`, `check-kube-apiserver-available.rb`, `check-kube-pods-restarting.rb`, `check-kube-pods-running.rb`, `check-kube-pods-runtime.rb`, `check-kube-service-available.rb` and 62 more
- allow-list: `osqueryi` - 9 removed: `"select * from apps"`, `"select * from certificates"`, `"select * from chrome_extensions"`, `"select * from logged_in_users"`, `"select name, path, pid FROM processes WHERE on_disk = 0"`, `"select network_name, last_connected, captive_portal FROM wifi_networks WHERE captive_portal=1"`, `"select path, type, round((blocks_available * blocks_size *10e-10),2) as gigs_free from mounts where path='/'"`, `"select pid, name, uid, resident_size from processes order by resident_size desc limit 10"` and 1 more
- allow-list: `running_processes.rb` - 5 allowed argument pattern(s) added: `--parent_cache_dir`, `-d`, `/Library/Caches/servicenow/agent-client-collector/`, `/var/cache/servicenow/agent-client-collector/`, `C:\ProgramData\ServiceNow\agent-client-collector\cache`; 1 removed: `""` (empty)
- allow-list: `tcp_connections.rb` - 5 allowed argument pattern(s) added: `--parent_cache_dir`, `-d`, `/Library/Caches/servicenow/agent-client-collector/`, `/var/cache/servicenow/agent-client-collector/`, `C:\ProgramData\ServiceNow\agent-client-collector\cache`; 1 removed: `""` (empty)

**[5.0.0](5.0.0.md)** (from 4.3.2)

- acc.yml: `connect-without-mid` now set to `false` (was only documented)
- acc.yml: `instance-url` now set to `""` (was only documented)
- acc.yml: `registration-key` now set to `""` (was only documented)

**[6.0.0](6.0.0.md)** (from 5.0.4)

- acc.yml: new key `pac-file` documented (commented out, example `https://example.com/proxy.pac`)
- allow-list: `acc` - 14 allowed argument pattern(s) added: `--cache-dir=(.*)`, `--config-file=(.*)`, `--exec-timeout=(.*)`, `--format=(text|json)`, `--run-timeout=(.*)`, `--suite=(.*)`, `--suites`, `--test-timeout=(.*)` and 6 more; 2 removed: `self-test debug`, `self-test verbose`
- allow-list: `acc` arguments are now matched as regular expressions

**[6.1.0](6.1.0.md)** (from 6.0.4)

> The unit now stops the whole process tree (KillMode=control-group); 6.3.0 reverted this and 6.4.0 restored it for good. The 6.5.1 release notes report that stopping the service on Linux now ends child processes.

- systemd unit: `Service.KillMode` `process` -> `control-group`
- systemd unit: `Service.KillSignal` (absent) -> `SIGTERM`
- systemd unit: `Service.SendSIGKILL` (absent) -> `yes`
- systemd unit: `Service.TimeoutStopSec` (absent) -> `30`

**[6.3.0](6.3.0.md)** (from 6.1.0)

> The 6.1.0 unit change was reverted in this version and restored in 6.4.0.

- systemd unit: `Service.KillMode` `control-group` -> `process`
- systemd unit: `Service.KillSignal` `SIGTERM` -> (removed)
- systemd unit: `Service.SendSIGKILL` `yes` -> (removed)
- systemd unit: `Service.TimeoutStopSec` `30` -> (removed)

**[6.4.0](6.4.0.md)** (from 6.3.0)

> From here on the unit stops the agent's whole process tree, waiting 30 s before SIGKILL.

- allow-list: 1 command(s) removed: `runUpgrade.rb`
- allow-list: no longer accepts any arguments for `read-file.rb`
- allow-list: `read-file.rb` arguments are now matched as regular expressions
- systemd unit: `Service.KillMode` `process` -> `control-group`
- systemd unit: `Service.KillSignal` (absent) -> `SIGTERM`
- systemd unit: `Service.SendSIGKILL` (absent) -> `yes`
- systemd unit: `Service.TimeoutStopSec` (absent) -> `30`

**[7.1.1](7.1.1.md)** (from 7.0.4)

> `read-file.rb` may now also read the AI proxy log, for the AI proxy introduced in this version. The template itself is unchanged: the install script appends `ai-proxy-enabled: true` to acc.yml when the AI proxy is enabled at install (7.1.3 script).

- allow-list: `read-file.rb` - 3 allowed argument pattern(s) added: `/servicenow/agent-client-collector/ai_proxy\.log`, `AGENT_LOG_ROOT`, `\\ServiceNow\\agent-client-collector\\log\\ai_proxy\.log`


## Versions

Latest: **[7.1.3](7.1.3.md)**.

| Version | On the server | Ubuntu x86_64 | Debian x86_64 | Debian 8 | Ubuntu ARM64 | RPM x86_64 | Windows x64 | macOS Intel | macOS ARM64 | Change log | acc.yml | Report |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|---|---|
| [7.1.3](7.1.3.md) | 2026-11-04 | yes | yes | - | yes | yes | yes | yes | yes | [Patch](7.1.3.md#change-log) | same | [qualification report](../reports/7.1.3/README.md) |
| [7.1.2](7.1.2.md) | 2026-10-23 | yes | yes | - | yes | yes | yes | yes | yes | - | same |  |
| [7.1.1](7.1.1.md) | 2026-09-24 | yes | yes | - | yes | yes | yes | yes | yes | [Minor](7.1.1.md#change-log) | [changed](7.1.1.md#changes-from-the-previous-version) |  |
| [7.0.4](7.0.4.md) | 2026-09-03 | yes | yes | - | yes | yes | yes | yes | yes | [Major](7.0.4.md#change-log) | same |  |
| [7.0.3](7.0.3.md) | 2026-09-02 | yes | yes | - | yes | yes | yes | yes | yes | - | same |  |
| [7.0.2](7.0.2.md) | 2026-09-01 | yes | yes | - | yes | yes | yes | yes | yes | - | same |  |
| [7.0.1](7.0.1.md) | 2026-08-31 | yes | yes | - | yes | yes | yes | yes | yes | - | same |  |
| [6.6.4](6.6.4.md) | 2026-08-06 | yes | yes | - | yes | yes | yes | yes | yes | [Patch](6.6.4.md#change-log) | same |  |
| [6.6.2](6.6.2.md) | 2026-07-20 | yes | yes | - | yes | yes | yes | yes | yes | - | same |  |
| [6.6.1](6.6.1.md) | 2026-06-29 | yes | yes | - | yes | yes | yes | yes | yes | [Minor](6.6.1.md#change-log) | same |  |
| [6.5.1](6.5.1.md) | 2026-06-18 | yes | yes | - | yes | yes | yes | yes | yes | [Patch](6.5.1.md#change-log) | same |  |
| [6.5.0](6.5.0.md) | 2026-06-05 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [6.4.0](6.4.0.md) | 2026-05-29 | yes | yes | - | - | yes | yes | yes | yes | - | [changed](6.4.0.md#changes-from-the-previous-version) |  |
| [6.3.0](6.3.0.md) | 2026-04-22 | yes | yes | - | - | yes | yes | yes | yes | - | [changed](6.3.0.md#changes-from-the-previous-version) |  |
| [6.1.0](6.1.0.md) | 2026-04-10 | yes | yes | - | - | yes | yes | yes | yes | - | [changed](6.1.0.md#changes-from-the-previous-version) |  |
| [6.0.4](6.0.4.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | [Patch](6.0.4.md#change-log) | same |  |
| [6.0.1](6.0.1.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [6.0.0](6.0.0.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | - | - | [changed](6.0.0.md#changes-from-the-previous-version) |  |
| [5.0.4](5.0.4.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [5.0.2](5.0.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | [Patch](5.0.2.md#change-log) | same |  |
| [5.0.1](5.0.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | [Patch](5.0.1.md#change-log) | same |  |
| [5.0.0](5.0.0.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | [Minor](5.0.0.md#change-log) | [changed](5.0.0.md#changes-from-the-previous-version) |  |
| [4.3.2](4.3.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [4.3.0](4.3.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [4.2.2](4.2.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [4.2.1](4.2.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | [Minor](4.2.1.md#change-log) | same |  |
| [4.2.0](4.2.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [4.1.1](4.1.1.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | [Patch](4.1.1.md#change-log) | same |  |
| [4.1.0](4.1.0.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [4.0.0](4.0.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [3.5.5](3.5.5.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [3.5.3](3.5.3.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [3.5.2](3.5.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - | [changed](3.5.2.md#changes-from-the-previous-version) |  |
| [3.4.1](3.4.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - | same |  |
| [3.4.0](3.4.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | - | [changed](3.4.0.md#changes-from-the-previous-version) |  |
| [3.3.1](3.3.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - | [changed](3.3.1.md#changes-from-the-previous-version) |  |
| [3.2.0](3.2.0.md) | 2026-01-27 | yes | yes | - | - | - | yes | yes | yes | - | [changed](3.2.0.md#changes-from-the-previous-version) |  |
| [3.1.0](3.1.0.md) | 2026-02-11 | yes | yes | - | - | - | yes | yes | yes | - | [changed](3.1.0.md#changes-from-the-previous-version) |  |
| [3.0.0](3.0.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | yes | - | - | [changed](3.0.0.md#changes-from-the-previous-version) |  |
| [2.10.1](2.10.1.md) | 2026-01-27 | yes | yes | yes | - | - | yes | yes | - | - | same |  |
| [2.10.0](2.10.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - | - | same |  |
| [2.9.2](2.9.2.md) | 2026-01-27 | yes | yes | yes | - | - | yes | yes | - | - | same |  |
| [2.9.0](2.9.0.md) | 2026-02-11 | yes | yes | yes | - | - | yes | yes | - | - | same |  |
| [2.8.2](2.8.2.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - | - | same |  |
| [2.7.0](2.7.0.md) | 2026-02-11 | yes | - | - | - | - | - | - | - | - | [changed](2.7.0.md#changes-from-the-previous-version) |  |
| [2.6.0](2.6.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - | - | [changed](2.6.0.md#changes-from-the-previous-version) |  |
| [2.5.0](2.5.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - | - | - |  |

"On the server" is the earliest file date the server reports for that version - releases older than 2026 carry the date they were last copied there, not their release date. "Change log" names the release type ServiceNow gave the version on the Store; versions without one have no release notes there. "acc.yml" says whether the shipped configuration, default allow-list or service unit differs from the version before.

Framework releases on the Store with no agent package of the same number (the app shipped no new agent build): [4.3.1](4.3.1.md), [6.6.3](6.6.3.md).
