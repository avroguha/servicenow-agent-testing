# ACC agent qualification (home lab) - agent 7.1.3

Instance `https://dev463696.service-now.com` · MID Server `dl-mid` · 2026-11-08T05:18:00Z → 2026-11-08T06:39:24Z
Instance build `glide-brazil-08-25-2026__patch1-hotfix1-10-10-2026_10-12-2026_0745.zip` · Agent Client Collector Framework 7.1.3

## Agent verdict: SAFE

0 failure(s) owned by the agent, 25 environment finding(s) (server prerequisites, instance content or MID). Totals: 319 pass, 25 fail, 90 warn, 100 skip, 0 error.

Packages installed in this run: `agent-client-collector-7.1.3-ubuntu-1804_amd64.deb` (linux-x86_64-deb, sha256 `acffe08d92af2143…`); `agent-client-collector-7.1.3-x86_64.rpm` (linux-x86_64-rpm, sha256 `9d189e2169e443a5…`); `agent-client-collector-7.1.3-windows-x64.msi` (windows-x86_64, sha256 `113b3355d0a67dab…`).

Embedded runtimes read from the Linux package `agent-client-collector-7.1.3-ubuntu-1804_amd64.deb` before installing: Ruby 3.3.13 (2026-10-23), OpenSSL 3.5.9 (29 Sep 2026), Go 1.26.10. The Windows MSI is not unpacked; every host's values are read from the installed agent and listed below.

### Installed agent per host

| Host | Agent | Go | Ruby | OpenSSL | osquery (from the instance) |
|---|---|---|---|---|---|
| acc-debian12 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z | go1.26.10 | ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux] | OpenSSL 3.5.9 29 Sep 2026 | osqueryi version 5.18.1 |
| acc-rocky10 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z | go1.26.10 | ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux] | OpenSSL 3.5.9 29 Sep 2026 | osqueryi version 5.18.1 |
| acc-rocky9 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z | go1.26.10 | ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux] | OpenSSL 3.5.9 29 Sep 2026 | osqueryi version 5.18.1 |
| acc-suse156 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z | go1.26.10 | ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux] | OpenSSL 3.5.9 29 Sep 2026 | osqueryi version 5.18.1 |
| acc-ubuntu2204 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z | go1.26.10 | ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux] | OpenSSL 3.5.9 29 Sep 2026 | osqueryi version 5.18.1 |
| acc-ubuntu2404 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z | go1.26.10 | ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux] | OpenSSL 3.5.9 29 Sep 2026 | osqueryi version 5.18.1 |
| acc-win2025 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03T23:12:20Z | go1.26.10 | ruby 3.3.13 (2026-10-23 revision af48f08f21) [x64-mingw32ucrt] | OpenSSL 3.5.9 29 Sep 2026 | osqueryi.exe version 5.18.1 |

## Targets

| Target | OS | Package | Transport | Install | Environment | Connectivity | Discovery | Checks | Policies | Resources | Cleanup | UI | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| acc-ubuntu2404 | Ubuntu 24.04 LTS | linux-x86_64-deb | pct 192.168.5.94 | PASS 6/6 | WARN 2/3 | WARN 3/4 | PASS 8/8 | FAIL 13/29 | FAIL 3/15 | FAIL 3/4 | WARN 2/3 | PASS 3/3 | FAIL |
| acc-ubuntu2204 | Ubuntu 22.04 LTS | linux-x86_64-deb | pct 192.168.5.32 | PASS 6/6 | WARN 2/3 | WARN 3/4 | PASS 8/8 | FAIL 13/29 | FAIL 3/15 | FAIL 3/4 | WARN 2/3 | PASS 3/3 | FAIL |
| acc-debian12 | Debian GNU/Linux 12 (bookworm) | linux-x86_64-deb | pct 192.168.5.95 | PASS 6/6 | WARN 2/3 | WARN 3/4 | PASS 8/8 | FAIL 13/29 | FAIL 3/15 | FAIL 3/4 | WARN 2/3 | PASS 3/3 | FAIL |
| acc-rocky9 | Rocky Linux 9.4 (Blue Onyx) | linux-x86_64-rpm | pct 192.168.5.231 | PASS 6/6 | WARN 1/3 | WARN 3/4 | FAIL 7/8 | FAIL 13/29 | FAIL 3/15 | FAIL 3/4 | WARN 2/3 | PASS 3/3 | FAIL |
| acc-rocky10 | Rocky Linux 10.0 (Red Quartz) | linux-x86_64-rpm | pct 192.168.5.182 | PASS 6/6 | WARN 1/3 | WARN 3/4 | PASS 8/8 | FAIL 13/29 | FAIL 3/15 | FAIL 3/4 | WARN 2/3 | PASS 3/3 | FAIL |
| acc-suse156 | openSUSE Leap 15.6 | linux-x86_64-rpm | pct 192.168.5.98 | PASS 6/6 | WARN 2/3 | WARN 3/4 | PASS 8/8 | FAIL 13/29 | FAIL 3/15 | FAIL 3/4 | WARN 2/3 | PASS 3/3 | FAIL |
| acc-win2025 | Microsoft Windows Server 2025 Standard Evaluation | windows-x86_64 | ssh 192.168.5.56 | PASS 6/6 | PASS 2/2 | WARN 3/4 | PASS 8/8 | PASS 22/28 | WARN 2/13 | PASS 3/3 | WARN 2/3 | PASS 3/3 | WARN |

## Environment findings (not the agent's fault)

