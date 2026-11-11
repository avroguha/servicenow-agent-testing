"""Download index: every Agent Client Collector package ServiceNow publishes, per version, operating system and
architecture, written as Markdown pages into dist/ (``dist/README.md`` = all versions, ``dist/<version>.md`` = one
version with every package, its direct link, size, date on the server, signature file and SHA-256 where known).

The packages are ServiceNow's and stay on install.service-now.com - nothing is mirrored here. The server has no index,
so the catalog is built by HEAD requests: one per candidate version (``agents.published_versions``) and then one per
package file of every version found. The result is cached in ``dist/packages.json`` so the pages can be re-rendered
offline; SHA-256 sums are taken from the packages this tool downloaded into ``dist/<version>/`` and kept in the cache
once computed.

Each version page also carries a change log and the supported systems. Both come from the public ServiceNow Store
listing of the "Agent Client Collector Framework" app (JSON API under store.servicenow.com/api/sn_store/v1/): the
Framework app and the agent are released with the same version number (the 7.1.3 notes name the Ruby and OpenSSL that
agent 7.1.3 embeds). The Store keeps notes only for releases still offered for a supported platform family. The pages
show a summary written by hand in ``dist/changelog.json`` - ServiceNow's own text stays on the Store, linked - and
the cache keeps only a checksum of each version's notes, so a new or changed Store entry is flagged for review.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import html as htmllib
import json
import logging
import re
from datetime import datetime
from pathlib import Path

import requests

from . import accconfig
from .agents import published_versions
from .util import iso_now, safe_name, sha256_file, version_key

LOG = logging.getLogger("acctest.downloads")

BASE_URL = "https://install.service-now.com/glide/distribution/builds/package/app-signed/"

# Every package type ServiceNow has published, in the order the pages list them. `covers` is what the instance's
# install script installs it on (read from install_agent.sh: Ubuntu -> ubuntu-1804_amd64 / ubuntu-2204_arm64,
# Debian -> debian-9_amd64 whatever the release, every RHEL-like + SLES + Amazon Linux -> x86_64.rpm, macOS by arch).
PACKAGES = [
    {"classifier": "ubuntu-1804_amd64", "pkg": "deb", "os_key": "linux-x86_64-deb", "family": "linux", "arch": "x86_64",
     "label": "Ubuntu, x86_64 (.deb)",
     "covers": "every Ubuntu release (the install script picks this build for Ubuntu 18.04 and later and falls back to it for older ones); it also installs on other Debian-family distributions"},
    {"classifier": "debian-9_amd64", "pkg": "deb", "os_key": "", "family": "linux", "arch": "x86_64",
     "label": "Debian, x86_64 (.deb)",
     "covers": "every Debian release - the install script picks this build for Debian whatever the version (it is built on Debian 9)"},
    {"classifier": "debian-8_amd64", "pkg": "deb", "os_key": "", "family": "linux", "arch": "x86_64",
     "label": "Debian 8, x86_64 (.deb)",
     "covers": "Debian 8 only; published for the 2.x releases and 3.0.0, dropped afterwards"},
    {"classifier": "ubuntu-2204_arm64", "pkg": "deb", "os_key": "linux-aarch64-deb", "family": "linux", "arch": "aarch64",
     "label": "Ubuntu, ARM64 / aarch64 (.deb)",
     "covers": "Ubuntu 22.04 and later on ARM64 (the install script refuses older Ubuntu on ARM); published since 6.5.1"},
    {"classifier": "x86_64", "pkg": "rpm", "os_key": "linux-x86_64-rpm", "family": "linux", "arch": "x86_64",
     "label": "RHEL-family and SUSE, x86_64 (.rpm)",
     "covers": "RHEL, CentOS, Rocky, AlmaLinux, Oracle Linux, Amazon Linux, SLES and openSUSE (the install script accepts any distribution whose ID_LIKE says rhel or centos); published since 3.3.1. There is no ARM64 rpm"},
    {"classifier": "windows-x64", "pkg": "msi", "os_key": "windows-x86_64", "family": "windows", "arch": "x86_64",
     "label": "Windows, x64 (.msi)",
     "covers": "Windows Server and Windows desktops (the Store lists Windows 10 Enterprise and Windows 11 Pro/Enterprise), 64-bit Intel/AMD only. There is no Windows ARM64 build"},
    {"classifier": "macos_x64", "pkg": "pkg", "os_key": "macos-x86_64", "family": "macos", "arch": "x86_64",
     "label": "macOS, Intel (.pkg)",
     "covers": "macOS on Intel Macs (desktops and laptops); published since 2.9.0"},
    {"classifier": "macos_arm64", "pkg": "pkg", "os_key": "macos-arm64", "family": "macos", "arch": "arm64",
     "label": "macOS, Apple silicon (.pkg)",
     "covers": "macOS on Apple silicon (M-series) Macs; published since 3.1.0"},
]

STORE_LISTING_ID = "bc09636e1be06a50a85b16db234bcbd1"   # "Agent Client Collector Framework" on store.servicenow.com
STORE_API = "https://store.servicenow.com/api/sn_store/v1/store/listings/"
STORE_PAGE = "https://store.servicenow.com/store/app/" + STORE_LISTING_ID


def html_to_md(h: str) -> str:
    """The Store's small HTML fragments (p, ul/li nested, strong) as Markdown lines. Plain text, no links kept."""
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", h or "")
    out: list[str] = []
    depth = 0
    for tok in re.split(r"(?i)(</?ul[^>]*>|</?ol[^>]*>|<li[^>]*>|</li>|</p>|<br\s*/?>)", h):
        t = tok.lower()
        if t.startswith(("<ul", "<ol")):
            depth += 1
        elif t.startswith(("</ul", "</ol")):
            depth = max(0, depth - 1)
        elif t.startswith("<li"):
            out.append("  " * max(0, depth - 1) + "- ")
        elif t in ("</li>", "</p>") or t.startswith("<br"):
            out.append("\n")
        else:
            text = re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", "", tok))).replace("\u00a0", " ")
            if text.strip():
                if out and out[-1].endswith("- "):
                    out[-1] += text.strip()
                else:
                    out.append(text.strip())
    lines = [ln.rstrip() for ln in "\n".join(out).splitlines()]
    return "\n".join(ln for ln in lines if ln.strip() and ln.strip() != "-")


