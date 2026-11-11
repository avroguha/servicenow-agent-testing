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


## Versions

Latest: **[7.1.3](7.1.3.md)**.

| Version | On the server | Ubuntu x86_64 | Debian x86_64 | Debian 8 | Ubuntu ARM64 | RPM x86_64 | Windows x64 | macOS Intel | macOS ARM64 | Change log | Report |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|---|
| [7.1.3](7.1.3.md) | 2026-11-04 | yes | yes | - | yes | yes | yes | yes | yes | [Patch](7.1.3.md#change-log) | [qualification report](../reports/7.1.3/README.md) |
| [7.1.2](7.1.2.md) | 2026-10-23 | yes | yes | - | yes | yes | yes | yes | yes | - |  |
| [7.1.1](7.1.1.md) | 2026-09-24 | yes | yes | - | yes | yes | yes | yes | yes | [Minor](7.1.1.md#change-log) |  |
| [7.0.4](7.0.4.md) | 2026-09-03 | yes | yes | - | yes | yes | yes | yes | yes | [Major](7.0.4.md#change-log) |  |
| [7.0.3](7.0.3.md) | 2026-09-02 | yes | yes | - | yes | yes | yes | yes | yes | - |  |
| [7.0.2](7.0.2.md) | 2026-09-01 | yes | yes | - | yes | yes | yes | yes | yes | - |  |
| [7.0.1](7.0.1.md) | 2026-08-31 | yes | yes | - | yes | yes | yes | yes | yes | - |  |
| [6.6.4](6.6.4.md) | 2026-08-06 | yes | yes | - | yes | yes | yes | yes | yes | [Patch](6.6.4.md#change-log) |  |
| [6.6.2](6.6.2.md) | 2026-07-20 | yes | yes | - | yes | yes | yes | yes | yes | - |  |
| [6.6.1](6.6.1.md) | 2026-06-29 | yes | yes | - | yes | yes | yes | yes | yes | [Minor](6.6.1.md#change-log) |  |
| [6.5.1](6.5.1.md) | 2026-06-18 | yes | yes | - | yes | yes | yes | yes | yes | [Patch](6.5.1.md#change-log) |  |
| [6.5.0](6.5.0.md) | 2026-06-05 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [6.4.0](6.4.0.md) | 2026-05-29 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [6.3.0](6.3.0.md) | 2026-04-22 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [6.1.0](6.1.0.md) | 2026-04-10 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [6.0.4](6.0.4.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | [Patch](6.0.4.md#change-log) |  |
| [6.0.1](6.0.1.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [6.0.0](6.0.0.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | - | - |  |
| [5.0.4](5.0.4.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [5.0.2](5.0.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | [Patch](5.0.2.md#change-log) |  |
| [5.0.1](5.0.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | [Patch](5.0.1.md#change-log) |  |
| [5.0.0](5.0.0.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | [Minor](5.0.0.md#change-log) |  |
| [4.3.2](4.3.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [4.3.0](4.3.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [4.2.2](4.2.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [4.2.1](4.2.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | [Minor](4.2.1.md#change-log) |  |
| [4.2.0](4.2.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [4.1.1](4.1.1.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | [Patch](4.1.1.md#change-log) |  |
| [4.1.0](4.1.0.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [4.0.0](4.0.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [3.5.5](3.5.5.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [3.5.3](3.5.3.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [3.5.2](3.5.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [3.4.1](3.4.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [3.4.0](3.4.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [3.3.1](3.3.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes | - |  |
| [3.2.0](3.2.0.md) | 2026-01-27 | yes | yes | - | - | - | yes | yes | yes | - |  |
| [3.1.0](3.1.0.md) | 2026-02-11 | yes | yes | - | - | - | yes | yes | yes | - |  |
| [3.0.0](3.0.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | yes | - | - |  |
| [2.10.1](2.10.1.md) | 2026-01-27 | yes | yes | yes | - | - | yes | yes | - | - |  |
| [2.10.0](2.10.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - | - |  |
| [2.9.2](2.9.2.md) | 2026-01-27 | yes | yes | yes | - | - | yes | yes | - | - |  |
| [2.9.0](2.9.0.md) | 2026-02-11 | yes | yes | yes | - | - | yes | yes | - | - |  |
| [2.8.2](2.8.2.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - | - |  |
| [2.7.0](2.7.0.md) | 2026-02-11 | yes | - | - | - | - | - | - | - | - |  |
| [2.6.0](2.6.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - | - |  |
| [2.5.0](2.5.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - | - |  |

"On the server" is the earliest file date the server reports for that version - releases older than 2026 carry the date they were last copied there, not their release date. "Change log" names the release type ServiceNow gave the version on the Store; versions without one have no release notes there.

Framework releases on the Store with no agent package of the same number (the app shipped no new agent build): [4.3.1](4.3.1.md), [6.6.3](6.6.3.md).
