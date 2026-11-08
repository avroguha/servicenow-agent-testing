"""Home lab: provision disposable LXC containers on a Proxmox node, one per OS, and write targets.yml.

Only used when LAB_MODE=proxmox. Containers get DHCP addresses (no address bookkeeping), the node's template for the
OS, and the few packages the ACC install script needs (curl, gpg). Everything is reached with `pct exec`, so the
containers need no SSH server. VMIDs start at LAB_VMID_BASE and must sit in the node's disposable range.
"""
from __future__ import annotations

import logging
import shlex
import time

from .config import Settings, TargetSpec, load_targets, save_targets
from .targets import CmdResult, PctTransport, probe

LOG = logging.getLogger("acctest.lab")

# os key -> (template name fragment, pct ostype, os_key for the agent package, prerequisite install command)
LAB_OS = {
    "ubuntu2604": ("ubuntu-26.04-standard", "ubuntu", "linux-x86_64-deb",
                   "export DEBIAN_FRONTEND=noninteractive; apt-get -qq update && apt-get -qq install -y curl gpg unzip ca-certificates procps sudo iproute2"),
    "ubuntu2404": ("ubuntu-24.04-standard", "ubuntu", "linux-x86_64-deb",
                   "export DEBIAN_FRONTEND=noninteractive; apt-get -qq update && apt-get -qq install -y curl gpg unzip ca-certificates procps sudo iproute2"),
    "ubuntu2204": ("ubuntu-22.04-standard", "ubuntu", "linux-x86_64-deb",
                   "export DEBIAN_FRONTEND=noninteractive; apt-get -qq update && apt-get -qq install -y curl gpg unzip ca-certificates procps sudo iproute2"),
    "debian12": ("debian-12-standard", "debian", "linux-x86_64-deb",
                 "export DEBIAN_FRONTEND=noninteractive; apt-get -qq update && apt-get -qq install -y curl gpg unzip ca-certificates procps sudo iproute2"),
    "rocky9": ("rockylinux-9-default", "centos", "linux-x86_64-rpm",
               "dnf -q -y install curl gnupg2 unzip procps-ng hostname sudo iproute which >/dev/null"),
    "rocky10": ("rockylinux-10-default", "centos", "linux-x86_64-rpm",
                "dnf -q -y install curl gnupg2 unzip procps-ng hostname sudo iproute which >/dev/null"),
    "suse156": ("opensuse-15.6-default", "opensuse", "linux-x86_64-rpm",
                "zypper -n -q install curl gpg2 unzip procps hostname sudo iproute2 which >/dev/null"),
    "alpine": ("alpine-3", "alpine", "unsupported",
               "apk add -q curl gnupg unzip bash procps"),
}


# one package at a time, whichever package manager exists; failures are reported, not fatal
PREREQ_RETRY = """
set +e
export DEBIAN_FRONTEND=noninteractive
if command -v apt-get >/dev/null; then apt-get -qq update; for p in curl gpg unzip ca-certificates procps sudo iproute2; do apt-get -qq install -y $p >/dev/null 2>&1 || echo "apt failed: $p"; done
elif command -v dnf >/dev/null; then for p in curl gnupg2 unzip procps-ng hostname sudo iproute which; do dnf -q -y install $p >/dev/null 2>&1 || echo "dnf failed: $p"; done
elif command -v zypper >/dev/null; then for p in curl gpg2 unzip procps hostname sudo iproute2 which; do zypper -n -q install $p >/dev/null 2>&1 || echo "zypper failed: $p"; done
elif command -v apk >/dev/null; then apk add -q curl gnupg unzip bash procps || echo "apk failed"
fi
"""


def _node(settings: Settings, cmd: str, timeout: int = 300) -> CmdResult:
    return PctTransport(settings.pve_host, settings.pve_user, settings.pve_ssh_key, 0).node_run(cmd, timeout)


def find_template(settings: Settings, fragment: str) -> str:
    r = _node(settings, "pveam list local")
    if not r.ok:
        raise RuntimeError(f"pveam list failed on {settings.pve_host}: {r.err.strip() or r.out.strip()}")
    for line in r.out.splitlines():
        name = line.split()[0] if line.strip() else ""
        if fragment in name:
            return name
    raise RuntimeError(f"no container template matching {fragment!r} on {settings.pve_host} (pveam list local)")


def ct_status(settings: Settings, vmid: int) -> str:
    r = _node(settings, f"pct status {vmid}", 60)
    if not r.ok:
        return "missing"
    return r.out.strip().split()[-1] if r.out.strip() else "unknown"