def systems_only(md: str) -> str:
    """From the listing's key-features text keep just the operating-system lists, under our own architecture headings."""
    out: list[str] = []
    for ln in md.splitlines():
        m = re.search(r"(?i)supported operating systems on (\S+) architecture", ln)
        if m:
            out += ["", f"**{m.group(1)}**", ""]
        elif ln.lstrip().startswith("- ") and out:
            out.append(ln)
    return "\n".join(out).strip()


def fetch_store(timeout: int = 60) -> dict:
    """The Framework listing from the public Store API: supported systems and every version still listed, with date,
    release type, compatible platform families and a checksum of its release notes (the text itself is not kept)."""
    hdr = {"Accept": "application/json"}
    listing = requests.get(STORE_API + STORE_LISTING_ID, headers=hdr, timeout=timeout)
    listing.raise_for_status()
    vers = requests.get(STORE_API + STORE_LISTING_ID + "/versions?limit=200", headers=hdr, timeout=timeout)
    vers.raise_for_status()
    L = listing.json()["result"]
    out = {"listing_url": STORE_PAGE, "fetched_at": iso_now(), "title": L.get("title", ""),
           "listed_version": (L.get("version_details") or {}).get("version", ""),
           "supported_systems_md": systems_only(html_to_md(L.get("key_features", ""))), "versions": []}
    for r in vers.json()["result"]["data"]:
        out["versions"].append({"version": r["version"], "publish_date": r.get("publish_date", ""),
                                "release_type": r.get("release_type", ""),
                                "families": [c.get("name", "") for c in r.get("compatibility_list") or []],
                                "notes_sha256": hashlib.sha256((r.get("release_notes") or "").encode("utf-8")).hexdigest()})
    return out


