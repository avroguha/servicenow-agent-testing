"""What runs inside an agent package: the embedded Ruby, OpenSSL and gems.

The agent ships its own Ruby (plugins are Ruby scripts) and its own OpenSSL, so a Ruby or OpenSSL CVE is fixed only by a
NEW AGENT BUILD - upgrading the ACC Framework app on the instance changes nothing on the servers (ServiceNow KB1710136).
This module reads the versions straight out of the Debian package in dist/ (an `ar` archive holding data.tar.*), without
installing anything, so a CVE question ("which agent version carries Ruby >= 3.3.13?") is answered from the downloads.

The rpm, msi and pkg builds of one version embed the same runtimes (one build per version); the deb is simply the
easiest to open with the standard library.
"""
from __future__ import annotations

import gzip
import io
import logging
import lzma
import re
import tarfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

LOG = logging.getLogger("acctest.runtimes")
RUBY_RE = re.compile(rb"ruby (\d+\.\d+\.\d+) \((\d{4}-\d\d-\d\d)[^)]*\)")
OPENSSL_RE = re.compile(rb"OpenSSL (\d+\.\d+\.\d+[a-z]?) +(\d+ \w+ \d{4})")


@dataclass
class Runtimes:
    package: str
    ruby: str = ""              # e.g. 3.3.13
    ruby_date: str = ""         # release date of that Ruby
    openssl: str = ""           # e.g. 3.5.9
    openssl_date: str = ""
    ruby_api: str = ""          # gems directory (3.3.0)
    gems: dict = field(default_factory=dict)   # default/bundled gem name -> version (the ones CVEs are filed against)
    all_gems: dict = field(default_factory=dict)   # every gem shipped under lib/ruby/gems/<api>/gems
    libs: dict = field(default_factory=dict)       # embedded shared libraries: libyaml -> 0.2.5 ...
    go_version: str = ""        # Go toolchain the acc binary was built with
    binaries: list = field(default_factory=list)   # names under embedded/bin and bin
    files: int = 0
    error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def components(self) -> list[dict]:
        """Flat inventory rows for the security team: name, version, kind, where it came from."""
        rows = [{"component": "Agent Client Collector", "version": Path(self.package).name.split("-")[3] if self.package.count("-") >= 4 else "", "kind": "agent package", "source": Path(self.package).name}]
        if self.go_version:
            rows.append({"component": "Go runtime (acc binary)", "version": self.go_version, "kind": "compiler/runtime", "source": "bin/acc"})
        if self.ruby:
            rows.append({"component": "Ruby (embedded)", "version": f"{self.ruby} ({self.ruby_date})", "kind": "interpreter", "source": "embedded/bin/ruby"})
        if self.openssl:
            rows.append({"component": "OpenSSL (embedded)", "version": f"{self.openssl} ({self.openssl_date})", "kind": "crypto library", "source": "embedded/lib/libcrypto"})
        for k, v in sorted(self.libs.items()):
            rows.append({"component": k, "version": v, "kind": "shared library", "source": "embedded/lib"})
        for k, v in sorted(self.all_gems.items()):
            rows.append({"component": f"gem {k}", "version": v, "kind": "Ruby gem", "source": f"embedded/lib/ruby/gems/{self.ruby_api}"})
        return rows

    def summary(self) -> str:
        if self.error:
            return f"could not read {Path(self.package).name}: {self.error}"
        g = ", ".join(f"{k} {v}" for k, v in sorted(self.gems.items()))
        return f"Ruby {self.ruby} ({self.ruby_date}), OpenSSL {self.openssl} ({self.openssl_date})" + (f"; gems: {g}" if g else "")


def _vkey(v: str) -> tuple:
    return tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[.\-]", v))


def ar_members(data: bytes):
    """Yield (name, bytes) from a Unix `ar` archive (what a .deb is)."""
    if data[:8] != b"!<arch>\n":
        raise ValueError("not an ar archive")
    i = 8
    while i + 60 <= len(data):
        name = data[i:i + 16].decode("ascii", "replace").strip().rstrip("/")
        size = int(data[i + 48:i + 58].decode("ascii").strip() or "0")
        i += 60
        yield name, data[i:i + size]
        i += size + (size % 2)


