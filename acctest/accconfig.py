"""The agent's shipped configuration per version: acc.yml defaults, the default command allow-list and the systemd
unit, read from the Ubuntu x86_64 package of every published version, and what changed between versions.

Only facts are kept (key names, default values, which keys are documented but commented out, allow-list command
names, unit settings) - never ServiceNow's comment text. The result is cached in ``dist/configs.json`` and rendered
into the download pages by ``downloads``. A package that is not already in ``dist/<version>/`` is downloaded to a
temporary file, read and deleted, so collecting all versions needs disk for one package at a time.
"""
from __future__ import annotations

import hashlib
import io
import json
import logging
import re
import tarfile
import tempfile
from pathlib import Path

import requests

from .runtimes import _decompress, ar_members
from .util import iso_now, safe_name, version_key

LOG = logging.getLogger("acctest.accconfig")

ACC_YML = "etc/servicenow/agent-client-collector/acc.yml.example"
ALLOW_LIST = "etc/servicenow/agent-client-collector/check-allow-list.json.default"
UNIT = "lib/systemd/system/acc.service"

_KEY = re.compile(r"^(\s*)([A-Za-z0-9_.-]+):(?:\s+(.*?))?\s*$")
_ITEM = re.compile(r"^(\s*)-\s+(.*?)\s*$")


def _value(raw: str):
    raw = re.sub(r"\s+#.*$", "", raw or "").strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return raw


def parse_acc_yml(text: str) -> dict:
    """{'active': {dotted.key: value}, 'documented': {dotted.key: value}}. 'documented' = keys present only as a
    commented-out example (an option that exists but is off / at its built-in default). Lists become lists. Prose
    comments are ignored: a comment line counts only when it looks like `key: value` or a list item of such a key."""
    res: dict[str, dict] = {"active": {}, "documented": {}}
    stack: dict[bool, list[tuple[int, str]]] = {True: [], False: []}   # per kind: (indent, key) path
    last_list: dict[bool, str | None] = {True: None, False: None}
    for line in text.splitlines():
        if not line.strip() or line.strip() in ("---", "##", "#"):
            continue
        commented = line.lstrip().startswith("#")
        body = line.lstrip()[1:] if commented else line
        if commented and body.startswith("#"):
            continue
        kind = not commented        # True = active
        target = res["active"] if kind else res["documented"]
        m = _KEY.match(body)
        if m and not (commented and " " in m.group(2)):
            indent, key, val = len(m.group(1)), m.group(2), m.group(3)
            if commented and indent > 3 and not stack[kind]:
                continue        # an indented "word:" inside prose
            path = stack[kind]
            while path and path[-1][0] >= indent:
                path.pop()
            full = ".".join([p[1] for p in path] + [key])
            if val is None or val == "" or val.startswith("#"):
                path.append((indent, key))
                target.setdefault(full, None)
                last_list[kind] = full
            else:
                target[full] = _value(val)
                last_list[kind] = None
            continue
        mi = _ITEM.match(body)
        if mi and last_list[kind]:
            k = last_list[kind]
            cur = target.get(k)
            target[k] = (cur if isinstance(cur, list) else []) + [_value(mi.group(2))]
            continue
        if commented:
            continue            # prose
        last_list[kind] = None
    # a documented key that is also active is just the active one
    for k in list(res["documented"]):
        if k in res["active"]:
            del res["documented"][k]
    # parents that only group children carry no value of their own
    for kind in res.values():
        for k in [k for k, v in kind.items() if v is None and any(x.startswith(k + ".") for x in kind)]:
            del kind[k]
    return res


def parse_allow_list(text: str) -> dict:
    try:
        entries = json.loads(text)
    except ValueError as e:
        return {"error": f"not JSON: {e}", "count": 0, "commands": []}
    ents = [e for e in entries if isinstance(e, dict) and e.get("exec")]
    cmds = sorted({str(e["exec"]) for e in ents})
    free_args = sorted({str(e["exec"]) for e in ents if e.get("skip_arguments")})
    args: dict[str, list[str]] = {}
    regex = sorted({str(e["exec"]) for e in ents if e.get("use_regex")})
    for e in ents:
        if e.get("skip_arguments"):
            continue
        args.setdefault(str(e["exec"]), [])
        for a in e.get("args") or []:
            if str(a) not in args[str(e["exec"])]:
                args[str(e["exec"])].append(str(a))
    return {"count": len(entries), "commands": cmds, "any_arguments": free_args, "regex": regex,
            "args": {k: sorted(v) for k, v in sorted(args.items())}}


