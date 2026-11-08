# ACC agent qualification (home lab) - agent 7.1.3

Instance `https://dev463696.service-now.com` · MID Server `dl-mid` · 2026-11-08T07:48:57Z → 2026-11-08T08:01:19Z
Instance build `glide-brazil-08-25-2026__patch1-hotfix1-10-10-2026_10-12-2026_0745.zip` · Agent Client Collector Framework 7.1.3

## Agent verdict: SAFE

0 failure(s) owned by the agent, 0 environment finding(s) (server prerequisites, instance content or MID). Totals: 64 pass, 0 fail, 4 warn, 17 skip, 0 error.

Packages installed in this run: `agent-client-collector-7.1.3-windows-x64.msi` (windows-x86_64, sha256 `113b3355d0a67dab…`).

Embedded runtimes read from the Linux package `agent-client-collector-7.1.3-ubuntu-1804_amd64.deb` before installing: Ruby 3.3.13 (2026-10-23), OpenSSL 3.5.9 (29 Sep 2026), Go 1.26.10. The Windows MSI is not unpacked; every host's values are read from the installed agent and listed below.

### Installed agent per host

| Host | Agent | Go | Ruby | OpenSSL | osquery (from the instance) |
|---|---|---|---|---|---|
| acc-win2025 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03T23:12:20Z | go1.26.10 | ruby 3.3.13 (2026-10-23 revision af48f08f21) [x64-mingw32ucrt] | OpenSSL 3.5.9 29 Sep 2026 | osqueryi.exe version 5.18.1 |

## Targets

| Target | OS | Package | Transport | Install | Environment | Connectivity | Discovery | Checks | Policies | Resources | Cleanup | UI | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| acc-win2025 | Microsoft Windows Server 2025 Standard Evaluation | windows-x86_64 | ssh 192.168.5.56 | PASS 5/6 | PASS 2/2 | WARN 3/4 | PASS 8/8 | PASS 22/28 | WARN 2/13 | PASS 4/4 | WARN 2/3 | WARN 2/3 | WARN |

## Performance: agent resource usage and host impact

Agent = the whole agent process tree (acc plus the checks and osquery it spawns); CPU in % of one core, share = the same CPU as a fraction of all cores on the host. fds are open descriptors (handles on Windows); load1 is the 1-minute load average (processor queue length on Windows).

### acc-win2025 - Microsoft Windows Server 2025 Standard Evaluation · 4 cores · 92 samples every 5s

| Phase | Seconds | Agent CPU avg / peak | Share of host | Agent RSS avg / peak MB | Procs / threads / fds | Disk read / written MB | Host CPU busy avg / peak | Load1 max | Host memory used Δ MB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| connect | 0 | no samples | | | | | | | |
| discovery | 66 | 8.4% / 31.7% | 2.09% | 161 / 264 | 6 / 65 / 1570 | 35.5 / 0.7 | 16.4% / 32.1% | 0 | +82 |
| checks | 296 | 6.4% / 47.8% | 1.59% | 102 / 264 | 6 / 65 / 1510 | 27.5 / 0.2 | 10.4% / 32.8% | 5 | +118 |
| policies | 64 | 4.3% / 43.6% | 1.06% | 78 / 164 | 6 / 49 / 1314 | 3.5 / 0 | 6.1% / 25.7% | 0 | +46 |
| inventory | 0 | no samples | | | | | | | |
| idle | 65 | 0.8% / 1.6% | 0.19% | 70 / 70 | 1 / 16 / 375 | 0 / 0 | 5.5% / 18.8% | 0 | +0 |
| all working phases | 426 | 6.4% / 47.8% | 1.59% | 107 / 264 | 6 / 65 / 1570 | 66.6 / 0.9 | 10.7% / 32.8% | 5 | +82 |
| whole window | 491 | 5.6% / 47.8% | 1.41% | 102 / 264 | 6 / 65 / 1570 | 66.6 / 0.9 | 10% / 32.8% | 5 | +82 |