def load_changelog(dist_root: Path) -> dict:
    p = dist_root / "changelog.json"
    return json.loads(p.read_text(encoding="utf-8")).get("versions", {}) if p.exists() else {}


def changelog_problems(store: dict | None, changelog: dict) -> list[str]:
    """Store versions with no summary yet, or whose notes changed since the summary was written."""
    probs = []
    for sv in (store or {}).get("versions", []):
        e = changelog.get(sv["version"])
        if not e:
            probs.append(f"{sv['version']}: release notes on the Store have no summary in dist/changelog.json yet")
        elif e.get("notes_sha256") and e["notes_sha256"] != sv.get("notes_sha256"):
            probs.append(f"{sv['version']}: the Store's release notes changed since the summary was written - review it")
    return probs


SHORT = {"ubuntu-1804_amd64": "Ubuntu x86_64", "debian-9_amd64": "Debian x86_64", "debian-8_amd64": "Debian 8",
         "ubuntu-2204_arm64": "Ubuntu ARM64", "x86_64": "RPM x86_64", "windows-x64": "Windows x64",
         "macos_x64": "macOS Intel", "macos_arm64": "macOS ARM64"}


def package_file(version: str, p: dict) -> str:
    return f"agent-client-collector-{version}-{p['classifier']}.{p['pkg']}"


def signature_file(version: str, p: dict) -> str:
    """deb and rpm packages come with a zip holding the detached signature; msi and pkg are signed in place."""
    if p["pkg"] in ("msi", "pkg"):
        return ""
    return f"agent-client-collector-{version}-{p['classifier']}-{p['pkg']}-{p['pkg']}.zip"


def _head(url: str) -> dict:
    err = ""
    for _ in range(3):
        try:
            r = requests.head(url, timeout=30, allow_redirects=True)
            return {"available": r.status_code == 200, "status": r.status_code,
                    "size": int(r.headers.get("Content-Length", "0") or 0),
                    "last_modified": r.headers.get("Last-Modified", ""), "etag": r.headers.get("Install-Etag", "")}
        except requests.RequestException as e:
            err = str(e)
    return {"available": False, "status": 0, "size": 0, "last_modified": "", "etag": "", "error": err}


def probe(base_url: str = BASE_URL, versions: list[str] | None = None, workers: int = 16) -> dict:
    """Ask the download server what exists: every published version (unless given) and every package of each.
    Returns the catalog dict that the pages are rendered from."""
    if versions is None:
        found = published_versions(base_url)
        versions = [v["version"] for v in found]
    jobs: list[tuple[str, dict, str, str]] = []
    for v in versions:
        for p in PACKAGES:
            jobs.append((v, p, "package", package_file(v, p)))
            sig = signature_file(v, p)
            if sig:
                jobs.append((v, p, "signature", sig))
    LOG.info("probing %d files for %d versions on %s", len(jobs), len(versions), base_url)
    with cf.ThreadPoolExecutor(workers) as ex:
        heads = list(ex.map(lambda j: _head(base_url + j[3]), jobs))
    cat: dict = {"base_url": base_url, "probed_at": iso_now(), "versions": []}
    by_version: dict[str, list] = {v: [] for v in versions}
    for (v, p, kind, fname), h in zip(jobs, heads):
        by_version[v].append({"classifier": p["classifier"], "pkg": p["pkg"], "kind": kind, "file": fname,
                              "url": base_url + fname, **h})
    for v in sorted(versions, key=version_key):
        files = by_version[v]
        dates = [f["last_modified"] for f in files if f.get("available") and f.get("last_modified")]
        cat["versions"].append({"version": v, "files": files,
                                "last_modified": min(dates, key=_parse_date) if dates else ""})
    return cat