def parse_unit(text: str) -> dict:
    out: dict[str, str] = {}
    sec = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            sec = line[1:-1]
        elif "=" in line and not line.startswith(("#", ";")):
            k, v = line.split("=", 1)
            key = f"{sec}.{k.strip()}"
            out[key] = (out[key] + " | " + v.strip()) if key in out else v.strip()   # Environment= repeats
    return out


def read_deb(data: bytes) -> dict:
    found: dict[str, bytes] = {}
    for name, blob in ar_members(data):
        if not name.startswith("data.tar"):
            continue
        tf = tarfile.open(fileobj=io.BytesIO(_decompress(name, blob)))
        for m in tf.getmembers():
            n = m.name.lstrip("./")
            if m.isfile() and n in (ACC_YML, ALLOW_LIST, UNIT):
                found[n] = tf.extractfile(m).read()
    rec: dict = {}
    if ACC_YML in found:
        rec["acc_yml_sha256"] = hashlib.sha256(found[ACC_YML]).hexdigest()
        rec["acc_yml"] = parse_acc_yml(found[ACC_YML].decode("utf-8", "replace"))
    if ALLOW_LIST in found:
        rec["allow_list_sha256"] = hashlib.sha256(found[ALLOW_LIST]).hexdigest()
        rec["allow_list"] = parse_allow_list(found[ALLOW_LIST].decode("utf-8", "replace"))
    if UNIT in found:
        rec["unit"] = parse_unit(found[UNIT].decode("utf-8", "replace"))
    rec["missing"] = [n for n in (ACC_YML, ALLOW_LIST, UNIT) if n not in found]
    return rec


def _local_deb(dist_root: Path, version: str) -> Path | None:
    vdir = dist_root / safe_name(version)
    want = f"agent-client-collector-{version}-ubuntu-1804_amd64.deb"
    hits = list(vdir.rglob(want)) if vdir.exists() else []
    return hits[0] if hits else None


def collect(versions: list[str], dist_root: Path, base_url: str, cache: dict | None = None, force: bool = False) -> dict:
    """Config facts for every version, reusing cached entries unless `force`."""
    out = {"collected_at": iso_now(), "source": "Ubuntu x86_64 deb of each version", "versions": dict((cache or {}).get("versions", {}))}
    for v in sorted(versions, key=version_key):
        if v in out["versions"] and not force:
            continue
        local = _local_deb(dist_root, v)
        try:
            if local:
                data = local.read_bytes()
                src = "local"
            else:
                url = f"{base_url}agent-client-collector-{v}-ubuntu-1804_amd64.deb"
                LOG.info("downloading %s to read its configuration", url.rsplit("/", 1)[-1])
                with tempfile.TemporaryFile() as tmp:
                    with requests.get(url, stream=True, timeout=120) as r:
                        r.raise_for_status()
                        for chunk in r.iter_content(1 << 20):
                            tmp.write(chunk)
                    tmp.seek(0)
                    data = tmp.read()
                src = "downloaded"
            rec = read_deb(data)
            rec["package_sha256"] = hashlib.sha256(data).hexdigest()
            rec["read_from"] = src
        except Exception as e:  # noqa: BLE001 - record and carry on with the other versions
            LOG.warning("could not read the configuration of %s: %s", v, e)
            rec = {"error": str(e)}
        out["versions"][v] = rec
    return out


def load(dist_root: Path) -> dict | None:
    p = dist_root / "configs.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(cfg: dict, dist_root: Path) -> Path:
    p = dist_root / "configs.json"
    p.write_text(json.dumps(cfg, indent=1, sort_keys=False) + "\n", encoding="utf-8", newline="\n")
    return p


def _names(items, limit: int = 0) -> str:
    items = list(items)
    shown = items if not limit or len(items) <= limit else items[:limit]
    s = ", ".join(f"`{x}`" if x != "" else '`""` (empty)' for x in shown)
    return s + (f" and {len(items) - len(shown)} more" if len(shown) < len(items) else "")


def _fmt(v) -> str:
    if v is None:
        return "(empty)"
    if isinstance(v, list):
        return ", ".join(f"`{x}`" for x in v) if v else "(empty list)"
    return f"`{v}`" if v != "" else '`""`'


