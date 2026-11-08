"""Result model shared by the runner and the report."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .util import iso_now

PASS, FAIL, WARN, SKIP, ERROR = "pass", "fail", "warn", "skip", "error"
ORDER = {FAIL: 0, ERROR: 1, WARN: 2, PASS: 3, SKIP: 4}

# Who owns a failure - the question every reader of the report asks first ("is it the agent, or my server?").
CAUSES = {
    "agent": "the agent package itself (binary, service, embedded runtime) - changes with the agent version",
    "content": "check content delivered from the instance through the MID (plugin assets, check definitions, allow-lists) - "
               "the same on every agent version until the content app is fixed",
    "target": "the server under test (missing prerequisites, permissions, files, network)",
    "instance": "the instance or the MID Server (listener, plugin cache, API, discovery processing)",
}


@dataclass
class TestResult:
    id: str
    name: str
    section: str                 # Pre-flight | Packages | Install | Connectivity | Discovery | Checks | Policies | Resources | Cleanup | UI
    status: str
    target: str = ""             # target name, empty for instance-wide tests
    message: str = ""            # one line: what was verified / what failed
    details: str = ""            # evidence: command output, record dumps, etc.
    evidence: dict = field(default_factory=dict)
    screenshot: str = ""         # relative path inside the results directory
    cause: str = ""              # for a failure: agent | content | target | instance | "" (not attributed) - see CAUSES
    started: str = field(default_factory=iso_now)
    duration_s: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RunResult:
    version: str
    instance: str
    mid_server: str
    backend_url: str
    started: str = field(default_factory=iso_now)
    finished: str = ""
    title: str = ""
    build: str = ""
    app_version: str = ""
    settings: dict = field(default_factory=dict)
    targets: list[dict] = field(default_factory=list)
    packages: list[dict] = field(default_factory=list)
    results: list[TestResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, r: TestResult) -> TestResult:
        self.results.append(r)
        return r

    def counts(self, target: str | None = None) -> dict:
        rows = [r for r in self.results if target is None or r.target == target]
        return {s: sum(1 for r in rows if r.status == s) for s in (PASS, FAIL, WARN, SKIP, ERROR)}

    runtimes: dict = field(default_factory=dict)   # embedded Ruby / OpenSSL / gems of the qualified package (runtimes.Runtimes)
    components: list[dict] = field(default_factory=list)   # inventory rows {component, version, kind, source, target}
    perf: list[dict] = field(default_factory=list)   # performance sampling per target (perf.analyze output + target, distro)

    def agent_failures(self) -> list:
        """Failures the AGENT owns: cause 'agent', or no cause (the evidence did not say - read it before shipping)."""
        return [r for r in self.results if r.status in (FAIL, ERROR) and r.cause in ("agent", "")]

    def env_failures(self) -> list:
        """Failures owned by the server, the instance content or the MID - not the agent build."""
        return [r for r in self.results if r.status in (FAIL, ERROR) and r.cause not in ("agent", "")]

    def agent_verdict(self) -> str:
        """pass = nothing attributable to the agent failed (environment findings may still exist); fail otherwise.
        skip = nothing ran."""
        if not any(r.status == PASS for r in self.results):
            return SKIP
        return FAIL if self.agent_failures() else PASS

    def causes(self) -> dict:
        """Failures grouped by cause ('' = not attributed)."""
        out: dict = {}
        for r in self.results:
            if r.status in (FAIL, ERROR):
                out[r.cause] = out.get(r.cause, 0) + 1
        return out

    def overall(self) -> str:
        c = self.counts()
        if c[FAIL] or c[ERROR]:
            return FAIL
        if c[WARN]:
            return WARN
        return PASS if c[PASS] else SKIP

    def to_dict(self) -> dict:
        d = asdict(self)
        d["results"] = [r.to_dict() for r in self.results]
        d["overall"] = self.overall()
        d["counts"] = self.counts()
        return d

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str), encoding="utf-8")


class Timer:
    def __init__(self):
        self.t0 = time.time()

    def seconds(self) -> float:
        return round(time.time() - self.t0, 1)