def provision(settings: Settings) -> list[TargetSpec]:
    settings.require("PVE_HOST", "PVE_SSH_KEY")
    if not settings.lab_os_list:
        raise SystemExit("LAB_OS_LIST is empty - nothing to provision")
    existing = {t.name: t for t in load_targets(settings)}
    targets: list[TargetSpec] = []
    for i, os_name in enumerate(settings.lab_os_list):
        if os_name not in LAB_OS:
            LOG.error("unknown lab OS %r (known: %s)", os_name, ", ".join(LAB_OS))
            continue
        frag, ostype, os_key, prereq = LAB_OS[os_name]
        vmid = settings.lab_vmid_base + i
        host = f"{settings.lab_hostname_prefix}-{os_name}"
        st = ct_status(settings, vmid)
        if st == "missing":
            tpl = find_template(settings, frag)
            LOG.info("creating CT %d (%s) from %s", vmid, host, tpl)
            args = ["pct", "create", str(vmid), tpl, "--hostname", host, "--memory", str(settings.lab_ct_memory_mb),
                    "--cores", str(settings.lab_ct_cores), "--rootfs", f"{settings.lab_storage}:{settings.lab_ct_disk_gb}",
                    "--net0", f"name=eth0,bridge={settings.lab_bridge},ip=dhcp", "--nameserver", settings.lab_nameservers,
                    "--unprivileged", "1", "--features", "nesting=1", "--ostype", ostype, "--start", "1",
                    "--description", "acctest ACC agent target (disposable)"]
            r = _node(settings, " ".join(shlex.quote(a) for a in args), 600)
            # pct exits non-zero with WARNINGS on some templates; treat a running container as success
            if not r.ok and ct_status(settings, vmid) == "missing":
                raise RuntimeError(f"pct create {vmid} failed: {r.err.strip() or r.out.strip()}")
            time.sleep(8)
        elif st == "stopped":
            LOG.info("starting CT %d", vmid)
            _node(settings, f"pct start {vmid}", 120)
            time.sleep(8)
        tr = PctTransport(settings.pve_host, settings.pve_user, settings.pve_ssh_key, vmid)
        # DNS: pct seeds resolv.conf from the node, which often points somewhere the container cannot reach
        ns = "\n".join(f"nameserver {n}" for n in settings.lab_nameservers.split())
        tr.run(f"printf '{ns}\\n' > /etc/resolv.conf; for i in 1 2 3 4 5 6; do getent hosts install.service-now.com >/dev/null && break; sleep 3; done", 120)
        LOG.info("installing prerequisites in CT %d", vmid)
        r = tr.run(prereq, 600)
        if not r.ok:
            LOG.warning("prerequisite install in CT %d returned %d: %s - retrying package by package", vmid, r.rc, (r.err or r.out)[-300:])
            tr.run(PREREQ_RETRY, 600)
        missing = [x for x in ("curl", "gpg", "unzip") if not tr.run(f"command -v {x} >/dev/null 2>&1 || command -v {x}2 >/dev/null 2>&1", 60).ok]
        if missing:
            LOG.error("CT %d still lacks %s - the agent install script will fail there", vmid, ", ".join(missing))
        facts = probe(tr, "linux")
        spec = existing.get(host) or TargetSpec(name=host, os=os_key)
        spec.os = os_key
        spec.transport = "pct"
        spec.vmid = vmid
        spec.pve_host = settings.pve_host
        spec.host = facts.get("IP", "")
        spec.family = "linux"
        spec.distro = facts.get("PRETTY", "")
        spec.arch = facts.get("ARCH", "x86_64")
        spec.pkg = "deb" if os_key.endswith("deb") else "rpm"
        spec.labels = {"lab": True, "lab_os": os_name}
        spec.expected_ci_class = "cmdb_ci_linux_server"
        targets.append(spec)
        LOG.info("CT %d %s ready: %s at %s", vmid, host, spec.distro, spec.host)
    # keep non-lab targets the user added by hand
    others = [t for t in existing.values() if not (t.labels or {}).get("lab")]
    save_targets(settings, targets + others)
    return targets


def destroy(settings: Settings, force: bool = False) -> list[int]:
    gone = []
    for t in load_targets(settings):
        if t.transport != "pct" or not (t.labels or {}).get("lab"):
            continue
        if not force and t.vmid < settings.lab_vmid_base:
            LOG.warning("refusing to destroy CT %d below LAB_VMID_BASE", t.vmid)
            continue
        LOG.info("destroying CT %d (%s)", t.vmid, t.name)
        _node(settings, f"pct stop {t.vmid}", 120)
        r = _node(settings, f"pct destroy {t.vmid} --purge 1", 300)
        if r.ok or "does not exist" in (r.err + r.out):
            gone.append(t.vmid)
        else:
            LOG.error("pct destroy %d: %s", t.vmid, r.err.strip() or r.out.strip())
    remaining = [t for t in load_targets(settings) if t.vmid not in gone]
    save_targets(settings, remaining)
    return gone


def status(settings: Settings) -> list[dict]:
    out = []
    for t in load_targets(settings):
        if t.transport == "pct":
            out.append({"name": t.name, "vmid": t.vmid, "status": ct_status(settings, t.vmid), "host": t.host, "os": t.os})
    return out
