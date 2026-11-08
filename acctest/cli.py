"""Command line: python acctest.py <command> [options]

  env check                 show the effective settings (secrets redacted) and what is missing
  preflight                 instance, ACC app, MID listener, API key, targets - no changes unless MID_AUTO_CONFIGURE /
                            ACC_API_KEY_AUTO_CREATE allow them
  versions                  which agent version the instance offers and the OS packages that exist for it
  download [--version V]    fetch the packages + install script into dist/<version>/
  lab provision|destroy|status   home lab only (LAB_MODE=proxmox)
  mid setup                 create/start the ACC listener on MID_SERVER_NAME (needs MID_AUTO_CONFIGURE=true)
  mid sync                  push the current ACC plugin assets to the MID servers (fixes 'hash does not match' ACC-1500)
  apikey                    make sure an API key exists and is stored in .env
  fixtures create|delete|status  a custom check definition + policy named acctest-* on the instance (lab use)
  run [--version V] [--mode package|script] [--skip-install] [--targets a,b]
                            full qualification -> results/<version>/result.html
  report <version>          re-render result.html from results/<version>/result.json
  uninstall [--targets a,b] remove the agent from the targets
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, agents, fixtures, lab, mid as midmod
from .config import PROJECT_ROOT, Settings, load_targets
from .report import write_report
from .results import RunResult, TestResult
from .runner import Runner, write_index
from .snow import SNClient, SNError
from .util import setup_logging


def _sn(s: Settings) -> SNClient:
    s.require("SN_INSTANCE", "SN_USER", "SN_PASS")
    return SNClient(s.sn_instance, s.sn_user, s.sn_pass, s.sn_verify_tls, s.sn_timeout_s)


def cmd_env(s: Settings, a) -> int:
    print(f"settings file: {s.env_path} ({'present' if s.env_path.exists() else 'MISSING - copy .env.example to .env'})")
    for k, v in s.redacted().items():
        print(f"  {k}={v}")
    missing = [k for k in ("SN_INSTANCE", "SN_USER", "SN_PASS", "MID_SERVER_NAME", "MID_HOST") if not s.raw.get(k)]
    print("targets file:", s.targets_file, f"({len(load_targets(s))} targets)" if s.targets_file.exists() else "(missing)")
    if missing:
        print("MISSING:", ", ".join(missing))
        return 1
    return 0


def cmd_preflight(s: Settings, a) -> int:
    r = Runner(s)
    run = RunResult(version="preflight", instance=s.sn_instance, mid_server=s.mid_server_name, backend_url=s.backend_url(), title=s.report_title)
    ok = r.preflight(run)
    print()
    for t in run.results:
        print(f"  [{t.status.upper():5}] {t.name}: {t.message}")
    print("\npre-flight:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def cmd_versions(s: Settings, a) -> int:
    sn = _sn(s)
    cat = agents.read_catalog(sn, a.version)
    print(f"instance agent version : {cat.version}   (ACC Framework app {cat.app_version}, dev_mode={cat.dev_mode})")
    print(f"download base          : {cat.base_url}")
    print("instance OS map        :", ", ".join(f"{k} -> {v['c']}.{v['p']}" for k, v in cat.os_map.items()))
    print("\npackages (os key -> file, on server?):")
    for p in cat.packages:
        ok, size = agents.available(p.url)
        print(f"  {p.os_key:22} {p.file:60} {'yes' if ok else 'NO ':3} {size / (1 << 20):7.1f} MB  {p.instance_label}")
    print("\nTargets: give one server per os key you want qualified (targets.yml). Linux distro -> package: Ubuntu/Debian -> "
          "linux-x86_64-deb, RHEL/Rocky/Alma/Oracle/Amazon/SLES -> linux-x86_64-rpm, Windows -> windows-x86_64.")
    local = agents.list_local_versions(s.agent_download_dir)
    print("versions already in", s.agent_download_dir, ":", ", ".join(local) or "none")
    if a.published:
        print("\nprobing the download server for every published version (HEAD per candidate, ~30 s)...")
        for v in agents.published_versions(cat.base_url):
            print(f"  {v['version']:8} {v['size'] / (1 << 20):6.1f} MB  {v['last_modified']}")
        print("qualify one with: python acctest.py run --version <x.y.z>   (runtimes: python acctest.py runtimes --version <x.y.z>)")
    return 0


def cmd_runtimes(s: Settings, a) -> int:
    """Embedded Ruby / OpenSSL / gems per agent version, read from the deb in dist/ (downloaded when missing)."""
    from . import runtimes
    versions = a.version or agents.list_local_versions(s.agent_download_dir)
    if not versions:
        print("no versions in dist/ and none given: python acctest.py runtimes --version 7.1.3 --version 7.1.2")
        return 2
    sn = None
    print(f"{'agent':9} {'Ruby':24} {'OpenSSL':24} gems")
    for v in versions:
        deb = runtimes.find_deb(s.agent_download_dir, v)
        if not deb:
            sn = sn or _sn(s)
            agents.download_catalog(agents.read_catalog(sn, v), s.agent_download_dir, ["linux-x86_64-deb"])
            deb = runtimes.find_deb(s.agent_download_dir, v)
        if not deb:
            print(f"{v:9} no deb package available")
            continue
        rt = runtimes.inspect_deb(deb)
        if rt.error:
            print(f"{v:9} {rt.error}")
            continue
        gems = ", ".join(f"{k} {val}" for k, val in sorted(rt.gems.items()))
        print(f"{v:9} {rt.ruby + ' (' + rt.ruby_date + ')':24} {rt.openssl + ' (' + rt.openssl_date + ')':24} {gems}")
    print("\nA Ruby/OpenSSL CVE is fixed only by a build whose embedded version carries the fix; upgrading the instance app changes nothing on the servers.")
    return 0


def cmd_download(s: Settings, a) -> int:
    sn = _sn(s)
    cat = agents.read_catalog(sn, a.version)
    keys = [k for k in a.os.split(",") if k] if a.os else None
    m = agents.download_catalog(cat, s.agent_download_dir, keys, skip_existing=not a.force)
    for f in m["files"]:
        print(f"  {'ok ' if f.get('downloaded') else ('--' if f.get('available') else 'n/a')} {f.get('os_key', ''):22} {f['file']}  {(f.get('sha256') or '')[:16]}")
    print("manifest:", s.agent_download_dir / cat.version / "manifest.json")
    return 0


def cmd_lab(s: Settings, a) -> int:
    if s.lab_mode != "proxmox":
        print("LAB_MODE is not 'proxmox' - lab commands are for the home lab only")
        return 1
    if a.action == "provision":
        ts = lab.provision(s)
        print(f"{len(ts)} targets written to {s.targets_file}:")
        for t in ts:
            print(f"  {t.name:22} CT {t.vmid}  {t.distro:28} {t.host:16} {t.os}")
    elif a.action == "destroy":
        gone = lab.destroy(s, force=a.force)
        print("destroyed:", gone or "nothing")
    else:
        for row in lab.status(s):
            print(f"  {row['name']:22} CT {row['vmid']}  {row['status']:10} {row['host']:16} {row['os']}")
    return 0


def cmd_mid(s: Settings, a) -> int:
    sn = _sn(s)
    if a.action == "setup":
        st = midmod.ensure_listener(sn, s)
        print(f"MID {st['mid']['name']}: listener {st['action']}, endpoint {st['endpoint_url']}")
        print("  web server:", st["webserver"])
        print("  endpoint  :", st["endpoint"])
    elif a.action == "sync":
        out = midmod.sync_plugins(sn, s.mid_server_name)
        print(json.dumps(out, indent=1))
    else:
        print(json.dumps(midmod.listener_status(sn, s.mid_server_name), indent=1))
    return 0


def cmd_apikey(s: Settings, a) -> int:
    sn = _sn(s)
    k = midmod.ensure_api_key(sn, s)
    print(f"API key '{k['name']}' [{k['action']}] - value stored in {s.env_path} as ACC_API_KEY ({len(k['key'])} chars)")
    return 0


def cmd_fixtures(s: Settings, a) -> int:
    sn = _sn(s)
    if a.action == "create":
        out = fixtures.create(sn, table=a.table, ci_filter=a.filter or "", settings=s)
    elif a.action == "delete":
        out = fixtures.delete(sn)
    else:
        out = fixtures.status(sn)
    print(json.dumps(out, indent=1, default=str))
    return 0


def cmd_run(s: Settings, a) -> int:
    only = [x for x in a.targets.split(",") if x] if a.targets else None
    r = Runner(s, version=a.version, install_mode=a.mode or s.agent_install_mode, skip_install=a.skip_install, only_targets=only)
    run = r.execute()
    out = s.results_dir / run.version / f"{r.basename}.html"
    verdict = run.agent_verdict()
    env = run.env_failures()
    print(f"\nAGENT VERDICT {'SAFE' if verdict == 'pass' else ('NOT SAFE' if verdict == 'fail' else 'NOT TESTED')}: "
          f"{len(run.agent_failures())} agent-owned failure(s), {len(env)} environment finding(s) (server / instance content / MID)")
    print(f"ALL TESTS {run.overall().upper()}  {run.counts()}\nreport: {out}")
    # the exit code follows the AGENT verdict: environment findings are reported, they do not fail the qualification
    return 0 if verdict == "pass" else 1


def cmd_report(s: Settings, a) -> int:
    d = s.results_dir / a.version
    base = a.file or "result"
    j = json.loads((d / f"{base}.json").read_text(encoding="utf-8"))
    run = RunResult(**{k: v for k, v in j.items() if k in RunResult.__dataclass_fields__ and k != "results"})
    run.results = [TestResult(**{k: v for k, v in r.items() if k in TestResult.__dataclass_fields__}) for r in j["results"]]
    # a result.json written before cause attribution existed: attribute from the stored evidence
    from . import checks
    for r in run.results:
        if r.status in ("fail", "error") and not r.cause:
            if r.id == "resources.plugins" and "CRLF" in r.message:
                r.cause = "content"
            else:
                r.cause = checks.attribute({"output": (r.details or "") + "\n" + r.message}, r.status)[0]
    # fixture checks stored as pass whose output is a module error (rule added later): re-judge from the stored output
    import re as _re
    from . import fixtures
    for r in run.results:
        names = [n for n in _re.findall(r"'([^']+)'", r.name or "") if fixtures.is_fixture(n)]
        if r.status == "pass" and names and len(r.details or "") < 6000:
            ok, why = fixtures.verify_output(names[0], r.details or "")
            if not ok:
                r.status = "fail"
                r.cause = checks.attribute({"outcome": "complete", "output": r.details or ""}, "fail")[0]
                r.message = f"{r.message}; re-verified from the stored output: {why}"
    p = write_report(run, d, base)
    write_index(s.results_dir)
    print("written:", p)
    return 0


def cmd_uninstall(s: Settings, a) -> int:
    from .installer import Installer
    from .targets import make_transport, probe
    sn = _sn(s)
    cat = agents.read_catalog(sn, a.version)
    only = [x for x in a.targets.split(",") if x] if a.targets else None
    rc = 0
    for t in load_targets(s):
        if only and t.name not in only and t.os not in only:
            continue
        tr = make_transport(t, s)
        facts = probe(tr, t.family)
        r = Installer(t, tr, facts, s, cat).uninstall()
        print(f"{t.name}: exit {r.rc}\n{r.text(1500)}")
        rc |= r.rc
    return rc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="acctest", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--env", help="path to the .env file (default ./.env or $ACCTEST_ENV)")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--version-info", action="store_true", help="print the tool version and exit")
    sub = p.add_subparsers(dest="cmd")
    e = sub.add_parser("env"); e.add_argument("action", nargs="?", default="check")
    sub.add_parser("preflight")
    x = sub.add_parser("versions"); x.add_argument("--version"); x.add_argument("--published", action="store_true", help="probe the download server for every published agent version")
    rt = sub.add_parser("runtimes", help="embedded Ruby / OpenSSL / gems per agent version (from dist/, downloading the deb when missing)")
    rt.add_argument("--version", action="append", help="repeatable; default: every version in dist/")
    d = sub.add_parser("download"); d.add_argument("--version"); d.add_argument("--os", help="comma separated os keys"); d.add_argument("--force", action="store_true")
    lb = sub.add_parser("lab"); lb.add_argument("action", choices=["provision", "destroy", "status"]); lb.add_argument("--force", action="store_true")
    m = sub.add_parser("mid"); m.add_argument("action", choices=["setup", "status", "sync"])
    sub.add_parser("apikey")
    fx = sub.add_parser("fixtures"); fx.add_argument("action", choices=["create", "delete", "status"])
    fx.add_argument("--table", default="cmdb_ci_linux_server"); fx.add_argument("--filter", default="", help="encoded query selecting the test CIs, e.g. nameSTARTSWITHacc-")
    r = sub.add_parser("run"); r.add_argument("--version"); r.add_argument("--mode", choices=["package", "script"], default=None, help="default: AGENT_INSTALL_MODE from .env (package)")
    r.add_argument("--skip-install", action="store_true"); r.add_argument("--targets")
    rp = sub.add_parser("report"); rp.add_argument("version"); rp.add_argument("--file", help="basename inside results/<version>/ (default result; e.g. result-partial-20261108-0913)")
    u = sub.add_parser("uninstall"); u.add_argument("--version"); u.add_argument("--targets")
    a = p.parse_args(argv)
    if a.version_info:
        print("acctest", __version__)
        return 0
    if not a.cmd:
        p.print_help()
        return 2
    s = Settings.load(Path(a.env) if a.env else None)
    logdir = s.results_dir / "logs"
    setup_logging(a.verbose, logdir / f"acctest-{a.cmd}.log")
    try:
        return {"env": cmd_env, "preflight": cmd_preflight, "versions": cmd_versions, "download": cmd_download, "lab": cmd_lab,
                "mid": cmd_mid, "apikey": cmd_apikey, "fixtures": cmd_fixtures, "run": cmd_run, "report": cmd_report, "uninstall": cmd_uninstall,
                "runtimes": cmd_runtimes}[a.cmd](s, a)
    except SNError as e:
        print("ServiceNow error:", e, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