Host impact: CPU busy +5.2 points working vs idle; the agent tree itself averaged 1.59% of the host's CPU capacity while working.

## Components, modules and packages inside the agent (for the security audit)

Rows marked *package* were read from the downloaded package before installing; the hosts named were read after installation. Plugin content and osquery come from the instance, not from the agent package.

| Component | Version | Kind | Source | Seen on |
|---|---|---|---|---|
| Agent Client Collector | `7.1.3` | agent package | agent-client-collector-7.1.3-ubuntu-1804_amd64.deb | package |
| Agent Client Collector | `acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03T23:12:20Z` | agent | 7.1.3.3 | acc-win2025 |
| Go runtime (acc binary) | `1.26.10` | compiler/runtime | bin/acc | package |
| Go runtime (acc binary) | `go1.26.10` | compiler/runtime | bin/acc | acc-win2025 |
| Ruby (embedded) | `3.3.13 (2026-10-23)` | interpreter | embedded/bin/ruby | package |
| Ruby (embedded) | `ruby 3.3.13 (2026-10-23 revision af48f08f21) [x64-mingw32ucrt]` | interpreter | embedded/bin/ruby | acc-win2025 |
| OpenSSL (embedded) | `3.5.9 (29 Sep 2026)` | crypto library | embedded/lib/libcrypto | package |
| OpenSSL (embedded) | `OpenSSL 3.5.9 29 Sep 2026` | crypto library | embedded/lib | acc-win2025 |
| osquery (plugin asset) | `osqueryi.exe version 5.18.1` | tool (from the instance) | agent cache | acc-win2025 |
| libcrypt | `1.1.0` | shared library | embedded/lib | package |
| libcrypto-3-x64.dll | `3.5.9` | shared library | embedded/lib | acc-win2025 |
| libffi | `8.1.2` | shared library | embedded/lib | package |
| libffi-8.dll | ` ` | shared library | embedded/lib | acc-win2025 |
| libgcc_s_seh-1.dll | ` ` | shared library | embedded/lib | acc-win2025 |
| libruby | `3.3.13` | shared library | embedded/lib | package |
| libssl-3-x64.dll | `3.5.9` | shared library | embedded/lib | acc-win2025 |
| libstdc++-6.dll | ` ` | shared library | embedded/lib | acc-win2025 |
| libwinpthread-1.dll | `1, 0, 0, 0` | shared library | embedded/lib | acc-win2025 |
| libyaml-0 | `2.0.9` | shared library | embedded/lib | package |
| libyaml-0-2.dll | ` ` | shared library | embedded/lib | acc-win2025 |
| libz | `1.2.13` | shared library | embedded/lib | package |
| x64-ucrt-ruby330.dll | `3.3.13p207` | shared library | embedded/lib | acc-win2025 |
| zlib1.dll | `1.2.13` | shared library | embedded/lib | acc-win2025 |
| plugin asset acc-f-commons | `77 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset acc-f-modules | `6 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset acc-visibility-modules | `41 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset acc-visibility-modules-common | `45 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset acctest-scripts | `4 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset osquery | `1 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| gem abbrev | `0.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem abbrev | `0.1.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem addressable | `2.9.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem addressable | `2.9.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem base64 | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem base64 | `0.2.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem benchmark | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem benchmark | `0.3.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem bigdecimal | `3.1.5` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem bigdecimal | `3.1.5` | Ruby gem | embedded ruby | acc-win2025 |
| gem bundler | `2.5.22` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem bundler | `2.5.22` | Ruby gem | embedded ruby | acc-win2025 |
| gem cgi | `0.5.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem cgi | `0.5.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem csv | `3.2.8` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem csv | `3.2.8` | Ruby gem | embedded ruby | acc-win2025 |
| gem date | `3.3.4` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem date | `3.3.4` | Ruby gem | embedded ruby | acc-win2025 |
| gem debug | `1.9.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem debug | `1.9.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem delegate | `0.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem delegate | `0.3.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem did_you_mean | `1.6.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem did_you_mean | `1.6.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem digest | `3.1.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem digest | `3.1.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem drb | `2.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem drb | `2.2.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem english | `0.8.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem english | `0.8.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem erb | `4.0.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem erb | `4.0.3.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem error_highlight | `0.6.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem error_highlight | `0.6.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem etc | `1.4.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem etc | `1.4.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem fcntl | `1.1.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem fcntl | `1.1.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem ffi | `1.17.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem ffi-compiler | `1.4.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem ffi-compiler | `1.4.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem ffi-win32-extensions | `1.1.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem fiddle | `1.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem fiddle | `1.1.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem fileutils | `1.7.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem fileutils | `1.7.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem find | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem find | `0.2.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem forwardable | `1.3.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem forwardable | `1.3.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem getoptlong | `0.2.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem getoptlong | `0.2.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem io-nonblock | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem io-nonblock | `0.3.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem io-wait | `0.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem io-wait | `0.3.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem ipaddr | `1.2.6` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem ipaddr | `1.2.6` | Ruby gem | embedded ruby | acc-win2025 |
| gem irb | `1.13.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem irb | `1.13.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem json | `2.7.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem json | `2.7.2, 2.7.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem llhttp-ffi | `0.5.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem llhttp-ffi | `0.5.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem logger | `1.6.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem logger | `1.6.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem matrix | `0.4.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem matrix | `0.4.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem minitest | `5.20.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem minitest | `5.20.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem mixlib-cli | `1.7.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem mixlib-cli | `1.7.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem mutex_m | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem mutex_m | `0.2.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem net-ftp | `0.3.4` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-ftp | `0.3.4` | Ruby gem | embedded ruby | acc-win2025 |
| gem net-http | `0.4.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-http | `0.4.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem net-imap | `0.5.15` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-imap | `0.5.15` | Ruby gem | embedded ruby | acc-win2025 |
| gem net-pop | `0.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-pop | `0.1.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem net-protocol | `0.2.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-protocol | `0.2.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem net-smtp | `0.5.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-smtp | `0.5.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem nkf | `0.1.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem nkf | `0.1.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem observer | `0.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem observer | `0.1.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem open-uri | `0.4.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem open-uri | `0.4.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem open3 | `0.2.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem open3 | `0.2.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem openssl | `3.2.4` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem openssl | `3.2.4` | Ruby gem | embedded ruby | acc-win2025 |
| gem optparse | `0.4.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem optparse | `0.4.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem ostruct | `0.6.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem ostruct | `0.6.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem pathname | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem pathname | `0.3.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem power_assert | `2.0.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem power_assert | `2.0.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem pp | `0.5.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem pp | `0.5.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem prettyprint | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem prettyprint | `0.2.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem prime | `0.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem prime | `0.1.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem prism | `0.19.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem prism | `0.19.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem pstore | `0.2.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem pstore | `0.2.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem psych | `5.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem psych | `5.1.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem public_suffix | `7.0.5` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem public_suffix | `7.0.5` | Ruby gem | embedded ruby | acc-win2025 |
| gem racc | `1.7.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem racc | `1.7.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem rake | `13.1.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rake | `13.1.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem rb-readline | `0.5.5` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rb-readline | `0.5.5` | Ruby gem | embedded ruby | acc-win2025 |
| gem rbs | `3.5.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rbs | `3.5.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem rdoc | `6.6.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rdoc | `6.6.3.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem readline | `0.0.4` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem readline | `0.0.4` | Ruby gem | embedded ruby | acc-win2025 |
| gem reline | `0.5.10` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem reline | `0.5.10` | Ruby gem | embedded ruby | acc-win2025 |
| gem resolv | `0.3.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem resolv | `0.3.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem rexml | `3.4.4` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rexml | `3.4.4` | Ruby gem | embedded ruby | acc-win2025 |
| gem rinda | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rinda | `0.2.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem rss | `0.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rss | `0.3.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem ruby2_keywords | `0.0.5` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem ruby2_keywords | `0.0.5` | Ruby gem | embedded ruby | acc-win2025 |
| gem securerandom | `0.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem securerandom | `0.3.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem sensu-plugin | `4.0.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem sensu-plugin | `4.0.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem sensu-sn-readfile | `1.1.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem sensu-sn-readfile | `1.1.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem set | `1.1.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem set | `1.1.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem shellwords | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem shellwords | `0.2.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem singleton | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem singleton | `0.2.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem stringio | `3.1.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem stringio | `3.1.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem strscan | `3.0.9` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem strscan | `3.0.9` | Ruby gem | embedded ruby | acc-win2025 |
| gem syntax_suggest | `2.0.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem syntax_suggest | `2.0.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem syslog | `0.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem syslog | `0.1.2` | Ruby gem | embedded ruby | acc-win2025 |
| gem tempfile | `0.2.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem tempfile | `0.2.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem test-unit | `3.6.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem test-unit | `3.6.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem time | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem time | `0.3.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem timeout | `0.4.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem timeout | `0.4.1` | Ruby gem | embedded ruby | acc-win2025 |
| gem tmpdir | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem tmpdir | `0.2.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem tsort | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem tsort | `0.2.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem typeprof | `0.21.9` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem typeprof | `0.21.9` | Ruby gem | embedded ruby | acc-win2025 |
| gem un | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem un | `0.3.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem uri | `0.13.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem uri | `0.13.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem weakref | `0.1.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem weakref | `0.1.3` | Ruby gem | embedded ruby | acc-win2025 |
| gem win32-security | `0.5.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem win32ole | `1.8.10` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem win32ole | `1.8.10` | Ruby gem | embedded ruby | acc-win2025 |
| gem yaml | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem yaml | `0.3.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem zlib | `3.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem zlib | `3.1.2` | Ruby gem | embedded ruby | acc-win2025 |