def _decompress(name: str, blob: bytes) -> bytes:
    if name.endswith(".xz") or name.endswith(".lzma"):
        return lzma.decompress(blob)
    if name.endswith(".gz"):
        return gzip.decompress(blob)
    if name.endswith(".zst"):
        try:
            import zstandard  # optional; not pinned - only needed if ServiceNow ever switches the deb compression
        except ImportError as e:
            raise ValueError("data.tar.zst needs the 'zstandard' package") from e
        return zstandard.ZstdDecompressor().stream_reader(io.BytesIO(blob)).read()
    if name.endswith(".tar"):
        return blob
    raise ValueError(f"unknown data member {name}")


# gems CVEs get filed against; the version is the directory name under lib/ruby/gems/<api>/{gems,specifications}
GEMS_OF_INTEREST = ("rexml", "resolv", "uri", "cgi", "net-imap", "webrick", "openssl", "json", "rubygems-update", "bundler", "psych", "nokogiri", "rack")


def inspect_deb(path: Path) -> Runtimes:
    rt = Runtimes(package=str(path))
    try:
        data = path.read_bytes()
        for name, blob in ar_members(data):
            if not name.startswith("data.tar"):
                continue
            tf = tarfile.open(fileobj=io.BytesIO(_decompress(name, blob)))
            members = tf.getmembers()
            rt.files = len(members)
            names = [m.name for m in members]
            for n in names:
                m = re.search(r"lib/ruby/gems/([\d.]+)/", n)
                if m:
                    rt.ruby_api = m.group(1)
                    break
            for n in names:
                m = re.search(r"/(?:gems|specifications)/(?:default/)?(" + "|".join(re.escape(g) for g in GEMS_OF_INTEREST) + r")-(\d[\w.]*?)(?:\.gemspec|/.*)?$", n)
                if m and m.group(1) not in rt.gems:
                    rt.gems[m.group(1)] = m.group(2)
                m = re.search(r"/lib/ruby/gems/[\d.]+/(?:gems|specifications)/(?:default/)?([A-Za-z0-9_][A-Za-z0-9_.-]*?)-(\d[\w.]*?)(?:\.gemspec|/.*)?$", n)
                if m:
                    cur = rt.all_gems.get(m.group(1))
                    if cur is None or _vkey(m.group(2)) > _vkey(cur):
                        rt.all_gems[m.group(1)] = m.group(2)
                m = re.search(r"/embedded/lib/(lib[A-Za-z0-9_+-]+?)\.so\.(\d+(?:\.\d+)+)$", n)
                if m:
                    cur = rt.libs.get(m.group(1))
                    if cur is None or _vkey(m.group(2)) > _vkey(cur):
                        rt.libs[m.group(1)] = m.group(2)
                if re.search(r"/(?:embedded/)?bin/[^/]+$", n) and "/gems/" not in n:
                    rt.binaries.append(n.rsplit("/", 1)[1])
            rt.binaries = sorted(set(rt.binaries))
            acc = [n for n in names if n.endswith("/agent-client-collector/bin/acc")]
            if acc:
                b = tf.extractfile(acc[0]).read()
                m = re.search(rb"go(1\.\d+(?:\.\d+)?)", b)
                if m:
                    rt.go_version = m.group(1).decode()
            lib = [n for n in names if re.search(r"libruby\.so\.\d+\.\d+\.\d+$", n)] or [n for n in names if n.endswith("/embedded/bin/ruby")]
            if lib:
                b = tf.extractfile(lib[0]).read()
                m = RUBY_RE.search(b)
                if m:
                    rt.ruby, rt.ruby_date = m.group(1).decode(), m.group(2).decode()
            for n in names:
                if re.search(r"/embedded/lib/libcrypto\.so\.\d+$", n) or re.search(r"/embedded/lib/libssl\.so\.\d+$", n):
                    m = OPENSSL_RE.search(tf.extractfile(n).read())
                    if m:
                        rt.openssl, rt.openssl_date = m.group(1).decode(), m.group(2).decode()
                        break
            if not rt.ruby:
                rt.error = "no embedded Ruby found in the package"
            return rt
        rt.error = "no data.tar member"
    except Exception as e:  # a corrupt download must not kill a run
        rt.error = f"{type(e).__name__}: {e}"
    return rt


def find_deb(dist_root: Path, version: str) -> Path | None:
    d = dist_root / version
    if not d.is_dir():
        return None
    debs = sorted(d.rglob("*.deb"))
    for p in debs:  # prefer the x86_64 build
        if "amd64" in p.name:
            return p
    return debs[0] if debs else None
