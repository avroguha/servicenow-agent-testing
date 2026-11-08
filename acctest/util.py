"""Small helpers shared by every module: logging, time, hashing, subprocess."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

LOG = logging.getLogger("acctest")


def setup_logging(verbose: bool = False, logfile: Path | None = None) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if logfile:
        logfile.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(logfile, encoding="utf-8"))
    logging.basicConfig(level=level, format=fmt, handlers=handlers, force=True)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")


def sn_now(offset_seconds: int = 0) -> str:
    """A UTC timestamp in the format ServiceNow's Table API expects ('YYYY-MM-DD HH:MM:SS')."""
    return datetime.fromtimestamp(time.time() + offset_seconds, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_name(s: str) -> str:
    """A file-system safe token (versions, host names, check names)."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_") or "x"


def expand_path(p: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(p))).resolve()


def run_local(cmd: list[str], timeout: int = 120, input_text: str | None = None, check: bool = False) -> subprocess.CompletedProcess:
    """Run a local command (ssh, scp, ...) without a shell. Returns the CompletedProcess; raises only when check=True."""
    LOG.debug("local: %s", " ".join(cmd))
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, input=input_text, encoding="utf-8", errors="replace")
    if check and cp.returncode != 0:
        raise RuntimeError(f"command failed ({cp.returncode}): {' '.join(cmd)}\n{cp.stderr.strip()}")
    return cp


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def version_key(v: str):
    """Sort key for dotted versions ('3.10.1' > '3.9.4')."""
    parts = []
    for p in re.split(r"[.\-]", v):
        parts.append((0, int(p)) if p.isdigit() else (1, p))
    return parts


def wait_until(predicate, timeout: int, interval: int = 10, what: str = "condition"):
    """Poll predicate() until it returns a truthy value or timeout (seconds). Returns the value or None."""
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = predicate()
        if last:
            return last
        time.sleep(interval)
    LOG.warning("timed out after %ss waiting for %s", timeout, what)
    return None
