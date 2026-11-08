"""The qualification run: one agent version against every target, producing a RunResult for result.html.

Order per target: probe -> install -> service/config on the host -> agent Up on the instance (through the MID) ->
discovery -> check definitions -> policies -> CPU/cleanup on the host -> UI screenshots -> optional uninstall.
Every observation becomes a TestResult; nothing is inferred - every status comes from a command on the target or a
record on the instance.
"""
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path

from . import agents, checks, discovery, fixtures, mid as midmod, perf, resources, runtimes
from .browser import Browser
from .config import Settings, TargetSpec, load_targets
from .installer import Installer
from .report import write_report
from .results import ERROR, FAIL, PASS, SKIP, WARN, RunResult, TestResult, Timer
from .snow import SNClient, SNError
from .targets import distro_label, make_transport, pkg_kind, probe
from .util import iso_now, safe_name, sn_now

LOG = logging.getLogger("acctest.runner")
KEEPALIVE_ID = re.compile(r"\[keepalive\] \[agent\] \[([0-9a-f]{12,32})\]")


class Runner:
    def __init__(self, settings: Settings, version: str | None = None, install_mode: str = "package",
                 skip_install: bool = False, only_targets: list[str] | None = None):
        self.s = settings
        settings.require("SN_INSTANCE", "SN_USER", "SN_PASS", "MID_SERVER_NAME", "MID_HOST")
        self.sn = SNClient(settings.sn_instance, settings.sn_user, settings.sn_pass, settings.sn_verify_tls, settings.sn_timeout_s)
        self.version_req = version or settings.agent_version
        self.install_mode = install_mode
        self.skip_install = skip_install
        self.only_targets = only_targets
        self.run: RunResult | None = None
        self.out_dir: Path | None = None
        self.basename = "result" if not only_targets else "result-partial-" + time.strftime("%Y%m%d-%H%M")
        self.catalog: agents.AgentCatalog | None = None
        self.api_key = ""
        self.backend_url = settings.backend_url()
        self._facts: dict[str, dict] = {}   # probe facts per target name (host, ip, distro ...)
        self._env: dict[str, dict] = {}     # environment prerequisites per target name
        self._perf: dict[str, perf.PerfSession | None] = {}   # running performance sampler per target name

    # ---- helpers -------------------------------------------------------------------------------------------------
    def _add(self, section: str, rid: str, name: str, status: str, message: str = "", details: str = "", target: str = "",
             evidence: dict | None = None, timer: Timer | None = None, screenshot: str = "", cause: str = "") -> TestResult:
        if self.api_key:  # the installer echoes the key; the report is shared, so it never carries it
            message = message.replace(self.api_key, "***")
            details = (details or "").replace(self.api_key, "***")
        r = TestResult(id=f"{section.lower().replace(' ', '-')}.{rid}", name=name, section=section, status=status, target=target,
                       message=message, details=(details or "")[:20000], evidence=evidence or {}, screenshot=screenshot,
                       cause=cause if status in (FAIL, ERROR) else "", duration_s=timer.seconds() if timer else 0.0)
        self.run.add(r)
        icon = {PASS: "ok  ", FAIL: "FAIL", WARN: "warn", SKIP: "skip", ERROR: "ERR "}[status]
        LOG.info("[%s] %s%s: %s", icon, f"{target} " if target else "", name, message[:160])
        return r

    def _snapshot(self):
        if self.run and self.out_dir:
            self.run.finished = iso_now()
            write_report(self.run, self.out_dir, self.basename)

    # ---- pre-flight ----------------------------------------------------------------------------------------------
    def preflight(self, run: RunResult) -> bool:
        self.run = run
        ok = True
        t = Timer()
        try:
            info = self.sn.instance_info()
            run.build = info["build"]
            who = self.sn.whoami()
            self._add("Pre-flight", "instance", "Instance reachable with the configured user", PASS,
                      f"{info['instance']} build {info['build'].replace('glide-', '').replace('.zip', '')}, user {who.get('user_name', self.s.sn_user)}", timer=t)
        except Exception as e:
            self._add("Pre-flight", "instance", "Instance reachable with the configured user", FAIL, str(e), timer=t)
            return False
        t = Timer()
        app = self.sn.first("sys_scope", "scope=sn_agent", "name,version")
        if app:
            run.app_version = app["version"]
            self._add("Pre-flight", "acc-app", "Agent Client Collector Framework installed", PASS, f"{app['name']} {app['version']}", timer=t)
        else:
            self._add("Pre-flight", "acc-app", "Agent Client Collector Framework installed", FAIL, "scope sn_agent not found", timer=t)
            ok = False
        t = Timer()
        vis = self.sn.first("sys_scope", "scope=sn_acc_vis_content", "name,version")
        if vis and vis.get("version"):
            self._add("Pre-flight", "vis-app", "ACC Visibility content installed (discovery checks)", PASS, f"{vis['name']} {vis['version']}", timer=t)
        else:
            self._add("Pre-flight", "vis-app", "ACC Visibility content installed (discovery checks)", WARN,
                      "scope sn_acc_vis_content missing or still installing - only the framework's basic discovery check is available", timer=t)
        t = Timer()
        try:
            st = midmod.ensure_listener(self.sn, self.s)
            m = st["mid"]
            self.backend_url = st["endpoint_url"] or self.backend_url
            self._add("Pre-flight", "mid", "MID Server up, validated, ACC listener started", PASS,
                      f"{m['name']} ({m['ip_address']}, {m['version'].split('__')[0] if m.get('version') else ''}) endpoint {self.backend_url} [{st['action']}]",
                      evidence={"webserver": st["webserver"], "endpoint": st["endpoint"]}, timer=t)
        except SNError as e:
            self._add("Pre-flight", "mid", "MID Server up, validated, ACC listener started", FAIL, str(e), timer=t)
            ok = False
        run.backend_url = self.backend_url
        t = Timer()
        try:
            k = midmod.ensure_api_key(self.sn, self.s)
            self.api_key = k["key"]
            self._add("Pre-flight", "api-key", "ACC API key available", PASS, f"{k['name']} [{k['action']}]", timer=t)
        except SNError as e:
            self._add("Pre-flight", "api-key", "ACC API key available", FAIL, str(e), timer=t)
            ok = False
        t = Timer()
        try:
            a = midmod.assets_state(self.sn, self.s.mid_server_name)
            if a["stale"] and self.s.mid_auto_configure:
                res = midmod.sync_plugins(self.sn, self.s.mid_server_name)
                a = midmod.assets_state(self.sn, self.s.mid_server_name)
                self._add("Pre-flight", "plugin-cache", "MID serves the current ACC plugin assets", PASS if res.get("restart", {}).get("restarted") else WARN,
                          f"assets changed {a['assets_changed']} after the MID started - MID restarted ({res.get('restart')}); listener ready {res.get('listener_ready')}", timer=t)
            elif a["stale"]:
                self._add("Pre-flight", "plugin-cache", "MID serves the current ACC plugin assets", WARN,
                          f"ACC assets changed at {a['assets_changed']} but the MID started {a['mid_started']}: agents may fail with ACC-1500 "
                          "(hash mismatch) until the MID is restarted - run `mid sync` or set MID_AUTO_CONFIGURE=true", timer=t)
            else:
                self._add("Pre-flight", "plugin-cache", "MID serves the current ACC plugin assets", PASS,
                          f"{a['asset_count']} plugin assets, newest {a['assets_changed']}, MID started {a['mid_started']}", timer=t)
        except SNError as e:
            self._add("Pre-flight", "plugin-cache", "MID serves the current ACC plugin assets", WARN, str(e), timer=t)
        # custom plugin signing: the fixture plugin is signed; the agents must be able to validate the signer
        t = Timer()
        try:
            key, cert = fixtures.signing_material(self.s)
            import subprocess
            subj = subprocess.run(["openssl", "x509", "-in", str(cert), "-noout", "-subject", "-issuer", "-enddate"], capture_output=True, text=True).stdout.strip().replace("\n", "; ")
            anchor = fixtures.trust_anchor(self.s)
            _, certzip, _ = fixtures.signed_plugin(self.s)
            served, where = midmod.customer_cert_served(self.s, certzip.name)
            self._add("Pre-flight", "signing", "Custom plugin signing certificate published to the agents", PASS if served else WARN,
                      f"signer {subj}; trust anchor {anchor.name}" + (f" (installed on targets at install time)" if self.s.trust_signing_cert_on_targets else " (must already be trusted by the hosts)")
                      + f"; certificate zip {'served by the MID' if served else 'NOT served by the MID - custom plugins will be refused'} ({where})",
                      timer=t, evidence={"certificate": str(cert), "anchor": str(anchor), "zip": certzip.name, "mid_dir": midmod.customer_cert_dir(self.s) or "<MID home>/agent/static/cert/customer"},
                      cause="" if served else "instance")
        except Exception as e:
            self._add("Pre-flight", "signing", "Custom plugin signing certificate published to the agents", WARN, f"could not prepare signing material: {e}", timer=t)
        t = Timer()
        targets = self.targets()
        if targets:
            self._add("Pre-flight", "targets", "Targets defined", PASS, ", ".join(f"{x.name} ({x.os}, {x.transport})" for x in targets), timer=t)
        else:
            self._add("Pre-flight", "targets", "Targets defined", FAIL, f"no targets in {self.s.targets_file} (home: `lab provision`; company: fill targets.yml)", timer=t)
            ok = False
        return ok

    def targets(self) -> list[TargetSpec]:
        ts = [t for t in load_targets(self.s) if not t.skip]
        if self.only_targets:
            ts = [t for t in ts if t.name in self.only_targets or t.os in self.only_targets]
        return ts

    # ---- packages ------------------------------------------------------------------------------------------------
    def packages(self) -> bool:
        t = Timer()
        try:
            self.catalog = agents.read_catalog(self.sn, self.version_req)
        except SNError as e:
            self._add("Packages", "catalog", "Agent version and package list read from the instance", FAIL, str(e), timer=t)
            return False
        cat = self.catalog
        self.run.version = cat.version
        self._add("Packages", "catalog", "Agent version and package list read from the instance", PASS,
                  f"agent {cat.version} (app {cat.app_version}), {len(cat.packages)} packages, OS map {sorted(cat.os_map)}", timer=t,
                  evidence={"base_url": cat.base_url, "dev_mode": cat.dev_mode})
        wanted = sorted({x.os for x in self.targets()} | {"windows-x86_64", "linux-x86_64-deb", "linux-x86_64-rpm"})
        t = Timer()
        if self.s.agent_download:
            try:
                manifest = agents.download_catalog(cat, self.s.agent_download_dir, wanted)
            except Exception as e:
                self._add("Packages", "download", "Packages downloaded into dist/", FAIL, str(e), timer=t)
                return False
        else:
            mp = self.s.agent_download_dir / safe_name(cat.version) / "manifest.json"
            manifest = json.loads(mp.read_text()) if mp.exists() else {"files": []}
        self.run.packages = manifest.get("files", [])
        got = [f for f in self.run.packages if f.get("downloaded")]
        missing = [f["file"] for f in self.run.packages if f.get("os_key") in wanted and not f.get("downloaded")]
        self._add("Packages", "download", "Packages downloaded into dist/", PASS if not missing else WARN,
                  f"{len(got)} files in {self.s.agent_download_dir / safe_name(cat.version)}" + (f"; not available: {missing}" if missing else ""), timer=t)
        # what runs inside the package: the embedded Ruby / OpenSSL are what a CVE question is really about
        deb = runtimes.find_deb(self.s.agent_download_dir, safe_name(cat.version))
        if deb:
            t = Timer()
            rt = runtimes.inspect_deb(deb)
            self.run.runtimes = rt.to_dict()
            self.run.components = [dict(c, target="") for c in rt.components()]
            self._add("Packages", "runtimes", "Embedded runtimes read from the package", PASS if not rt.error else WARN, rt.summary(), timer=t,
                      evidence={"package": deb.name, "ruby": rt.ruby, "ruby_date": rt.ruby_date, "openssl": rt.openssl, "openssl_date": rt.openssl_date, **{f"gem {k}": v for k, v in rt.gems.items()}})
        need = [x for x in self.targets() if not agents.local_package(self.s.agent_download_dir, cat.version, x.os)]
        if need and self.install_mode == "package":
            self._add("Packages", "coverage", "A package exists for every target OS", FAIL,
                      "no package for: " + ", ".join(f"{x.name} ({x.os})" for x in need))
        else:
            self._add("Packages", "coverage", "A package exists for every target OS", PASS, "all target OS keys covered")
        self._snapshot()
        return True

    # ---- environment: what the HOST brings, recorded before the agent touches it ---------------------------------------
    def environment(self, spec: TargetSpec, tr) -> None:
        """Prerequisites of the server. Nothing here is the agent's fault, so everything is WARN/PASS with cause 'target';
        it is what lets a later failure be blamed on the right party."""
        name = spec.name
        t = Timer()
        env = resources.environment(tr, spec.family)
        f, tools = env["facts"], env["tools"]
        self._env[name] = env
        missing = sorted(k for k, v in tools.items() if v == "MISSING")
        if spec.family == "linux":
            impact = [f"{k}: {resources.LINUX_TOOL_IMPACT[k]}" for k in missing if k in resources.LINUX_TOOL_IMPACT]
            self._add("Environment", "tools", "Host tools the agent content relies on", PASS if not impact else WARN,
                      ("all present" if not missing else f"missing {', '.join(missing)}") + (" - " + "; ".join(impact) if impact else ""),
                      target=name, evidence=tools, timer=t, cause="" if not impact else "target")
            rules = int(f.get("SUDO_RULES", "0") or 0)
            self._add("Environment", "sudo", "sudo rules for the servicenow user", PASS if rules else WARN,
                      f"{rules} rule(s) for servicenow" + ("" if rules else " - serial numbers, sudo osquery/ss and agent self-upgrade will not work (expected on a fresh server)")
                      + (f"; requiretty set in {f.get('SUDO_REQUIRETTY')} file(s)" if (f.get("SUDO_REQUIRETTY") or "0") != "0" else ""),
                      target=name, cause="" if rules else "target")
            self._add("Environment", "resources", "Disk, memory and CPU available", PASS,
                      f"/var {f.get('DISK_VAR_MB')} MB free, /tmp {f.get('DISK_TMP_MB')} MB free, {f.get('MEM_FREE_MB')} MB RAM available, {f.get('NPROC')} cpu"
                      + (f", SELinux {f.get('SELINUX')}" if f.get("SELINUX") else "") + (f", firewall: {f.get('FIREWALL')}" if f.get("FIREWALL") not in (None, "", "none") else "")
                      + (f", container: {f.get('CONTAINER')}" if f.get("CONTAINER") else ""), target=name, evidence=f)
        else:
            admin = (f.get("IS_ADMIN") or "").lower() == "true"
            self._add("Environment", "tools", "PowerShell, msiexec and administrator rights", PASS if admin and "MISSING" not in tools.values() else WARN,
                      f"PowerShell {f.get('PS_VERSION')}, execution policy {f.get('EXEC_POLICY')}, administrator {f.get('IS_ADMIN')}" + (f", missing {', '.join(missing)}" if missing else ""),
                      target=name, evidence={**tools, **f}, timer=t, cause="" if admin else "target")
            self._add("Environment", "resources", "Disk, memory and CPU available", PASS,
                      f"C: {f.get('DISK_C_MB')} MB free, {f.get('MEM_FREE_MB')} MB RAM free, {f.get('NPROC')} cpu, firewall profiles on: {f.get('FIREWALL')}, Defender real-time {f.get('DEFENDER')}",
                      target=name, evidence=f)

    # ---- per target ----------------------------------------------------------------------------------------------
    def target(self, spec: TargetSpec, browser: Browser | None) -> None:
        name = spec.name
        tr = make_transport(spec, self.s)
        t = Timer()
        facts = probe(tr, spec.family)
        if facts.get("_rc", 1) != 0 or not facts.get("ID"):
            self._add("Install", "reach", "Target reachable", FAIL, f"{tr.describe()}: {facts.get('_err') or 'probe returned nothing'}", target=name, timer=t)
            return
        spec.distro = distro_label(facts)
        kind = pkg_kind(facts)
        self._facts[name] = facts
        self._add("Install", "reach", "Target reachable", PASS, f"{tr.describe()} - {spec.distro}, {facts.get('ARCH')}, {facts.get('NPROC')} cpu, {facts.get('MEM_MB')} MB",
                  target=name, evidence={k: v for k, v in facts.items() if not k.startswith("_")}, timer=t)
        self.environment(spec, tr)
        for td in self.run.targets:
            if td["name"] == name:
                td["distro"] = spec.distro
        if spec.family == "linux":
            expected = "deb" if spec.os.endswith("deb") else "rpm" if spec.os.endswith("rpm") else ""
            if kind and expected and kind != expected:
                self._add("Install", "pkgkind", "targets.yml os key matches the distro's package type", WARN,
                          f"{spec.os} says {expected} but {spec.distro} uses {kind}; using {kind}", target=name)
                spec.os = f"linux-{facts.get('ARCH', 'x86_64')}-{kind}"
            if facts.get("ARCH") not in ("x86_64", "aarch64"):
                self._add("Install", "arch", "CPU architecture supported by the agent", FAIL, f"{facts.get('ARCH')} is not supported", target=name)
                return
        inst = Installer(spec, tr, facts, self.s, self.catalog)

        # install
        t = Timer()
        pre = inst.status()
        if self.skip_install and pre.get("SERVICE") not in (None, "missing"):
            self._add("Install", "install", f"Agent {self.catalog.version} installed", SKIP, f"--skip-install; service {pre.get('SERVICE')}, version {pre.get('VERSION')}", target=name, timer=t)
        else:
            if pre.get("SERVICE") not in (None, "missing") and pre.get("VERSION"):
                self.run.notes.append(f"{name}: agent already present before the run ({pre.get('VERSION')}); the install ran on top of it (upgrade path)")
            r = inst.install(self.api_key, self.backend_url, self.install_mode)
            if r.ok:
                self._add("Install", "install", f"Agent {self.catalog.version} installed ({self.install_mode} mode)", PASS,
                          f"installer exit 0 in {t.seconds():.0f}s", details=r.text(6000), target=name, timer=t)
            else:
                self._add("Install", "install", f"Agent {self.catalog.version} installed ({self.install_mode} mode)", FAIL,
                          f"installer exit {r.rc}: {(r.err or r.out).strip().splitlines()[-1] if (r.err or r.out).strip() else 'no output'}",
                          details=r.text(8000), target=name, timer=t)
                if self.s.stop_on_install_failure:
                    raise SystemExit("install failed and STOP_ON_INSTALL_FAILURE=true")
                return

        # on-host state
        t = Timer()
        note = inst.container_accommodation()
        if note:
            self.run.notes.append(f"{name}: {note}")
            self._add("Install", "container", "Service unit starts in this environment", WARN, note, target=name)
        st = inst.status()
        cfg = inst.read_config()
        ver_ok = self.catalog.version in (st.get("VERSION") or "")
        svc_ok = st.get("SERVICE") in ("active", "Running")
        self._add("Install", "service", "acc service running and enabled", PASS if svc_ok else FAIL,
                  f"service {st.get('SERVICE')}, enabled {st.get('ENABLED', 'n/a')}, pid {st.get('PID')}", target=name, evidence=st, timer=t,
                  cause="" if svc_ok else ("target" if note else "agent"))
        self._add("Install", "version", "Installed binary reports the expected version", PASS if ver_ok else FAIL,
                  f"{st.get('VERSION') or 'no version output'} (expected {self.catalog.version})", target=name, cause="" if ver_ok else "agent")
        cfg_ok = self.backend_url in cfg and "api-key:" in cfg and ("encrypted:" in cfg or self.api_key in cfg)
        redacted = re.sub(r'(api-key:\s*").*?(")', r"\1***\2", cfg)
        self._add("Install", "config", "acc.yml points at the MID endpoint with the API key", PASS if cfg_ok else FAIL,
                  "backend-url and api-key present" if cfg_ok else "backend-url or api-key missing from acc.yml", details=redacted, target=name)
        if re.search(r"^\s*allow-list:\s*\S", cfg, re.M):
            self._add("Install", "allowlist", "check allow-list enabled in acc.yml", PASS, "allow-list configured", target=name)
        else:
            self._add("Install", "allowlist", "check allow-list enabled in acc.yml", WARN, "allow-list not configured (every command is allowed)", target=name)
        if not svc_ok:
            self._add("Connectivity", "log", "Agent log", WARN, "service not running - log tail attached", details=inst.tail_log(120), target=name)
            return
        self._snapshot()

        # connectivity: agent registers on the instance through the MID
        t = Timer()
        agent_id = ""
        log = inst.tail_log(400)
        m = KEEPALIVE_ID.search(log)
        if m:
            agent_id = m.group(1)
        host = facts.get("HOST", "")
        rec = discovery.wait_for_agent(self.sn, agent_id, host, facts.get("IP", ""), self.s.agent_up_timeout_s)
        if not rec:
            self._add("Connectivity", "registered", "Agent registered on the instance and Up", FAIL,
                      f"no agent record for id={agent_id or '?'} host={host} within {self.s.agent_up_timeout_s}s", details=inst.tail_log(120), target=name, timer=t)
            return
        agent_id = rec["agent_id"]
        up = (rec.get("status__display") or "").lower() == "up"
        self._add("Connectivity", "registered", "Agent registered on the instance and Up", PASS if up else FAIL,
                  f"{rec['name']} id {agent_id} status {rec.get('status__display')} since {rec.get('up_since')}", target=name,
                  evidence={k: rec[k] for k in ("sys_id", "name", "agent_id", "status__display", "agent_version", "mid__display", "ip_address", "up_since", "is_using_systemd", "cpu_protection_behavior", "data_collection__display") if k in rec}, timer=t)
        self._add("Connectivity", "mid", "Agent connected through the configured MID", PASS if rec.get("mid__display") == self.s.mid_server_name else FAIL,
                  f"mid {rec.get('mid__display')} (expected {self.s.mid_server_name})", target=name)
        # on an agent record that existed before this install (upgrade or downgrade in place) the version columns are
        # refreshed by the next agent refresh, minutes after the service came back - wait for it rather than fail
        t = Timer()
        waited = False
        while rec.get("agent_version") != self.catalog.version and t.seconds() < self.s.agent_up_timeout_s:
            waited = True
            time.sleep(20)
            rec = discovery.find_agent(self.sn, agent_id) or rec
        ver_seen = rec.get("agent_version") == self.catalog.version
        self._add("Connectivity", "version", "Instance sees the expected agent version", PASS if ver_seen else FAIL,
                  f"{rec.get('agent_version')} (expected {self.catalog.version})" + (f" - the record caught up after {t.seconds():.0f}s" if waited and ver_seen else ""),
                  target=name, timer=t if waited else None, cause="" if ver_seen else "agent")
        errs = [l for l in log.splitlines() if "[ERROR]" in l]
        self._add("Connectivity", "log", "Agent log free of errors after start", PASS if not errs else WARN,
                  f"{len(errs)} ERROR line(s) in the last 400 log lines" if errs else "no ERROR lines", details="\n".join(errs[-30:]), target=name)
        if not up:
            return
        self._snapshot()

        # performance sampler: runs on the host through discovery, checks and policies, stopped in resources()
        ps = None
        if spec.family == "linux" and self.s.perf_sampling:
            ps = perf.PerfSession(tr, step=self.s.perf_step_s)
            err = ps.start()
            if err:
                self._add("Resources", "perf", "Agent resource usage and host impact while working", WARN, f"performance sampler could not start: {err}", target=name)
                ps = None
        self._perf[name] = ps

        # discovery
        if ps:
            ps.mark("discovery")
        ci = self.discovery(spec, inst, rec, agent_id)
        self._snapshot()
        # checks + policies need the host CI
        if ci:
            if ps:
                ps.mark("checks")
            self.checks(spec, rec, ci)
            self._snapshot()
            if self.s.run_policies:
                if ps:
                    ps.mark("policies")
                self.policies(spec, rec, ci)
                self._snapshot()
        else:
            self._add("Checks", "skipped", "Check definitions tested on the agent", SKIP, "no host CI - discovery did not produce one", target=name)
            if self.s.run_policies:
                self._add("Policies", "skipped", "Policies evaluated against the host CI", SKIP, "no host CI", target=name)
        # resources and cleanup on the host
        self.resources(spec, tr, inst, cfg)
        self._snapshot()
        # UI
        if browser and browser.logged_in:
            self.ui(spec, browser, rec, ci)
        # uninstall
        if self.s.uninstall_after:
            t = Timer()
            r = inst.uninstall()
            left = inst.leftovers()
            clean = left.get("PROC", "0") in ("0", "") and left.get("BIN", "absent") == "absent" and left.get("PKG", "absent") == "absent"
            self._add("Uninstall", "remove", "Agent uninstalled and nothing left running", PASS if (r.ok and clean) else FAIL,
                      f"uninstaller exit {r.rc}; leftovers: {left}", details=r.text(4000), target=name, evidence=left, timer=t)

    # ---- discovery -----------------------------------------------------------------------------------------------
    def discovery(self, spec: TargetSpec, inst: Installer, rec: dict, agent_id: str) -> dict | None:
        name = spec.name
        t = Timer()
        since = sn_now(-5)
        try:
            discovery.run_discovery(self.sn, agent_id)
            self._add("Discovery", "trigger", "Discovery (collect host data) requested through the ACC API", PASS, "accepted", target=name, timer=t)
        except SNError as e:
            self._add("Discovery", "trigger", "Discovery (collect host data) requested through the ACC API", FAIL, str(e), target=name, timer=t)
        t = Timer()
        done = discovery.wait_for_discovery(self.sn, agent_id, since, self.s.discovery_timeout_s)
        state = (done or rec).get("host_data__display", "")
        ci_id = (done or {}).get("cmdb_ci") or ""
        if not (done and ci_id and state.lower().startswith("collected")):
            reason = discovery_failure_reason(inst.tail_log(400))
            if "hash of the file does not match" in reason and self.s.mid_auto_configure:
                self._add("Discovery", "plugin-cache", "Agent could fetch its plugin assets from the MID", WARN,
                          "ACC-1500 asset hash mismatch - the MID served a stale plugin; syncing + restarting the MID and retrying discovery once",
                          details=reason, target=name, timer=t)
                midmod.sync_plugins(self.sn, self.s.mid_server_name)
                since = sn_now(-5)
                t = Timer()
                try:
                    discovery.run_discovery(self.sn, agent_id)
                except SNError as e:
                    self.run.notes.append(f"{name}: discovery retry could not be requested: {e}")
                done = discovery.wait_for_discovery(self.sn, agent_id, since, self.s.discovery_timeout_s)
                state = (done or rec).get("host_data__display", "")
                ci_id = (done or {}).get("cmdb_ci") or ""
            elif reason:
                self.run.notes.append(f"{name}: discovery error on the agent: {reason[:300]}")
            inst_reason = discovery.instance_failure_reason(self.sn, agent_id)
        if done and ci_id and state.lower().startswith("collected"):
            self._add("Discovery", "collected", "Host data collected and a host CI bound to the agent", PASS,
                      f"host_data '{state}' at {done.get('host_data_last_collected')}, CI {done.get('cmdb_ci.name__display') or done.get('cmdb_ci__display')}", target=name, timer=t)
        else:
            log = inst.tail_log(400)
            errs = [l for l in log.splitlines() if "[ERROR]" in l]
            first = (inst_reason.splitlines() or [""])[0]
            # decisive first: did the MID restart after the collection was requested? The agent sends a discovery result once
            # (checks with an interval under 300 s are not retried), so a MID that was down at that moment loses it - not the agent's fault
            mid_started = (self.sn.first("ecc_agent", f"name={self.s.mid_server_name}", "started") or {}).get("started", "")
            if mid_started and mid_started > since:
                cause, hint = "instance", (f"the MID server {self.s.mid_server_name} restarted at {mid_started} (instance time), after the collection "
                                           f"was requested ({since}); the agent does not retry results of checks with an interval under 300 s, "
                                           "so the result was lost - re-run with the MID stable")
            else:
                cause, hint = checks.attribute({"output": inst_reason + "\n" + "\n".join(errs[-20:])}, FAIL)
            self._add("Discovery", "collected", "Host data collected and a host CI bound to the agent", FAIL,
                      f"host_data '{state or 'unknown'}' after {self.s.discovery_timeout_s}s, cmdb_ci {'set' if ci_id else 'empty'}; "
                      + (discovery_failure_reason(log)[:300] or first[:300] or f"last attempt {(done or rec).get('host_data_last_attempted')}")
                      + (f" [cause: {cause} - {hint}]" if hint else ""),
                      details="instance side:\n" + inst_reason + "\n\nagent log errors:\n" + "\n".join(errs[-20:]), target=name, timer=t, cause=cause)
            if not ci_id:
                return None
        ci = discovery.ci_record(self.sn, ci_id)
        if not ci:
            self._add("Discovery", "ci", "Host CI readable", FAIL, f"cmdb_ci {ci_id} not readable", target=name)
            return None
        cls = ci.get("sys_class_name", "")
        chain = discovery.class_chain(self.sn, cls)
        cls_ok = spec.expected_ci_class in chain
        self._add("Discovery", "ci-class", f"Host CI class is {spec.expected_ci_class}", PASS if cls_ok else FAIL, f"{cls} ({ci.get('name')})", target=name,
                  evidence={k: ci.get(k) for k in ("sys_id", "name", "sys_class_name", "ip_address", "fqdn", "os", "os_version", "serial_number", "cpu_count", "ram", "discovery_source", "last_discovered", "first_discovered", "virtual", "manufacturer__display", "model_id__display") if k in ci})
        host = inst.facts.get("HOST", "")
        name_ok = bool(host) and (ci.get("name", "").lower().startswith(host.lower()) or host.lower().startswith(ci.get("name", "").lower()))
        self._add("Discovery", "ci-name", "Host CI name matches the server's host name", PASS if name_ok else WARN, f"CI '{ci.get('name')}' vs host '{host}'", target=name)
        ip = inst.facts.get("IP", "")
        self._add("Discovery", "ci-ip", "Host CI IP matches the server", PASS if ip and ci.get("ip_address") == ip else WARN, f"CI {ci.get('ip_address')} vs host {ip}", target=name)
        os_ok = bool(ci.get("os"))
        self._add("Discovery", "ci-os", "Host CI carries OS and version", PASS if os_ok else WARN, f"os '{ci.get('os')}' version '{ci.get('os_version')}' serial '{ci.get('serial_number')}'", target=name)
        rel = discovery.ci_related(self.sn, ci_id)
        populated = {k: v for k, v in rel.items() if v > 0}
        self._add("Discovery", "ci-related", "Discovery populated related CI data", PASS if populated else WARN,
                  ", ".join(f"{k}={v}" for k, v in rel.items()), target=name, evidence=rel)
        src = ci.get("discovery_source", "")
        self._add("Discovery", "ci-source", "CI discovery source set by the agent", PASS if src else WARN, f"discovery_source '{src}', last_discovered {ci.get('last_discovered')}", target=name)
        ci["_chain"] = chain
        return ci

    # ---- checks ----------------------------------------------------------------------------------------------------
    def checks(self, spec: TargetSpec, rec: dict, ci: dict) -> None:
        name = spec.name
        t = Timer()
        try:
            defs = checks.list_check_defs(self.sn)
        except SNError as e:
            self._add("Checks", "list", "Check definitions read from the instance", FAIL, str(e), target=name, timer=t)
            return
        chain = ci.get("_chain") or [ci.get("sys_class_name", "")]
        origins = {"oob": 0, "customized": 0, "custom": 0}
        for d in defs:
            origins[d["origin"]] += 1
        self._add("Checks", "list", "Check definitions read from the instance", PASS,
                  f"{len(defs)} active: {origins['oob']} out-of-box, {origins['customized']} customized, {origins['custom']} custom", target=name, timer=t,
                  evidence={"custom": [d["name"] for d in defs if d["origin"] == "custom"], "customized": [d["name"] for d in defs if d["origin"] == "customized"]})
        applicable = [d for d in defs if checks.applies_to_class(d, chain)]
        if not self.s.include_oob_checks:
            applicable = [d for d in applicable if d["origin"] != "oob"]
        if not self.s.include_custom_checks:
            applicable = [d for d in applicable if d["origin"] == "oob"]
        if self.s.check_filter:
            applicable = [d for d in applicable if any(f.lower() in d["name"].lower() for f in self.s.check_filter)]
        skipped_internal = [d["name"] for d in applicable if d["internal"]]
        to_run = []
        for d in sorted(applicable, key=lambda d: (d["origin"] == "oob", d["name"].lower())):
            ok, why = checks.testable(d)
            if ok:
                to_run.append(d)
            elif not d["internal"]:
                self._add("Checks", "def-" + safe_name(d["name"]), f"Check '{d['name']}' [{d['origin']}]", SKIP, why, target=name)
        if skipped_internal:
            self._add("Checks", "internal", "Agent-internal check types (upgrade, restart, cancel, ...)", SKIP,
                      f"{len(skipped_internal)} framework-internal definitions are exercised by their own actions, not ad hoc: {', '.join(sorted(skipped_internal))}", target=name)
        remedied = False
        for d in to_run:
            t = Timer()
            rid = "def-" + safe_name(d["name"])
            title = f"Check '{d['name']}' [{d['origin']}, {d['type_name']}]"
            try:
                tid = checks.start_test(self.sn, d["sys_id"], ci["sys_id"])
            except SNError as e:
                self._add("Checks", rid, title, FAIL, f"could not start: {e}", target=name, timer=t, evidence={"command": d.get("command"), "check_def": d["sys_id"]})
                continue
            wait = checks.wait_seconds(self.s.check_timeout_s, d.get("timeout"))
            row = checks.wait_test(self.sn, tid, wait)
            if checks.is_asset_error(row) and not remedied and self.s.mid_auto_configure:
                # the MID served a plugin whose hash the agent rejects: sync + restart the MID once, then retry this check
                remedied = True
                self._add("Checks", "plugin-cache", "Agent could fetch its check plugins from the MID", WARN,
                          f"ACC-1500 plugin asset error on '{d['name']}' - syncing + restarting the MID once and retrying", details=(row.get("output") or "")[:2000], target=name, timer=t)
                midmod.sync_plugins(self.sn, self.s.mid_server_name)
                t = Timer()
                try:
                    tid = checks.start_test(self.sn, d["sys_id"], ci["sys_id"])
                    row = checks.wait_test(self.sn, tid, wait)
                except SNError as e:
                    row = {"outcome": "error", "error_msg": str(e), "output": ""}
            status, msg = checks.judge(row)
            if checks.is_allowlist_denial(row):
                # the agent's combined allow-list (its own file + the lists bundled with the check's plugin assets) has no entry for
                # this command on this OS. For shipped content that usually means "not meant for this platform" (or a content
                # defect) - a warning; for custom content it is a deployment gap - a failure.
                if d["origin"] == "oob":
                    status, msg = WARN, ("denied by the agent allow-list on this OS (no exec entry in the combined asset allow-list) - "
                                         "not applicable here, or the definition's assets/allow-list need attention")
                else:
                    status, msg = FAIL, "denied by the agent allow-list: custom checks need an allow-list entry on the agent (Generate allow-list content) - " + msg
            cause, hint = checks.attribute(row, status, d["origin"])
            if hint:
                msg = f"{msg} [cause: {cause} - {hint}]"
            if status == PASS and fixtures.is_fixture(d["name"]):
                # our own script: the agent ran it, now check it did its job (header, one JSON object per user, footer count)
                ok, why = fixtures.verify_output(d["name"], row.get("output") or "", self._facts.get(name))
                if ok:
                    msg = f"{msg}; script output verified: {why}"
                else:
                    cause, hint = checks.attribute(dict(row, outcome="complete"), FAIL, d["origin"])
                    status, msg = FAIL, (f"the custom script ran (exit {row.get('check_status')}) but its output is wrong: {why}"
                                         + (f" [cause: {cause} - {hint}]" if hint else ""))
            self._add("Checks", rid, title, status, msg, details=(row.get("output") or row.get("error_msg") or "")[:6000], target=name, timer=t, cause=cause,
                      evidence={"check_def": d["sys_id"], "test_result": tid, "command": d.get("command"), "timeout": d.get("timeout"), "exit_code": row.get("check_status")})
        # the agent's own self-test (SelfTest check type, driven by the "Run self-test" action)
        self.self_test(spec, rec)

    def self_test(self, spec: TargetSpec, rec: dict) -> None:
        name = spec.name
        t = Timer()
        d = self.sn.first("sn_agent_check_def", "check_script_type.name=SelfTest^active=true", "sys_id,name,timeout")
        if not d:
            self._add("Checks", "self-test", "Agent self-test", SKIP, "no SelfTest check definition on this instance", target=name)
            return
        runs_q = f"agent.agent_extended_info={rec['sys_id']}"
        have_tables = self.sn.table_exists("sn_agent_self_test_run")
        before = self.sn.count("sn_agent_self_test_run", runs_q) if have_tables else 0
        try:
            r = self.sn.s.post(f"{self.sn.instance}/api/sn_agent/agents/check_defs/{d['sys_id']}/run",
                               json={"table": "sn_agent_cmdb_ci_agent", "query": f"agent_extended_info={rec['sys_id']}", "priority": 0}, timeout=self.sn.timeout)
            if r.status_code >= 400:
                raise SNError(f"{r.status_code} {r.text[:300]}")
            j = r.json()
            req = (j.get("result") or j)["request_id"]
        except Exception as e:
            self._add("Checks", "self-test", "Agent self-test", FAIL, f"could not start: {e}", target=name, timer=t)
            return
        deadline = time.time() + self.s.check_timeout_s
        msg = "request still processing"
        while time.time() < deadline:
            rr = self.sn.s.get(f"{self.sn.instance}/api/sn_agent/agents/exec/run/{req}", timeout=self.sn.timeout)
            if rr.status_code == 200:
                jj = rr.json()
                msg = (jj.get("result") or jj).get("message", "done")
                break
            if rr.status_code not in (202,):
                msg = f"status {rr.status_code}: {rr.text[:200]}"
                break
            time.sleep(5)
        runs = []
        if have_tables:
            # the run record is written by the MID a few seconds after the request completes
            deadline = time.time() + 60
            while time.time() < deadline:
                if self.sn.count("sn_agent_self_test_run", runs_q) > before:
                    break
                time.sleep(5)
            runs = self.sn.query("sn_agent_self_test_run", runs_q + "^ORDERBYDESCsys_created_on",
                                 "sys_id,suite,total_tests,passed_tests,failed_tests,skipped_tests,timed_out,duration_seconds,sys_created_on", 1)
        results = []
        if runs and self.sn.table_exists("sn_agent_self_test_result"):
            results = self.sn.query("sn_agent_self_test_result", f"test_run={runs[0]['sys_id']}^ORDERBYstatus",
                                    "alias,test_name,status,message,error_code,duration_seconds", 100, display="true")
        failed = [x for x in results if (x.get("status") or "").lower() == "fail"]
        if runs and self.sn.count("sn_agent_self_test_run", runs_q) > before:
            r0 = runs[0]
            st = PASS if not failed and r0.get("timed_out") != "true" else WARN
            self._add("Checks", "self-test", "Agent self-test (acc self-test)", st,
                      f"suite {r0.get('suite')}: {r0.get('passed_tests')} passed, {r0.get('failed_tests')} failed, {r0.get('skipped_tests')} skipped"
                      + (", TIMED OUT" if r0.get("timed_out") == "true" else "")
                      + (" - failed: " + ", ".join(f"{x.get('alias')} ({x.get('message')})" for x in failed) if failed else ""),
                      details="\n".join(f"{x.get('status'):5} {x.get('alias')}: {x.get('message')}" + (f" [{x.get('error_code')}]" if x.get("error_code") else "") for x in results),
                      target=name, timer=t, evidence={"run": r0.get("sys_id"), "request": req})
        else:
            self._add("Checks", "self-test", "Agent self-test (acc self-test)", WARN, f"request {req}: {msg}; no new self-test run record", target=name, timer=t)

    # ---- policies --------------------------------------------------------------------------------------------------
    def policies(self, spec: TargetSpec, rec: dict, ci: dict) -> None:
        name = spec.name
        t = Timer()
        try:
            pols = checks.list_policies(self.sn)
        except SNError as e:
            self._add("Policies", "list", "Policies read from the instance", FAIL, str(e), target=name, timer=t)
            return
        self._add("Policies", "list", "Policies read from the instance", PASS,
                  f"{len(pols)} active published policies ({sum(1 for p in pols if p['origin'] != 'oob')} custom/customized)", target=name, timer=t,
                  evidence={"policies": [f"{p['name']} [{p['origin']}] -> {p.get('table')} {p.get('filter') or ''}" for p in pols]})
        for p in pols:
            rid = "pol-" + safe_name(p["name"])
            title = f"Policy '{p['name']}' [{p['origin']}]"
            if p["proxy"]:
                self._add("Policies", rid, title, SKIP, "proxy policy (runs on a proxy agent, not on the host itself)", target=name)
                continue
            t = Timer()
            match, why = checks.policy_matches_ci(self.sn, p, ci["sys_id"])
            if not match:
                self._add("Policies", rid, title, SKIP, why, target=name, timer=t)
                continue
            pc = checks.policy_clients(self.sn, p["sys_id"])
            agents_list = (pc or {}).get("agents_list") or ""
            assigned = rec["sys_id"] in agents_list or rec["agent_id"] in agents_list
            self._add("Policies", rid + "-assigned", title + " applies to this agent", PASS if assigned else WARN,
                      "agent listed in the policy's clients" if assigned else
                      ("policy matches the CI but its client list has not been calculated yet (no sn_agent_policy_clients row - the platform's policy "
                       "calculation job runs periodically)" if not pc else
                       f"policy matches the CI but the agent is not in its client list (calculated {pc.get('sys_updated_on')})"),
                      target=name, timer=t)
            for chk in p["checks"]:
                t = Timer()
                cid = rid + "-" + safe_name(chk["name"])
                ctitle = f"Policy '{p['name']}' check '{chk['name']}'"
                if chk.get("background") == "true":
                    self._add("Policies", cid, ctitle, SKIP, "background check", target=name)
                    continue
                try:
                    tid = checks.start_test(self.sn, chk["sys_id"], ci["sys_id"], instance=True)
                except SNError as e:
                    self._add("Policies", cid, ctitle, FAIL, f"could not start: {e}", target=name, timer=t)
                    continue
                row = checks.wait_test(self.sn, tid, checks.wait_seconds(self.s.check_timeout_s, chk.get("timeout")))
                status, msg = checks.judge(row)
                cause, hint = checks.attribute(row, status, p["origin"])
                if hint:
                    msg = f"{msg} [cause: {cause} - {hint}]"
                if status == PASS and fixtures.is_fixture(chk.get("check_def.name") or chk["name"]):
                    ok, why = fixtures.verify_output(chk.get("check_def.name") or chk["name"], row.get("output") or "", self._facts.get(name))
                    if ok:
                        msg = f"{msg}; script output verified: {why}"
                    else:
                        cause, hint = checks.attribute(dict(row, outcome="complete"), FAIL, p["origin"])
                        status, msg = FAIL, (f"the custom script ran (exit {row.get('check_status')}) but its output is wrong: {why}"
                                             + (f" [cause: {cause} - {hint}]" if hint else ""))
                self._add("Policies", cid, ctitle, status, msg, details=(row.get("output") or row.get("error_msg") or "")[:6000], target=name, timer=t, cause=cause,
                          evidence={"check_instance": chk["sys_id"], "check_def": chk.get("check_def.name"), "test_result": tid, "exit_code": row.get("check_status")})

    # ---- resources -------------------------------------------------------------------------------------------------
    def resources(self, spec: TargetSpec, tr, inst: Installer, cfg: str) -> None:
        name = spec.name
        ps = self._perf.pop(name, None)
        if ps:
            ps.mark("inventory")
        t = Timer()
        inv = resources.inventory(tr, spec.family)
        for c in inv["components"]:
            self.run.components.append(dict(c, target=name))
        fi = inv["facts"]
        self._add("Resources", "inventory", "Component inventory read from the installed agent", PASS if fi.get("ACC_VERSION") and fi.get("RUBY") else WARN,
                  f"{fi.get('ACC_VERSION') or 'agent version unknown'}; {fi.get('RUBY') or 'embedded Ruby not found'}; OpenSSL {fi.get('RUBY_OPENSSL') or fi.get('OPENSSL') or fi.get('OPENSSL_LIB') or '?'}; "
                  f"osquery {fi.get('OSQUERY') or 'not present'}; {sum(1 for c in inv['components'] if c['kind'] == 'Ruby gem')} gems, "
                  f"{sum(1 for c in inv['components'] if c['kind'].startswith('plugin content'))} plugin assets - full list in the Components section and components.csv",
                  target=name, timer=t, evidence={k: v for k, v in fi.items() if not k.startswith("_")})
        lim = resources.cpu_limits(cfg)
        self._add("Resources", "limits", "CPU protection configured in acc.yml", PASS if lim["present"] and not lim["disabled"] else WARN,
                  f"cpu_percentage_limit {lim['cpu_percentage_limit']:g}%, repeated_high_cpu_num {lim['repeated_high_cpu_num']:g}, "
                  f"monitor_interval {lim['monitor_interval_sec']:g}s, max-running-checks {lim['max_running_checks']:g}" + (" (DISABLED)" if lim["disabled"] else ""),
                  target=name, evidence=lim)
        t = Timer()
        if ps:
            ps.mark("idle")
        LOG.info("  sampling agent CPU on %s for %ss", name, self.s.cpu_sample_seconds)
        smp = resources.sample_cpu(tr, spec.family, self.s.cpu_sample_seconds)
        if "ERROR" in smp or "AVG_PCT" not in smp:
            self._add("Resources", "cpu", "Agent CPU within the configured threshold", FAIL, smp.get("ERROR") or smp.get("_err") or "sampler returned nothing", target=name, timer=t, evidence=smp)
        else:
            avg, peak = float(smp["AVG_PCT"]), float(smp["PEAK_PCT"])
            limit = lim["cpu_percentage_limit"]
            if avg <= limit + self.s.cpu_tolerance_pct:
                st = PASS if peak <= max(limit * lim["repeated_high_cpu_num"], limit + self.s.cpu_tolerance_pct) * 3 else WARN
            else:
                st = FAIL
            self._add("Resources", "cpu", "Agent CPU within the configured threshold", st,
                      f"avg {avg:.0f}% / peak {peak:.0f}% of one core over {smp.get('SAMPLES')} samples ({self.s.cpu_sample_seconds}s), limit {limit:g}% (+{self.s.cpu_tolerance_pct:g} tolerance); "
                      f"RSS {int(smp.get('RSS_KB', 0) or 0) // 1024} MB, {smp.get('THREADS')} threads, up to {smp.get('MAX_PROCS')} processes", target=name, timer=t, evidence=smp,
                      cause="" if st != FAIL else "agent")
        if ps:
            t = Timer()
            try:
                a = ps.stop()
            except Exception as e:  # the sampler must never sink the run
                a = {"samples": 0, "error": str(e)}
            self.perf_result(spec, a, t)
        if spec.family == "linux":
            t = Timer()
            pl = resources.plugin_state(tr, spec.family)
            bad = [x for x in (pl.get("CRLF_SHEBANG") or "").split(";") if x]
            assets = sorted({x.split("/", 1)[0] for x in bad})
            self._add("Resources", "plugins", "Plugin scripts delivered by the MID are executable on this OS", PASS if not bad else FAIL,
                      f"{pl.get('PLUGIN_DIRS')} plugin directories, {pl.get('SCRIPTS')} scripts"
                      + (f"; {len(bad)} script(s) have a CRLF shebang and fail with \"'ruby\\r': No such file\": {', '.join(bad[:8])}"
                         f" [cause: content - plugin asset(s) {', '.join(assets)} are shipped with Windows line endings by the content app on the instance; "
                         f"the same files reach every agent version, so this does not change with the agent]" if bad else "; none with Windows line endings"),
                      target=name, timer=t, evidence=pl, cause="content" if bad else "")
        LOG.info("  waiting %ss for the agent to clean up after its checks", self.s.cleanup_grace_s)
        time.sleep(self.s.cleanup_grace_s)
        t = Timer()
        cl = resources.cleanup_state(tr, spec.family)
        child = int(cl.get("CHILD_PROCS", "0") or 0)
        zomb = int(cl.get("ZOMBIES", "0") or 0)
        osq = int(cl.get("OSQUERY_PROCS", "0") or 0)
        tmp = [x for x in (cl.get("TMP_FILES") or "").split(";") if x and not x.endswith("/.osquery")]
        clean = child == 0 and zomb == 0 and osq == 0 and not tmp
        self._add("Cleanup", "processes", "No check processes, zombies or temp files left after discovery", PASS if clean else WARN,
                  f"child processes {child}, zombies {zomb}, osquery processes {osq}, temp files {len(tmp)}" + (f": {tmp}" if tmp else "")
                  + (f"; children: {cl.get('CHILD_CMDS')}" if child else ""), target=name, timer=t, evidence=cl)
        errs = int(cl.get("LOG_ERRORS", "0") or 0)
        panics = int(cl.get("LOG_PANICS", "0") or 0)
        self._add("Cleanup", "stability", "No panics or crashes in the agent log", PASS if panics == 0 else FAIL,
                  f"{panics} panic/fatal lines, {errs} error lines, service {cl.get('SERVICE')}, restarts seen {cl.get('RESTARTS', 'n/a')}, open files {cl.get('OPEN_FILES', 'n/a')}",
                  details="\n".join(l for l in inst.tail_log(300).splitlines() if "[ERROR]" in l or "panic" in l.lower())[-6000:], target=name,
                  cause="" if panics == 0 else "agent")
        cache = int(cl.get("CACHE_DU_KB", "0") or 0)
        self._add("Cleanup", "footprint", "Disk footprint of cache and logs", PASS if cache < 512 * 1024 else WARN,
                  f"cache {cache // 1024} MB, logs {int(cl.get('LOG_KB', '0') or 0) // 1024} MB", target=name)

    def perf_result(self, spec: TargetSpec, a: dict, t: Timer) -> None:
        """One test row + the per-phase table data from a finished performance sampling session."""
        name = spec.name
        title = "Agent resource usage and host impact while working"
        if not a.get("samples"):
            self._add("Resources", "perf", title, WARN, f"performance sampler returned no samples ({a.get('error') or a.get('sampler_log') or 'unknown reason'})",
                      target=name, timer=t, evidence={k: v for k, v in a.items() if k != "series"})
            return
        L = a["impact"]["load"]
        flags = []
        if L.get("samples"):
            if L["agent_cpu_avg"] > self.s.perf_cpu_avg_warn_pct:
                flags.append(f"agent avg CPU {L['agent_cpu_avg']:g}% of one core while working > {self.s.perf_cpu_avg_warn_pct:g}%")
            if L["agent_rss_peak_mb"] > self.s.perf_rss_peak_warn_mb:
                flags.append(f"agent RSS peak {L['agent_rss_peak_mb']} MB > {self.s.perf_rss_peak_warn_mb} MB")
        d = a["impact"].get("host_busy_delta")
        if d is not None and d > self.s.perf_host_impact_warn_pct:
            flags.append(f"host CPU busy {d:+g} points working vs idle > {self.s.perf_host_impact_warn_pct:g}")
        st = WARN if flags else PASS
        msg = perf.describe(a) + (f" [above the warning thresholds: {'; '.join(flags)}]" if flags else "")
        self.run.perf.append({"target": name, "distro": spec.distro, **a})
        self._add("Resources", "perf", title, st, msg, target=name, timer=t,
                  evidence={"ncpu": a["ncpu"], "step_s": a.get("step_s"), "samples": a["samples"], "io_readable": a.get("io_readable"),
                            "phases": "; ".join(f"{p['phase']} {p.get('duration_s', 0)}s" for p in a["phases"]), "impact": a["impact"]})

    # ---- UI --------------------------------------------------------------------------------------------------------
    def ui(self, spec: TargetSpec, b: Browser, rec: dict, ci: dict | None) -> None:
        name = spec.name
        t = Timer()
        shot = b.shot(f"{name}-agent", b.classic(f"sn_agent_cmdb_ci_agent.do?sys_id={rec.get('sys_id', '')}&sysparm_view=").replace("sn_agent_cmdb_ci_agent.do", "sn_agent_ci_extended_info.do"))
        txt = b.text()
        ok = rec["agent_id"] in txt or rec["name"] in txt
        self._add("UI", "agent-form", "Agent record renders in the UI", PASS if ok else WARN,
                  "agent form shows the agent" if ok else "could not confirm the agent on the form (see screenshot)", target=name, screenshot=shot, timer=t)
        if ci:
            t = Timer()
            shot = b.shot(f"{name}-ci", b.classic(f"{ci['sys_class_name']}.do?sys_id={ci['sys_id']}"))
            txt = b.text()
            ok = (ci.get("name") or "zzz") in txt
            self._add("UI", "ci-form", "Discovered host CI renders in the UI", PASS if ok else WARN,
                      "CI form shows the host" if ok else "could not confirm the CI name on the form (see screenshot)", target=name, screenshot=shot, timer=t)
        t = Timer()
        shot = b.shot(f"{name}-tests", b.classic(f"sn_agent_test_result_list.do?sysparm_query=agent={rec.get('sys_id', '')}^ORDERBYDESCsys_created_on"))
        self._add("UI", "test-results", "Test check results visible in the UI", PASS if shot else SKIP, "list screenshot taken" if shot else "no screenshot", target=name, screenshot=shot, timer=t)

    # ---- orchestration ---------------------------------------------------------------------------------------------
    def execute(self) -> RunResult:
        run = RunResult(version=self.version_req, instance=self.s.sn_instance, mid_server=self.s.mid_server_name,
                        backend_url=self.backend_url, title=self.s.report_title, settings=self.s.redacted())
        self.run = run
        self.out_dir = self.s.results_dir / safe_name(self.version_req if self.version_req != "latest" else "pending")
        ok = self.preflight(run)
        if ok and self.packages():
            self.out_dir = self.s.results_dir / safe_name(run.version)
            run.targets = [t.to_dict() for t in self.targets()]
            shots = self.out_dir / "screenshots"
            with Browser(self.s, shots) as b:
                if b.available:
                    if b.login():
                        self._add("UI", "login", "Headless browser login to the instance", PASS, "logged in")
                        shot = b.shot("agent_downloads", "/sn_agent_agent_downloads.do")
                        txt = b.html(frame=None) + b.text(frame=None)
                        self._add("UI", "downloads-page", "Agent Downloads page lists this version", PASS if run.version in txt else WARN,
                                  f"version {run.version} {'found' if run.version in txt else 'not found'} in the page's download links", screenshot=f"screenshots/{shot}" if shot else "")
                    else:
                        self._add("UI", "login", "Headless browser login to the instance", WARN, b.error or "login failed")
                else:
                    self._add("UI", "login", "Headless browser login to the instance", SKIP, b.error or "browser unavailable")
                for spec in self.targets():
                    LOG.info("=== target %s (%s) ===", spec.name, spec.os)
                    try:
                        self.target(spec, b if b.logged_in else None)
                    except SystemExit:
                        raise
                    except Exception as e:  # keep going with the next target, but record it
                        LOG.exception("target %s crashed", spec.name)
                        self._add("Install", "crash", "Test driver error", ERROR, f"{type(e).__name__}: {e}", target=spec.name)
            # screenshots are stored under screenshots/ - fix relative paths
            for r in run.results:
                if r.screenshot and not r.screenshot.startswith("screenshots/"):
                    r.screenshot = "screenshots/" + r.screenshot
        run.finished = iso_now()
        path = write_report(run, self.out_dir, self.basename)
        write_index(self.s.results_dir)
        if self.only_targets:
            run.notes.append(f"partial run (targets {', '.join(self.only_targets)}) - written as {path.name}; result.html keeps the last full run")
        LOG.info("report: %s  overall: %s  %s", path, run.overall().upper(), run.counts())
        return run