def diff(prev: dict | None, cur: dict, limit: int = 0) -> list[str]:
    """Human-readable differences in the shipped configuration from `prev` to `cur` (both read_deb records).
    `limit` > 0 shortens long name lists ("and N more")."""
    if not prev or "acc_yml" not in prev or "acc_yml" not in cur:
        return []
    out: list[str] = []
    pa, ca = prev["acc_yml"]["active"], cur["acc_yml"]["active"]
    pd, cd = prev["acc_yml"]["documented"], cur["acc_yml"]["documented"]
    for k in sorted(set(pa) | set(ca) | set(pd) | set(cd)):
        before = "set" if k in pa else ("documented" if k in pd else None)
        after = "set" if k in ca else ("documented" if k in cd else None)
        bv = pa.get(k, pd.get(k))
        av = ca.get(k, cd.get(k))
        if before is None:
            out.append(f"acc.yml: new key `{k}` " + (f"set to {_fmt(av)}" if after == "set" else f"documented (commented out, example {_fmt(av)})"))
        elif after is None:
            out.append(f"acc.yml: key `{k}` removed (was {'set to ' + _fmt(bv) if before == 'set' else 'documented'})")
        elif before != after:
            out.append(f"acc.yml: `{k}` " + ("now set to " + _fmt(av) + " (was only documented)" if after == "set"
                                              else "now only documented (was set to " + _fmt(bv) + ")"))
        elif bv != av:
            out.append(f"acc.yml: `{k}` default {_fmt(bv)} -> {_fmt(av)}" if before == "set"
                       else f"acc.yml: documented example of `{k}` {_fmt(bv)} -> {_fmt(av)}")
    pl, cl = prev.get("allow_list") or {}, cur.get("allow_list") or {}
    if pl and cl:
        add = sorted(set(cl.get("commands", [])) - set(pl.get("commands", [])))
        rem = sorted(set(pl.get("commands", [])) - set(cl.get("commands", [])))
        if add:
            out.append(f"allow-list: {len(add)} command(s) added: " + _names(add, limit))
        if rem:
            out.append(f"allow-list: {len(rem)} command(s) removed: " + _names(rem, limit))
        fa = sorted(set(pl.get("any_arguments", [])) - set(cl.get("any_arguments", [])) - set(rem))
        if fa:
            out.append("allow-list: no longer accepts any arguments for " + _names(fa, limit))
        fb = sorted(set(cl.get("any_arguments", [])) - set(pl.get("any_arguments", [])) - set(add))
        if fb:
            out.append("allow-list: now accepts any arguments for " + _names(fb, limit))
        pa_args, ca_args = pl.get("args") or {}, cl.get("args") or {}
        named = False
        for cmd in sorted(set(pa_args) & set(ca_args)):
            plus = [x for x in ca_args[cmd] if x not in pa_args[cmd]]
            minus = [x for x in pa_args[cmd] if x not in ca_args[cmd]]
            if plus or minus:
                named = True
                parts = []
                if plus:
                    parts.append(f"{len(plus)} allowed argument pattern(s) added: " + _names(plus, limit or 6))
                if minus:
                    parts.append(f"{len(minus)} removed: " + _names(minus, limit or 6))
                out.append(f"allow-list: `{cmd}` - " + "; ".join(parts))
        for cmd in sorted(set(cl.get("regex", [])) - set(pl.get("regex", [])) - set(add)):
            named = True
            out.append(f"allow-list: `{cmd}` arguments are now matched as regular expressions")
        if not (add or rem or fa or fb or named) and prev.get("allow_list_sha256") != cur.get("allow_list_sha256"):
            out.append("allow-list: the file changed without a change to commands or argument patterns (order or formatting)")
    pu, cu = prev.get("unit") or {}, cur.get("unit") or {}
    if pu and cu:
        for k in sorted(set(pu) | set(cu)):
            if pu.get(k) != cu.get(k):
                out.append(f"systemd unit: `{k}` {_fmt(pu.get(k)) if k in pu else '(absent)'} -> {_fmt(cu.get(k)) if k in cu else '(removed)'}")
    return out


def load_notes(dist_root: Path) -> dict:
    p = dist_root / "config-notes.json"
    return json.loads(p.read_text(encoding="utf-8")).get("versions", {}) if p.exists() else {}


