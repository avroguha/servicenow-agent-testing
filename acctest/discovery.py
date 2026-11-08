"""Agent registration and agent-based discovery (ACC-V) as seen from the instance.

The agent appears as a row in sn_agent_ci_extended_info (agent_id, status, agent_version, mid, cmdb_ci = the host CI
it discovered, host_data / host_data_last_collected = discovery state) with a companion CI in sn_agent_cmdb_ci_agent.
Discovery on demand is ``GET /api/sn_agent/agents/<agent_id>/discovery`` (same as the "Collect host data" button).
"""
from __future__ import annotations

import logging
import time

from .snow import SNClient, SNError

LOG = logging.getLogger("acctest.discovery")
INFO_FIELDS = ("sys_id,sys_updated_on,agent_id,name,status,agent_version,major_version,minor_version,patch_version,mid,mid.name,cmdb_ci,"
               "cmdb_ci.name,cmdb_ci.sys_class_name,host_data,host_data_last_collected,host_data_last_attempted,up_since,"
               "last_refreshed,ip_address,is_windows,is_using_systemd,cpu_protection_behavior,data_collection,"
               "running_checks_num,is_duplicate,no_suitable_mids,is_containerized,sys_created_on")


def find_agent(sn: SNClient, agent_id: str = "", host: str = "", ip: str = "") -> dict | None:
    """Locate the agent record: by agent id (authoritative, read from the target), else host name, else IP."""
    if agent_id:
        row = sn.first("sn_agent_ci_extended_info", f"agent_id={agent_id}", INFO_FIELDS, display="all")
        if row:
            return _flat(row)
    if host:
        # the record is named Agent_<host> on 7.x (plain <host> on older releases)
        row = sn.first("sn_agent_ci_extended_info", f"name=Agent_{host}^ORname={host}^ORnameSTARTSWITHAgent_{host}.^ORnameSTARTSWITH{host}.", INFO_FIELDS, display="all")
        if row:
            return _flat(row)
    if ip:
        row = sn.first("sn_agent_ci_extended_info", f"ip_address={ip}", INFO_FIELDS, display="all")
        if row:
            return _flat(row)
    return None


def _flat(row: dict) -> dict:
    """display='all' rows carry {value, display_value}; flatten to value with <field>__display for the label."""
    out = {}
    for k, v in row.items():
        if isinstance(v, dict):
            out[k] = v.get("value", "")
            out[k + "__display"] = v.get("display_value", "")
        else:
            out[k] = v
    return out


def wait_for_agent(sn: SNClient, agent_id: str, host: str, ip: str, timeout: int, interval: int = 15) -> dict | None:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = find_agent(sn, agent_id, host, ip)
        if last and (last.get("status__display") or "").lower() == "up":
            return last
        time.sleep(interval)
    return last


def agent_api(sn: SNClient, agent_id: str, related: bool = True) -> dict:
    r = sn.s.get(f"{sn.instance}/api/sn_agent/agents/{agent_id}", headers={"X-Include-Related-Cis": "true" if related else "false"},
                 timeout=sn.timeout)
    if r.status_code >= 400:
        raise SNError(f"GET agents/{agent_id} -> {r.status_code}: {r.text[:300]}")
    return r.json().get("result", r.json())


def run_discovery(sn: SNClient, agent_id: str) -> dict:
    r = sn.s.get(f"{sn.instance}/api/sn_agent/agents/{agent_id}/discovery", timeout=sn.timeout)
    if r.status_code >= 400:
        raise SNError(f"run discovery for {agent_id} -> {r.status_code}: {r.text[:300]}")
    return r.json()


def wait_for_discovery(sn: SNClient, agent_id: str, since: str, timeout: int, interval: int = 15) -> dict | None:
    """Wait until host data has been collected after `since` (instance time 'YYYY-MM-DD HH:MM:SS') and a CI is bound."""
    deadline = time.time() + timeout
    t0 = time.time()
    last = None
    saw_collecting = False
    while time.time() < deadline:
        last = find_agent(sn, agent_id)
        if last:
            collected = last.get("host_data_last_collected") or ""
            if last.get("cmdb_ci") and collected and collected >= since:
                return last
            state = (last.get("host_data__display") or "").lower()
            if state.startswith("collecting"):
                saw_collecting = True
            # fail fast: the platform flips host_data to "Collection failed" within seconds of a bad check result
            elif state.startswith("collection failed") and (saw_collecting or (time.time() - t0 > 90 and (last.get("sys_updated_on") or "") >= since)):
                return last
        time.sleep(interval)
    return last


