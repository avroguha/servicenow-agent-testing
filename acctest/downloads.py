"""Download index: every Agent Client Collector package ServiceNow publishes, per version, operating system and
architecture, written as Markdown pages into dist/ (``dist/README.md`` = all versions, ``dist/<version>.md`` = one
version with every package, its direct link, size, date on the server, signature file and SHA-256 where known).

The packages are ServiceNow's and stay on install.service-now.com - nothing is mirrored here. The server has no index,
so the catalog is built by HEAD requests: one per candidate version (``agents.published_versions``) and then one per
package file of every version found. The result is cached in ``dist/packages.json`` so the pages can be re-rendered
offline; SHA-256 sums are taken from the packages this tool downloaded into ``dist/<version>/`` and kept in the cache
once computed.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import logging
from datetime import datetime
from pathlib import Path

import requests

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
     "covers": "Windows Server and Windows client, 64-bit Intel/AMD. There is no Windows ARM64 build"},
    {"classifier": "macos_x64", "pkg": "pkg", "os_key": "macos-x86_64", "family": "macos", "arch": "x86_64",
     "label": "macOS, Intel (.pkg)",
     "covers": "macOS on Intel Macs; published since 2.9.0"},
    {"classifier": "macos_arm64", "pkg": "pkg", "os_key": "macos-arm64", "family": "macos", "arch": "arm64",
     "label": "macOS, Apple silicon (.pkg)",
     "covers": "macOS on M-series Macs; published since 3.1.0"},
]

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


def render_version(entry: dict, base_url: str, reports_dir: Path | None = None) -> str:
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
    out += ["", "## Installing", "",
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


def render_index(cat: dict, reports_dir: Path | None = None) -> str:
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
    latest = versions[0]["version"] if versions else ""
    out += ["", "## Versions", "", f"Latest: **[{latest}]({latest}.md)**." if latest else "", "",
            "| Version | On the server | " + " | ".join(SHORT[p["classifier"]] for p in PACKAGES) + " | Report |",
            "|---|---|" + "|".join(":-:" for _ in PACKAGES) + "|---|"]
    for e in versions:
        avail = {f["classifier"] for f in e["files"] if f["kind"] == "package" and f.get("available")}
        cells = " | ".join("yes" if p["classifier"] in avail else "-" for p in PACKAGES)
        rep = _report_link(reports_dir, e["version"], "../")
        out.append(f"| [{e['version']}]({e['version']}.md) | {day(e.get('last_modified', ''))} | {cells} | {rep} |")
    out += ["", "\"On the server\" is the earliest file date the server reports for that version - releases older than "
            "2026 carry the date they were last copied there, not their release date.", ""]
    return "\n".join(out)


def write_pages(cat: dict, dist_root: Path, reports_dir: Path | None = None) -> list[Path]:
    """Write dist/packages.json, dist/README.md and dist/<version>.md for every version in the catalog."""
    dist_root.mkdir(parents=True, exist_ok=True)
    written = []
    cache = dist_root / "packages.json"
    cache.write_text(json.dumps(cat, indent=1), encoding="utf-8")
    written.append(cache)
    idx = dist_root / "README.md"
    idx.write_text(render_index(cat, reports_dir), encoding="utf-8", newline="\n")
    written.append(idx)
    for e in cat["versions"]:
        p = dist_root / f"{safe_name(e['version'])}.md"
        p.write_text(render_version(e, cat.get("base_url", BASE_URL), reports_dir), encoding="utf-8", newline="\n")
        written.append(p)
    return written


def load_cache(dist_root: Path) -> dict | None:
    p = dist_root / "packages.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None