def _parse_date(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError:
        return datetime.min


def day(s: str) -> str:
    d = _parse_date(s)
    return d.strftime("%Y-%m-%d") if d != datetime.min else (s or "")


def merge_hashes(cat: dict, dist_root: Path, previous: dict | None = None) -> int:
    """SHA-256 of every file that exists locally under dist/<version>/ ; sums from a previous catalog are kept for
    files that are no longer on disk. Returns how many sums the catalog now carries."""
    prev: dict[str, str] = {}
    for v in (previous or {}).get("versions", []):
        for f in v.get("files", []):
            if f.get("sha256"):
                prev[f["file"]] = f["sha256"]
    n = 0
    for v in cat["versions"]:
        vdir = dist_root / safe_name(v["version"])
        local = {p.name: p for p in vdir.rglob("*")} if vdir.exists() else {}
        for f in v["files"]:
            p = local.get(f["file"])
            if p and p.is_file() and (not f.get("size") or p.stat().st_size == f["size"]):
                f["sha256"] = sha256_file(p)
            elif f["file"] in prev:
                f["sha256"] = prev[f["file"]]
            if f.get("sha256"):
                n += 1
    return n


def _mb(size: int) -> str:
    return f"{size / (1 << 20):.1f} MB" if size else ""


def _report_link(reports_dir: Path | None, version: str, rel: str) -> str:
    if reports_dir and (reports_dir / version / "README.md").exists():
        return f"[qualification report]({rel}reports/{version}/README.md)"
    return ""


CL_HEADS = (("new", "New"), ("changed", "Changed"), ("fixed", "Fixed"), ("security", "Security and library updates"),
            ("observed", "Observed by this harness"))


def render_changelog(v: str, store: dict | None, changelog: dict, all_versions: list[str]) -> list[str]:
    out = ["## Change log", ""]
    svs = {s["version"]: s for s in (store or {}).get("versions", [])}
    url = (store or {}).get("listing_url", STORE_PAGE)
    sv, cl = svs.get(v), changelog.get(v)
    if sv or cl:
        if sv:
            fam = ", ".join(sv.get("families") or [])
            out += [f"Agent Client Collector Framework {v}: {sv.get('release_type', '')} release, published on the Store "
                    f"{sv.get('publish_date', '')}" + (f", for the {fam} platform families." if fam else "."), ""]
        if cl:
            for key, head in CL_HEADS:
                items = cl.get(key) or []
                if items:
                    out += [f"**{head}**", ""] + [f"- {i}" for i in items] + [""]
            out += [f"Summarised from ServiceNow's release notes; the full text is on the [Store listing]({url}) "
                    "under Version details, Release notes.", ""]
        else:
            out += [f"ServiceNow published release notes for this version on the [Store listing]({url}); "
                    "they are not summarised here yet.", ""]
        return out
    # no Store entry with this number: say so and point at the neighbours that have one
    known = sorted(set(svs) | set(changelog), key=version_key)
    lower = [k for k in known if version_key(k) < version_key(v)]
    higher = [k for k in known if version_key(k) > version_key(v)]
    near = []
    if lower:
        near.append(f"[{lower[-1]}]({lower[-1]}.md)")
    if higher:
        near.append(f"[{higher[0]}]({higher[0]}.md)")
    if lower or not higher:
        why = ("The Store lists no Agent Client Collector Framework release with this number, so ServiceNow publishes no "
               "release notes for it (agent builds and Framework releases mostly share numbers, not always).")
    else:
        why = ("The Store keeps release notes only for Framework releases still offered for a supported platform family; "
               f"this version is older than the oldest one listed ({higher[0]}).")
    out += [why + (" Nearest versions with a change log: " + " and ".join(near) + "." if near else ""), ""]
    return out


def render_version(entry: dict, base_url: str, reports_dir: Path | None = None, store: dict | None = None,
                   changelog: dict | None = None, all_versions: list[str] | None = None, configs: dict | None = None) -> str:
    v = entry["version"]
    files = {(f["classifier"], f["kind"]): f for f in entry["files"]}
    out = [f"# Agent Client Collector {v} - downloads", "",
           "Every package ServiceNow publishes for this agent version, with the direct link on ServiceNow's download server. "
           "The agent is ServiceNow's product; the files are served by ServiceNow and are not mirrored in this repository. "
           "See [NOTICE.md](../NOTICE.md).", ""]
    rep = _report_link(reports_dir, v, "../")
    if rep:
        out += [f"This version was qualified with this harness: {rep}.", ""]
    out += [f"On the server since: {day(entry.get('last_modified', ''))} (earliest file date). Base URL: `{base_url}`", ""]
    out += ["| Operating system / architecture | Package | Size | On the server | Signature | SHA-256 |", "|---|---|---|---|---|---|"]
    for p in PACKAGES:
        pk = files.get((p["classifier"], "package"))
        sg = files.get((p["classifier"], "signature"))
        if not pk or not pk.get("available"):
            out.append(f"| {p['label']} | *not published for {v}* |  |  |  |  |")
            continue
        sig = f"[{sg['file']}]({sg['url']})" if sg and sg.get("available") else ("signed package" if p["pkg"] in ("msi", "pkg") else "*missing*")
        sha = f"`{pk['sha256']}`" if pk.get("sha256") else "download to verify"
        out.append(f"| {p['label']} | [{pk['file']}]({pk['url']}) | {_mb(pk.get('size', 0))} | {day(pk.get('last_modified', ''))} | {sig} | {sha} |")
    out += ["", "SHA-256 sums are shown for the packages this harness downloaded and checked; the others can be verified "
            "against the signature zip (deb/rpm: a detached signature over the package, checked by the install script with "
            "ServiceNow's certificate) or the embedded signature (msi/pkg).", ""]
    out += ["## Which package for which system", ""]
    for p in PACKAGES:
        pk = files.get((p["classifier"], "package"))
        if pk and pk.get("available"):
            out.append(f"* **{p['label']}** - {p['covers']}.")
    out += ["", "The packages are the same for servers and desktops: one Windows MSI, one rpm, one deb per architecture, "
            "one macOS pkg per architecture. Which operating system releases ServiceNow supports is listed in "
            "[Server or desktop](README.md#server-or-desktop) on the index page.", ""]
    out += render_changelog(v, store, changelog or {}, all_versions or [])
    out += accconfig.render_section(v, configs, all_versions or [], (configs or {}).get("_notes"))
    out += ["## Installing", "",
            "The instance's own install script (served at `/api/sn_agent/agents/install_agent`, Linux and macOS) downloads the right "
            "package for the host, verifies its signature, installs it and writes `acc.yml` with the MID endpoint and API key:", "",
            "```bash", f'ACC_VERSION={v} ACC_API_KEY="<api key>" ACC_MID="wss://<mid host>:8800/ws/events" bash -c "$(curl -L https://<instance>.service-now.com/api/sn_agent/agents/install_agent)"', "```", "",
            "By hand, with the package downloaded from the links above:", "",
            "```bash", f"sudo dpkg -i {package_file(v, PACKAGES[0])}      # Debian / Ubuntu (use the ARM64 or Debian file on those systems)",
            f"sudo rpm -vi {package_file(v, PACKAGES[4])}             # RHEL-family / SUSE",
            f"sudo installer -target / -pkg {package_file(v, PACKAGES[7])}   # macOS (Intel: the macos_x64 file)", "```", "",
            "```powershell", f'msiexec /i {package_file(v, PACKAGES[5])} /qn ACC_API_KEY="<api key>" ACC_MID="wss://<mid host>:8800/ws/events"', "```", "",
            "After a manual Linux or macOS install, set `endpoint` and `api-key` in `acc.yml` "
            "(`/etc/servicenow/agent-client-collector/acc.yml`) and restart the `acc` service. The Windows MSI takes both as properties.", ""]
    return "\n".join(out)


def render_index(cat: dict, reports_dir: Path | None = None, changelog: dict | None = None, configs: dict | None = None) -> str:
    versions = sorted(cat["versions"], key=lambda e: version_key(e["version"]), reverse=True)
    out = ["# Agent Client Collector - all published versions", "",
           "Every agent version on ServiceNow's download server and the packages that exist for it, found by asking the "
           f"server file by file (there is no index). Probed {cat.get('probed_at', '')[:10]}; base URL `{cat.get('base_url', BASE_URL)}`. "
           "Open a version for the direct links, sizes, signatures and SHA-256 sums. The packages are ServiceNow's and are "
           "not mirrored here (see [NOTICE.md](../NOTICE.md)).", "",
           "Regenerate with `python acctest.py downloads` (re-probes the server) or `python acctest.py downloads --no-probe` "
           "(re-renders from `packages.json`).", "",
           "## Package types", "", "| Column | File | Covers |", "|---|---|---|"]
    for p in PACKAGES:
        out.append(f"| {SHORT[p['classifier']]} | `agent-client-collector-<version>-{p['classifier']}.{p['pkg']}` | {p['covers']} |")
    store = cat.get("store") or {}
    out += ["", "## Server or desktop", "",
            "The same packages install on servers and on desktops or laptops - there is no separate desktop build. "
            "ServiceNow's Store listing describes the Framework as suitable for on-premises servers, VMs, cloud instances "
            "and end-user desktops and laptops, and lists these systems"
            + (f" for version {store['listed_version']}" if store.get("listed_version") else "")
            + (f" (fetched {store.get('fetched_at', '')[:10]} from the [Store listing]({store.get('listing_url', STORE_PAGE)})):" if store else ":"), ""]
    if store.get("supported_systems_md"):
        out += [store["supported_systems_md"], ""]
    else:
        out += [f"(not fetched - see the [Store listing]({STORE_PAGE}))", ""]
    out += ["Limits that matter for desktops and laptops:", "",
            "- There is no Windows build for ARM. The only ARM64 Linux build is for Ubuntu 22.04 or later. Apple silicon Macs are supported.",
            "- The Monitoring (ACC-M) and Log Analytics (ACC-L) apps that run on the agent are supported on server operating systems only.",
            "- The listing says the Framework does not support Virtual Desktop Infrastructure, while the 7.0.4 release notes announce "
            "official support for non-persistent VDI. Check with ServiceNow before relying on either.", ""]
    if configs:
        out += accconfig.render_history(configs, configs.get("_notes"), configs.get("_highlights"))
    latest = versions[0]["version"] if versions else ""
    out += ["", "## Versions", "", f"Latest: **[{latest}]({latest}.md)**." if latest else "", "",
            "| Version | On the server | " + " | ".join(SHORT[p["classifier"]] for p in PACKAGES) + " | Change log | acc.yml | Report |",
            "|---|---|" + "|".join(":-:" for _ in PACKAGES) + "|---|---|---|"]
    cv = (configs or {}).get("versions", {})
    cordered = sorted([x for x in cv if "acc_yml" in cv[x]], key=version_key)
    cchanged = {cur for prev, cur in zip(cordered, cordered[1:]) if accconfig.diff(cv[prev], cv[cur])}
    svs = {s["version"]: s for s in store.get("versions", [])}
    for e in versions:
        avail = {f["classifier"] for f in e["files"] if f["kind"] == "package" and f.get("available")}
        cells = " | ".join("yes" if p["classifier"] in avail else "-" for p in PACKAGES)
        rep = _report_link(reports_dir, e["version"], "../")
        sv = svs.get(e["version"])
        has = sv or (changelog or {}).get(e["version"])
        cl = f"[{(sv or {}).get('release_type') or 'yes'}]({e['version']}.md#change-log)" if has else "-"
        acc = (f"[changed]({e['version']}.md#changes-from-the-previous-version)" if e["version"] in cchanged
               else ("same" if e["version"] in cv and "acc_yml" in cv[e["version"]] and e["version"] != (cordered or [""])[0] else "-"))
        out.append(f"| [{e['version']}]({e['version']}.md) | {day(e.get('last_modified', ''))} | {cells} | {cl} | {acc} | {rep} |")
    out += ["", "\"On the server\" is the earliest file date the server reports for that version - releases older than "
            "2026 carry the date they were last copied there, not their release date. \"Change log\" names the release type "
            "ServiceNow gave the version on the Store; versions without one have no release notes there. \"acc.yml\" says "
            "whether the shipped configuration, default allow-list or service unit differs from the version before.", ""]
    pkg_versions = {e["version"] for e in cat["versions"]}
    store_only = [s["version"] for s in store.get("versions", []) if s["version"] not in pkg_versions]
    if store_only:
        out += ["Framework releases on the Store with no agent package of the same number (the app shipped no new agent "
                "build): " + ", ".join(f"[{v}]({v}.md)" for v in sorted(store_only, key=version_key)) + ".", ""]
    return "\n".join(out)


def write_pages(cat: dict, dist_root: Path, reports_dir: Path | None = None, changelog: dict | None = None,
                configs: dict | None = None) -> list[Path]:
    """Write dist/packages.json, dist/README.md and dist/<version>.md for every version in the catalog."""
    dist_root.mkdir(parents=True, exist_ok=True)
    written = []
    cache = dist_root / "packages.json"
    cache.write_text(json.dumps(cat, indent=1), encoding="utf-8")
    written.append(cache)
    idx = dist_root / "README.md"
    if changelog is None:
        changelog = load_changelog(dist_root)
    if configs is None:
        configs = accconfig.load(dist_root)
    if configs is not None:
        raw = (dist_root / "config-notes.json")
        data = json.loads(raw.read_text(encoding="utf-8")) if raw.exists() else {}
        configs = dict(configs, _notes=data.get("versions", {}), _highlights=data.get("highlights", []))
    idx.write_text(render_index(cat, reports_dir, changelog, configs), encoding="utf-8", newline="\n")
    written.append(idx)
    pkg_versions = {e["version"] for e in cat["versions"]}
    for sv in (cat.get("store") or {}).get("versions", []):
        if sv["version"] in pkg_versions:
            continue
        p = dist_root / f"{safe_name(sv['version'])}.md"
        body = [f"# Agent Client Collector Framework {sv['version']} - no agent package", "",
                f"ServiceNow released the Framework app {sv['version']} on the Store, but the download server holds no agent "
                f"package numbered {sv['version']}. A Framework release installs whichever agent build its property "
                "sn_agent.agent_version names, and that number can differ from the app's own; agent changes in these notes "
                "reached hosts through a neighbouring agent build. See the [index](README.md) for the agent versions around it.", ""]
        body += render_changelog(sv["version"], cat.get("store"), changelog, [])
        p.write_text("\n".join(body), encoding="utf-8", newline="\n")
        written.append(p)
    for e in cat["versions"]:
        p = dist_root / f"{safe_name(e['version'])}.md"
        p.write_text(render_version(e, cat.get("base_url", BASE_URL), reports_dir, cat.get("store"), changelog,
                                    [x["version"] for x in cat["versions"]], configs), encoding="utf-8", newline="\n")
        written.append(p)
    return written


def load_cache(dist_root: Path) -> dict | None:
    p = dist_root / "packages.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None
