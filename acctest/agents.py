"""Agent package catalog: which agent versions and OS packages the instance offers, and downloading them to dist/.

The instance is the source of truth. The ACC Framework app (scope ``sn_agent``) carries the agent version in the
property ``sn_agent.agent_version`` and the OS -> package map in the ``AgentScripts`` script include; the packages
themselves are served publicly from install.service-now.com. The Linux install script is served by the instance at
``/api/sn_agent/agents/install_agent`` and is stored beside the packages because it is the thing ServiceNow changes
between releases.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import requests

from .snow import SNClient, SNError
from .util import iso_now, safe_name, sha256_file, version_key

LOG = logging.getLogger("acctest.agents")

# Package keys the tool understands, in the vocabulary of targets.yml `os:`; `pkg` mirrors the install script.
# "key" is what the instance's osMap calls the entry ('c' = classifier in the file name, 'p' = package type).
OS_KEYS = {
    # os key          classifier        pkg    family     arch
    "linux-x86_64-deb": ("ubuntu-1804_amd64", "deb", "linux", "x86_64"),
    "linux-x86_64-rpm": ("x86_64", "rpm", "linux", "x86_64"),
    "linux-aarch64-deb": ("ubuntu-2204_arm64", "deb", "linux", "aarch64"),
    "windows-x86_64": ("windows-x64", "msi", "windows", "x86_64"),
    "macos-x86_64": ("macos_x64", "pkg", "macos", "x86_64"),
    "macos-arm64": ("macos_arm64", "pkg", "macos", "arm64"),
}


@dataclass
class AgentPackage:
    os_key: str
    classifier: str
    pkg: str
    family: str
    arch: str
    file: str
    url: str
    sig_file: str = ""
    sig_url: str = ""
    instance_label: str = ""     # how the instance's download page names it ("RHEL/CentOS 7", ...)

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class AgentCatalog:
    version: str
    base_url: str
    dev_mode: bool
    app_version: str
    packages: list[AgentPackage] = field(default_factory=list)
    os_map: dict = field(default_factory=dict)
    install_script: str = ""

    def package_for(self, os_key: str) -> AgentPackage | None:
        for p in self.packages:
            if p.os_key == os_key:
                return p
        return None

    def to_dict(self) -> dict:
        return {"version": self.version, "base_url": self.base_url, "dev_mode": self.dev_mode,
                "app_version": self.app_version, "os_map": self.os_map,
                "packages": [p.to_dict() for p in self.packages]}


_OSMAP_RE = re.compile(r"'([^']+)'\s*:\s*\{\s*'c'\s*:\s*'([^']+)'\s*,\s*'p'\s*:\s*'([^']+)'\s*\}", re.S)


def read_catalog(sn: SNClient, version: str | None = None) -> AgentCatalog:
    """Build the catalog from the instance. `version` None/'latest' -> the instance's current agent version."""
    app = sn.first("sys_scope", "scope=sn_agent", "name,version")
    if not app:
        raise SNError("Agent Client Collector Framework (scope sn_agent) is not installed on this instance")
    dev_mode = (sn.property("sn_agent.dev_mode") or "false") == "true"
    if dev_mode:
        base = "https://install.service-now.com/glide/distribution/builds/package/agent-client-collector/"
        inst_version = (sn.property("sn_agent.agent_snapshot_version") or "") + "-SNAPSHOT"
    else:
        base = "https://install.service-now.com/glide/distribution/builds/package/app-signed/"
        inst_version = sn.property("sn_agent.agent_version") or ""
    if not inst_version:
        raise SNError("sn_agent.agent_version property is empty - the ACC Framework install looks incomplete")
    v = inst_version if not version or version == "latest" else version

    # The instance's own OS map, read from the AgentScripts script include (falls back to the built-in table).
    os_map: dict[str, dict] = {}
    si = sn.first("sys_script_include", "name=AgentScripts^sys_scope.scope=sn_agent", "script")
    if si:
        for label, c, p in _OSMAP_RE.findall(si["script"]):
            os_map[label] = {"c": c, "p": p}
    if not os_map:
        LOG.warning("could not read AgentScripts.osMap from the instance; using the built-in package table")

    cat = AgentCatalog(version=v, base_url=base, dev_mode=dev_mode, app_version=app["version"], os_map=os_map)
    seen_files: set[str] = set()
    for os_key, (classifier, pkg, family, arch) in OS_KEYS.items():
        # prefer the classifier the instance uses for this package type/arch, if it differs
        label = next((lbl for lbl, m in os_map.items() if m["c"] == classifier), "")
        fname = f"agent-client-collector-{v}-{classifier}.{pkg}"
        if fname in seen_files:
            continue
        seen_files.add(fname)
        sig = "" if pkg in ("pkg", "msi") else f"agent-client-collector-{v}-{classifier}-{pkg}-{pkg}.zip"
        cat.packages.append(AgentPackage(os_key, classifier, pkg, family, arch, fname, base + fname, sig,
                                         base + sig if sig else "", label))
    # every other classifier the instance lists that we have no key for (older distros) - keep for completeness
    for label, m in os_map.items():
        fname = f"agent-client-collector-{v}-{m['c']}.{m['p']}"
        if fname in seen_files:
            continue
        seen_files.add(fname)
        family = "windows" if m["p"] == "msi" else ("macos" if m["p"] == "pkg" else "linux")
        arch = "arm64" if "arm64" in m["c"] else "x86_64"
        key = "legacy-" + safe_name(m["c"]) + "-" + m["p"]
        sig = "" if m["p"] in ("pkg", "msi") else f"agent-client-collector-{v}-{m['c']}-{m['p']}-{m['p']}.zip"
        cat.packages.append(AgentPackage(key, m["c"], m["p"], family, arch, fname, base + fname, sig,
                                         base + sig if sig else "", label))
    try:
        r = sn._req("GET", "/api/sn_agent/agents/install_agent", raw=True)
        cat.install_script = r.text
        if v != inst_version:
            # the script hard-codes the instance's version; rewrite it for the requested one
            cat.install_script = re.sub(r"^ACC_VERSION=.*$", f"ACC_VERSION={v}", cat.install_script, count=1, flags=re.M)
    except SNError as e:
        LOG.warning("could not fetch the install script from the instance: %s", e)
    return cat