| Cause | Target | Test | What |
|---|---|---|---|
| Instance content | acc-debian12 | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | exit 127: the check could not execute properly - /usr/bin/env: 'ruby\r': No such file or directory /usr/bin/env: use -[v]S to pass options in shebang lines [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| Instance content | acc-debian12 | Check 'acctest-custom-os-version' [custom, ] | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-debian12 | Plugin scripts delivered by the MID are executable on this OS | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb, acc-visibility-modules-common/bin/file_output_split.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this d… |
| Instance content | acc-debian12 | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-rocky10 | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | exit 127: the check could not execute properly - /usr/bin/env: ‘ruby\r’: No such file or directory /usr/bin/env: use -[v]S to pass options in shebang lines [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| Instance content | acc-rocky10 | Check 'acctest-custom-os-version' [custom, ] | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-rocky10 | Plugin scripts delivered by the MID are executable on this OS | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/file_output_split.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this d… |
| Instance content | acc-rocky10 | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-rocky9 | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | exit 127: the check could not execute properly - /usr/bin/env: ‘ruby\r’: No such file or directory [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| Instance content | acc-rocky9 | Check 'acctest-custom-os-version' [custom, ] | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-rocky9 | Plugin scripts delivered by the MID are executable on this OS | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/file_output_split.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb, acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this d… |
| Instance content | acc-rocky9 | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-suse156 | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | exit 127: the check could not execute properly - /usr/bin/env: ‘ruby\r’: No such file or directory [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| Instance content | acc-suse156 | Check 'acctest-custom-os-version' [custom, ] | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-suse156 | Plugin scripts delivered by the MID are executable on this OS | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/file_output_split.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this d… |
| Instance content | acc-suse156 | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-ubuntu2204 | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | exit 127: the check could not execute properly - /usr/bin/env: 'ruby\r': No such file or directory [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| Instance content | acc-ubuntu2204 | Check 'acctest-custom-os-version' [custom, ] | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-ubuntu2204 | Plugin scripts delivered by the MID are executable on this OS | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb, acc-visibility-modules-common/bin/file_output_split.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this d… |
| Instance content | acc-ubuntu2204 | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-ubuntu2404 | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | exit 127: the check could not execute properly - /usr/bin/env: 'ruby\r': No such file or directory /usr/bin/env: use -[v]S to pass options in shebang lines [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| Instance content | acc-ubuntu2404 | Check 'acctest-custom-os-version' [custom, ] | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance content | acc-ubuntu2404 | Plugin scripts delivered by the MID are executable on this OS | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/file_output_split.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this d… |
| Instance content | acc-ubuntu2404 | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| Instance / MID | acc-rocky9 | Host data collected and a host CI bound to the agent | host_data 'Collection failed' after 900s, cmdb_ci set; 2026-11-08 05:48:47 instance: In AgentNowHandler.createAccErrorsFromCheckResults: missing data for checkResult on ecc sysid=9905faaf83145f9055981896feaad38c with index=0 for agent id = f6d0e934517624fd and check definition id=undefined and check instance id=undefined |

## Components, modules and packages inside the agent (for the security audit)

Rows marked *package* were read from the downloaded package before installing; the hosts named were read after installation. Plugin content and osquery come from the instance, not from the agent package.

| Component | Version | Kind | Source | Seen on |
|---|---|---|---|---|
| Agent Client Collector | `7.1.3` | agent package | agent-client-collector-7.1.3-ubuntu-1804_amd64.deb | package |
| Agent Client Collector | `acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03T23:12:20Z` | agent | 7.1.3.3 | acc-win2025 |
| Agent Client Collector | `acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z` | agent | 7.1.3-3 | acc-debian12, acc-ubuntu2204, acc-ubuntu2404 |
| Agent Client Collector | `acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z` | agent | 7.1.3-1 | acc-rocky10, acc-rocky9, acc-suse156 |
| Go runtime (acc binary) | `1.26.10` | compiler/runtime | bin/acc | package |
| Go runtime (acc binary) | `go1.26.10` | compiler/runtime | bin/acc | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| Ruby (embedded) | `3.3.13 (2026-10-23)` | interpreter | embedded/bin/ruby | package |
| Ruby (embedded) | `ruby 3.3.13 (2026-10-23 revision af48f08f21) [x64-mingw32ucrt]` | interpreter | embedded/bin/ruby | acc-win2025 |
| Ruby (embedded) | `ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux]` | interpreter | embedded/bin/ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| OpenSSL (embedded) | `3.5.9 (29 Sep 2026)` | crypto library | embedded/lib/libcrypto | package |
| OpenSSL (embedded) | `OpenSSL 3.5.9 29 Sep 2026` | crypto library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| osquery (plugin asset) | `osqueryi version 5.18.1` | tool (from the instance) | agent cache | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| osquery (plugin asset) | `osqueryi.exe version 5.18.1` | tool (from the instance) | agent cache | acc-win2025 |
| libcrypt | `1.1.0` | shared library | embedded/lib | package |
| libcrypt.so.1 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libcrypt.so.1.1.0 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libcrypto-3-x64.dll | `3.5.9` | shared library | embedded/lib | acc-win2025 |
| libcrypto.so.3 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libffi | `8.1.2` | shared library | embedded/lib | package |
| libffi-8.dll | ` ` | shared library | embedded/lib | acc-win2025 |
| libffi.so.8 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libffi.so.8.1.2 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libgcc_s_seh-1.dll | ` ` | shared library | embedded/lib | acc-win2025 |
| libowcrypt.so.1 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libruby | `3.3.13` | shared library | embedded/lib | package |
| libruby.so.3.3 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libruby.so.3.3.13 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libssl-3-x64.dll | `3.5.9` | shared library | embedded/lib | acc-win2025 |
| libssl.so.3 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libstdc++-6.dll | ` ` | shared library | embedded/lib | acc-win2025 |
| libwinpthread-1.dll | `1, 0, 0, 0` | shared library | embedded/lib | acc-win2025 |
| libyaml-0 | `2.0.9` | shared library | embedded/lib | package |
| libyaml-0-2.dll | ` ` | shared library | embedded/lib | acc-win2025 |
| libyaml-0.so.2 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libyaml-0.so.2.0.9 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libz | `1.2.13` | shared library | embedded/lib | package |
| libz.so.1 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| libz.so.1.2.13 | ` ` | shared library | embedded/lib | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| x64-ucrt-ruby330.dll | `3.3.13p207` | shared library | embedded/lib | acc-win2025 |
| zlib1.dll | `1.2.13` | shared library | embedded/lib | acc-win2025 |
| plugin asset acc-f-commons | `77 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset acc-f-commons | `77 files, 608 KB` | plugin content (from the instance) | agent cache | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| plugin asset acc-f-modules | `6 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset acc-f-modules | `7 files, 76 KB` | plugin content (from the instance) | agent cache | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| plugin asset acc-visibility-modules | `21 files, 184 KB` | plugin content (from the instance) | agent cache | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| plugin asset acc-visibility-modules | `41 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset acc-visibility-modules-common | `45 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset acc-visibility-modules-common | `45 files, 408 KB` | plugin content (from the instance) | agent cache | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| plugin asset acctest-scripts | `4 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset acctest-scripts | `4 files, 28 KB` | plugin content (from the instance) | agent cache | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| plugin asset osquery | `1 files` | plugin content (from the instance) | agent cache | acc-win2025 |
| plugin asset osquery | `1 files, 85152 KB` | plugin content (from the instance) | agent cache | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| gem abbrev | `0.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem abbrev | `0.1.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem addressable | `2.9.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem addressable | `2.9.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem base64 | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem base64 | `0.2.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem benchmark | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem benchmark | `0.3.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem bigdecimal | `3.1.5` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem bigdecimal | `3.1.5` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem bundler | `2.5.22` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem bundler | `2.5.22` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem cgi | `0.5.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem cgi | `0.5.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem csv | `3.2.8` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem csv | `3.2.8` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem date | `3.3.4` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem date | `3.3.4` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem debug | `1.9.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem debug | `1.9.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem delegate | `0.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem delegate | `0.3.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem did_you_mean | `1.6.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem did_you_mean | `1.6.3` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem digest | `3.1.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem digest | `3.1.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem drb | `2.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem drb | `2.2.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem english | `0.8.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem english | `0.8.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem erb | `4.0.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem erb | `4.0.3.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem error_highlight | `0.6.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem error_highlight | `0.6.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem etc | `1.4.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem etc | `1.4.3` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem fcntl | `1.1.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem fcntl | `1.1.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem ffi | `1.17.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem ffi | `1.17.0 x86_64-linux-gnu` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404 |
| gem ffi-compiler | `1.4.2` | Ruby gem | embedded ruby | acc-rocky10, acc-rocky9, acc-suse156 |
| gem ffi-compiler | `1.4.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem ffi-compiler | `1.4.3` | Ruby gem | embedded ruby | acc-debian12, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem ffi-win32-extensions | `1.1.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem fiddle | `1.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem fiddle | `1.1.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem fileutils | `1.7.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem fileutils | `1.7.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem find | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem find | `0.2.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem forwardable | `1.3.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem forwardable | `1.3.3` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem getoptlong | `0.2.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem getoptlong | `0.2.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem io-nonblock | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem io-nonblock | `0.3.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem io-wait | `0.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem io-wait | `0.3.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem ipaddr | `1.2.6` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem ipaddr | `1.2.6` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem irb | `1.13.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem irb | `1.13.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem json | `2.7.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem json | `2.7.2, 2.7.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem llhttp-ffi | `0.5.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem llhttp-ffi | `0.5.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem logger | `1.6.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem logger | `1.6.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem matrix | `0.4.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem matrix | `0.4.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem minitest | `5.20.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem minitest | `5.20.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem mixlib-cli | `1.7.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem mixlib-cli | `1.7.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem mutex_m | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem mutex_m | `0.2.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem net-ftp | `0.3.4` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-ftp | `0.3.4` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem net-http | `0.4.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-http | `0.4.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem net-imap | `0.5.15` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-imap | `0.5.15` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem net-pop | `0.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-pop | `0.1.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem net-protocol | `0.2.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-protocol | `0.2.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem net-smtp | `0.5.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem net-smtp | `0.5.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem nkf | `0.1.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem nkf | `0.1.3` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem observer | `0.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem observer | `0.1.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem open-uri | `0.4.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem open-uri | `0.4.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem open3 | `0.2.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem open3 | `0.2.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem openssl | `3.2.4` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem openssl | `3.2.4` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem optparse | `0.4.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem optparse | `0.4.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem ostruct | `0.6.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem ostruct | `0.6.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem pathname | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem pathname | `0.3.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem power_assert | `2.0.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem power_assert | `2.0.3` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem pp | `0.5.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem pp | `0.5.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem prettyprint | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem prettyprint | `0.2.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem prime | `0.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem prime | `0.1.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem prism | `0.19.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem prism | `0.19.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem pstore | `0.2.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem pstore | `0.2.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem psych | `5.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem psych | `5.1.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem public_suffix | `7.0.5` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem public_suffix | `7.0.5` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem racc | `1.7.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem racc | `1.7.3` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem rake | `13.1.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rake | `13.1.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem rb-readline | `0.5.5` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rb-readline | `0.5.5` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem rbs | `3.5.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rbs | `3.5.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem rdoc | `6.6.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rdoc | `6.6.3.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem readline | `0.0.4` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem readline | `0.0.4` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem reline | `0.5.10` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem reline | `0.5.10` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem resolv | `0.3.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem resolv | `0.3.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem rexml | `3.4.4` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rexml | `3.4.4` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem rinda | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rinda | `0.2.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem rss | `0.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem rss | `0.3.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem ruby2_keywords | `0.0.5` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem ruby2_keywords | `0.0.5` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem securerandom | `0.3.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem securerandom | `0.3.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem sensu-plugin | `4.0.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem sensu-plugin | `4.0.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem sensu-sn-readfile | `1.1.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem sensu-sn-readfile | `1.1.3` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem set | `1.1.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem set | `1.1.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem shellwords | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem shellwords | `0.2.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem singleton | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem singleton | `0.2.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem stringio | `3.1.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem stringio | `3.1.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem strscan | `3.0.9` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem strscan | `3.0.9` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem syntax_suggest | `2.0.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem syntax_suggest | `2.0.3` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem syslog | `0.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem syslog | `0.1.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem tempfile | `0.2.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem tempfile | `0.2.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem test-unit | `3.6.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem test-unit | `3.6.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem time | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem time | `0.3.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem timeout | `0.4.1` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem timeout | `0.4.1` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem tmpdir | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem tmpdir | `0.2.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem tsort | `0.2.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem tsort | `0.2.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem typeprof | `0.21.9` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem typeprof | `0.21.9` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem un | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem un | `0.3.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem uri | `0.13.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem uri | `0.13.3` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem weakref | `0.1.3` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem weakref | `0.1.3` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem win32-security | `0.5.0` | Ruby gem | embedded ruby | acc-win2025 |
| gem win32ole | `1.8.10` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem win32ole | `1.8.10` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem yaml | `0.3.0` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem yaml | `0.3.0` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |
| gem zlib | `3.1.2` | Ruby gem | embedded/lib/ruby/gems/3.3.0 | package |
| gem zlib | `3.1.2` | Ruby gem | embedded ruby | acc-debian12, acc-rocky10, acc-rocky9, acc-suse156, acc-ubuntu2204, acc-ubuntu2404, acc-win2025 |

## All tests

### Pre-flight (8)

| Status | Test | Target | Result |
|---|---|---|---|
| WARN | Custom plugin signing certificate published to the agents |  | signer subject=C=US, O=acctest lab, CN=acctest plugin signing; issuer=C=US, O=acctest lab, CN=acctest lab root CA; notAfter=Nov 7 05:03:51 2029 GMT; trust anchor acctest-lab-root.cer (installed on targets at install time); certificate zip NOT served by the MID - custom plugins will be refused (https://192.168.5.230:8800/static/cert/customer/acctest-customer-certs-f8216616b920.zip -> HTTPSConnectionPool(host='192.168.5.230', port=8800): Max retries exceeded with url: /static/cert/customer/acctest-customer-certs-f8216616b920.zip (Caused by NewConnectionError("HTTPSConnection(host='192.168.5.230', port=8800): Failed to establish a new connection: [WinError 10061] No connection could be made be… |
| PASS | ACC API key available |  | (from .env) [used] |
| PASS | ACC Visibility content installed (discovery checks) |  | Agent Client Collector for Visibility Content 2.1.1 |
| PASS | Agent Client Collector Framework installed |  | Agent Client Collector Framework 7.1.3 |
| PASS | Instance reachable with the configured user |  | https://dev463696.service-now.com build brazil-08-25-2026__patch1-hotfix1-10-10-2026_10-12-2026_0745, user admin |
| PASS | MID Server up, validated, ACC listener started |  | dl-mid (192.168.5.230, brazil-08-25-2026) endpoint wss://192.168.5.230:8800/ws/events [existing] |
| PASS | MID serves the current ACC plugin assets |  | assets changed 2026-11-08 05:04:34 after the MID started - MID restarted ({'restarted': True, 'started': '2026-11-08 05:18:44'}); listener ready False |
| PASS | Targets defined |  | acc-ubuntu2404 (linux-x86_64-deb, pct), acc-ubuntu2204 (linux-x86_64-deb, pct), acc-debian12 (linux-x86_64-deb, pct), acc-rocky9 (linux-x86_64-rpm, pct), acc-rocky10 (linux-x86_64-rpm, pct), acc-suse156 (linux-x86_64-rpm, pct), acc-win2025 (windows-x86_64, ssh) |

### Packages (4)

| Status | Test | Target | Result |
|---|---|---|---|
| PASS | A package exists for every target OS |  | all target OS keys covered |
| PASS | Agent version and package list read from the instance |  | agent 7.1.3 (app 7.1.3), 8 packages, OS map ['Debian 8', 'Debian 9', 'RHEL/CentOS 7', 'Ubuntu 18.04', 'Ubuntu 22.04 (arm64)', 'Windows', 'macOS', 'macOS_arm64'] |
| PASS | Embedded runtimes read from the package |  | Ruby 3.3.13 (2026-10-23), OpenSSL 3.5.9 (29 Sep 2026); gems: bundler 2.5.22, cgi 0.5.0, json 2.7.1, net-imap 0.5.15, openssl 3.2.4, psych 5.1.2, resolv 0.3.2, rexml 3.4.4, uri 0.13.3 |
| PASS | Packages downloaded into dist/ |  | 5 files in <project>\dist\7.1.3 |

### Install (42)

| Status | Test | Target | Result |
|---|---|---|---|
| PASS | Agent 7.1.3 installed (package mode) | acc-debian12 | installer exit 0 in 57s |
| PASS | Installed binary reports the expected version | acc-debian12 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z (expected 7.1.3) |
| PASS | Target reachable | acc-debian12 | pct 9522 via root@192.168.5.137 - Debian GNU/Linux 12 (bookworm), x86_64, 2 cpu, 1024 MB |
| PASS | acc service running and enabled | acc-debian12 | service active, enabled enabled, pid 29432 |
| PASS | acc.yml points at the MID endpoint with the API key | acc-debian12 | backend-url and api-key present |
| PASS | check allow-list enabled in acc.yml | acc-debian12 | allow-list configured |
| PASS | Agent 7.1.3 installed (package mode) | acc-rocky10 | installer exit 0 in 45s |
| PASS | Installed binary reports the expected version | acc-rocky10 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z (expected 7.1.3) |
| PASS | Target reachable | acc-rocky10 | pct 9524 via root@192.168.5.137 - Rocky Linux 10.0 (Red Quartz), x86_64, 2 cpu, 1024 MB |
| PASS | acc service running and enabled | acc-rocky10 | service active, enabled enabled, pid 35719 |
| PASS | acc.yml points at the MID endpoint with the API key | acc-rocky10 | backend-url and api-key present |
| PASS | check allow-list enabled in acc.yml | acc-rocky10 | allow-list configured |
| PASS | Agent 7.1.3 installed (package mode) | acc-rocky9 | installer exit 0 in 48s |
| PASS | Installed binary reports the expected version | acc-rocky9 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z (expected 7.1.3) |
| PASS | Target reachable | acc-rocky9 | pct 9523 via root@192.168.5.137 - Rocky Linux 9.4 (Blue Onyx), x86_64, 2 cpu, 1024 MB |
| PASS | acc service running and enabled | acc-rocky9 | service active, enabled enabled, pid 35176 |
| PASS | acc.yml points at the MID endpoint with the API key | acc-rocky9 | backend-url and api-key present |
| PASS | check allow-list enabled in acc.yml | acc-rocky9 | allow-list configured |
| PASS | Agent 7.1.3 installed (package mode) | acc-suse156 | installer exit 0 in 52s |
| PASS | Installed binary reports the expected version | acc-suse156 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z (expected 7.1.3) |
| PASS | Target reachable | acc-suse156 | pct 9525 via root@192.168.5.137 - openSUSE Leap 15.6, x86_64, 2 cpu, 1024 MB |
| PASS | acc service running and enabled | acc-suse156 | service active, enabled enabled, pid 23084 |
| PASS | acc.yml points at the MID endpoint with the API key | acc-suse156 | backend-url and api-key present |
| PASS | check allow-list enabled in acc.yml | acc-suse156 | allow-list configured |
| PASS | Agent 7.1.3 installed (package mode) | acc-ubuntu2204 | installer exit 0 in 76s |
| PASS | Installed binary reports the expected version | acc-ubuntu2204 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z (expected 7.1.3) |
| PASS | Target reachable | acc-ubuntu2204 | pct 9521 via root@192.168.5.137 - Ubuntu 22.04 LTS, x86_64, 2 cpu, 1024 MB |
| PASS | acc service running and enabled | acc-ubuntu2204 | service active, enabled enabled, pid 27875 |
| PASS | acc.yml points at the MID endpoint with the API key | acc-ubuntu2204 | backend-url and api-key present |
| PASS | check allow-list enabled in acc.yml | acc-ubuntu2204 | allow-list configured |
| PASS | Agent 7.1.3 installed (package mode) | acc-ubuntu2404 | installer exit 0 in 64s |
| PASS | Installed binary reports the expected version | acc-ubuntu2404 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z (expected 7.1.3) |
| PASS | Target reachable | acc-ubuntu2404 | pct 9520 via root@192.168.5.137 - Ubuntu 24.04 LTS, x86_64, 2 cpu, 1024 MB |
| PASS | acc service running and enabled | acc-ubuntu2404 | service active, enabled enabled, pid 48772 |
| PASS | acc.yml points at the MID endpoint with the API key | acc-ubuntu2404 | backend-url and api-key present |
| PASS | check allow-list enabled in acc.yml | acc-ubuntu2404 | allow-list configured |
| PASS | Agent 7.1.3 installed (package mode) | acc-win2025 | installer exit 0 in 47s |
| PASS | Installed binary reports the expected version | acc-win2025 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03T23:12:20Z (expected 7.1.3) |
| PASS | Target reachable | acc-win2025 | ssh(windows) Administrator@192.168.5.56 - Microsoft Windows Server 2025 Standard Evaluation, AMD64, 4 cpu, 6143 MB |
| PASS | acc service running and enabled | acc-win2025 | service Running, enabled n/a, pid 3932 |
| PASS | acc.yml points at the MID endpoint with the API key | acc-win2025 | backend-url and api-key present |
| PASS | check allow-list enabled in acc.yml | acc-win2025 | allow-list configured |

### Environment (20)

| Status | Test | Target | Result |
|---|---|---|---|
| WARN | sudo rules for the servicenow user | acc-debian12 | 0 rule(s) for servicenow - serial numbers, sudo osquery/ss and agent self-upgrade will not work (expected on a fresh server) |
| WARN | Host tools the agent content relies on | acc-rocky10 | missing dmidecode, tar - dmidecode: serial number / hardware fields stay empty |
| WARN | sudo rules for the servicenow user | acc-rocky10 | 0 rule(s) for servicenow - serial numbers, sudo osquery/ss and agent self-upgrade will not work (expected on a fresh server) |
| WARN | Host tools the agent content relies on | acc-rocky9 | missing dmidecode, tar - dmidecode: serial number / hardware fields stay empty |
| WARN | sudo rules for the servicenow user | acc-rocky9 | 0 rule(s) for servicenow - serial numbers, sudo osquery/ss and agent self-upgrade will not work (expected on a fresh server) |
| WARN | Host tools the agent content relies on | acc-suse156 | missing dmidecode - dmidecode: serial number / hardware fields stay empty |
| WARN | sudo rules for the servicenow user | acc-ubuntu2204 | 0 rule(s) for servicenow - serial numbers, sudo osquery/ss and agent self-upgrade will not work (expected on a fresh server) |
| WARN | sudo rules for the servicenow user | acc-ubuntu2404 | 0 rule(s) for servicenow - serial numbers, sudo osquery/ss and agent self-upgrade will not work (expected on a fresh server) |
| PASS | Disk, memory and CPU available | acc-debian12 | /var 6549 MB free, /tmp 6549 MB free, 996 MB RAM available, 2 cpu, container: lxc |
| PASS | Host tools the agent content relies on | acc-debian12 | all present |
| PASS | Disk, memory and CPU available | acc-rocky10 | /var 6783 MB free, /tmp 6783 MB free, 982 MB RAM available, 2 cpu, SELinux Disabled, container: lxc |
| PASS | Disk, memory and CPU available | acc-rocky9 | /var 6674 MB free, /tmp 6674 MB free, 986 MB RAM available, 2 cpu, SELinux Disabled, container: lxc |
| PASS | Disk, memory and CPU available | acc-suse156 | /var 6756 MB free, /tmp 6756 MB free, 986 MB RAM available, 2 cpu, container: lxc |
| PASS | sudo rules for the servicenow user | acc-suse156 | 1 rule(s) for servicenow |
| PASS | Disk, memory and CPU available | acc-ubuntu2204 | /var 6309 MB free, /tmp 6309 MB free, 984 MB RAM available, 2 cpu, firewall: Status: inactive, container: lxc |
| PASS | Host tools the agent content relies on | acc-ubuntu2204 | all present |
| PASS | Disk, memory and CPU available | acc-ubuntu2404 | /var 6343 MB free, /tmp 6343 MB free, 979 MB RAM available, 2 cpu, firewall: Status: inactive, container: lxc |
| PASS | Host tools the agent content relies on | acc-ubuntu2404 | all present |
| PASS | Disk, memory and CPU available | acc-win2025 | C: 49664 MB free, 4445 MB RAM free, 4 cpu, firewall profiles on: Domain,Private,Public, Defender real-time True |
| PASS | PowerShell, msiexec and administrator rights | acc-win2025 | PowerShell 5.1.26100.1591, execution policy RemoteSigned, administrator True |

### Connectivity (28)

| Status | Test | Target | Result |
|---|---|---|---|
| WARN | Agent log free of errors after start | acc-debian12 | 15 ERROR line(s) in the last 400 log lines |
| WARN | Agent log free of errors after start | acc-rocky10 | 16 ERROR line(s) in the last 400 log lines |
| WARN | Agent log free of errors after start | acc-rocky9 | 15 ERROR line(s) in the last 400 log lines |
| WARN | Agent log free of errors after start | acc-suse156 | 10 ERROR line(s) in the last 400 log lines |
| WARN | Agent log free of errors after start | acc-ubuntu2204 | 22 ERROR line(s) in the last 400 log lines |
| WARN | Agent log free of errors after start | acc-ubuntu2404 | 30 ERROR line(s) in the last 400 log lines |
| WARN | Agent log free of errors after start | acc-win2025 | 14 ERROR line(s) in the last 400 log lines |
| PASS | Agent connected through the configured MID | acc-debian12 | mid dl-mid (expected dl-mid) |
| PASS | Agent registered on the instance and Up | acc-debian12 | Agent_acc-debian12 id 7c7f698587312739 status Up since 2026-11-08 05:20:59 |
| PASS | Instance sees the expected agent version | acc-debian12 | 7.1.3 (expected 7.1.3) |
| PASS | Agent connected through the configured MID | acc-rocky10 | mid dl-mid (expected dl-mid) |
| PASS | Agent registered on the instance and Up | acc-rocky10 | Agent_acc-rocky10 id 189cd441da63bbdc status Up since 2026-11-08 05:51:27 |
| PASS | Instance sees the expected agent version | acc-rocky10 | 7.1.3 (expected 7.1.3) |
| PASS | Agent connected through the configured MID | acc-rocky9 | mid dl-mid (expected dl-mid) |
| PASS | Agent registered on the instance and Up | acc-rocky9 | Agent_acc-rocky9 id f6d0e934517624fd status Up since 2026-11-08 05:20:59 |
| PASS | Instance sees the expected agent version | acc-rocky9 | 7.1.3 (expected 7.1.3) |
| PASS | Agent connected through the configured MID | acc-suse156 | mid dl-mid (expected dl-mid) |
| PASS | Agent registered on the instance and Up | acc-suse156 | Agent_acc-suse156 id 211f592f68ebaa2f status Up since 2026-11-08 05:51:27 |
| PASS | Instance sees the expected agent version | acc-suse156 | 7.1.3 (expected 7.1.3) |
| PASS | Agent connected through the configured MID | acc-ubuntu2204 | mid dl-mid (expected dl-mid) |
| PASS | Agent registered on the instance and Up | acc-ubuntu2204 | Agent_acc-ubuntu2204 id 2669b332365db9e4 status Up since 2026-11-08 05:20:59 |
| PASS | Instance sees the expected agent version | acc-ubuntu2204 | 7.1.3 (expected 7.1.3) |
| PASS | Agent connected through the configured MID | acc-ubuntu2404 | mid dl-mid (expected dl-mid) |
| PASS | Agent registered on the instance and Up | acc-ubuntu2404 | Agent_acc-ubuntu2404 id d30005d07123ad5a status Up since 2026-11-08 05:20:59 |
| PASS | Instance sees the expected agent version | acc-ubuntu2404 | 7.1.3 (expected 7.1.3) |
| PASS | Agent connected through the configured MID | acc-win2025 | mid dl-mid (expected dl-mid) |
| PASS | Agent registered on the instance and Up | acc-win2025 | Agent_ACCWIN2025 id cdf287544e6e8ff6 status Up since 2026-11-08 05:51:27 |
| PASS | Instance sees the expected agent version | acc-win2025 | 7.1.3 (expected 7.1.3) |

### Discovery (56)

| Status | Test | Target | Result |
|---|---|---|---|
| FAIL *(cause: Instance / MID)* | Host data collected and a host CI bound to the agent | acc-rocky9 | host_data 'Collection failed' after 900s, cmdb_ci set; 2026-11-08 05:48:47 instance: In AgentNowHandler.createAccErrorsFromCheckResults: missing data for checkResult on ecc sysid=9905faaf83145f9055981896feaad38c with index=0 for agent id = f6d0e934517624fd and check definition id=undefined and check instance id=undefined |
| PASS | CI discovery source set by the agent | acc-debian12 | discovery_source 'ACC-Visibility', last_discovered 2026-11-08 05:40:17 |
| PASS | Discovery (collect host data) requested through the ACC API | acc-debian12 | accepted |
| PASS | Discovery populated related CI data | acc-debian12 | cmdb_ci_network_adapter=1, cmdb_ci_ip_address=2, cmdb_ci_file_system=1, cmdb_sam_sw_install=-1, cmdb_software_instance=0, cmdb_running_process=25, cmdb_rel_ci=135 |
| PASS | Host CI IP matches the server | acc-debian12 | CI 192.168.5.95 vs host 192.168.5.95 |
| PASS | Host CI carries OS and version | acc-debian12 | os 'Linux Debian' version '12.0' serial '' |
| PASS | Host CI class is cmdb_ci_linux_server | acc-debian12 | cmdb_ci_linux_server (acc-debian12) |
| PASS | Host CI name matches the server's host name | acc-debian12 | CI 'acc-debian12' vs host 'acc-debian12' |
| PASS | Host data collected and a host CI bound to the agent | acc-debian12 | host_data 'Collected' at 2026-11-08 05:40:19, CI acc-debian12 |
| PASS | CI discovery source set by the agent | acc-rocky10 | discovery_source 'ACC-Visibility', last_discovered 2026-11-08 06:09:47 |
| PASS | Discovery (collect host data) requested through the ACC API | acc-rocky10 | accepted |
| PASS | Discovery populated related CI data | acc-rocky10 | cmdb_ci_network_adapter=1, cmdb_ci_ip_address=1, cmdb_ci_file_system=1, cmdb_sam_sw_install=-1, cmdb_software_instance=0, cmdb_running_process=22, cmdb_rel_ci=134 |
| PASS | Host CI IP matches the server | acc-rocky10 | CI 192.168.5.182 vs host 192.168.5.182 |
| PASS | Host CI carries OS and version | acc-rocky10 | os 'Linux Rocky' version '10.0' serial '' |
| PASS | Host CI class is cmdb_ci_linux_server | acc-rocky10 | cmdb_ci_linux_server (acc-rocky10) |
| PASS | Host CI name matches the server's host name | acc-rocky10 | CI 'acc-rocky10' vs host 'acc-rocky10' |
| PASS | Host data collected and a host CI bound to the agent | acc-rocky10 | host_data 'Collected' at 2026-11-08 06:09:48, CI acc-rocky10 |
| PASS | CI discovery source set by the agent | acc-rocky9 | discovery_source 'ACC-Visibility', last_discovered 2026-11-07 23:29:07 |
| PASS | Discovery (collect host data) requested through the ACC API | acc-rocky9 | accepted |
| PASS | Discovery populated related CI data | acc-rocky9 | cmdb_ci_network_adapter=1, cmdb_ci_ip_address=2, cmdb_ci_file_system=1, cmdb_sam_sw_install=-1, cmdb_software_instance=0, cmdb_running_process=16, cmdb_rel_ci=133 |
| PASS | Host CI IP matches the server | acc-rocky9 | CI 192.168.5.231 vs host 192.168.5.231 |
| PASS | Host CI carries OS and version | acc-rocky9 | os 'Linux Rocky' version '9.4' serial '' |
| PASS | Host CI class is cmdb_ci_linux_server | acc-rocky9 | cmdb_ci_linux_server (acc-rocky9) |
| PASS | Host CI name matches the server's host name | acc-rocky9 | CI 'acc-rocky9' vs host 'acc-rocky9' |
| PASS | CI discovery source set by the agent | acc-suse156 | discovery_source 'ACC-Visibility', last_discovered 2026-11-08 06:19:51 |
| PASS | Discovery (collect host data) requested through the ACC API | acc-suse156 | accepted |
| PASS | Discovery populated related CI data | acc-suse156 | cmdb_ci_network_adapter=1, cmdb_ci_ip_address=2, cmdb_ci_file_system=1, cmdb_sam_sw_install=-1, cmdb_software_instance=0, cmdb_running_process=16, cmdb_rel_ci=135 |
| PASS | Host CI IP matches the server | acc-suse156 | CI 192.168.5.98 vs host 192.168.5.98 |
| PASS | Host CI carries OS and version | acc-suse156 | os 'Linux SuSE' version '15.6' serial '' |
| PASS | Host CI class is cmdb_ci_linux_server | acc-suse156 | cmdb_ci_linux_server (acc-suse156) |
| PASS | Host CI name matches the server's host name | acc-suse156 | CI 'acc-suse156' vs host 'acc-suse156' |
| PASS | Host data collected and a host CI bound to the agent | acc-suse156 | host_data 'Collected' at 2026-11-08 06:19:53, CI acc-suse156 |
| PASS | CI discovery source set by the agent | acc-ubuntu2204 | discovery_source 'ACC-Visibility', last_discovered 2026-11-08 05:31:23 |
| PASS | Discovery (collect host data) requested through the ACC API | acc-ubuntu2204 | accepted |
| PASS | Discovery populated related CI data | acc-ubuntu2204 | cmdb_ci_network_adapter=1, cmdb_ci_ip_address=2, cmdb_ci_file_system=1, cmdb_sam_sw_install=-1, cmdb_software_instance=335, cmdb_running_process=24, cmdb_rel_ci=135 |
| PASS | Host CI IP matches the server | acc-ubuntu2204 | CI 192.168.5.32 vs host 192.168.5.32 |
| PASS | Host CI carries OS and version | acc-ubuntu2204 | os 'Linux Ubuntu' version '22.04' serial '' |
| PASS | Host CI class is cmdb_ci_linux_server | acc-ubuntu2204 | cmdb_ci_linux_server (acc-ubuntu2204) |
| PASS | Host CI name matches the server's host name | acc-ubuntu2204 | CI 'acc-ubuntu2204' vs host 'acc-ubuntu2204' |
| PASS | Host data collected and a host CI bound to the agent | acc-ubuntu2204 | host_data 'Collected' at 2026-11-08 05:31:24, CI acc-ubuntu2204 |
| PASS | CI discovery source set by the agent | acc-ubuntu2404 | discovery_source 'ACC-Visibility', last_discovered 2026-11-08 05:21:39 |
| PASS | Discovery (collect host data) requested through the ACC API | acc-ubuntu2404 | accepted |
| PASS | Discovery populated related CI data | acc-ubuntu2404 | cmdb_ci_network_adapter=1, cmdb_ci_ip_address=2, cmdb_ci_file_system=1, cmdb_sam_sw_install=-1, cmdb_software_instance=0, cmdb_running_process=30, cmdb_rel_ci=135 |
| PASS | Host CI IP matches the server | acc-ubuntu2404 | CI 192.168.5.94 vs host 192.168.5.94 |
| PASS | Host CI carries OS and version | acc-ubuntu2404 | os 'Linux Ubuntu' version '24.04' serial '' |
| PASS | Host CI class is cmdb_ci_linux_server | acc-ubuntu2404 | cmdb_ci_linux_server (acc-ubuntu2404) |
| PASS | Host CI name matches the server's host name | acc-ubuntu2404 | CI 'acc-ubuntu2404' vs host 'acc-ubuntu2404' |
| PASS | Host data collected and a host CI bound to the agent | acc-ubuntu2404 | host_data 'Collected' at 2026-11-08 05:21:40, CI acc-ubuntu2404 |
| PASS | CI discovery source set by the agent | acc-win2025 | discovery_source 'ACC-Visibility', last_discovered 2026-11-08 06:29:34 |
| PASS | Discovery (collect host data) requested through the ACC API | acc-win2025 | accepted |
| PASS | Discovery populated related CI data | acc-win2025 | cmdb_ci_network_adapter=1, cmdb_ci_ip_address=2, cmdb_ci_file_system=3, cmdb_sam_sw_install=-1, cmdb_software_instance=0, cmdb_running_process=102, cmdb_rel_ci=11 |
| PASS | Host CI IP matches the server | acc-win2025 | CI 192.168.5.56 vs host 192.168.5.56 |
| PASS | Host CI carries OS and version | acc-win2025 | os 'Windows 2025 Standard Evaluation' version '10.0.26100' serial '94888934-BD2E-4C29-ACED-2CBC94F018EB' |
| PASS | Host CI class is cmdb_ci_win_server | acc-win2025 | cmdb_ci_win_server (accwin2025) |
| PASS | Host CI name matches the server's host name | acc-win2025 | CI 'accwin2025' vs host 'ACCWIN2025' |
| PASS | Host data collected and a host CI bound to the agent | acc-win2025 | host_data 'Collected' at 2026-11-08 06:29:35, CI accwin2025 |

### Checks (202)

| Status | Test | Target | Result |
|---|---|---|---|
| FAIL *(cause: Instance content)* | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | acc-debian12 | exit 127: the check could not execute properly - /usr/bin/env: 'ruby\r': No such file or directory /usr/bin/env: use -[v]S to pass options in shebang lines [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| FAIL *(cause: Instance content)* | Check 'acctest-custom-os-version' [custom, ] | acc-debian12 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| FAIL *(cause: Instance content)* | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | acc-rocky10 | exit 127: the check could not execute properly - /usr/bin/env: ‘ruby\r’: No such file or directory /usr/bin/env: use -[v]S to pass options in shebang lines [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| FAIL *(cause: Instance content)* | Check 'acctest-custom-os-version' [custom, ] | acc-rocky10 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| FAIL *(cause: Instance content)* | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | acc-rocky9 | exit 127: the check could not execute properly - /usr/bin/env: ‘ruby\r’: No such file or directory [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| FAIL *(cause: Instance content)* | Check 'acctest-custom-os-version' [custom, ] | acc-rocky9 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| FAIL *(cause: Instance content)* | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | acc-suse156 | exit 127: the check could not execute properly - /usr/bin/env: ‘ruby\r’: No such file or directory [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| FAIL *(cause: Instance content)* | Check 'acctest-custom-os-version' [custom, ] | acc-suse156 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| FAIL *(cause: Instance content)* | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | acc-ubuntu2204 | exit 127: the check could not execute properly - /usr/bin/env: 'ruby\r': No such file or directory [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| FAIL *(cause: Instance content)* | Check 'acctest-custom-os-version' [custom, ] | acc-ubuntu2204 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| FAIL *(cause: Instance content)* | Check 'VISC Browser Extension Discovery' [oob, VISC Browser Extension Discovery] | acc-ubuntu2404 | exit 127: the check could not execute properly - /usr/bin/env: 'ruby\r': No such file or directory /usr/bin/env: use -[v]S to pass options in shebang lines [cause: content - the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version] |
| FAIL *(cause: Instance content)* | Check 'acctest-custom-os-version' [custom, ] | acc-ubuntu2404 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| WARN | Agent self-test (acc self-test) | acc-debian12 | suite default: 7 passed, 1 failed, 1 skipped - failed: SudoSSCommandAccessTest (Unable to run ss command with sudo) |
| WARN | Check 'Software installations and usage metrics' [oob, ExtendedDiscovery] | acc-debian12 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get URL Metric' [oob, VISC URL Metric] | acc-debian12 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get application metric' [oob, VISC Application metric] | acc-debian12 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension device init' [oob, VISC Browser extension init] | acc-debian12 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension init' [oob, VISC Browser extension init] | acc-debian12 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension' [oob, VISC Browser extension] | acc-debian12 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get targeted URL metric' [oob, VISC Targeted URL Metric] | acc-debian12 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Agent self-test (acc self-test) | acc-rocky10 | suite default: 7 passed, 1 failed, 1 skipped - failed: SudoSSCommandAccessTest (Unable to run ss command with sudo) |
| WARN | Check 'Software installations and usage metrics' [oob, ExtendedDiscovery] | acc-rocky10 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get URL Metric' [oob, VISC URL Metric] | acc-rocky10 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get application metric' [oob, VISC Application metric] | acc-rocky10 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension device init' [oob, VISC Browser extension init] | acc-rocky10 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension init' [oob, VISC Browser extension init] | acc-rocky10 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension' [oob, VISC Browser extension] | acc-rocky10 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get targeted URL metric' [oob, VISC Targeted URL Metric] | acc-rocky10 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Agent self-test (acc self-test) | acc-rocky9 | suite default: 7 passed, 1 failed, 1 skipped - failed: SudoSSCommandAccessTest (Unable to run ss command with sudo) |
| WARN | Check 'Software installations and usage metrics' [oob, ExtendedDiscovery] | acc-rocky9 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get URL Metric' [oob, VISC URL Metric] | acc-rocky9 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get application metric' [oob, VISC Application metric] | acc-rocky9 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension device init' [oob, VISC Browser extension init] | acc-rocky9 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension init' [oob, VISC Browser extension init] | acc-rocky9 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension' [oob, VISC Browser extension] | acc-rocky9 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get targeted URL metric' [oob, VISC Targeted URL Metric] | acc-rocky9 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Agent self-test (acc self-test) | acc-suse156 | suite default: 7 passed, 1 failed, 1 skipped - failed: SudoSSCommandAccessTest (Unable to run ss command with sudo) |
| WARN | Check 'Software installations and usage metrics' [oob, ExtendedDiscovery] | acc-suse156 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get URL Metric' [oob, VISC URL Metric] | acc-suse156 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get application metric' [oob, VISC Application metric] | acc-suse156 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension device init' [oob, VISC Browser extension init] | acc-suse156 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension init' [oob, VISC Browser extension init] | acc-suse156 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension' [oob, VISC Browser extension] | acc-suse156 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get targeted URL metric' [oob, VISC Targeted URL Metric] | acc-suse156 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Agent self-test (acc self-test) | acc-ubuntu2204 | suite default: 7 passed, 1 failed, 1 skipped - failed: SudoSSCommandAccessTest (Unable to run ss command with sudo) |
| WARN | Check 'Software installations and usage metrics' [oob, ExtendedDiscovery] | acc-ubuntu2204 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get URL Metric' [oob, VISC URL Metric] | acc-ubuntu2204 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get application metric' [oob, VISC Application metric] | acc-ubuntu2204 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension device init' [oob, VISC Browser extension init] | acc-ubuntu2204 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension init' [oob, VISC Browser extension init] | acc-ubuntu2204 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension' [oob, VISC Browser extension] | acc-ubuntu2204 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get targeted URL metric' [oob, VISC Targeted URL Metric] | acc-ubuntu2204 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Agent self-test (acc self-test) | acc-ubuntu2404 | suite default: 7 passed, 1 failed, 1 skipped - failed: SudoSSCommandAccessTest (Unable to run ss command with sudo) |
| WARN | Check 'Software installations and usage metrics' [oob, ExtendedDiscovery] | acc-ubuntu2404 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get URL Metric' [oob, VISC URL Metric] | acc-ubuntu2404 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get application metric' [oob, VISC Application metric] | acc-ubuntu2404 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension device init' [oob, VISC Browser extension init] | acc-ubuntu2404 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension init' [oob, VISC Browser extension init] | acc-ubuntu2404 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get browser extension' [oob, VISC Browser extension] | acc-ubuntu2404 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| WARN | Check 'VISC Get targeted URL metric' [oob, VISC Targeted URL Metric] | acc-ubuntu2404 | denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - not applicable here, or the definition's assets/allow-list need attention |
| PASS | Check 'Enhanced Discovery' [oob, Enhanced Discovery] | acc-debian12 | exit 0 (OK), 53965 chars of output |
| PASS | Check 'File Based Discovery - File Management' [oob, ExtendedDiscovery] | acc-debian12 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - Java GLAS' [oob, ExtendedDiscovery] | acc-debian12 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - License Key' [oob, ExtendedDiscovery] | acc-debian12 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SAM' [oob, ExtendedDiscovery] | acc-debian12 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SWID' [oob, ExtendedDiscovery] | acc-debian12 | exit 0 (OK), 107 chars of output |
| PASS | Check 'Installed Software' [oob, ExtendedDiscovery] | acc-debian12 | exit 0 (OK), 43814 chars of output |
| PASS | Check 'Oracle GLAS HW data collection' [oob, ExtendedDiscovery] | acc-debian12 | exit 0 (OK), 4235 chars of output |
| PASS | Check 'Oracle GLAS Java Process Discovery' [oob, Oracle GLAS Java Process Discovery] | acc-debian12 | exit 0 (OK), 29 chars of output |
| PASS | Check 'TLS SSL Certificate Capture' [oob, TLS SSL Certificate Capture] | acc-debian12 | exit 0 (OK), 2 chars of output |
| PASS | Check 'acctest-users-linux' [custom, ] | acc-debian12 | exit 0 (OK), 2919 chars of output; script output verified: 24 users, 1 admin(s): root |
| PASS | Check 'check-discovery-basic' [oob, Discovery] | acc-debian12 | exit 0 (OK), 4044 chars of output |
| PASS | Check definitions read from the instance | acc-debian12 | 41 active: 38 out-of-box, 0 customized, 3 custom |
| PASS | Check 'Enhanced Discovery' [oob, Enhanced Discovery] | acc-rocky10 | exit 0 (OK), 52597 chars of output |
| PASS | Check 'File Based Discovery - File Management' [oob, ExtendedDiscovery] | acc-rocky10 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - Java GLAS' [oob, ExtendedDiscovery] | acc-rocky10 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - License Key' [oob, ExtendedDiscovery] | acc-rocky10 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SAM' [oob, ExtendedDiscovery] | acc-rocky10 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SWID' [oob, ExtendedDiscovery] | acc-rocky10 | exit 0 (OK), 107 chars of output |
| PASS | Check 'Installed Software' [oob, ExtendedDiscovery] | acc-rocky10 | exit 0 (OK), 27630 chars of output |
| PASS | Check 'Oracle GLAS HW data collection' [oob, ExtendedDiscovery] | acc-rocky10 | exit 0 (OK), 4269 chars of output |
| PASS | Check 'Oracle GLAS Java Process Discovery' [oob, Oracle GLAS Java Process Discovery] | acc-rocky10 | exit 0 (OK), 29 chars of output |
| PASS | Check 'TLS SSL Certificate Capture' [oob, TLS SSL Certificate Capture] | acc-rocky10 | exit 0 (OK), 2 chars of output |
| PASS | Check 'acctest-users-linux' [custom, ] | acc-rocky10 | exit 0 (OK), 2100 chars of output; script output verified: 18 users, 5 admin(s): halt, operator, root, shutdown, sync |
| PASS | Check 'check-discovery-basic' [oob, Discovery] | acc-rocky10 | exit 0 (OK), 3395 chars of output |
| PASS | Check definitions read from the instance | acc-rocky10 | 41 active: 38 out-of-box, 0 customized, 3 custom |
| PASS | Check 'Enhanced Discovery' [oob, Enhanced Discovery] | acc-rocky9 | exit 0 (OK), 52460 chars of output |
| PASS | Check 'File Based Discovery - File Management' [oob, ExtendedDiscovery] | acc-rocky9 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - Java GLAS' [oob, ExtendedDiscovery] | acc-rocky9 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - License Key' [oob, ExtendedDiscovery] | acc-rocky9 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SAM' [oob, ExtendedDiscovery] | acc-rocky9 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SWID' [oob, ExtendedDiscovery] | acc-rocky9 | exit 0 (OK), 107 chars of output |
| PASS | Check 'Installed Software' [oob, ExtendedDiscovery] | acc-rocky9 | exit 0 (OK), 28471 chars of output |
| PASS | Check 'Oracle GLAS HW data collection' [oob, ExtendedDiscovery] | acc-rocky9 | exit 0 (OK), 4261 chars of output |
| PASS | Check 'Oracle GLAS Java Process Discovery' [oob, Oracle GLAS Java Process Discovery] | acc-rocky9 | exit 0 (OK), 29 chars of output |
| PASS | Check 'TLS SSL Certificate Capture' [oob, TLS SSL Certificate Capture] | acc-rocky9 | exit 0 (OK), 2 chars of output |
| PASS | Check 'acctest-users-linux' [custom, ] | acc-rocky9 | exit 0 (OK), 1942 chars of output; script output verified: 17 users, 5 admin(s): halt, operator, root, shutdown, sync |
| PASS | Check 'check-discovery-basic' [oob, Discovery] | acc-rocky9 | exit 0 (OK), 3221 chars of output |
| PASS | Check definitions read from the instance | acc-rocky9 | 41 active: 38 out-of-box, 0 customized, 3 custom |
| PASS | Check 'Enhanced Discovery' [oob, Enhanced Discovery] | acc-suse156 | exit 0 (OK), 51122 chars of output |
| PASS | Check 'File Based Discovery - File Management' [oob, ExtendedDiscovery] | acc-suse156 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - Java GLAS' [oob, ExtendedDiscovery] | acc-suse156 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - License Key' [oob, ExtendedDiscovery] | acc-suse156 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SAM' [oob, ExtendedDiscovery] | acc-suse156 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SWID' [oob, ExtendedDiscovery] | acc-suse156 | exit 0 (OK), 107 chars of output |
| PASS | Check 'Installed Software' [oob, ExtendedDiscovery] | acc-suse156 | exit 0 (OK), 27422 chars of output |
| PASS | Check 'Oracle GLAS HW data collection' [oob, ExtendedDiscovery] | acc-suse156 | exit 0 (OK), 4267 chars of output |
| PASS | Check 'Oracle GLAS Java Process Discovery' [oob, Oracle GLAS Java Process Discovery] | acc-suse156 | exit 0 (OK), 29 chars of output |
| PASS | Check 'TLS SSL Certificate Capture' [oob, TLS SSL Certificate Capture] | acc-suse156 | exit 0 (OK), 2 chars of output |
| PASS | Check 'acctest-users-linux' [custom, ] | acc-suse156 | exit 0 (OK), 461 chars of output; script output verified: 3 users, 1 admin(s): root |
| PASS | Check 'check-discovery-basic' [oob, Discovery] | acc-suse156 | exit 0 (OK), 3078 chars of output |
| PASS | Check definitions read from the instance | acc-suse156 | 41 active: 38 out-of-box, 0 customized, 3 custom |
| PASS | Check 'Enhanced Discovery' [oob, Enhanced Discovery] | acc-ubuntu2204 | exit 0 (OK), 54474 chars of output |
| PASS | Check 'File Based Discovery - File Management' [oob, ExtendedDiscovery] | acc-ubuntu2204 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - Java GLAS' [oob, ExtendedDiscovery] | acc-ubuntu2204 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - License Key' [oob, ExtendedDiscovery] | acc-ubuntu2204 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SAM' [oob, ExtendedDiscovery] | acc-ubuntu2204 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SWID' [oob, ExtendedDiscovery] | acc-ubuntu2204 | exit 0 (OK), 107 chars of output |
| PASS | Check 'Installed Software' [oob, ExtendedDiscovery] | acc-ubuntu2204 | exit 0 (OK), 54766 chars of output |
| PASS | Check 'Oracle GLAS HW data collection' [oob, ExtendedDiscovery] | acc-ubuntu2204 | exit 0 (OK), 4238 chars of output |
| PASS | Check 'Oracle GLAS Java Process Discovery' [oob, Oracle GLAS Java Process Discovery] | acc-ubuntu2204 | exit 0 (OK), 29 chars of output |
| PASS | Check 'TLS SSL Certificate Capture' [oob, TLS SSL Certificate Capture] | acc-ubuntu2204 | exit 0 (OK), 2 chars of output |
| PASS | Check 'acctest-users-linux' [custom, ] | acc-ubuntu2204 | exit 0 (OK), 3574 chars of output; script output verified: 29 users, 1 admin(s): root |
| PASS | Check 'check-discovery-basic' [oob, Discovery] | acc-ubuntu2204 | exit 0 (OK), 4058 chars of output |
| PASS | Check definitions read from the instance | acc-ubuntu2204 | 41 active: 38 out-of-box, 0 customized, 3 custom |
| PASS | Check 'Enhanced Discovery' [oob, Enhanced Discovery] | acc-ubuntu2404 | exit 0 (OK), 54733 chars of output |
| PASS | Check 'File Based Discovery - File Management' [oob, ExtendedDiscovery] | acc-ubuntu2404 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - Java GLAS' [oob, ExtendedDiscovery] | acc-ubuntu2404 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - License Key' [oob, ExtendedDiscovery] | acc-ubuntu2404 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SAM' [oob, ExtendedDiscovery] | acc-ubuntu2404 | exit 0 (OK), 107 chars of output |
| PASS | Check 'File Based Discovery - SWID' [oob, ExtendedDiscovery] | acc-ubuntu2404 | exit 0 (OK), 107 chars of output |
| PASS | Check 'Installed Software' [oob, ExtendedDiscovery] | acc-ubuntu2404 | exit 0 (OK), 58869 chars of output |
| PASS | Check 'Oracle GLAS HW data collection' [oob, ExtendedDiscovery] | acc-ubuntu2404 | exit 0 (OK), 4238 chars of output |
| PASS | Check 'Oracle GLAS Java Process Discovery' [oob, Oracle GLAS Java Process Discovery] | acc-ubuntu2404 | exit 0 (OK), 29 chars of output |
| PASS | Check 'TLS SSL Certificate Capture' [oob, TLS SSL Certificate Capture] | acc-ubuntu2404 | exit 0 (OK), 2 chars of output |
| PASS | Check 'acctest-users-linux' [custom, ] | acc-ubuntu2404 | exit 0 (OK), 3541 chars of output; script output verified: 29 users, 1 admin(s): root |
| PASS | Check 'check-discovery-basic' [oob, Discovery] | acc-ubuntu2404 | exit 0 (OK), 4250 chars of output |
| PASS | Check definitions read from the instance | acc-ubuntu2404 | 41 active: 38 out-of-box, 0 customized, 3 custom |
| PASS | Agent self-test (acc self-test) | acc-win2025 | suite default: 9 passed, 0 failed, 1 skipped |
| PASS | Check 'Enhanced Discovery' [oob, Enhanced Discovery] | acc-win2025 | exit 0 (OK), 13486 chars of output |
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
| PASS | Check 'check-discovery-basic' [oob, Discovery] | acc-win2025 | exit 0 (OK), 8822 chars of output |
| PASS | Check definitions read from the instance | acc-win2025 | 41 active: 38 out-of-box, 0 customized, 3 custom |
| SKIP | Agent-internal check types (upgrade, restart, cancel, ...) | acc-debian12 | 14 framework-internal definitions are exercised by their own actions, not ad hoc: Agent Upgrade - DEB, Agent Upgrade - MAC, Agent Upgrade - MSI, Agent Upgrade - RPM, Cancel, Regenerate Agent ID, Restart agent, System Command, TestCheck - OSQuery [Linux], TestCheck - OSQuery [Mac], TestCheck - OSQuery [Windows], check-read-log, config file reader, self-test |
| SKIP | Check 'FBD SAM Process Scan' [oob] | acc-debian12 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'File Based Discovery Background' [oob] | acc-debian12 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM Background Data collection ( Non OsqueryD )' [oob] | acc-debian12 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM background log check' [oob] | acc-debian12 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'Software Discovery via Running Process' [oob] | acc-debian12 | background check (ad-hoc test not supported by the platform) |
| SKIP | Agent-internal check types (upgrade, restart, cancel, ...) | acc-rocky10 | 14 framework-internal definitions are exercised by their own actions, not ad hoc: Agent Upgrade - DEB, Agent Upgrade - MAC, Agent Upgrade - MSI, Agent Upgrade - RPM, Cancel, Regenerate Agent ID, Restart agent, System Command, TestCheck - OSQuery [Linux], TestCheck - OSQuery [Mac], TestCheck - OSQuery [Windows], check-read-log, config file reader, self-test |
| SKIP | Check 'FBD SAM Process Scan' [oob] | acc-rocky10 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'File Based Discovery Background' [oob] | acc-rocky10 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM Background Data collection ( Non OsqueryD )' [oob] | acc-rocky10 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM background log check' [oob] | acc-rocky10 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'Software Discovery via Running Process' [oob] | acc-rocky10 | background check (ad-hoc test not supported by the platform) |
| SKIP | Agent-internal check types (upgrade, restart, cancel, ...) | acc-rocky9 | 14 framework-internal definitions are exercised by their own actions, not ad hoc: Agent Upgrade - DEB, Agent Upgrade - MAC, Agent Upgrade - MSI, Agent Upgrade - RPM, Cancel, Regenerate Agent ID, Restart agent, System Command, TestCheck - OSQuery [Linux], TestCheck - OSQuery [Mac], TestCheck - OSQuery [Windows], check-read-log, config file reader, self-test |
| SKIP | Check 'FBD SAM Process Scan' [oob] | acc-rocky9 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'File Based Discovery Background' [oob] | acc-rocky9 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM Background Data collection ( Non OsqueryD )' [oob] | acc-rocky9 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM background log check' [oob] | acc-rocky9 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'Software Discovery via Running Process' [oob] | acc-rocky9 | background check (ad-hoc test not supported by the platform) |
| SKIP | Agent-internal check types (upgrade, restart, cancel, ...) | acc-suse156 | 14 framework-internal definitions are exercised by their own actions, not ad hoc: Agent Upgrade - DEB, Agent Upgrade - MAC, Agent Upgrade - MSI, Agent Upgrade - RPM, Cancel, Regenerate Agent ID, Restart agent, System Command, TestCheck - OSQuery [Linux], TestCheck - OSQuery [Mac], TestCheck - OSQuery [Windows], check-read-log, config file reader, self-test |
| SKIP | Check 'FBD SAM Process Scan' [oob] | acc-suse156 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'File Based Discovery Background' [oob] | acc-suse156 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM Background Data collection ( Non OsqueryD )' [oob] | acc-suse156 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM background log check' [oob] | acc-suse156 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'Software Discovery via Running Process' [oob] | acc-suse156 | background check (ad-hoc test not supported by the platform) |
| SKIP | Agent-internal check types (upgrade, restart, cancel, ...) | acc-ubuntu2204 | 14 framework-internal definitions are exercised by their own actions, not ad hoc: Agent Upgrade - DEB, Agent Upgrade - MAC, Agent Upgrade - MSI, Agent Upgrade - RPM, Cancel, Regenerate Agent ID, Restart agent, System Command, TestCheck - OSQuery [Linux], TestCheck - OSQuery [Mac], TestCheck - OSQuery [Windows], check-read-log, config file reader, self-test |
| SKIP | Check 'FBD SAM Process Scan' [oob] | acc-ubuntu2204 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'File Based Discovery Background' [oob] | acc-ubuntu2204 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM Background Data collection ( Non OsqueryD )' [oob] | acc-ubuntu2204 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM background log check' [oob] | acc-ubuntu2204 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'Software Discovery via Running Process' [oob] | acc-ubuntu2204 | background check (ad-hoc test not supported by the platform) |
| SKIP | Agent-internal check types (upgrade, restart, cancel, ...) | acc-ubuntu2404 | 14 framework-internal definitions are exercised by their own actions, not ad hoc: Agent Upgrade - DEB, Agent Upgrade - MAC, Agent Upgrade - MSI, Agent Upgrade - RPM, Cancel, Regenerate Agent ID, Restart agent, System Command, TestCheck - OSQuery [Linux], TestCheck - OSQuery [Mac], TestCheck - OSQuery [Windows], check-read-log, config file reader, self-test |
| SKIP | Check 'FBD SAM Process Scan' [oob] | acc-ubuntu2404 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'File Based Discovery Background' [oob] | acc-ubuntu2404 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM Background Data collection ( Non OsqueryD )' [oob] | acc-ubuntu2404 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM background log check' [oob] | acc-ubuntu2404 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'Software Discovery via Running Process' [oob] | acc-ubuntu2404 | background check (ad-hoc test not supported by the platform) |
| SKIP | Agent-internal check types (upgrade, restart, cancel, ...) | acc-win2025 | 14 framework-internal definitions are exercised by their own actions, not ad hoc: Agent Upgrade - DEB, Agent Upgrade - MAC, Agent Upgrade - MSI, Agent Upgrade - RPM, Cancel, Regenerate Agent ID, Restart agent, System Command, TestCheck - OSQuery [Linux], TestCheck - OSQuery [Mac], TestCheck - OSQuery [Windows], check-read-log, config file reader, self-test |
| SKIP | Check 'FBD SAM Process Scan' [oob] | acc-win2025 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'File Based Discovery Background' [oob] | acc-win2025 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM Background Data collection ( Non OsqueryD )' [oob] | acc-win2025 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'SAM background log check' [oob] | acc-win2025 | background check (ad-hoc test not supported by the platform) |
| SKIP | Check 'Software Discovery via Running Process' [oob] | acc-win2025 | background check (ad-hoc test not supported by the platform) |

### Policies (103)

| Status | Test | Target | Result |
|---|---|---|---|
| FAIL *(cause: Instance content)* | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | acc-debian12 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| FAIL *(cause: Instance content)* | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | acc-rocky10 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| FAIL *(cause: Instance content)* | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | acc-rocky9 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| FAIL *(cause: Instance content)* | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | acc-suse156 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| FAIL *(cause: Instance content)* | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | acc-ubuntu2204 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| FAIL *(cause: Instance content)* | Policy 'acctest-custom-policy' check 'acctest-custom-os-version' | acc-ubuntu2404 | exit 0 (OK), 1046 chars of output; script output verified: output present; re-verified from the stored output: the shipped module returned an error instead of data: cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath': wrong number of arguments (given 3, expected 4) (ArgumentError)\n\tfrom /var/cache/servicen |
| WARN | Policy 'Software Installed Policy' [oob] applies to this agent | acc-debian12 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-custom-policy' [custom] applies to this agent | acc-debian12 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-users-linux-policy' [custom] applies to this agent | acc-debian12 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'Software Installed Policy' [oob] applies to this agent | acc-rocky10 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-custom-policy' [custom] applies to this agent | acc-rocky10 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-users-linux-policy' [custom] applies to this agent | acc-rocky10 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'Software Installed Policy' [oob] applies to this agent | acc-rocky9 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-custom-policy' [custom] applies to this agent | acc-rocky9 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-users-linux-policy' [custom] applies to this agent | acc-rocky9 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'Software Installed Policy' [oob] applies to this agent | acc-suse156 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-custom-policy' [custom] applies to this agent | acc-suse156 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-users-linux-policy' [custom] applies to this agent | acc-suse156 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'Software Installed Policy' [oob] applies to this agent | acc-ubuntu2204 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-custom-policy' [custom] applies to this agent | acc-ubuntu2204 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-users-linux-policy' [custom] applies to this agent | acc-ubuntu2204 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'Software Installed Policy' [oob] applies to this agent | acc-ubuntu2404 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-custom-policy' [custom] applies to this agent | acc-ubuntu2404 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'acctest-users-linux-policy' [custom] applies to this agent | acc-ubuntu2404 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| WARN | Policy 'Software Installed Policy' [oob] applies to this agent | acc-win2025 | policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy calculation job runs periodically) |
| PASS | Policies read from the instance | acc-debian12 | 11 active published policies (3 custom/customized) |
| PASS | Policy 'Software Installed Policy' check 'Installed Software' | acc-debian12 | exit 0 (OK), 43814 chars of output |
| PASS | Policy 'acctest-users-linux-policy' check 'acctest-users-linux' | acc-debian12 | exit 0 (OK), 2919 chars of output; script output verified: 24 users, 1 admin(s): root |
| PASS | Policies read from the instance | acc-rocky10 | 11 active published policies (3 custom/customized) |
| PASS | Policy 'Software Installed Policy' check 'Installed Software' | acc-rocky10 | exit 0 (OK), 27630 chars of output |
| PASS | Policy 'acctest-users-linux-policy' check 'acctest-users-linux' | acc-rocky10 | exit 0 (OK), 2100 chars of output; script output verified: 18 users, 5 admin(s): halt, operator, root, shutdown, sync |
| PASS | Policies read from the instance | acc-rocky9 | 11 active published policies (3 custom/customized) |
| PASS | Policy 'Software Installed Policy' check 'Installed Software' | acc-rocky9 | exit 0 (OK), 28471 chars of output |
| PASS | Policy 'acctest-users-linux-policy' check 'acctest-users-linux' | acc-rocky9 | exit 0 (OK), 1942 chars of output; script output verified: 17 users, 5 admin(s): halt, operator, root, shutdown, sync |
| PASS | Policies read from the instance | acc-suse156 | 11 active published policies (3 custom/customized) |
| PASS | Policy 'Software Installed Policy' check 'Installed Software' | acc-suse156 | exit 0 (OK), 27422 chars of output |
| PASS | Policy 'acctest-users-linux-policy' check 'acctest-users-linux' | acc-suse156 | exit 0 (OK), 461 chars of output; script output verified: 3 users, 1 admin(s): root |
| PASS | Policies read from the instance | acc-ubuntu2204 | 11 active published policies (3 custom/customized) |
| PASS | Policy 'Software Installed Policy' check 'Installed Software' | acc-ubuntu2204 | exit 0 (OK), 54766 chars of output |
| PASS | Policy 'acctest-users-linux-policy' check 'acctest-users-linux' | acc-ubuntu2204 | exit 0 (OK), 3574 chars of output; script output verified: 29 users, 1 admin(s): root |
| PASS | Policies read from the instance | acc-ubuntu2404 | 11 active published policies (3 custom/customized) |
| PASS | Policy 'Software Installed Policy' check 'Installed Software' | acc-ubuntu2404 | exit 0 (OK), 58869 chars of output |
| PASS | Policy 'acctest-users-linux-policy' check 'acctest-users-linux' | acc-ubuntu2404 | exit 0 (OK), 3541 chars of output; script output verified: 29 users, 1 admin(s): root |
| PASS | Policies read from the instance | acc-win2025 | 11 active published policies (3 custom/customized) |
| PASS | Policy 'Software Installed Policy' check 'Installed Software' | acc-win2025 | exit 0 (OK), 2984 chars of output |
| SKIP | Policy 'Enhanced Discovery Policy' [oob] | acc-debian12 | policy selects CIs by script/group - not evaluated |
| SKIP | Policy 'SAM background policy' [oob] | acc-debian12 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'SAM discovery ' [oob] | acc-debian12 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'VISC Browser Extension Discovery' [oob] | acc-debian12 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac^ORosLIKElinux' |
| SKIP | Policy 'VISC Get application metric' [oob] | acc-debian12 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension device init' [oob] | acc-debian12 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension init' [oob] | acc-debian12 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'acctest-users-windows-policy' [custom] | acc-debian12 | CI is not in cmdb_ci_win_server with filter 'nameSTARTSWITHacc-' |
| SKIP | Policy 'Enhanced Discovery Policy' [oob] | acc-rocky10 | policy selects CIs by script/group - not evaluated |
| SKIP | Policy 'SAM background policy' [oob] | acc-rocky10 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'SAM discovery ' [oob] | acc-rocky10 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'VISC Browser Extension Discovery' [oob] | acc-rocky10 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac^ORosLIKElinux' |
| SKIP | Policy 'VISC Get application metric' [oob] | acc-rocky10 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension device init' [oob] | acc-rocky10 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension init' [oob] | acc-rocky10 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'acctest-users-windows-policy' [custom] | acc-rocky10 | CI is not in cmdb_ci_win_server with filter 'nameSTARTSWITHacc-' |
| SKIP | Policy 'Enhanced Discovery Policy' [oob] | acc-rocky9 | policy selects CIs by script/group - not evaluated |
| SKIP | Policy 'SAM background policy' [oob] | acc-rocky9 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'SAM discovery ' [oob] | acc-rocky9 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'VISC Browser Extension Discovery' [oob] | acc-rocky9 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac^ORosLIKElinux' |
| SKIP | Policy 'VISC Get application metric' [oob] | acc-rocky9 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension device init' [oob] | acc-rocky9 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension init' [oob] | acc-rocky9 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'acctest-users-windows-policy' [custom] | acc-rocky9 | CI is not in cmdb_ci_win_server with filter 'nameSTARTSWITHacc-' |
| SKIP | Policy 'Enhanced Discovery Policy' [oob] | acc-suse156 | policy selects CIs by script/group - not evaluated |
| SKIP | Policy 'SAM background policy' [oob] | acc-suse156 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'SAM discovery ' [oob] | acc-suse156 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'VISC Browser Extension Discovery' [oob] | acc-suse156 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac^ORosLIKElinux' |
| SKIP | Policy 'VISC Get application metric' [oob] | acc-suse156 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension device init' [oob] | acc-suse156 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension init' [oob] | acc-suse156 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'acctest-users-windows-policy' [custom] | acc-suse156 | CI is not in cmdb_ci_win_server with filter 'nameSTARTSWITHacc-' |
| SKIP | Policy 'Enhanced Discovery Policy' [oob] | acc-ubuntu2204 | policy selects CIs by script/group - not evaluated |
| SKIP | Policy 'SAM background policy' [oob] | acc-ubuntu2204 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'SAM discovery ' [oob] | acc-ubuntu2204 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'VISC Browser Extension Discovery' [oob] | acc-ubuntu2204 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac^ORosLIKElinux' |
| SKIP | Policy 'VISC Get application metric' [oob] | acc-ubuntu2204 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension device init' [oob] | acc-ubuntu2204 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension init' [oob] | acc-ubuntu2204 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'acctest-users-windows-policy' [custom] | acc-ubuntu2204 | CI is not in cmdb_ci_win_server with filter 'nameSTARTSWITHacc-' |
| SKIP | Policy 'Enhanced Discovery Policy' [oob] | acc-ubuntu2404 | policy selects CIs by script/group - not evaluated |
| SKIP | Policy 'SAM background policy' [oob] | acc-ubuntu2404 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'SAM discovery ' [oob] | acc-ubuntu2404 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEWindows^ORosLIKEMac' |
| SKIP | Policy 'VISC Browser Extension Discovery' [oob] | acc-ubuntu2404 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac^ORosLIKElinux' |
| SKIP | Policy 'VISC Get application metric' [oob] | acc-ubuntu2404 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension device init' [oob] | acc-ubuntu2404 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'VISC Get browser extension init' [oob] | acc-ubuntu2404 | CI is not in cmdb_ci_computer with filter 'sys_class_name=cmdb_ci_computer^osLIKEwindows^ORosLIKEmac' |
| SKIP | Policy 'acctest-users-windows-policy' [custom] | acc-ubuntu2404 | CI is not in cmdb_ci_win_server with filter 'nameSTARTSWITHacc-' |
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

### Resources (27)

| Status | Test | Target | Result |
|---|---|---|---|
| FAIL *(cause: Instance content)* | Plugin scripts delivered by the MID are executable on this OS | acc-debian12 | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb, acc-visibility-modules-common/bin/file_output_split.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this does not change with the agent] |
| FAIL *(cause: Instance content)* | Plugin scripts delivered by the MID are executable on this OS | acc-rocky10 | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/file_output_split.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this does not change with the agent] |
| FAIL *(cause: Instance content)* | Plugin scripts delivered by the MID are executable on this OS | acc-rocky9 | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/file_output_split.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb, acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this does not change with the agent] |
| FAIL *(cause: Instance content)* | Plugin scripts delivered by the MID are executable on this OS | acc-suse156 | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/file_output_split.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this does not change with the agent] |
| FAIL *(cause: Instance content)* | Plugin scripts delivered by the MID are executable on this OS | acc-ubuntu2204 | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb, acc-visibility-modules-common/bin/file_output_split.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this does not change with the agent] |
| FAIL *(cause: Instance content)* | Plugin scripts delivered by the MID are executable on this OS | acc-ubuntu2404 | 5 plugin directories, 138 scripts; 5 script(s) have a CRLF shebang and fail with "'ruby\r': No such file": acc-visibility-modules-common/bin/browser_extension_discovery.rb, acc-visibility-modules-common/bin/file_output_split.rb, acc-visibility-modules-common/bin/tls_ssl_certs_common.rb, acc-visibility-modules-common/bin/fbd/file_delta_detector.rb, acc-visibility-modules-common/bin/fbd/chunk/chunk_sender.rb [cause: content - plugin asset(s) acc-visibility-modules-common are shipped with Windows line endings by the content app on the instance; the same files reach every agent version, so this does not change with the agent] |
| PASS | Agent CPU within the configured threshold | acc-debian12 | avg 0% / peak 0% of one core over 12 samples (60s), limit 5% (+5 tolerance); RSS 40 MB, 8 threads, up to 1 processes |
| PASS | CPU protection configured in acc.yml | acc-debian12 | cpu_percentage_limit 5%, repeated_high_cpu_num 3, monitor_interval 60s, max-running-checks 10 |
| PASS | Component inventory read from the installed agent | acc-debian12 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z; ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux]; OpenSSL OpenSSL 3.5.9 29 Sep 2026; osquery osqueryi version 5.18.1; 94 gems, 6 plugin assets - full list in the Components section and components.csv |
| PASS | Agent CPU within the configured threshold | acc-rocky10 | avg 0% / peak 0% of one core over 12 samples (60s), limit 5% (+5 tolerance); RSS 39 MB, 9 threads, up to 1 processes |
| PASS | CPU protection configured in acc.yml | acc-rocky10 | cpu_percentage_limit 5%, repeated_high_cpu_num 3, monitor_interval 60s, max-running-checks 10 |
| PASS | Component inventory read from the installed agent | acc-rocky10 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z; ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux]; OpenSSL OpenSSL 3.5.9 29 Sep 2026; osquery osqueryi version 5.18.1; 94 gems, 6 plugin assets - full list in the Components section and components.csv |
| PASS | Agent CPU within the configured threshold | acc-rocky9 | avg 0% / peak 0% of one core over 12 samples (60s), limit 5% (+5 tolerance); RSS 39 MB, 9 threads, up to 1 processes |
| PASS | CPU protection configured in acc.yml | acc-rocky9 | cpu_percentage_limit 5%, repeated_high_cpu_num 3, monitor_interval 60s, max-running-checks 10 |
| PASS | Component inventory read from the installed agent | acc-rocky9 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z; ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux]; OpenSSL OpenSSL 3.5.9 29 Sep 2026; osquery osqueryi version 5.18.1; 94 gems, 6 plugin assets - full list in the Components section and components.csv |
| PASS | Agent CPU within the configured threshold | acc-suse156 | avg 0% / peak 0% of one core over 12 samples (60s), limit 5% (+5 tolerance); RSS 40 MB, 9 threads, up to 1 processes |
| PASS | CPU protection configured in acc.yml | acc-suse156 | cpu_percentage_limit 5%, repeated_high_cpu_num 3, monitor_interval 60s, max-running-checks 10 |
| PASS | Component inventory read from the installed agent | acc-suse156 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z; ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux]; OpenSSL OpenSSL 3.5.9 29 Sep 2026; osquery osqueryi version 5.18.1; 94 gems, 6 plugin assets - full list in the Components section and components.csv |
| PASS | Agent CPU within the configured threshold | acc-ubuntu2204 | avg 0% / peak 0% of one core over 12 samples (60s), limit 5% (+5 tolerance); RSS 41 MB, 9 threads, up to 1 processes |
| PASS | CPU protection configured in acc.yml | acc-ubuntu2204 | cpu_percentage_limit 5%, repeated_high_cpu_num 3, monitor_interval 60s, max-running-checks 10 |
| PASS | Component inventory read from the installed agent | acc-ubuntu2204 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z; ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux]; OpenSSL OpenSSL 3.5.9 29 Sep 2026; osquery osqueryi version 5.18.1; 94 gems, 6 plugin assets - full list in the Components section and components.csv |
| PASS | Agent CPU within the configured threshold | acc-ubuntu2404 | avg 0% / peak 0% of one core over 12 samples (60s), limit 5% (+5 tolerance); RSS 40 MB, 9 threads, up to 1 processes |
| PASS | CPU protection configured in acc.yml | acc-ubuntu2404 | cpu_percentage_limit 5%, repeated_high_cpu_num 3, monitor_interval 60s, max-running-checks 10 |
| PASS | Component inventory read from the installed agent | acc-ubuntu2404 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z; ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux]; OpenSSL OpenSSL 3.5.9 29 Sep 2026; osquery osqueryi version 5.18.1; 94 gems, 6 plugin assets - full list in the Components section and components.csv |
| PASS | Agent CPU within the configured threshold | acc-win2025 | avg 1% / peak 2% of one core over 12 samples (60s), limit 5% (+5 tolerance); RSS 69 MB, 15 threads, up to 1 processes |
| PASS | CPU protection configured in acc.yml | acc-win2025 | cpu_percentage_limit 5%, repeated_high_cpu_num 3, monitor_interval 60s, max-running-checks 10 |
| PASS | Component inventory read from the installed agent | acc-win2025 | acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03T23:12:20Z; ruby 3.3.13 (2026-10-23 revision af48f08f21) [x64-mingw32ucrt]; OpenSSL OpenSSL 3.5.9 29 Sep 2026; osquery osqueryi.exe version 5.18.1; 96 gems, 6 plugin assets - full list in the Components section and components.csv |

### Cleanup (21)

| Status | Test | Target | Result |
|---|---|---|---|
| WARN | No check processes, zombies or temp files left after discovery | acc-debian12 | child processes 0, zombies 0, osquery processes 0, temp files 1: ['/tmp/acctest-signing.cer'] |
| WARN | No check processes, zombies or temp files left after discovery | acc-rocky10 | child processes 0, zombies 0, osquery processes 0, temp files 1: ['/tmp/acctest-signing.cer'] |
| WARN | No check processes, zombies or temp files left after discovery | acc-rocky9 | child processes 0, zombies 0, osquery processes 0, temp files 2: ['/tmp/acctest-signing.cer', '/tmp/acctest'] |
| WARN | No check processes, zombies or temp files left after discovery | acc-suse156 | child processes 0, zombies 0, osquery processes 0, temp files 1: ['/tmp/acctest-signing.cer'] |
| WARN | No check processes, zombies or temp files left after discovery | acc-ubuntu2204 | child processes 0, zombies 0, osquery processes 0, temp files 1: ['/tmp/acctest-signing.cer'] |
| WARN | No check processes, zombies or temp files left after discovery | acc-ubuntu2404 | child processes 0, zombies 0, osquery processes 0, temp files 2: ['/tmp/acctest-signing.cer', '/tmp/acctest'] |
| WARN | No check processes, zombies or temp files left after discovery | acc-win2025 | child processes 0, zombies 0, osquery processes 0, temp files 2: ['C:\\Windows\\Temp\\acctest-lab-root.cer', 'C:\\Windows\\Temp\\acctest-signing.cer'] |
| PASS | Disk footprint of cache and logs | acc-debian12 | cache 84 MB, logs 0 MB |
| PASS | No panics or crashes in the agent log | acc-debian12 | 0 panic/fatal lines, 60 error lines, service active, restarts seen 69, open files 19 |
| PASS | Disk footprint of cache and logs | acc-rocky10 | cache 84 MB, logs 0 MB |
| PASS | No panics or crashes in the agent log | acc-rocky10 | 0 panic/fatal lines, 101 error lines, service active, restarts seen 6, open files 21 |
| PASS | Disk footprint of cache and logs | acc-rocky9 | cache 84 MB, logs 1 MB |
| PASS | No panics or crashes in the agent log | acc-rocky9 | 0 panic/fatal lines, 107 error lines, service active, restarts seen 8, open files 20 |
| PASS | Disk footprint of cache and logs | acc-suse156 | cache 84 MB, logs 0 MB |
| PASS | No panics or crashes in the agent log | acc-suse156 | 0 panic/fatal lines, 87 error lines, service active, restarts seen 97, open files 21 |
| PASS | Disk footprint of cache and logs | acc-ubuntu2204 | cache 84 MB, logs 0 MB |
| PASS | No panics or crashes in the agent log | acc-ubuntu2204 | 0 panic/fatal lines, 40 error lines, service active, restarts seen 62, open files 18 |
| PASS | Disk footprint of cache and logs | acc-ubuntu2404 | cache 84 MB, logs 1 MB |
| PASS | No panics or crashes in the agent log | acc-ubuntu2404 | 0 panic/fatal lines, 120 error lines, service active, restarts seen 12, open files 20 |
| PASS | Disk footprint of cache and logs | acc-win2025 | cache 0 MB, logs 0 MB |
| PASS | No panics or crashes in the agent log | acc-win2025 | 0 panic/fatal lines, 28 error lines, service Running, restarts seen n/a, open files n/a |

### UI (23)

| Status | Test | Target | Result |
|---|---|---|---|
| PASS | Agent Downloads page lists this version |  | version 7.1.3 found in the page's download links |
| PASS | Headless browser login to the instance |  | logged in |
| PASS | Agent record renders in the UI | acc-debian12 | agent form shows the agent |
| PASS | Discovered host CI renders in the UI | acc-debian12 | CI form shows the host |
| PASS | Test check results visible in the UI | acc-debian12 | list screenshot taken |
| PASS | Agent record renders in the UI | acc-rocky10 | agent form shows the agent |
| PASS | Discovered host CI renders in the UI | acc-rocky10 | CI form shows the host |
| PASS | Test check results visible in the UI | acc-rocky10 | list screenshot taken |
| PASS | Agent record renders in the UI | acc-rocky9 | agent form shows the agent |
| PASS | Discovered host CI renders in the UI | acc-rocky9 | CI form shows the host |
| PASS | Test check results visible in the UI | acc-rocky9 | list screenshot taken |
| PASS | Agent record renders in the UI | acc-suse156 | agent form shows the agent |
| PASS | Discovered host CI renders in the UI | acc-suse156 | CI form shows the host |
| PASS | Test check results visible in the UI | acc-suse156 | list screenshot taken |
| PASS | Agent record renders in the UI | acc-ubuntu2204 | agent form shows the agent |
| PASS | Discovered host CI renders in the UI | acc-ubuntu2204 | CI form shows the host |
| PASS | Test check results visible in the UI | acc-ubuntu2204 | list screenshot taken |
| PASS | Agent record renders in the UI | acc-ubuntu2404 | agent form shows the agent |
| PASS | Discovered host CI renders in the UI | acc-ubuntu2404 | CI form shows the host |
| PASS | Test check results visible in the UI | acc-ubuntu2404 | list screenshot taken |
| PASS | Agent record renders in the UI | acc-win2025 | agent form shows the agent |
| PASS | Discovered host CI renders in the UI | acc-win2025 | CI form shows the host |
| PASS | Test check results visible in the UI | acc-win2025 | list screenshot taken |

## Notes

* acc-ubuntu2404: agent already present before the run (acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z); the install ran on top of it (upgrade path)
* acc-ubuntu2204: agent already present before the run (acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z); the install ran on top of it (upgrade path)
* acc-debian12: agent already present before the run (acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:03:47.750Z); the install ran on top of it (upgrade path)
* acc-rocky9: agent already present before the run (acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z); the install ran on top of it (upgrade path)
* acc-rocky10: agent already present before the run (acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z); the install ran on top of it (upgrade path)
* acc-suse156: agent already present before the run (acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-04T01:06:41Z); the install ran on top of it (upgrade path)
* acc-win2025: agent already present before the run (acc version 7.1.3, build dd94c9bd05a867348c700f5a8e65f4eb1112e8c0, built 2026-11-03T23:12:20Z); the install ran on top of it (upgrade path)

Generated by acctest. Secrets are redacted; host names and addresses are those of the environment the run was made in. The HTML report beside this file carries the evidence (command output, record values, log lines) for every row.