## All tests

### Pre-flight (8)

| Status | Test | Target | Result |
|---|---|---|---|
| PASS | ACC API key available |  | (from .env) [used] |
| PASS | ACC Visibility content installed (discovery checks) |  | Agent Client Collector for Visibility Content 2.1.1 |
| PASS | Agent Client Collector Framework installed |  | Agent Client Collector Framework 7.1.3 |
| PASS | Custom plugin signing certificate published to the agents |  | signer subject=C=US, O=acctest lab, CN=acctest plugin signing; issuer=C=US, O=acctest lab, CN=acctest lab root CA; notAfter=Nov 7 05:03:51 2029 GMT; trust anchor acctest-lab-root.cer (installed on targets at install time); certificate zip served by the MID (https://192.168.5.230:8800/static/cert/customer/acctest-customer-certs-f8216616b920.zip -> HTTP 200) |
| PASS | Instance reachable with the configured user |  | https://dev463696.service-now.com build brazil-08-25-2026__patch1-hotfix1-10-10-2026_10-12-2026_0745, user admin |
| PASS | MID Server up, validated, ACC listener started |  | dl-mid (192.168.5.230, brazil-08-25-2026) endpoint wss://192.168.5.230:8800/ws/events [existing] |
| PASS | MID serves the current ACC plugin assets |  | 19 plugin assets, newest 2026-11-08 05:04:34, MID started 2026-11-08 05:49:23 |
| PASS | Targets defined |  | acc-win2025 (windows-x86_64, ssh) |

### Packages (4)

| Status | Test | Target | Result |
|---|---|---|---|
| PASS | A package exists for every target OS |  | all target OS keys covered |
| PASS | Agent version and package list read from the instance |  | agent 7.1.3 (app 7.1.3), 8 packages, OS map ['Debian 8', 'Debian 9', 'RHEL/CentOS 7', 'Ubuntu 18.04', 'Ubuntu 22.04 (arm64)', 'Windows', 'macOS', 'macOS_arm64'] |
| PASS | Embedded runtimes read from the package |  | Ruby 3.3.13 (2026-10-23), OpenSSL 3.5.9 (29 Sep 2026); gems: bundler 2.5.22, cgi 0.5.0, json 2.7.1, net-imap 0.5.15, openssl 3.2.4, psych 5.1.2, resolv 0.3.2, rexml 3.4.4, uri 0.13.3 |
| PASS | Packages downloaded into dist/ |  | 5 files in <project>\dist\7.1.3 |

### Install (6)

| Status | Test | Target | Result |
|---|---|---|---|
| PASS | Installed binary reports the expected version | acc-win2025 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03T23:12:20Z (expected 7.1.3) |
| PASS | Target reachable | acc-win2025 | ssh(windows) Administrator@192.168.5.56 - Microsoft Windows Server 2025 Standard Evaluation, AMD64, 4 cpu, 6143 MB |
| PASS | acc service running and enabled | acc-win2025 | service Running, enabled n/a, pid 3932 |
| PASS | acc.yml points at the MID endpoint with the API key | acc-win2025 | backend-url and api-key present |
| PASS | check allow-list enabled in acc.yml | acc-win2025 | allow-list configured |
| SKIP | Agent 7.1.3 installed | acc-win2025 | --skip-install; service Running, version acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03T23:12:20Z |

### Environment (2)

| Status | Test | Target | Result |
|---|---|---|---|
| PASS | Disk, memory and CPU available | acc-win2025 | C: 49665 MB free, 4398 MB RAM free, 4 cpu, firewall profiles on: Domain,Private,Public, Defender real-time True |
| PASS | PowerShell, msiexec and administrator rights | acc-win2025 | PowerShell 5.1.26100.1591, execution policy RemoteSigned, administrator True |

### Connectivity (4)

| Status | Test | Target | Result |
|---|---|---|---|
| WARN | Agent log free of errors after start | acc-win2025 | 1 ERROR line(s) in the last 400 log lines |
| PASS | Agent connected through the configured MID | acc-win2025 | mid dl-mid (expected dl-mid) |
| PASS | Agent registered on the instance and Up | acc-win2025 | Agent_ACCWIN2025 id cdf287544e6e8ff6 status Up since 2026-11-08 05:51:27 |
| PASS | Instance sees the expected agent version | acc-win2025 | 7.1.3 (expected 7.1.3) |

### Discovery (8)

| Status | Test | Target | Result |
|---|---|---|---|
| PASS | CI discovery source set by the agent | acc-win2025 | discovery_source 'ACC-Visibility', last_discovered 2026-11-08 07:50:53 |
| PASS | Discovery (collect host data) requested through the ACC API | acc-win2025 | accepted |
| PASS | Discovery populated related CI data | acc-win2025 | cmdb_ci_network_adapter=1, cmdb_ci_ip_address=2, cmdb_ci_file_system=3, cmdb_sam_sw_install=-1, cmdb_software_instance=0, cmdb_running_process=103, cmdb_rel_ci=11 |
| PASS | Host CI IP matches the server | acc-win2025 | CI 192.168.5.56 vs host 192.168.5.56 |
| PASS | Host CI carries OS and version | acc-win2025 | os 'Windows 2025 Standard Evaluation' version '10.0.26100' serial '94888934-BD2E-4C29-ACED-2CBC94F018EB' |
| PASS | Host CI class is cmdb_ci_win_server | acc-win2025 | cmdb_ci_win_server (accwin2025) |
| PASS | Host CI name matches the server's host name | acc-win2025 | CI 'accwin2025' vs host 'ACCWIN2025' |
| PASS | Host data collected and a host CI bound to the agent | acc-win2025 | host_data 'Collected' at 2026-11-08 07:50:54, CI accwin2025 |

### Checks (28)

| Status | Test | Target | Result |
|---|---|---|---|
| PASS | Agent self-test (acc self-test) | acc-win2025 | suite default: 9 passed, 0 failed, 1 skipped |
| PASS | Check 'Enhanced Discovery' [oob, Enhanced Discovery] | acc-win2025 | exit 0 (OK), 13678 chars of output |
| PASS | Check 'File Based Discovery - File Management' [oob, ExtendedDiscovery] | acc-win2025 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - Java GLAS' [oob, ExtendedDiscovery] | acc-win2025 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - License Key' [oob, ExtendedDiscovery] | acc-win2025 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SAM' [oob, ExtendedDiscovery] | acc-win2025 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SWID' [oob, ExtendedDiscovery] | acc-win2025 | exit 0 (OK), 107 chars of output |
| PASS | Check 'Installed Software' [oob, ExtendedDiscovery] | acc-win2025 | exit 0 (OK), 2984 chars of output |
| PASS | Check 'Oracle GLAS HW data collection' [oob, ExtendedDiscovery] | acc-win2025 | exit 0 (OK), 23456 chars of output |
| PASS | Check 'Oracle GLAS Java Process Discovery' [oob, Oracle GLAS Java Process Discovery] | acc-win2025 | exit 0 (OK), 29 chars of output |
| PASS | Check 'Software installations and usage metrics' [oob, ExtendedDiscovery] | acc-win2025 | exit 0 (OK), 3577 chars of output |
| PASS | Check 'TLS SSL Certificate Capture' [oob, TLS SSL Certificate Capture] | acc-win2025 | exit 0 (OK), 2 chars of output |
| PASS | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | acc-win2025 | exit 0 (OK), 59 chars of output |
| PASS | Check 'VISC Get URL Metric' [oob, VISC URL Metric] | acc-win2025 | exit 0 (OK), 126 chars of output |
| PASS | Check 'VISC Get application metric' [oob, VISC Application metric] | acc-win2025 | exit 0 (OK), 145 chars of output |
| PASS | Check 'VISC Get browser extension device init' [oob, VISC Browser extension init] | acc-win2025 | exit 0 (OK), 52 chars of output |
| PASS | Check 'VISC Get browser extension init' [oob, VISC Browser extension init] | acc-win2025 | exit 0 (OK), 112 chars of output |
| PASS | Check 'VISC Get browser extension' [oob, VISC Browser extension] | acc-win2025 | exit 0 (OK), 2 chars of output |
| PASS | Check 'VISC Get targeted URL metric' [oob, VISC Targeted URL Metric] | acc-win2025 | exit 0 (OK), 116 chars of output |
| PASS | Check 'acctest-users-windows' [custom, ] | acc-win2025 | exit 0 (OK), 1938 chars of output; script output verified: 10 users, 2 admin(s): Administrator, lab_normal |
| PASS | Check 'check-discovery-basic' [oob, Discovery] | acc-win2025 | exit 0 (OK), 8645 chars of output |
| PASS | Check definitions read from the instance | acc-win2025 | 41 active: 38 out-of-box, 0 customized, 3 custom |
| SKIP | Agent-internal check types (upgrade, restart, cancel, ...) | acc-win2025 | 14 framework-internal definitions are exercised by their own actions, not ad hoc: Agent Upgrade - DEB, Agent Upgrade - MAC, Agent Upgrade - MSI, Agent Upgrade - RPM, Cancel, Regenerate Agent ID, Restart agent, System Command, TestCheck - OSQuery [Linux], TestCheck - OSQuery [Mac], TestCheck - OSQuery [Windows], check-read-log, config file reader, self-test |
| SKIP | Check 'FBD SAM Process Scan' [oob] | acc-win2025 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'File Based Discovery Background' [oob] | acc-win2025 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM Background Data collection ( Non OsqueryD )' [oob] | acc-win2025 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM background log check' [oob] | acc-win2025 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'Software Discovery via Running Process' [oob] | acc-win2025 | background check (ad-hoc test not supported by the platform) |

### Policies (13)

| Status | Test | Target | Result |
|---|---|---|---|
| WARN | Policy 'Software Installed Policy' [oob] applies to this agent | acc-win2025 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| PASS | Policies read from the instance | acc-win2025 | 11 active published policies (3 custom/customized) |
| PASS | Policy 'Software Installed Policy' check 'Installed Software' | acc-win2025 | exit 0 (OK), 2984 chars of output |
| SKIP | Policy 'Enhanced Discovery Policy' [oob] | acc-win2025 | policy selects CIs by script/group - not evaluated |
| SKIP | Policy 'SAM background policy' [oob] | acc-win2025 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'SAM discovery ' [oob] | acc-win2025 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'VISC Browser Extension Discovery' [oob] | acc-win2025 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac^ORosLIKElinux' |
| SKIP | Policy 'VISC Get application metric' [oob] | acc-win2025 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension device init' [oob] | acc-win2025 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension init' [oob] | acc-win2025 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'acctest-custom-policy' [custom] | acc-win2025 | CI is not in cmdb_ci_linux_server with filter 'nameSTARTSWITHacc-' |
| SKIP | Policy 'acctest-users-linux-policy' [custom] | acc-win2025 | CI is not in cmdb_ci_linux_server with filter 'nameSTARTSWITHacc-' |
| SKIP | Policy 'acctest-users-windows-policy' [custom] | acc-win2025 | CI is not in cmdb_ci_win_server with filter 'nameSTARTSWITHacc-' |

### Resources (4)

| Status | Test | Target | Result |
|---|---|---|---|
| PASS | Agent CPU within the configured threshold | acc-win2025 | avg 1% / peak 2% of one core over 12 samples (60s), limit 5% (+5 tolerance); RSS 69 MB, 16 threads, up to 1 processes |
| PASS | Agent resource usage and host impact while working | acc-win2025 | while working (discovery + checks + policies, 426s): agent avg 6.4% / peak 47.8% of one core = 1.59% of the host's 4 cores; RSS avg 107 / peak 264 MB; up to 6 processes, 65 threads, 1570 fds; disk read 66.6 MB / written 0.9 MB; host CPU busy avg 10.7% (peak 32.8%), load1 max 5, host memory used +82 MB; idle (65s): agent avg 0.8% of one core, RSS 70 MB; host CPU busy avg 5.5%; host impact: CPU busy +5.2 points working vs idle |
| PASS | CPU protection configured in acc.yml | acc-win2025 | cpu_percentage_limit 5%, repeated_high_cpu_num 3, monitor_interval 60s, max-running-checks 10 |
| PASS | Component inventory read from the installed agent | acc-win2025 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03T23:12:20Z; ruby 3.3.13 (2026-10-23 revision af48f08f21) [x64-mingw32ucrt]; OpenSSL OpenSSL 3.5.9 29 Sep 2026; osquery osqueryi.exe version 5.18.1; 96 gems, 6 plugin assets - full list in the Components section and components.csv |

### Cleanup (3)

| Status | Test | Target | Result |
|---|---|---|---|
| WARN | No check processes, zombies or temp files left after discovery | acc-win2025 | child processes 0, zombies 0, osquery processes 0, temp files 2: ['C:\\Windows\\Temp\\acctest-lab-root.cer', 'C:\\Windows\\Temp\\acctest-signing.cer'] |
| PASS | Disk footprint of cache and logs | acc-win2025 | cache 0 MB, logs 0 MB |
| PASS | No panics or crashes in the agent log | acc-win2025 | 0 panic/fatal lines, 30 error lines, service Running, restarts seen n/a, open files n/a |

### UI (5)

| Status | Test | Target | Result |
|---|---|---|---|
| WARN | Discovered host CI renders in the UI | acc-win2025 | could not confirm the CI name on the form (see screenshot) |
| PASS | Agent Downloads page lists this version |  | version 7.1.3 found in the page's download links |
| PASS | Headless browser login to the instance |  | logged in |
| PASS | Agent record renders in the UI | acc-win2025 | agent form shows the agent |
| PASS | Test check results visible in the UI | acc-win2025 | list screenshot taken |

Generated by acctest. Secrets are redacted; host names and addresses are those of the environment the run was made in. The HTML report beside this file carries the evidence (command output, record values, log lines) for every row.