def available(url: str, timeout: int = 60) -> tuple[bool, int]:
    """HEAD a package URL: (exists, size)."""
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)
        return r.status_code == 200, int(r.headers.get("Content-Length", "0") or 0)
    except requests.RequestException:
        return False, 0


def published_versions(base_url: str, classifier: str = "ubuntu-1804_amd64.deb", majors: range = range(2, 10), minors: int = 13,
                       patches: int = 13, workers: int = 24) -> list[dict]:
    """Which agent versions exist on the download server? There is no index: the server answers HEAD per file, so this
    probes every <major>.<minor>.<patch> in the given ranges for one classifier (~1,000 HEADs, half a minute).
    Returns [{version, size, last_modified}] sorted by version. Use it to answer "which earlier version can we fall
    back to" - then qualify that version with `run --version`."""
    import concurrent.futures as cf
    cands = [f"{M}.{m}.{p}" for M in majors for m in range(minors) for p in range(patches)]

    def head(v: str):
        try:
            r = requests.head(f"{base_url}agent-client-collector-{v}-{classifier}", timeout=30, allow_redirects=True)
            if r.status_code == 200:
                return {"version": v, "size": int(r.headers.get("Content-Length", "0") or 0), "last_modified": r.headers.get("Last-Modified", "")}
        except requests.RequestException:
            pass
        return None

    with cf.ThreadPoolExecutor(workers) as ex:
        found = [x for x in ex.map(head, cands) if x]
    return sorted(found, key=lambda x: version_key(x["version"]))


def download_catalog(cat: AgentCatalog, dest_root: Path, os_keys: list[str] | None = None, skip_existing: bool = True) -> dict:
    """Download the packages (and the install script) into <dest_root>/<version>/<os_key>/ and write manifest.json.
    Returns the manifest dict. Packages that do not exist on the server are recorded with available=false."""
    vdir = dest_root / safe_name(cat.version)
    vdir.mkdir(parents=True, exist_ok=True)
    manifest = {"version": cat.version, "app_version": cat.app_version, "base_url": cat.base_url,
                "downloaded_at": iso_now(), "files": []}
    if cat.install_script:
        sp = vdir / "install_agent.sh"
        sp.write_text(cat.install_script, encoding="utf-8", newline="\n")
        manifest["files"].append({"os_key": "linux", "file": "install_agent.sh", "path": str(sp.relative_to(dest_root)),
                                  "sha256": sha256_file(sp), "size": sp.stat().st_size, "source": "instance:/api/sn_agent/agents/install_agent"})
    wanted = [p for p in cat.packages if not os_keys or p.os_key in os_keys]
    for p in wanted:
        if p.os_key.startswith("legacy-") and os_keys is None:
            # legacy distro builds are listed in the manifest but only fetched when asked for
            ok, size = available(p.url)
            manifest["files"].append({"os_key": p.os_key, "file": p.file, "url": p.url, "available": ok, "size": size,
                                      "downloaded": False, "label": p.instance_label})
            continue
        pdir = vdir / p.os_key
        pdir.mkdir(exist_ok=True)
        for fname, url in ((p.file, p.url), (p.sig_file, p.sig_url)):
            if not fname:
                continue
            target = pdir / fname
            ok, size = available(url)
            entry = {"os_key": p.os_key, "file": fname, "url": url, "available": ok, "size": size,
                     "path": str(target.relative_to(dest_root)), "label": p.instance_label}
            if not ok:
                LOG.warning("not available on the download server: %s", url)
                entry["downloaded"] = False
            elif skip_existing and target.exists() and target.stat().st_size == size and size > 0:
                LOG.info("already present: %s", target.name)
                entry["downloaded"] = True
                entry["sha256"] = sha256_file(target)
            else:
                LOG.info("downloading %s (%d MB)", fname, size // (1 << 20))
                with requests.get(url, stream=True, timeout=120) as r:
                    r.raise_for_status()
                    with open(target, "wb") as f:
                        for chunk in r.iter_content(1 << 20):
                            f.write(chunk)
                entry["downloaded"] = True
                entry["sha256"] = sha256_file(target)
            manifest["files"].append(entry)
    (vdir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (vdir / "catalog.json").write_text(json.dumps(cat.to_dict(), indent=2), encoding="utf-8")
    return manifest


def local_package(dest_root: Path, version: str, os_key: str) -> Path | None:
    vdir = dest_root / safe_name(version) / os_key
    if not vdir.exists():
        return None
    for f in sorted(vdir.iterdir()):
        if f.suffix in (".deb", ".rpm", ".msi", ".pkg"):
            return f
    return None


def local_install_script(dest_root: Path, version: str) -> Path | None:
    p = dest_root / safe_name(version) / "install_agent.sh"
    return p if p.exists() else None


def list_local_versions(dest_root: Path) -> list[str]:
    if not dest_root.exists():
        return []
    return sorted((d.name for d in dest_root.iterdir() if d.is_dir() and (d / "manifest.json").exists()), key=version_key)