def render_section(version: str, cfg: dict | None, all_versions: list[str], notes: dict | None = None) -> list[str]:
    """The 'Configuration (acc.yml)' section of one version page."""
    out = ["## Configuration (acc.yml)", ""]
    vs = (cfg or {}).get("versions", {})
    rec = vs.get(version)
    if not rec or "acc_yml" not in rec:
        why = (rec or {}).get("error") or "not collected yet - run `python acctest.py downloads --configs`"
        return out + [f"The shipped configuration of this version was not read ({why}).", ""]
    out += ["Defaults the deb installs as `acc.yml.example`, read from the Ubuntu x86_64 package. On a fresh install the "
            "install script copies it to `acc.yml` and fills in `backend-url` and `api-key` (or, MID-less, `instance-url` and "
            "`registration-key`); an upgrade keeps the existing `acc.yml`. The Windows MSI carries the same template (byte for "
            "byte in 7.1.3) and writes `C:\\ProgramData\\ServiceNow\\agent-client-collector\\config\\acc.yml`. The rpm ships no "
            "template: there `acc.yml` is written by `acc gateway mid` and has no `allow-list:` line. Linux path: "
            "`/etc/servicenow/agent-client-collector/acc.yml`.", ""]
    out += ["| Key | Default | Status |", "|---|---|---|"]
    a, d = rec["acc_yml"]["active"], rec["acc_yml"]["documented"]
    for k in a:
        out.append(f"| `{k}` | {_fmt(a[k])} | set |")
    for k in d:
        out.append(f"| `{k}` | {_fmt(d[k]) if not isinstance(d[k], list) else f'{len(d[k])} entries'} | documented, commented out |")
    al = rec.get("allow_list") or {}
    if al:
        out += ["", f"Default command allow-list (`check-allow-list.json.default`): {al.get('count', 0)} entries for "
                f"{len(al.get('commands', []))} commands, {len(al.get('any_arguments', []))} of them allowed with any arguments."]
    u = rec.get("unit") or {}
    if u:
        keep = [k for k in ("Service.User", "Service.Restart", "Service.RestartSec", "Service.KillMode", "Service.TimeoutStopSec",
                            "Service.CPUSchedulingPolicy", "Service.Nice", "Service.CPUWeight") if k in u]
        if keep:
            out += ["", "Service unit (`acc.service`, deb): " + ", ".join(f"{k.split('.', 1)[1]}={u[k]}" for k in keep) + "."]
    # change from the previous version that has a record
    ordered = sorted([v for v in vs if "acc_yml" in vs[v]], key=version_key)
    prev = [v for v in ordered if version_key(v) < version_key(version)]
    out += ["", "### Changes from the previous version", ""]
    if not prev:
        out += ["This is the oldest version read; nothing to compare with.", ""]
        return out
    p = prev[-1]
    ch = diff(vs[p], rec)
    for n in (notes or {}).get(version, []):
        out += [f"> {n}", ""]
    if not ch:
        out += [f"None - the shipped configuration, allow-list and unit are the same as in [{p}]({p}.md).", ""]
    else:
        out += [f"Compared with [{p}]({p}.md):", ""] + [f"- {c}" for c in ch] + [""]
    return out


def render_history(cfg: dict | None, notes: dict | None = None, highlights: list[str] | None = None) -> list[str]:
    """Index section: every version whose shipped configuration differs from the one before."""
    vs = (cfg or {}).get("versions", {})
    ordered = sorted([v for v in vs if "acc_yml" in vs[v]], key=version_key)
    out = ["## acc.yml changes across versions", "",
           f"Read from the Ubuntu x86_64 package of {len(ordered)} versions. Only versions whose shipped `acc.yml`, default "
           "allow-list or service unit differ from the version before are listed; each version page has its full default "
           "table.", ""]
    if highlights:
        out += ["What matters when upgrading:", ""] + [f"- {h}" for h in highlights] + [""]
    for prev, cur in zip(ordered, ordered[1:]):
        ch = diff(vs[prev], vs[cur], limit=8)
        if ch:
            out += [f"**[{cur}]({cur}.md)** (from {prev})", ""] + [f"> {n}" for n in (notes or {}).get(cur, [])] \
                + ([""] if (notes or {}).get(cur) else []) + [f"- {c}" for c in ch] + [""]
    return out
