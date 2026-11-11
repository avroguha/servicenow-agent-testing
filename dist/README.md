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
| Windows x64 | `agent-client-collector-<version>-windows-x64.msi` | Windows Server and Windows client, 64-bit Intel/AMD. There is no Windows ARM64 build |
| macOS Intel | `agent-client-collector-<version>-macos_x64.pkg` | macOS on Intel Macs; published since 2.9.0 |
| macOS ARM64 | `agent-client-collector-<version>-macos_arm64.pkg` | macOS on M-series Macs; published since 3.1.0 |

## Versions

Latest: **[7.1.3](7.1.3.md)**.

| Version | On the server | Ubuntu x86_64 | Debian x86_64 | Debian 8 | Ubuntu ARM64 | RPM x86_64 | Windows x64 | macOS Intel | macOS ARM64 | Report |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|
| [7.1.3](7.1.3.md) | 2026-11-04 | yes | yes | - | yes | yes | yes | yes | yes | [qualification report](../reports/7.1.3/README.md) |
| [7.1.2](7.1.2.md) | 2026-10-23 | yes | yes | - | yes | yes | yes | yes | yes |  |
| [7.1.1](7.1.1.md) | 2026-09-24 | yes | yes | - | yes | yes | yes | yes | yes |  |
| [7.0.4](7.0.4.md) | 2026-09-03 | yes | yes | - | yes | yes | yes | yes | yes |  |
| [7.0.3](7.0.3.md) | 2026-09-02 | yes | yes | - | yes | yes | yes | yes | yes |  |
| [7.0.2](7.0.2.md) | 2026-09-01 | yes | yes | - | yes | yes | yes | yes | yes |  |
| [7.0.1](7.0.1.md) | 2026-08-31 | yes | yes | - | yes | yes | yes | yes | yes |  |
| [6.6.4](6.6.4.md) | 2026-08-06 | yes | yes | - | yes | yes | yes | yes | yes |  |
| [6.6.2](6.6.2.md) | 2026-07-20 | yes | yes | - | yes | yes | yes | yes | yes |  |
| [6.6.1](6.6.1.md) | 2026-06-29 | yes | yes | - | yes | yes | yes | yes | yes |  |
| [6.5.1](6.5.1.md) | 2026-06-18 | yes | yes | - | yes | yes | yes | yes | yes |  |
| [6.5.0](6.5.0.md) | 2026-06-05 | yes | yes | - | - | yes | yes | yes | yes |  |
| [6.4.0](6.4.0.md) | 2026-05-29 | yes | yes | - | - | yes | yes | yes | yes |  |
| [6.3.0](6.3.0.md) | 2026-04-22 | yes | yes | - | - | yes | yes | yes | yes |  |
| [6.1.0](6.1.0.md) | 2026-04-10 | yes | yes | - | - | yes | yes | yes | yes |  |
| [6.0.4](6.0.4.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [6.0.1](6.0.1.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes |  |
| [6.0.0](6.0.0.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | - |  |
| [5.0.4](5.0.4.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [5.0.2](5.0.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [5.0.1](5.0.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [5.0.0](5.0.0.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [4.3.2](4.3.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [4.3.0](4.3.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes |  |
| [4.2.2](4.2.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [4.2.1](4.2.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [4.2.0](4.2.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes |  |
| [4.1.1](4.1.1.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes |  |
| [4.1.0](4.1.0.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [4.0.0](4.0.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes |  |
| [3.5.5](3.5.5.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [3.5.3](3.5.3.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [3.5.2](3.5.2.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [3.4.1](3.4.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [3.4.0](3.4.0.md) | 2026-02-11 | yes | yes | - | - | yes | yes | yes | yes |  |
| [3.3.1](3.3.1.md) | 2026-01-27 | yes | yes | - | - | yes | yes | yes | yes |  |
| [3.2.0](3.2.0.md) | 2026-01-27 | yes | yes | - | - | - | yes | yes | yes |  |
| [3.1.0](3.1.0.md) | 2026-02-11 | yes | yes | - | - | - | yes | yes | yes |  |
| [3.0.0](3.0.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | yes | - |  |
| [2.10.1](2.10.1.md) | 2026-01-27 | yes | yes | yes | - | - | yes | yes | - |  |
| [2.10.0](2.10.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - |  |
| [2.9.2](2.9.2.md) | 2026-01-27 | yes | yes | yes | - | - | yes | yes | - |  |
| [2.9.0](2.9.0.md) | 2026-02-11 | yes | yes | yes | - | - | yes | yes | - |  |
| [2.8.2](2.8.2.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - |  |
| [2.7.0](2.7.0.md) | 2026-02-11 | yes | - | - | - | - | - | - | - |  |
| [2.6.0](2.6.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - |  |
| [2.5.0](2.5.0.md) | 2026-01-27 | yes | yes | yes | - | - | yes | - | - |  |

"On the server" is the earliest file date the server reports for that version - releases older than 2026 carry the date they were last copied there, not their release date.
