"""Offline tests - no instance, no lab. Run with:  python -m unittest discover -s tests -v"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from acctest import agents, checks, resources  # noqa: E402
from acctest.config import Settings, TargetSpec, load_targets, parse_env_file  # noqa: E402
from acctest.report import render  # noqa: E402
from acctest.results import FAIL, PASS, SKIP, WARN, RunResult, TestResult  # noqa: E402
from acctest.runner import discovery_failure_reason  # noqa: E402
from acctest.targets import pkg_kind  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


class EnvFile(unittest.TestCase):
    def test_parse_quotes_comments_and_inline_comments(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text('# c\nA=1\nB="two words"  \nC=\'x#y\'\nD=val   # note\nexport E=5\nEMPTY=\n', encoding="utf-8")
            env = parse_env_file(p)
        self.assertEqual(env, {"A": "1", "B": "two words", "C": "x#y", "D": "val", "E": "5", "EMPTY": ""})

    def test_example_env_covers_every_setting_and_holds_no_secret(self):
        env = parse_env_file(ROOT / ".env.example")
        for key in ("SN_INSTANCE", "SN_USER", "SN_PASS", "MID_SERVER_NAME", "MID_HOST", "MID_WS_PORT", "ACC_API_KEY", "AGENT_VERSION",
                    "TARGETS_FILE", "LAB_MODE", "CPU_SAMPLE_SECONDS", "RESULTS_DIR", "BROWSER_ENABLED", "UNINSTALL_AFTER",
                    "PERF_SAMPLING", "PERF_STEP_S", "PERF_CPU_AVG_WARN_PCT", "PERF_RSS_PEAK_WARN_MB", "PERF_HOST_IMPACT_WARN_PCT"):
            self.assertIn(key, env, key)
        self.assertEqual(env["ACC_API_KEY"], "")
        self.assertIn("change-me", env["SN_PASS"])
        self.assertNotIn("service-now.com/", env["SN_INSTANCE"].replace("devNNNNNN.service-now.com", ""))

    def test_settings_defaults_and_overrides(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text("SN_INSTANCE=https://x.service-now.com/\nSN_USER=u\nSN_PASS=p\nMID_HOST=m\nCPU_TOLERANCE_PCT=2.5\nLAB_OS_LIST=a, b\n", encoding="utf-8")
            os.environ["MID_WS_PORT"] = "9900"
            try:
                s = Settings.load(p)
            finally:
                del os.environ["MID_WS_PORT"]
        self.assertEqual(s.sn_instance, "https://x.service-now.com")
        self.assertEqual(s.mid_ws_port, 9900)
        self.assertEqual(s.backend_url(), "wss://m:9900/ws/events")
        self.assertEqual(s.cpu_tolerance_pct, 2.5)
        self.assertEqual(s.lab_os_list, ["a", "b"])
        self.assertEqual(s.agent_version, "latest")

    def test_redaction_hides_secrets_only(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text("SN_PASS=secret\nACC_API_KEY=k\nACC_API_KEY_NAME=name\nTARGET_SSH_KEY=~/.ssh/id\nACC_API_KEY_AUTO_CREATE=true\n", encoding="utf-8")
            r = Settings.load(p).redacted()
        self.assertEqual(r["SN_PASS"], "***")
        self.assertEqual(r["ACC_API_KEY"], "***")
        self.assertEqual(r["ACC_API_KEY_NAME"], "name")
        self.assertEqual(r["TARGET_SSH_KEY"], "~/.ssh/id")
        self.assertEqual(r["ACC_API_KEY_AUTO_CREATE"], "true")

    def test_write_back_replaces_or_appends(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text("A=1\nACC_API_KEY=\nB=2\n", encoding="utf-8")
            s = Settings.load(p)
            s.write_back("ACC_API_KEY", "xyz")
            s.write_back("NEW", "1")
            txt = p.read_text(encoding="utf-8")
        self.assertIn('ACC_API_KEY="xyz"', txt)
        self.assertIn('NEW="1"', txt)
        self.assertEqual(txt.count("ACC_API_KEY"), 1)


class Targets(unittest.TestCase):
    def test_example_targets_load(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text(f"TARGETS_FILE={(ROOT / 'targets.example.yml').as_posix()}\nTARGET_SSH_USER=deploy\n", encoding="utf-8")
            s = Settings.load(p)
            ts = load_targets(s)
        names = [t.name for t in ts]
        self.assertIn("rhel9-app01", names)
        win = next(t for t in ts if t.name == "win2022-app01")
        self.assertEqual(win.family, "windows")
        self.assertEqual(win.expected_ci_class, "cmdb_ci_win_server")
        ub = next(t for t in ts if t.name == "ubuntu2204-web01")
        self.assertEqual(ub.user, "deploy")

    def test_pkg_kind(self):
        self.assertEqual(pkg_kind({"ID": "ubuntu"}), "deb")
        self.assertEqual(pkg_kind({"ID": "rocky", "ID_LIKE": "rhel centos fedora"}), "rpm")
        self.assertEqual(pkg_kind({"ID": "opensuse-leap", "ID_LIKE": "suse opensuse"}), "rpm")
        self.assertEqual(pkg_kind({"ID": "sles"}), "rpm")
        self.assertEqual(pkg_kind({"ID": "windows"}), "msi")
        self.assertEqual(pkg_kind({"ID": "alpine"}), "")


class Catalog(unittest.TestCase):
    def test_os_keys_build_servicenow_file_names(self):
        for key, (c, p, fam, arch) in agents.OS_KEYS.items():
            fname = f"agent-client-collector-7.1.3-{c}.{p}"
            self.assertTrue(fname.endswith(("." + p)), fname)
            self.assertIn(fam, ("linux", "windows", "macos"))
        self.assertEqual(agents.OS_KEYS["linux-x86_64-deb"][0], "ubuntu-1804_amd64")
        self.assertEqual(agents.OS_KEYS["linux-x86_64-rpm"][0], "x86_64")
        self.assertEqual(agents.OS_KEYS["windows-x86_64"][0], "windows-x64")

    def test_osmap_regex_reads_instance_script(self):
        js = "'RHEL/CentOS 7': {\n 'c': 'x86_64',\n 'p': 'rpm'\n }, 'Windows': { 'c': 'windows-x64', 'p': 'msi' }"
        found = dict((lbl, (c, p)) for lbl, c, p in agents._OSMAP_RE.findall(js))
        self.assertEqual(found["RHEL/CentOS 7"], ("x86_64", "rpm"))
        self.assertEqual(found["Windows"], ("windows-x64", "msi"))


class Checks(unittest.TestCase):
    def test_origin_classification(self):
        self.assertEqual(checks.classify_origin({"sys_scope.scope": "sn_agent", "sys_customer_update": "false"}), "oob")
        self.assertEqual(checks.classify_origin({"sys_scope.scope": "sn_acc_vis_content", "sys_customer_update": "true"}), "customized")
        self.assertEqual(checks.classify_origin({"sys_scope.scope": "global", "sys_customer_update": "true"}), "custom")
        self.assertEqual(checks.classify_origin({"sys_scope.scope": "x_avro_ops", "sys_customer_update": "false"}), "custom")

    def test_applicability_and_testability(self):
        chain = ["cmdb_ci_linux_server", "cmdb_ci_server", "cmdb_ci_computer", "cmdb_ci"]
        d = {"check_group.ci_type": "", "active": "true", "internal": False, "background": "false", "secure_params": 0, "missing_mandatory": [], "type_name": "x"}
        self.assertTrue(checks.applies_to_class(d, chain))
        self.assertFalse(checks.applies_to_class({**d, "check_group.ci_type": "cmdb_ci_win_server"}, chain))
        self.assertEqual(checks.testable(d), (True, ""))
        self.assertFalse(checks.testable({**d, "background": "true"})[0])
        self.assertFalse(checks.testable({**d, "secure_params": 1})[0])
        self.assertFalse(checks.testable({**d, "missing_mandatory": ["path"]})[0])
        self.assertFalse(checks.testable({**d, "internal": True, "type_name": "Upgrade"})[0])

    def test_judge(self):
        self.assertEqual(checks.judge({"outcome": "complete", "check_status": "0", "output": "ok"})[0], "pass")
        self.assertEqual(checks.judge({"outcome": "complete", "check_status": "2", "output": "disk 95%"})[0], "pass")
        self.assertEqual(checks.judge({"outcome": "complete", "check_status": "3", "output": "???"})[0], "warn")
        self.assertEqual(checks.judge({"outcome": "complete", "check_status": "0", "output": "sh: foo: command not found"})[0], "fail")
        self.assertEqual(checks.judge({"outcome": "timeout", "error_msg": ""})[0], "fail")

    def test_attribute_names_the_owner_of_a_failure(self):
        crlf = {"outcome": "complete", "output": "/usr/bin/env: 'ruby\\r': No such file or directory"}
        self.assertEqual(checks.attribute(crlf, "fail")[0], "content")
        self.assertEqual(checks.attribute({"outcome": "complete", "output": "/usr/bin/env: 'ruby\r': No such file"}, "fail")[0], "content")
        self.assertEqual(checks.attribute({"outcome": "complete", "output": "sh: 1: which: not found"}, "fail")[0], "target")
        self.assertEqual(checks.attribute({"outcome": "complete", "output": "bash: ifconfig: command not found"}, "fail")[0], "target")
        self.assertEqual(checks.attribute({"outcome": "complete", "output": "sh: endpoint_discovery.rb: No such file or directory"}, "fail")[0], "content")
        self.assertEqual(checks.attribute({"outcome": "complete", "output": "Error getting assets: hash of the file does not match"}, "fail")[0], "instance")
        self.assertEqual(checks.attribute({"outcome": "complete", "output": "command denied by the agent allow list"}, "fail", "custom")[0], "content")
        self.assertEqual(checks.attribute({"outcome": "complete", "output": "cat: /etc/shadow: Permission denied"}, "fail")[0], "target")
        self.assertEqual(checks.attribute({"outcome": "timeout", "output": ""}, "fail"), ("", ""))
        self.assertEqual(checks.attribute(crlf, "pass"), ("", ""))  # only failures carry a cause
        # the MID went away while the result was in flight (agent log lines) -> environment, not the agent
        mid_lost = {"outcome": "complete", "output": "[ERROR] [agent] [Connection error: websocket: close 1006 (abnormal closure)] transport receive error\n"
                    "[ERROR] [agent] [dial tcp 10.20.30.5:8800: connect: connection refused] reconnection attempt failed to the url: wss://10.20.30.5:8800/ws/events"}
        self.assertEqual(checks.attribute(mid_lost, "fail")[0], "instance")
        # a 'connection refused' from some tool a script called is NOT the MID
        self.assertEqual(checks.attribute({"outcome": "complete", "output": "curl: (7) connection refused"}, "fail"), ("", ""))
        # a Ruby crash inside a shipped module (content), reported through endpoint_discovery's error envelope
        rb = {"outcome": "complete", "output": '{"basic_inventory":{"error_backtrace":"/var/cache/servicenow/agent-client-collector/acc-f-commons/bin/command_runner.rb:56:in `runCmd\'",'
              '"error_msg":"cmd_err: /var/cache/servicenow/agent-client-collector/acc-f-modules/bin/import_commons_scripts.rb:7:in `getCommonsScriptFullPath\': wrong number of arguments (given 3, expected 4) (ArgumentError)"}}'}
        cause, hint = checks.attribute(rb, "fail")
        self.assertEqual(cause, "content")
        self.assertIn("ArgumentError", hint)


class Resources(unittest.TestCase):
    def test_cpu_limits_from_acc_yml(self):
        yml = "agent_cpu_threshold:\n  cpu_percentage_limit: 7 # x\n  repeated_high_cpu_num: 4\nmax-running-checks: 12\n"
        lim = resources.cpu_limits(yml)
        self.assertEqual(lim["cpu_percentage_limit"], 7)
        self.assertEqual(lim["repeated_high_cpu_num"], 4)
        self.assertEqual(lim["max_running_checks"], 12)
        self.assertTrue(lim["present"])
        self.assertFalse(lim["disabled"])
        self.assertEqual(resources.cpu_limits("")["cpu_percentage_limit"], 5)

    def test_parse_kv(self):
        self.assertEqual(resources.parse_kv("A=1\nB=x=y\nnoeq\n"), {"A": "1", "B": "x=y"})

    def test_sampler_scripts_format(self):
        s = resources.LINUX_SAMPLER % {"dur": 30, "step": 5}
        self.assertIn("DUR=30", s)
        self.assertIn("date +%s", s)


class Runtimes(unittest.TestCase):
    def test_inspect_synthetic_deb(self):
        import gzip, io, tarfile, tempfile
        from acctest import runtimes
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tf:
            def add(name, data):
                ti = tarfile.TarInfo(name); ti.size = len(data); tf.addfile(ti, io.BytesIO(data))
            add("./usr/share/servicenow/agent-client-collector/embedded/lib/libruby.so.3.3.13", b"\x7fELF junk ruby 3.3.13 (2026-10-23 revision af48f08f21) [x86_64-linux] more")
            add("./usr/share/servicenow/agent-client-collector/embedded/lib/libcrypto.so.3", b"\x7fELF OpenSSL 3.5.9 29 Sep 2026 built on")
            add("./usr/share/servicenow/agent-client-collector/embedded/lib/ruby/gems/3.3.0/specifications/default/rexml-3.4.4.gemspec", b"spec")
            add("./usr/share/servicenow/agent-client-collector/embedded/lib/ruby/gems/3.3.0/gems/resolv-0.3.2/lib/resolv.rb", b"rb")
        data_tgz = gzip.compress(buf.getvalue())

        def ar_entry(name, data):
            hdr = f"{name:<16}{'0':<12}{'0':<6}{'0':<6}{'100644':<8}{len(data):<10}`\n".encode()
            return hdr + data + (b"\n" if len(data) % 2 else b"")
        deb = b"!<arch>\n" + ar_entry("debian-binary", b"2.0\n") + ar_entry("control.tar.gz", gzip.compress(b"")) + ar_entry("data.tar.gz", data_tgz)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "agent-client-collector-9.9.9-ubuntu-1804_amd64.deb"
            p.write_bytes(deb)
            rt = runtimes.inspect_deb(p)
        self.assertEqual(rt.error, "")
        self.assertEqual((rt.ruby, rt.ruby_date, rt.openssl, rt.openssl_date, rt.ruby_api), ("3.3.13", "2026-10-23", "3.5.9", "29 Sep 2026", "3.3.0"))
        self.assertEqual(rt.gems, {"rexml": "3.4.4", "resolv": "0.3.2"})
        self.assertIn("Ruby 3.3.13", rt.summary())

    def test_inspect_rejects_non_deb(self):
        import tempfile
        from acctest import runtimes
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.deb"; p.write_bytes(b"not an archive")
            self.assertTrue(runtimes.inspect_deb(p).error)


class Fixtures(unittest.TestCase):
    def test_plugin_archive_is_clean_and_executable(self):
        import tarfile, tempfile
        from acctest import fixtures
        with tempfile.TemporaryDirectory() as d:
            p = fixtures.build_plugin(Path(d))
            self.assertEqual(p.name, "acctest-scripts.tar.gz")
            with tarfile.open(p) as tf:
                members = {m.name: m for m in tf.getmembers()}
                self.assertIn("bin/acctest_users.sh", members)
                self.assertIn("bin/acctest_users.ps1", members)
                self.assertIn("bin/acctest_users.cmd", members)
                self.assertIn("allow_list/check-allow-list.json", members)
                self.assertEqual(members["bin/acctest_users.sh"].mode & 0o111, 0o111, "scripts must be executable")
                sh = tf.extractfile("bin/acctest_users.sh").read()
                self.assertTrue(sh.startswith(b"#!/bin/sh\n"), "LF shebang - the exact defect the Visibility content has")
                self.assertNotIn(b"\r", sh)
                cmd = tf.extractfile("bin/acctest_users.cmd").read()
                self.assertIn(b"\r\n", cmd)
                allow = json.loads(tf.extractfile("allow_list/check-allow-list.json").read())
                self.assertEqual({e["exec"] for e in allow}, {"acctest_users.sh", "acctest_users.cmd", "acctest_users.ps1"})
                for m in members.values():
                    self.assertFalse(m.name.startswith("._") or "/._" in m.name)
        # every fixture command is allow-listed
        for f in fixtures.FIXTURES.values():
            if f["assets_from"] == fixtures.ASSET_NAME:
                self.assertIn(f["command"].split()[0], {e["exec"] for e in allow})

    def test_signing_wraps_the_archive_the_way_the_agent_expects(self):
        import base64, shutil, subprocess, tarfile, tempfile, zipfile
        from acctest import fixtures
        if not shutil.which("openssl"):
            self.skipTest("openssl not on PATH")
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            key, cert = d / "k.pem", d / "c.pem"
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", str(key), "-out", str(cert), "-subj", "/CN=t", "-days", "2"],
                           check=True, capture_output=True, env={**os.environ, "MSYS_NO_PATHCONV": "1"})
            inner = fixtures.build_plugin(d)
            outer = fixtures.sign_plugin(inner, key)
            with tarfile.open(outer) as tf:
                names = tf.getnames()
                self.assertEqual(sorted(names), ["acctest-scripts.sig", "acctest-scripts.tar.gz"])
                sig = base64.b64decode(tf.extractfile("acctest-scripts.sig").read())
                (d / "sig.bin").write_bytes(sig)
                self.assertEqual(tf.extractfile("acctest-scripts.tar.gz").read(), inner.read_bytes())
            pub = d / "pub.pem"
            pub.write_bytes(subprocess.run(["openssl", "x509", "-in", str(cert), "-pubkey", "-noout"], check=True, capture_output=True).stdout)
            v = subprocess.run(["openssl", "dgst", "-sha256", "-verify", str(pub), "-signature", str(d / "sig.bin"), str(inner)], capture_output=True, text=True)
            self.assertIn("Verified OK", v.stdout)
            z = fixtures.build_cert_zip(cert, d)
            self.assertRegex(z.name, r"^acctest-customer-certs-[0-9a-f]{12}\.zip$")
            with zipfile.ZipFile(z) as zf:
                self.assertEqual(len(zf.namelist()), 1)
                self.assertTrue(zf.namelist()[0].endswith("/c.pem"))

    def test_verify_output_judges_the_script_result(self):
        from acctest import fixtures
        good = ("ACCTEST_USERS v1 os=linux host=web01 user=servicenow\n"
                '{"user":"root","uid":0,"gid":0,"home":"/root","shell":"/bin/bash","groups":["root"],"admin":true}\n'
                '{"user":"app","uid":1001,"gid":1001,"home":"/home/app","shell":"/bin/sh","groups":["app","sudo"],"admin":true}\n'
                "ACCTEST_USERS end count=2\n")
        ok, why = fixtures.verify_output("acctest-users-linux", good, {"HOST": "web01"})
        self.assertTrue(ok, why)
        self.assertIn("2 users, 2 admin(s)", why)
        self.assertFalse(fixtures.verify_output("acctest-users-linux", good.replace("count=2", "count=5"))[0])
        self.assertFalse(fixtures.verify_output("acctest-users-linux", good.replace('"user":"root"', '"user":"toor"'))[0])
        self.assertFalse(fixtures.verify_output("acctest-users-linux", "garbage")[0])
        self.assertFalse(fixtures.verify_output("acctest-users-linux", good, {"HOST": "other"})[0])
        win = ('ACCTEST_USERS v1 os=windows host=WIN1 user=SYSTEM\n{"user":"Administrator","sid":"S-1-5-21-1-500","enabled":true,'
               '"password_required":true,"last_logon":null,"groups":["Administrators"],"admin":true}\nACCTEST_USERS end count=1\n')
        self.assertTrue(fixtures.verify_output("acctest-users-windows", win, {"HOST": "win1"})[0])
        self.assertEqual(fixtures.verify_output("not-a-fixture", "x"), (True, ""))
        # the OS-version fixture reuses a shipped module: data is a pass, the content's own error envelope is not
        self.assertTrue(fixtures.verify_output("acctest-custom-os-version", '{"basic_inventory":{"os":"Linux Rocky","os_version":"9.4"}}')[0])
        self.assertFalse(fixtures.verify_output("acctest-custom-os-version", "")[0])
        ok, why = fixtures.verify_output("acctest-custom-os-version",
                                         '{"basic_inventory":{"error_backtrace":"x.rb:1","error_msg":"cmd_err: import_commons_scripts.rb:7: wrong number of arguments (given 3, expected 4) (ArgumentError)"}}')
        self.assertFalse(ok)
        self.assertIn("wrong number of arguments", why)


class Verdict(unittest.TestCase):
    def test_agent_verdict_ignores_environment_failures(self):
        run = RunResult(version="7.1.3", instance="i", mid_server="m", backend_url="b")
        run.add(TestResult(id="a", name="Install", section="Install", status=PASS, target="t1"))
        run.add(TestResult(id="b", name="CRLF plugin", section="Checks", status=FAIL, target="t1", cause="content"))
        run.add(TestResult(id="c", name="which missing", section="Discovery", status=FAIL, target="t1", cause="target"))
        self.assertEqual(run.agent_verdict(), PASS)
        self.assertEqual(len(run.env_failures()), 2)
        run.add(TestResult(id="d", name="panic", section="Cleanup", status=FAIL, target="t1", cause="agent"))
        self.assertEqual(run.agent_verdict(), FAIL)
        run2 = RunResult(version="1", instance="i", mid_server="m", backend_url="b")
        run2.add(TestResult(id="a", name="x", section="Install", status=PASS))
        run2.add(TestResult(id="e", name="unknown", section="Checks", status=FAIL))   # unattributed counts against the agent
        self.assertEqual(run2.agent_verdict(), FAIL)
        html = render(run)
        self.assertIn("Agent verdict", html)
        self.assertIn("Environment findings", html)
        self.assertIn("NOT SAFE", html)

    def test_components_from_package(self):
        from acctest import runtimes
        rt = runtimes.Runtimes(package="agent-client-collector-7.1.3-ubuntu-1804_amd64.deb", ruby="3.3.13", ruby_date="2026-10-23",
                               openssl="3.5.9", openssl_date="29 Sep 2026", ruby_api="3.3.0", all_gems={"rexml": "3.4.4"}, libs={"libyaml": "0.2.5"}, go_version="1.24.3")
        rows = rt.components()
        names = [r["component"] for r in rows]
        self.assertEqual(rows[0]["version"], "7.1.3")
        for n in ("Go runtime (acc binary)", "Ruby (embedded)", "OpenSSL (embedded)", "libyaml", "gem rexml"):
            self.assertIn(n, names)


class Perf(unittest.TestCase):
    def _csv(self):
        # 100 ticks/s, 4 cores -> host total advances 400 ticks per second. Rows every 5 s: idle 0-60 s (agent 0 ticks,
        # host 2% busy), discovery 60-120 s (agent 150 ticks per 5 s = 30% of one core, host 12% busy), checks 120-180 s.
        rows, total, idle, at, rb = [], 0, 0, 0, 0
        for k in range(0, 37):
            t = k * 5
            if k:
                busy = 0.02 if t <= 60 else 0.12
                total += 2000
                idle += int(2000 * (1 - busy))
                if t > 60:
                    at += 150
                    rb += 1 << 20
            rss = 60000 if t <= 60 else 90000
            rows.append(f"{1000 + t},{total},{idle},0.5,8000000,6000000,{at},{rss},15,40,{1 if t <= 60 else 3},{rb},0,1")
        return "\n".join(rows)

    def test_analyze_phases_and_impact(self):
        from acctest import perf
        marks = [("idle", 1000), ("discovery", 1060), ("checks", 1120)]
        a = perf.analyze(self._csv(), marks, tck=100, ncpu=4, t_end=1180)
        self.assertEqual(a["samples"], 37)
        ph = {p["phase"]: p for p in a["phases"]}
        self.assertEqual(ph["idle"]["agent_cpu_avg"], 0)
        self.assertAlmostEqual(ph["discovery"]["agent_cpu_avg"], 30.0, places=1)
        self.assertAlmostEqual(ph["discovery"]["agent_share_avg"], 7.5, places=1)
        self.assertEqual(ph["discovery"]["agent_rss_peak_mb"], 88)
        self.assertAlmostEqual(ph["idle"]["host_busy_avg"], 2.0, places=1)
        self.assertAlmostEqual(ph["checks"]["host_busy_avg"], 12.0, places=1)
        self.assertEqual(ph["checks"]["agent_read_mb"], 12)
        self.assertAlmostEqual(a["impact"]["host_busy_delta"], 10.0, places=1)
        self.assertEqual(a["impact"]["load"]["agent_procs_max"], 3)
        self.assertIn("host impact", perf.describe(a))
        self.assertTrue(a["io_readable"])
        # scripts are fully expanded
        s = perf.start_script(5)
        self.assertNotIn("__", s.replace("__DIR__", "").replace("__SCRIPT__", "").replace("__STEP__", "") if False else s.replace("ACCTEST_SAMPLER_EOF", ""))
        self.assertIn("/tmp/acctest-perf/sampler.sh 5 ", s)
        self.assertIn("---CSV---", perf.stop_script())
        w = perf.start_script(7, "windows")
        self.assertIn("sampler.ps1`\" 7 ", w)
        self.assertNotIn("__STEP__", w)
        self.assertIn("Win32_PerfRawData_PerfOS_Processor", w)
        self.assertIn("'@", w)              # the here-string closes
        self.assertIn("---CSV---", perf.stop_script("windows"))

    def test_analyze_handles_garbage_and_exited_children(self):
        from acctest import perf
        a = perf.analyze("junk\n1,2\n", [("idle", 0)], 100, 1, 10)
        self.assertEqual(a["samples"], 0)
        self.assertEqual(perf.describe(a), "no samples")
        # a child exiting makes the tree counters drop: the delta is clamped, never negative
        csv_text = "100,1000,900,0,1,1,500,1000,1,1,2,0,0,1\n105,1500,1350,0,1,1,200,800,1,1,1,0,0,1"
        a = perf.analyze(csv_text, [("idle", 100)], 100, 1, 105)
        self.assertEqual(a["overall"]["agent_cpu_avg"], 0)


class Report(unittest.TestCase):
    def test_render_contains_failures_and_matrix(self):
        run = RunResult(version="7.1.3", instance="https://x", mid_server="m", backend_url="wss://m:8800/ws/events", title="T")
        run.targets = [{"name": "t1", "os": "linux-x86_64-deb", "transport": "ssh", "host": "h"}]
        run.add(TestResult(id="a", name="Install", section="Install", status=PASS, target="t1", message="ok"))
        run.add(TestResult(id="b", name="Disco", section="Discovery", status=FAIL, target="t1", message="boom", details="trace <x>"))
        run.add(TestResult(id="c", name="Skip", section="Checks", status=SKIP, target="t1", message="n/a"))
        run.add(TestResult(id="d", name="Warn", section="Resources", status=WARN, target="t1", message="hm"))
        run.add(TestResult(id="e", name="Plugins", section="Resources", status=FAIL, target="t1", message="crlf", cause="content"))
        html = render(run)
        self.assertIn("What failed", html)
        self.assertIn("boom", html)
        self.assertIn("Whose fault is it?", html)
        self.assertIn("Instance content: 1", html)
        self.assertIn("Not attributed: 1", html)
        self.assertEqual(run.causes(), {"": 1, "content": 1})
        self.assertIn("&lt;x&gt;", html)
        self.assertIn("t1", html)
        self.assertEqual(run.overall(), FAIL)
        self.assertEqual(run.counts()[PASS], 1)
        self.assertIn("prefers-color-scheme", html)

    def test_markdown_report(self):
        from acctest.report import render_markdown
        run = RunResult(version="7.1.3", instance="https://x", mid_server="m", backend_url="b", title="T")
        run.targets = [{"name": "t1", "os": "linux-x86_64-deb", "transport": "ssh", "host": "h", "distro": "Ubuntu 24.04"}]
        run.add(TestResult(id="a", name="Install", section="Install", status=PASS, target="t1", message="ok | fine"))
        run.add(TestResult(id="b", name="Plugins", section="Resources", status=FAIL, target="t1", message="crlf", cause="content"))
        run.components = [{"component": "gem rexml", "version": "3.4.4", "kind": "Ruby gem", "source": "gems", "target": "t1"},
                          {"component": "gem rexml", "version": "3.4.4", "kind": "Ruby gem", "source": "gems", "target": ""}]
        run.perf = [{"target": "t1", "distro": "Ubuntu 24.04", "ncpu": 2, "samples": 3, "step_s": 5, "phases": [
            {"phase": "idle", "samples": 2, "duration_s": 10, "agent_cpu_avg": 0.1, "agent_cpu_peak": 0.4, "agent_share_avg": 0.05, "agent_rss_avg_mb": 42,
             "agent_rss_peak_mb": 42, "agent_procs_max": 1, "agent_threads_max": 9, "agent_fds_max": 19, "agent_read_mb": 0, "agent_write_mb": 0,
             "host_busy_avg": 15.5, "host_busy_peak": 27.6, "load1_max": 4.57, "host_mem_delta_mb": 1}],
            "impact": {"load": {"samples": 0, "duration_s": 0}, "idle": {}, "host_busy_delta": None}, "overall": {"samples": 0, "duration_s": 0}}]
        md = render_markdown(run)
        self.assertIn("# T - agent 7.1.3", md)
        self.assertIn("Agent verdict: SAFE", md)
        self.assertIn("| ok \\| fine |", md)            # pipes in a message cannot break the table
        self.assertIn("| gem rexml | `3.4.4` | Ruby gem | gems | package, t1 |", md)   # one row per distinct component
        self.assertIn("| idle | 10 | 0.1% / 0.4% |", md)
        self.assertIn("Environment findings", md)
        self.assertIn("Instance content", md)

    def test_json_roundtrip(self):
        run = RunResult(version="1", instance="i", mid_server="m", backend_url="b")
        run.add(TestResult(id="a", name="n", section="Install", status=PASS))
        d = run.to_dict()
        self.assertEqual(d["overall"], PASS)
        json.dumps(d)


class Runner(unittest.TestCase):
    def test_discovery_failure_reason_picks_asset_error(self):
        log = "x [INFO] fine\ny [ERROR] [agent] error getting assets for check: could not validate downloaded asset acc-f-commons: hash of the file does not match expected hash abc\nz [INFO] later"
        self.assertIn("hash of the file does not match", discovery_failure_reason(log))
        self.assertEqual(discovery_failure_reason("only [INFO] lines"), "")


class Hygiene(unittest.TestCase):
    def test_signing_keys_never_leave_the_state_directory(self):
        gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/.state/", gi, "the lab signing key lives in .state/ - it must stay ignored")
        for p in ROOT.rglob("*.key"):
            self.assertIn(".state", p.parts, f"private key outside .state: {p}")
        for p in (ROOT / "acctest").rglob("*"):
            self.assertNotIn(p.suffix, (".key", ".pem", ".cer", ".crt"), f"certificate material inside the package: {p}")

    def test_gitignore_protects_env_and_targets(self):
        gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pat in ("/.env", "/targets.yml", "/dist/*", "/results/*"):
            self.assertIn(pat, gi)
        self.assertIn("!/.env.example", gi)

    def test_no_instance_specific_values_in_committed_files(self):
        """Committed sources must not carry the real instance name, credentials, API key or lab addresses. The values are
        read from the local, git-ignored .env and targets.yml - so this test never spells them out itself; without those
        files (a fresh clone) it only checks the generic placeholders."""
        import re as _re
        bad: set[str] = set()
        env = ROOT / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if "=" not in line or line.lstrip().startswith("#"):
                    continue
                k, v = line.split("=", 1)
                v = v.split(" #")[0].strip().strip("'\"")
                if k.strip() in ("SN_INSTANCE", "SN_USER", "SN_PASS", "ACC_API_KEY", "MID_SERVER_NAME", "PVE_HOST", "MID_HOST") and len(v) >= 5:
                    bad.add(v)
                    host = _re.sub(r"^https?://", "", v).split("/")[0].split(".")[0]
                    if len(host) >= 5:
                        bad.add(host)  # the bare instance name, e.g. devNNNNNN
        tg = ROOT / "targets.yml"
        if tg.exists():
            bad.update(_re.findall(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3})\.\d{1,3}\b", tg.read_text(encoding="utf-8")))  # lab /24 prefixes
        bad -= {"admin", "https", "localhost"}
        files = (list((ROOT / "acctest").rglob("*.py")) + list((ROOT / "acctest").rglob("*.sh")) + list((ROOT / "acctest").rglob("*.ps1"))
                 + list((ROOT / "tests").glob("*.py")) + [ROOT / ".env.example", ROOT / "targets.example.yml", ROOT / "README.md", ROOT / "NOTICE.md", ROOT / "acctest.py"])
        for f in files:
            if not f.exists():
                continue
            txt = f.read_text(encoding="utf-8")
            for b in sorted(bad):
                self.assertNotIn(b, txt, f"a value from .env / targets.yml found in {f.name}")


if __name__ == "__main__":
    unittest.main()