def discovery_failure_reason(log: str) -> str:
    """The most telling line about a failed discovery check in the agent log (asset / allow-list / command errors)."""
    for line in reversed(log.splitlines()):
        low = line.lower()
        if "error getting assets" in low or "hash of the file does not match" in low or "acc-1500" in low:
            return line.strip()[:600]
    for line in reversed(log.splitlines()):
        if "[ERROR]" in line and ("discovery" in line.lower() or "check" in line.lower()):
            return line.strip()[:600]
    return ""


def write_index(results_dir: Path) -> None:
    """results/index.html - one line per version with its overall result."""
    rows = []
    files = sorted((f for d in results_dir.iterdir() if d.is_dir() for f in d.glob("result*.json")), key=lambda p: p.stat().st_mtime, reverse=True)
    for f in files:
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        c = j.get("counts", {})
        kind = "full" if f.stem == "result" else "partial"
        rows.append(f"<tr><td><a href='{f.parent.name}/{f.stem}.html'>{f.parent.name}</a></td><td>{kind}</td><td>{j.get('overall', '').upper()}</td><td>{j.get('started', '')}</td>"
                    f"<td>{c.get('pass', 0)}</td><td>{c.get('fail', 0)}</td><td>{c.get('warn', 0)}</td><td>{c.get('skip', 0)}</td><td>{', '.join(t.get('name', '') for t in j.get('targets', []))}</td></tr>")
    html = ("<!doctype html><html><head><meta charset='utf-8'><title>ACC agent qualification runs</title><style>body{font:14px sans-serif;margin:24px}"
            "table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:6px 10px}</style></head><body><h1>ACC agent qualification runs</h1>"
            "<table><tr><th>Version</th><th>Run</th><th>Overall</th><th>Started</th><th>Pass</th><th>Fail</th><th>Warn</th><th>Skip</th><th>Targets</th></tr>"
            + "".join(rows) + "</table></body></html>")
    (results_dir / "index.html").write_text(html, encoding="utf-8")
