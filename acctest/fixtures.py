"""Lab fixtures: CUSTOM content on the instance so the custom-content path is exercised even where none exists yet.

Three custom check definitions, each in its own published custom policy:

  acctest-custom-os-version   an allow-listed shipped command (basic inventory) used as a custom check - proves a
                              custom definition runs at all on a stock agent
  acctest-users-linux         a CUSTOM PLUGIN: a shell script deployed to the agent as the asset "acctest-scripts"
                              (bin/acctest_users.sh); lists local users with groups and admin status as JSON lines
  acctest-users-windows       the same plugin's PowerShell script (bin/acctest_users.ps1 through acctest_users.cmd)

How a custom plugin reaches an agent on ACC 7.x (learned on the instance, 2026-11-08):
  * sn_agent_asset + ONE attachment named <asset>.tar.gz (validator: [A-Za-z0-9_.-], < 100 chars, must end .tar.gz);
    inside: bin/<scripts> (mode 0755) and allow_list/<name>.json - the agent merges that allow-list with its own, so the
    check command needs an "exec" entry there or the agent answers "check command denied by the agent allow list".
  * the record cannot be inserted over REST without its attachment (the before-insert validator aborts), so it is
    inserted from a run-once script with workflow off, the file is attached, then it is activated with workflow on.
  * sha512 is computed by the platform from the attachment; the MID serves the file under
    /static/acc_plugin/<os>/<platform>/<version>/<arch>/<name>.tar.gz once it has synced (the MID is restarted when the
    agent reports ACC-1500 / asset errors - see runner).
  * a check definition points at the asset through sn_agent_asset_name (the glide_list `assets`), and at a CI class
    through sn_agent_check_group.ci_type (so the Linux script is never offered to a Windows agent).

Everything is named acctest-* and removed by `fixtures delete`. At the company the real custom definitions and
policies are tested in the same run; these exist for environments without them.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import logging
import re
import subprocess
import tarfile
import time
import uuid
from pathlib import Path

from .snow import SNClient, SNError

LOG = logging.getLogger("acctest.fixtures")

ASSET_NAME = "acctest-scripts"
PLUGIN_DIR = Path(__file__).resolve().parent / "fixture_plugin"
MARKER = "ACCTEST_USERS v1"

# name -> definition. `expect` is checked by the runner against the test output (fixture-aware verification).
FIXTURES = {
    "acctest-custom-os-version": {
        "label": "acctest custom OS version", "command": "endpoint_discovery.rb --compact --select=basic_inventory",
        "assets_from": "check-discovery-basic", "ci_type": "cmdb_ci_linux_server", "group": "acctest-linux",
        "policy": "acctest-custom-policy", "policy_table": "cmdb_ci_linux_server", "timeout": "60",
        "description": "acctest fixture: a custom check definition reusing an allow-listed shipped command",
        "expect": {"os": None, "user": None},
    },
    "acctest-users-linux": {
        "label": "acctest local users (Linux)", "command": "acctest_users.sh", "assets_from": ASSET_NAME,
        "ci_type": "cmdb_ci_linux_server", "group": "acctest-linux", "policy": "acctest-users-linux-policy",
        "policy_table": "cmdb_ci_linux_server", "timeout": "120",
        "description": "acctest fixture: a custom plugin script (sh) deployed through an asset, lists local users and their groups",
        "expect": {"os": "linux", "user": "root"},
    },
    "acctest-users-windows": {
        "label": "acctest local users (Windows)", "command": "acctest_users.cmd", "assets_from": ASSET_NAME,
        "ci_type": "cmdb_ci_win_server", "group": "acctest-windows", "policy": "acctest-users-windows-policy",
        "policy_table": "cmdb_ci_win_server", "timeout": "180",
        "description": "acctest fixture: a custom plugin script (PowerShell) deployed through an asset, lists local users and their groups",
        "expect": {"os": "windows", "user": "Administrator"},
    },
}
# kept for callers of the old single-fixture API
CHECK_NAME = "acctest-custom-os-version"
POLICY_NAME = "acctest-custom-policy"
COMMAND = FIXTURES[CHECK_NAME]["command"]


def is_fixture(check_name: str) -> bool:
    return check_name in FIXTURES


# ---- the plugin archive ---------------------------------------------------------------------------------------------
def build_plugin(dest: Path | None = None) -> Path:
    """acctest-scripts.tar.gz from fixture_plugin/: bin/* executable, LF line endings (CRLF only for the .cmd), no
    platform noise (no ._ files, uid/gid 0, fixed mtime) so the hash is stable across machines."""
    dest = dest or (Path(__file__).resolve().parent.parent / ".state")
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{ASSET_NAME}.tar.gz"
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz", format=tarfile.GNU_FORMAT) as tf:
        for p in sorted(PLUGIN_DIR.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(PLUGIN_DIR).as_posix()
            data = p.read_bytes().replace(b"\r\n", b"\n")
            if p.suffix.lower() == ".cmd":
                data = data.replace(b"\n", b"\r\n")
            ti = tarfile.TarInfo(rel)
            ti.size = len(data)
            ti.mtime = 1_700_000_000
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = "root"
            ti.mode = 0o755 if rel.startswith("bin/") else 0o644
            tf.addfile(ti, io.BytesIO(data))
    out.write_bytes(buf.getvalue())
    return out


def _sha512(p: Path) -> str:
    return hashlib.sha512(p.read_bytes()).hexdigest()


# ---- signing ------------------------------------------------------------------------------------------------------------
# How ACC 7.x verifies a plugin (worked out against ServiceNow's own signed assets, 2026-11-08):
#   outer <name>.tar.gz = { <name>.sig , <name>.tar.gz (the real plugin) }   (ServiceNow also ships a .t64 PKCS7 blob - optional)
#   <name>.sig = base64( RSA PKCS#1 v1.5 signature, SHA-256, over the inner tar.gz bytes )
#   the agent tries every certificate under <conf>/cert/servicenow and <conf>/cert/customer; a customer certificate reaches
#   the agent as a zip the MID serves from <MID home>/agent/static/cert/customer/<anything>.zip (PEM .cer files inside)
#   and the certificate must chain to a root the HOST trusts ("x509: certificate signed by unknown authority" otherwise) -
#   at the company that is the internal CA; in the lab the self-signed signing certificate is installed as a root.
def signing_material(settings) -> tuple[Path, Path]:
    """(key, cert) PEM files of the plugin-signing certificate: the configured ones, or a lab pair generated once under
    .state/signing. The lab pair is a two-tier PKI - a root CA (no EKU) that the hosts trust, and a code-signing leaf
    issued by it - because RHEL/SUSE (p11-kit) leave an anchor WITHOUT the serverAuth purpose out of the TLS bundle that
    Go programs such as the agent read; a plain self-signed code-signing certificate is trusted on Debian/Ubuntu only."""
    if settings.plugin_signing_key and settings.plugin_signing_cert:
        return Path(settings.plugin_signing_key).expanduser(), Path(settings.plugin_signing_cert).expanduser()
    d = Path(__file__).resolve().parent.parent / ".state" / "signing"
    d.mkdir(parents=True, exist_ok=True)
    key, cert, ca_key, ca = d / "acctest-signing.key", d / "acctest-signing.cer", d / "acctest-lab-root.key", d / "acctest-lab-root.cer"
    if not (key.exists() and cert.exists() and ca.exists()):
        import os
        env = dict(os.environ, MSYS_NO_PATHCONV="1")   # Git Bash would rewrite the -subj path
        run = lambda *a: subprocess.run(["openssl", *a], check=True, capture_output=True, env=env)
        run("req", "-x509", "-newkey", "rsa:4096", "-sha256", "-days", "3650", "-nodes", "-keyout", str(ca_key), "-out", str(ca),
            "-subj", "/C=US/O=acctest lab/CN=acctest lab root CA", "-addext", "basicConstraints=critical,CA:true", "-addext", "keyUsage=critical,keyCertSign,cRLSign")
        csr = d / "acctest-signing.csr"
        run("req", "-new", "-newkey", "rsa:4096", "-sha256", "-nodes", "-keyout", str(key), "-out", str(csr), "-subj", "/C=US/O=acctest lab/CN=acctest plugin signing")
        ext = d / "leaf.ext"
        ext.write_text("basicConstraints=CA:false\nkeyUsage=digitalSignature\nextendedKeyUsage=codeSigning\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n")
        run("x509", "-req", "-in", str(csr), "-CA", str(ca), "-CAkey", str(ca_key), "-CAcreateserial", "-days", "1095", "-sha256", "-out", str(cert), "-extfile", str(ext))
        LOG.info("generated a lab root CA and plugin-signing certificate in %s", d)
    return key, cert


def trust_anchor(settings) -> Path:
    """The certificate the HOSTS must trust for signed plugins: the configured CA (PLUGIN_SIGNING_CA), else the lab root,
    else the signing certificate itself."""
    if settings.plugin_signing_ca:
        return Path(settings.plugin_signing_ca).expanduser()
    key, cert = signing_material(settings)
    ca = cert.parent / "acctest-lab-root.cer"
    return ca if ca.exists() and not settings.plugin_signing_cert else cert


def sign_plugin(inner: Path, key: Path, out: Path | None = None) -> Path:
    """Wrap the plugin archive in the signed outer archive ACC expects. Returns the outer file (same base name)."""
    sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(key), str(inner)], check=True, capture_output=True).stdout
    base = inner.name[:-len(".tar.gz")]
    out = out or inner.with_name(f"{base}.signed.tar.gz")
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz", format=tarfile.GNU_FORMAT) as tf:
        for name, data in ((f"{base}.sig", base64.b64encode(sig)), (f"{base}.tar.gz", inner.read_bytes())):
            ti = tarfile.TarInfo(name)
            ti.size, ti.mtime, ti.mode, ti.uid, ti.gid = len(data), 1_700_000_000, 0o644, 0, 0
            tf.addfile(ti, io.BytesIO(data))
    out.write_bytes(buf.getvalue())
    return out


def build_cert_zip(cert: Path, out_dir: Path) -> Path:
    """The zip the MID serves to agents from <MID home>/agent/static/cert/customer/ (same layout as SNCertificates.zip).
    Named after the certificate's fingerprint: an agent that already holds a zip of a given name does not fetch it
    again, so a re-issued certificate under the old zip name never reaches agents that saw the first one."""
    import zipfile
    fp = hashlib.sha256(cert.read_bytes()).hexdigest()[:12]
    out = out_dir / f"acctest-customer-certs-{fp}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(cert, f"acctestCertificates-{fp}/{cert.name}")
    return out


def signed_plugin(settings) -> tuple[Path, Path, Path]:
    """(outer signed archive named <asset>.tar.gz, certificate zip for the MID, certificate). Builds everything."""
    key, cert = signing_material(settings)
    stage = Path(__file__).resolve().parent.parent / ".state" / "signing"
    stage.mkdir(parents=True, exist_ok=True)
    inner = build_plugin(stage / "inner")
    (stage / "upload").mkdir(parents=True, exist_ok=True)
    outer = sign_plugin(inner, key, stage / "upload" / f"{ASSET_NAME}.tar.gz")   # the attachment must be named <asset>.tar.gz
    zipf = build_cert_zip(cert, stage)
    return outer, zipf, cert


def ensure_asset(sn: SNClient, tar: Path) -> dict:
    """The sn_agent_asset 'acctest-scripts' (os/platform/arch = all) carrying `tar`. Replaces the attachment when the
    local file differs. Returns {asset_id, asset_name_id, sha512, state}."""
    out: dict = {"local_sha512": _sha512(tar)}
    a = sn.first("sn_agent_asset", f"name={ASSET_NAME}^directory=false", "sys_id,sha512,active")
    if not a:
        aid = uuid.uuid4().hex
        sn.run_script(
            "var gr = new GlideRecord('sn_agent_asset'); gr.initialize(); gr.setNewGuidValue(%s); gr.setValue('name', %s);"
            "gr.setValue('os', 'all'); gr.setValue('platform', 'all'); gr.setValue('arch', 'all'); gr.setValue('active', false);"
            "gr.setValue('description', 'acctest fixture: custom plugin scripts (acctest_users.sh / .ps1)'); gr.setWorkflow(false);"
            "var id = gr.insert(); OUT({id: id});" % (json.dumps(aid), json.dumps(ASSET_NAME)), 120, "asset-insert")
        a = {"sys_id": aid, "sha512": "", "active": "false"}
        out["state"] = "created"
    else:
        out["state"] = "existing"
    aid = a["sys_id"]
    att = sn.first("sys_attachment", f"table_name=sn_agent_asset^table_sys_id={aid}", "sys_id,file_name,size_bytes")
    if att and (a.get("sha512") or "") != out["local_sha512"]:
        sn.delete("sys_attachment", att["sys_id"])
        att = None
        out["state"] = "attachment replaced"
    if not att:
        r = sn.s.post(f"{sn.instance}/api/now/attachment/file",
                      params={"table_name": "sn_agent_asset", "table_sys_id": aid, "file_name": tar.name},
                      data=tar.read_bytes(), headers={"Content-Type": "application/gzip"}, timeout=sn.timeout)
        if r.status_code >= 400:
            raise SNError(f"attaching {tar.name} -> {r.status_code}: {r.text[:300]}")
        time.sleep(3)
    res = sn.run_script(
        "var gr = new GlideRecord('sn_agent_asset'); if (!gr.get(%s)) { OUT({error: 'asset vanished'}); } else {"
        "gr.setValue('active', true); gr.setWorkflow(true); gr.update();"
        "var h = ''; try { h = String(new global.AgentGlobalUtils().getSHA512(gr.getUniqueValue())); } catch (e) { h = 'ERR ' + e; }"
        "if (h && h.indexOf('ERR') != 0) { gr.setValue('sha512', h); gr.setWorkflow(false); gr.update(); }"
        "var n = new GlideRecord('sn_agent_asset_name'); n.addQuery('name', gr.getValue('name')); n.query();"
        "if (!n.next()) { n.initialize(); n.setValue('name', gr.getValue('name')); n.insert(); n.get(n.getUniqueValue()); }"
        "OUT({active: gr.getValue('active'), sha512: gr.getValue('sha512'), name: gr.getValue('name'), name_id: n.getUniqueValue(), hash_err: h.indexOf('ERR') == 0 ? h : ''}); }"
        % json.dumps(aid), 180, "asset-activate")
    info = (res or [{}])[0]
    if info.get("error"):
        raise SNError(info["error"])
    out.update({"asset_id": aid, "asset_name_id": info.get("name_id"), "sha512": info.get("sha512"), "active": info.get("active"),
                "hash_err": info.get("hash_err")})
    if out["sha512"] != out["local_sha512"]:
        out["warning"] = "instance sha512 differs from the local file (platform computes it from the attachment)"
    return out


# ---- groups, definitions, policies -------------------------------------------------------------------------------
def ensure_group(sn: SNClient, name: str, ci_type: str) -> str:
    g = sn.first("sn_agent_check_group", f"group={name}", "sys_id,ci_type")
    if g:
        if g.get("ci_type") != ci_type:
            sn.update("sn_agent_check_group", g["sys_id"], {"ci_type": ci_type})
        return g["sys_id"]
    return sn.insert("sn_agent_check_group", {"group": name, "ci_type": ci_type})["sys_id"]


def status(sn: SNClient) -> dict:
    out: dict = {"asset": sn.first("sn_agent_asset", f"name={ASSET_NAME}^directory=false", "sys_id,active,sha512,os,platform,arch"), "fixtures": {}}
    for name, f in FIXTURES.items():
        d = sn.first("sn_agent_check_def", f"name={name}", "sys_id,name,active,command,assets,check_group.ci_type")
        p = sn.first("sn_agent_policy", f"name={f['policy']}", "sys_id,name,active,publish_status,is_draft,table,filter", display="all")
        checks = sn.query("sn_agent_check", f"monitoring_policy.name={f['policy']}", "sys_id,name,active,is_draft", 20) if p else []
        out["fixtures"][name] = {"check_def": d, "policy": p, "check_instances": checks}
    return out


def create(sn: SNClient, table: str = "cmdb_ci_linux_server", ci_filter: str = "", wait_publish_s: int = 300, settings=None) -> dict:
    """Create or refresh everything. `table`/`ci_filter` apply to the Linux policies; the Windows policy uses
    cmdb_ci_win_server with the same filter. With `settings` the plugin archive is SIGNED (see signed_plugin)."""
    out: dict = {}
    if settings is not None:
        tar, certzip, cert = signed_plugin(settings)
        out["plugin"] = str(tar)
        out["signed_with"] = str(cert)
        out["certificate_zip_for_mid"] = str(certzip)
        out["mid_certificate_dir"] = "<MID Server home>/agent/static/cert/customer/  (copy the zip there; agents fetch it on the next verification failure)"
        from . import mid as midmod
        out["mid_publish"] = midmod.publish_customer_certs(settings, certzip)
        if out["mid_publish"].get("published"):
            out["mid_serves_zip"] = midmod.customer_cert_served(settings, certzip.name)
    else:
        tar = build_plugin()
        out["plugin"] = str(tar)
    out["asset"] = ensure_asset(sn, tar)
    name_ids = {n["name"]: n["sys_id"] for n in sn.query("sn_agent_asset_name", "", "sys_id,name", 200)}
    for name, f in FIXTURES.items():
        res: dict = {}
        gid = ensure_group(sn, f["group"], f["ci_type"])
        if f["assets_from"] == ASSET_NAME:
            assets = out["asset"]["asset_name_id"] or name_ids.get(ASSET_NAME, "")
        else:
            tmpl = sn.first("sn_agent_check_def", f"name={f['assets_from']}", "assets") or {}
            assets = tmpl.get("assets", "")
        fields = {"name": name, "label": f["label"], "command": f["command"], "exec_mode": "execv", "timeout": f["timeout"],
                  "interval": "3600", "is_interval": "true", "active": "true", "assets": assets, "check_group": gid,
                  "send_results": "always", "description": f["description"]}
        d = sn.first("sn_agent_check_def", f"name={name}", "sys_id,command,assets,check_group")
        if not d:
            d = sn.insert("sn_agent_check_def", fields)
            res["check_def"] = "created"
        else:
            if d.get("command") != f["command"] or d.get("assets") != assets or d.get("check_group") != gid:
                sn.update("sn_agent_check_def", d["sys_id"], {"command": f["command"], "assets": assets, "check_group": gid})
                res["check_def"] = "updated"
            else:
                res["check_def"] = "existing"
        res["check_def_id"] = d["sys_id"]

        ptable = f["policy_table"] if f["policy_table"] != "cmdb_ci_linux_server" else table
        p = sn.first("sn_agent_policy", f"name={f['policy']}", "sys_id,publish_status,is_draft,active")
        if not p:
            p = sn.insert("sn_agent_policy", {
                "name": f["policy"], "description": f"acctest fixture: schedules {name} on the test servers",
                "table": ptable, "filter": ci_filter, "active": "true", "is_interval": "true", "interval": "3600",
                "checks_str": d["sys_id"],   # the platform refuses a policy without it and generates the instances from it
            })
            res["policy"] = "created"
            time.sleep(5)
        else:
            res["policy"] = "existing"
        res["policy_id"] = p["sys_id"]
        c = sn.first("sn_agent_check", f"monitoring_policy={p['sys_id']}^check_def={d['sys_id']}", "sys_id,command") or \
            sn.first("sn_agent_check", f"monitoring_policy={p['sys_id']}^name={name}", "sys_id,command")
        if not c:
            c = sn.insert("sn_agent_check", {"name": name, "label": f["label"], "monitoring_policy": p["sys_id"], "check_def": d["sys_id"],
                                             "command": f["command"], "exec_mode": "execv", "timeout": f["timeout"], "interval": "3600",
                                             "is_interval": "true", "active": "true"})
            res["check_instance"] = "created"
        else:
            if c.get("command") != f["command"]:
                sn.update("sn_agent_check", c["sys_id"], {"command": f["command"]})
            res["check_instance"] = "existing"
        res["check_instance_id"] = c["sys_id"]
        res.update(publish(sn, p["sys_id"], wait_publish_s))
        out[name] = res
    return out


def publish(sn: SNClient, policy_id: str, wait_s: int = 300) -> dict:
    """Sandbox -> published through the ACC API, like the Publish button; waits for the status."""
    out: dict = {}
    r = sn.s.get(f"{sn.instance}/api/sn_agent/agents/policy/publish/{policy_id}", timeout=sn.timeout)
    out["publish_http"] = r.status_code
    deadline = time.time() + wait_s
    while time.time() < deadline:
        pp = sn.first("sn_agent_policy", f"sys_id={policy_id}", "publish_status,publish_error,is_draft", display="all") or {}
        st = pp.get("publish_status")
        st = st.get("display_value") if isinstance(st, dict) else st
        err = pp.get("publish_error")
        out["publish_status"] = st
        out["publish_error"] = err.get("value") if isinstance(err, dict) else err
        if st in ("Published", "Published*", "Error", "Not processed"):
            break
        time.sleep(10)
    return out


def delete(sn: SNClient) -> dict:
    out: dict = {}
    for name, f in FIXTURES.items():
        p = sn.first("sn_agent_policy", f"name={f['policy']}", "sys_id")
        if p:
            try:
                sn.s.get(f"{sn.instance}/api/sn_agent/agents/policy/deactivate/{p['sys_id']}", timeout=sn.timeout)
            except Exception:
                pass
            for ch in sn.query("sn_agent_policy", f"published_parent={p['sys_id']}^ORrelated_policy={p['sys_id']}", "sys_id", 20):
                for c in sn.query("sn_agent_check", f"monitoring_policy={ch['sys_id']}", "sys_id", 50):
                    sn.delete("sn_agent_check", c["sys_id"])
                sn.delete("sn_agent_policy", ch["sys_id"])
            for c in sn.query("sn_agent_check", f"monitoring_policy={p['sys_id']}", "sys_id", 50):
                sn.delete("sn_agent_check", c["sys_id"])
            sn.delete("sn_agent_policy", p["sys_id"])
            out[f["policy"]] = "deleted"
        d = sn.first("sn_agent_check_def", f"name={name}", "sys_id")
        if d:
            for pd in sn.query("sn_agent_check_param_def", f"check_def={d['sys_id']}", "sys_id", 50):
                sn.delete("sn_agent_check_param_def", pd["sys_id"])
            sn.delete("sn_agent_check_def", d["sys_id"])
            out[name] = "deleted"
    for g in sn.query("sn_agent_check_group", "groupSTARTSWITHacctest-", "sys_id", 10):
        sn.delete("sn_agent_check_group", g["sys_id"])
    a = sn.first("sn_agent_asset", f"name={ASSET_NAME}^directory=false", "sys_id")
    if a:
        for att in sn.query("sys_attachment", f"table_name=sn_agent_asset^table_sys_id={a['sys_id']}", "sys_id", 5):
            sn.delete("sys_attachment", att["sys_id"])
        sn.delete("sn_agent_asset", a["sys_id"])
        out["asset"] = "deleted"
    return out


# ---- verification of what the scripts returned -----------------------------------------------------------------------
def verify_output(check_name: str, output: str, facts: dict | None = None) -> tuple[bool, str]:
    """Did the custom script do its job? For the user-listing scripts: header marker, one valid JSON object per user with
    the expected keys, the footer count matching, and the OS's built-in administrator present."""
    f = FIXTURES.get(check_name)
    if not f:
        return True, ""
    exp = f["expect"]
    if exp["os"] is None:
        if not output.strip():
            return False, "empty output"
        if '"error_backtrace"' in output or '"error_msg"' in output:
            m = re.search(r'"error_msg":\s*"((?:[^"\\]|\\.){0,220})', output)
            return False, "the shipped module returned an error instead of data: " + (m.group(1) if m else output[:220])
        return True, "output present"
    lines = [l.rstrip("\r") for l in output.splitlines() if l.strip()]
    if not lines or not lines[0].startswith(MARKER):
        return False, f"first line is not the '{MARKER}' marker: {lines[0][:120] if lines else 'no output'}"
    if f"os={exp['os']}" not in lines[0]:
        return False, f"header says a different OS: {lines[0][:120]}"
    rows = []
    for l in lines[1:]:
        if l.startswith("{"):
            try:
                rows.append(json.loads(l))
            except ValueError:
                return False, f"a user line is not valid JSON: {l[:120]}"
    if not rows:
        return False, "no user lines"
    bad = [r for r in rows if not isinstance(r, dict) or "user" not in r or "groups" not in r or "admin" not in r]
    if bad:
        return False, f"{len(bad)} user line(s) lack user/groups/admin keys"
    users = {r["user"] for r in rows}
    if exp["user"] not in users:
        return False, f"built-in account {exp['user']} missing from the {len(rows)} users returned"
    footer = [l for l in lines if l.startswith("ACCTEST_USERS end")]
    if not footer:
        return False, "footer line missing (script did not finish)"
    try:
        n = int(footer[-1].split("count=")[1].strip())
    except (IndexError, ValueError):
        n = -1
    if n != len(rows):
        return False, f"footer count {n} != {len(rows)} user lines"
    admins = sorted(r["user"] for r in rows if r.get("admin") is True)
    host = (facts or {}).get("HOST", "")
    if host and f"host={host}" not in lines[0] and f"host={host.upper()}" not in lines[0] and f"host={host.split('.')[0]}" not in lines[0]:
        return False, f"header host does not match the target ({host}): {lines[0][:120]}"
    return True, f"{len(rows)} users, {len(admins)} admin(s): {', '.join(admins[:6])}"