def ci_record(sn: SNClient, ci_sys_id: str) -> dict:
    """The host CI read from its OWN class table (cmdb_ci itself has no os / cpu / ram columns)."""
    base = sn.get("cmdb_ci", ci_sys_id, "sys_id,sys_class_name", display="false")
    if not base:
        return {}
    table = base.get("sys_class_name") or "cmdb_ci"
    fields = ("sys_id,name,sys_class_name,ip_address,fqdn,host_name,os,os_version,os_domain,serial_number,cpu_count,cpu_core_count,"
              "ram,disk_space,discovery_source,last_discovered,first_discovered,manufacturer,model_id,virtual,sys_updated_on,sys_created_on,"
              "install_status,operational_status,correlation_id")
    try:
        row = sn.get(table, ci_sys_id, fields, display="all")
    except SNError:
        row = sn.get("cmdb_ci", ci_sys_id, "sys_id,name,sys_class_name,ip_address,fqdn,discovery_source,last_discovered,sys_updated_on", display="all")
    return _flat(row) if row else {}


def ci_related(sn: SNClient, ci_sys_id: str) -> dict:
    """What agent discovery hung off the host CI: software, network adapters, IPs, file systems, running processes."""
    out = {}
    for table, field in (("cmdb_ci_network_adapter", "cmdb_ci"), ("cmdb_ci_ip_address", "nic.cmdb_ci"),
                         ("cmdb_ci_file_system", "computer"), ("cmdb_sam_sw_install", "installed_on"),
                         ("cmdb_software_instance", "installed_on"), ("cmdb_running_process", "computer")):
        try:
            out[table] = sn.count(table, f"{field}={ci_sys_id}")
        except SNError:
            out[table] = -1
    try:
        out["cmdb_rel_ci"] = sn.count("cmdb_rel_ci", f"parent={ci_sys_id}^ORchild={ci_sys_id}")
    except SNError:
        out["cmdb_rel_ci"] = -1
    return out


def class_chain(sn: SNClient, table: str) -> list[str]:
    """[table, parent, grandparent, ...] from sys_db_object."""
    chain = []
    t = table
    for _ in range(12):
        if not t or t in chain:
            break
        chain.append(t)
        row = sn.first("sys_db_object", f"name={t}", "super_class.name")
        t = (row or {}).get("super_class.name", "")
    return chain


def instance_failure_reason(sn: SNClient, agent_id: str, minutes: int = 30) -> str:
    """What the INSTANCE recorded about this agent's discovery: the ACC framework's log lines and the status/output
    of the last discovery check result the MID forwarded (ecc_queue MonitoringProbe input)."""
    import html as _html
    import json as _json
    parts: list[str] = []
    try:
        for l in sn.query("syslog", f"sys_created_on>=javascript:gs.minutesAgoStart({minutes})^messageLIKE{agent_id}^levelIN1,2^ORDERBYDESCsys_created_on",
                          "sys_created_on,message", 5):
            parts.append(f"{l['sys_created_on']} instance: {l['message'][:400]}")
    except SNError:
        pass
    try:
        rows = sn.query("ecc_queue", f"queue=input^topic=MonitoringProbe^sys_created_on>=javascript:gs.minutesAgoStart({minutes})^payloadLIKE{agent_id}^ORDERBYDESCsys_created_on",
                        "sys_created_on,payload", 2)
        for r in rows:
            p = _html.unescape(r.get("payload") or "")
            i, j = p.find("<output>"), p.find("</output>")
            if i < 0 or j < 0:
                continue
            try:
                for item in _json.loads(p[i + 8:j]):
                    if not isinstance(item, dict) or (item.get("agent_id") or item.get("agentId") or agent_id) != agent_id:
                        continue  # the MID batches several agents' results into one ECC record - another agent's error is not this one's
                    ch = item.get("check", {})
                    if ch.get("name"):
                        parts.append(f"{r['sys_created_on']} check {ch.get('name')} status {ch.get('status')} {ch.get('error_code') or ''}: {str(ch.get('output'))[:800]}")
                        break
            except ValueError:
                parts.append(f"{r['sys_created_on']} probe output: {p[i + 8:j][:400]}")
            break
    except SNError:
        pass
    return chr(10).join(parts)
