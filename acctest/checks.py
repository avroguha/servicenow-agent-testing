"""Check definitions and policies: enumerate what the instance has, decide what applies to a target, run it, judge it.

Vocabulary (ACC Framework 7.x):
  sn_agent_check_def       a check definition (OOB from sn_agent / sn_acc_vis_content / sn_itmon, or custom)
  sn_agent_check_type      how the MID handles the result (Discovery, TestCheck, SelfTest, Upgrade, ... )
  sn_agent_check_group     binds a check def to a CI class (ci_type); default class is cmdb_ci_computer
  sn_agent_check_param_def parameters (mandatory ones without a default cannot be tested blindly)
  sn_agent_policy          a published policy = checks scheduled on the agents whose CI matches table + filter
  sn_agent_check           a check instance inside a policy
  sn_agent_test_result     the result of an ad-hoc "Test check" (status 0 pending 1 in progress 2 complete 3 error
                           4 cancelled; check_status = the check's exit code; output = stdout)

Ad-hoc run: POST /api/sn_agent/agents/check_defs/<id>/test {ci_id} -> test_result_id; GET /exec/test/<id> returns
202 while pending, 200 when complete (the CI must be the discovered host CI of a class allowed by the check group,
with an agent that is Up). Check instances: POST /check_instances/<id>/test.
"""
from __future__ import annotations

import json
import logging
import re
import time

from .snow import SNClient, SNError

LOG = logging.getLogger("acctest.checks")

# check types that are agent-internal operations (driven by their own UI actions), not content to run ad hoc
INTERNAL_TYPES = {"Upgrade", "Cancel", "Restart", "Regenerate Agent ID", "AddAttachment", "ReportFile", "TestCheck", "SelfTest",
                  "ProtectAgent", "ProtectAgent_DisabledCheckPayload", "Upgrade log file", "System Command"}
OOB_SCOPES_PREFIX = "sn_"
EXIT_LABEL = {0: "OK", 1: "WARNING", 2: "CRITICAL"}

CHECK_DEF_FIELDS = ("sys_id,name,label,active,description,command,command_prefix,background,timeout,exec_mode,interval,is_cron,"
                    "check_script_type,check_script_type.name,check_group,check_group.group,check_group.ci_type,sys_scope,"
                    "sys_scope.scope,sys_scope.name,sys_package.name,sys_customer_update,sys_created_by,sys_created_on,sys_updated_on,"
                    "assets,config_files,send_results,sys_overrides")


def list_check_defs(sn: SNClient, active_only: bool = True) -> list[dict]:
    q = "active=true" if active_only else ""
    rows = sn.query_all("sn_agent_check_def", q, CHECK_DEF_FIELDS, page=300)
    params = sn.query_all("sn_agent_check_param_def", "active=true", "check_def,name,mandatory,default_value,value_required", page=500)
    secure = sn.query_all("sn_agent_check_secure_param_def", "", "check_def,name", page=500)
    by_def: dict[str, list] = {}
    for p in params:
        by_def.setdefault(p["check_def"], []).append(p)
    sec_by_def: dict[str, int] = {}
    for p in secure:
        sec_by_def[p["check_def"]] = sec_by_def.get(p["check_def"], 0) + 1
    for r in rows:
        r["params"] = by_def.get(r["sys_id"], [])
        r["secure_params"] = sec_by_def.get(r["sys_id"], 0)
        r["origin"] = classify_origin(r)
        r["type_name"] = r.get("check_script_type.name", "")
        r["internal"] = r["type_name"] in INTERNAL_TYPES
        r["missing_mandatory"] = [p["name"] for p in r["params"] if p.get("mandatory") == "true" and not p.get("default_value")]
    return rows


def classify_origin(r: dict) -> str:
    """oob | customized | custom."""
    scope = r.get("sys_scope.scope") or ""
    if scope.startswith(OOB_SCOPES_PREFIX):
        return "customized" if r.get("sys_customer_update") == "true" else "oob"
    return "custom"


def applies_to_class(r: dict, class_chain: list[str]) -> bool:
    """A check applies when its group's ci_type is the target CI class or one of its ancestors (default cmdb_ci_computer)."""
    ci_type = r.get("check_group.ci_type") or "cmdb_ci_computer"
    return ci_type in class_chain


def testable(r: dict) -> tuple[bool, str]:
    """Can this definition be exercised with an ad-hoc test? (reason when not)"""
    if r.get("active") != "true":
        return False, "inactive"
    if r["internal"]:
        return False, f"internal check type {r['type_name']}"
    if r.get("background") == "true":
        return False, "background check (ad-hoc test not supported by the platform)"
    if r["secure_params"]:
        return False, "needs credentials (secure parameters)"
    if r["missing_mandatory"]:
        return False, "mandatory parameters without default: " + ", ".join(r["missing_mandatory"])
    return True, ""


# ---- running --------------------------------------------------------------------------------------------------------
def start_test(sn: SNClient, check_def_id: str, ci_id: str, instance: bool = False) -> str:
    kind = "check_instances" if instance else "check_defs"
    r = sn.s.post(f"{sn.instance}/api/sn_agent/agents/{kind}/{check_def_id}/test", json={"ci_id": ci_id}, timeout=sn.timeout)
    if r.status_code >= 400:
        try:
            detail = r.json().get("error", {})
            msg = f"{detail.get('message', '')}: {detail.get('detail', '')}"
        except Exception:
            msg = r.text[:300]
        raise SNError(f"test request refused ({r.status_code}) {msg}")
    j = r.json()
    return (j.get("result") or j)["test_result_id"]


def wait_test(sn: SNClient, test_result_id: str, timeout: int, interval: int = 5) -> dict:
    """Poll until complete/error/timeout. Returns the sn_agent_test_result row plus 'outcome'."""
    deadline = time.time() + timeout
    http = None
    while time.time() < deadline:
        r = sn.s.get(f"{sn.instance}/api/sn_agent/agents/exec/test/{test_result_id}", timeout=sn.timeout)
        http = r.status_code
        if http == 200:
            break
        if http not in (202,):
            break
        time.sleep(interval)
    row = sn.get("sn_agent_test_result", test_result_id,
                 "sys_id,status,check_status,output,error_msg,agent,agent_request,check_def,check_instance,sys_created_on,sys_updated_on") or {}
    status = row.get("status", "")
    if http == 200 and status == "2":
        row["outcome"] = "complete"
    elif http == 408 or status in ("0", "1"):
        row["outcome"] = "timeout"
    elif status == "3" or (http or 0) >= 400:
        row["outcome"] = "error"
    elif status == "4":
        row["outcome"] = "cancelled"
    else:
        row["outcome"] = "unknown"
    row["http"] = http
    return row


def is_allowlist_denial(row: dict) -> bool:
    low = ((row.get("output") or "") + (row.get("error_msg") or "")).lower()[:400]
    return "denied by the agent allow list" in low or "not allowed by allow-list" in low


def is_asset_error(row: dict) -> bool:
    low = (row.get("output") or "").lower() + (row.get("error_msg") or "").lower()
    return "hash of the file does not match" in low or "error getting assets" in low or "could not validate downloaded asset" in low


def wait_seconds(settings_timeout: int, def_timeout) -> int:
    """How long to wait for one ad-hoc test: at least CHECK_TIMEOUT_S, and at least the definition's own timeout + 30 s."""
    try:
        t = int(str(def_timeout or "0").strip())
    except ValueError:
        t = 0
    return max(settings_timeout, min(t + 30, 1800))


def judge(row: dict, output_limit: int = 2000) -> tuple[str, str]:
    """(status, message) from a finished test result. The question is 'does the agent run this check correctly',
    not 'is the host healthy': OK/WARNING/CRITICAL exit codes with output all count as a working check."""
    out = (row.get("output") or "").strip()
    if row["outcome"] != "complete":
        return "fail", f"{row['outcome']}: {row.get('error_msg') or 'no result from the agent within the timeout'}"
    try:
        rc = int(row.get("check_status") or 0)
    except ValueError:
        rc = -1
    low = out.lower()
    if "hash of the file does not match" in low or "error getting assets" in low or "could not validate downloaded asset" in low:
        return "fail", "ACC-1500 plugin asset error (the MID served a stale or unknown plugin): " + out[:200].replace(chr(10), " ")
    # execution-level failures show up at the START of the output (the shell / interpreter / allow-list speaks first);
    # the same words deeper inside a check's own structured output are data (e.g. a script reporting what it could not read)
    head = low[:400]
    exec_err = any(t in head for t in ("command not found", "no such file or directory", "is not recognized as an internal or external command",
                                        "executable file not found", "exec format error", "denied by the agent allow list", "not allowed by allow-list",
                                        "/usr/bin/env:", "traceback (most recent call last)"))
    if exec_err:
        return "fail", f"exit {rc}: the check could not execute properly - " + out[:200].replace("\n", " ")
    if rc in EXIT_LABEL:
        return "pass", f"exit {rc} ({EXIT_LABEL[rc]}), {len(out)} chars of output"
    if "permission denied" in head:
        return "fail", f"exit {rc}: permission denied - " + out[:200].replace("\n", " ")
    return "warn", f"exit {rc} (UNKNOWN) - " + out[:200].replace("\n", " ")


def attribute(row: dict, status: str, origin: str = "oob") -> tuple[str, str]:
    """Who owns a failed check: (cause, one-line hint). Causes are results.CAUSES keys; '' when it cannot be told.

    The shell / interpreter speaks first in the output, so the head of the output says what could not run:
      'ruby\\r': No such file      -> the plugin script has Windows line endings: content shipped by the instance app
      <plugin>.rb: No such file    -> the plugin asset did not arrive or lacks the file: content / MID
      <system tool>: not found     -> the server lacks a prerequisite: target
      permission denied            -> target (sudoers, file modes)
      hash of the file does not match (ACC-1500) -> the MID served a stale plugin: instance
      allow-list denial            -> the allow-list travels with the content: content
      no result within the timeout -> cannot be told apart here (agent hung, MID queue, slow host): ''
    """
    if status not in ("fail", "error"):
        return "", ""
    out = ((row.get("output") or "") + " " + (row.get("error_msg") or ""))
    low = out.lower()
    head = low[:400]
    if "\\r" in head or "\r" in head[:200] or "ruby\\r" in head:
        return "content", "the plugin script has Windows (CRLF) line endings - shipped that way by the content app; independent of the agent version"
    if "couldn't verify asset" in low or "signature file" in low or "no custom certificates" in low:
        return "target", ("the agent's acc.yml has verify-plugin-signature on (the default) and this plugin carries no ServiceNow signature: "
                          "custom plugins need signing per ServiceNow's procedure, or verify-plugin-signature: false on the agents")
    if "hash of the file does not match" in low or "error getting assets" in low or "could not validate downloaded asset" in low:
        return "instance", "the MID served a plugin the agent rejects (stale plugin cache) - restart/sync the MID"
    if (("websocket: close 1006" in low or "reconnection attempt failed" in low or "connection refused" in low) and "wss://" in low) \
            or "mid server not found" in low:
        return "instance", ("the agent lost its MID connection (MID restarted or unreachable) while the result was in flight; the agent does "
                            "not retry results of checks with an interval under 300 s, by design - re-run with the MID stable")
    if '"error_backtrace"' in out or re.search(r"/(?:acc-f-[a-z-]+|acc-visibility[a-z-]*)/bin/\S+\.rb:\d+:in ", out):
        err = re.search(r"\((\w+(?:Error|Exception))\)", out)
        return "content", (f"a shipped plugin module crashed inside the content ({err.group(1) if err else 'Ruby error'}) - module code "
                           "delivered by the content app, not the agent")
    if "denied by the agent allow list" in low or "not allowed by allow-list" in low:
        return "content", ("the allow-list delivered with the check content has no entry for this command on this OS"
                           + (" - generate allow-list content for the custom check" if origin == "custom" else ""))
    if "permission denied" in head:
        return "target", "the servicenow user lacks a permission on this server (sudoers entry, file mode)"
    m = re.search(r"(?:env: |/bin/sh: \d*:? ?|bash: )?'?([^\s':]+)'?: (?:no such file or directory|command not found|not found)", head)
    if m:
        what = m.group(1)
        if re.search(r"\.(rb|sh|py|ps1)$", what) or "/acc-" in what or "agent-client-collector" in what:
            return "content", f"the plugin file {what} is missing from the delivered asset"
        return "target", f"'{what}' is not installed on this server (agent checks expect it in PATH)"
    if "traceback (most recent call last)" in head or "exec format error" in head:
        return "content", "the plugin script itself crashed"
    if row.get("outcome") in ("timeout", "error", "cancelled"):
        return "", ""
    return "", ""


# ---- policies -------------------------------------------------------------------------------------------------------
POLICY_FIELDS = ("sys_id,name,description,active,publish_status,table,filter,is_draft,published_parent,sys_scope.scope,sys_customer_update,"
                 "monitored_ci_type_script,monitored_ci_type_group,proxy_advanced,single_proxy_agent,proxy_cluster,interval,is_interval,is_cron,"
                 "sys_created_by,sys_updated_on,checks_str")


def list_policies(sn: SNClient) -> list[dict]:
    rows = sn.query_all("sn_agent_policy", "active=true^is_draft=false^published_parentISEMPTY", POLICY_FIELDS, page=300)
    for p in rows:
        p["origin"] = classify_origin({"sys_scope.scope": p.get("sys_scope.scope"), "sys_customer_update": p.get("sys_customer_update")})
        p["checks"] = sn.query("sn_agent_check", f"monitoring_policy={p['sys_id']}^active=true^is_draft=false",
                               "sys_id,name,label,check_def,check_def.name,check_def.check_script_type.name,background,interval,timeout,command", 100)
        p["proxy"] = any(p.get(k) == "true" for k in ("proxy_advanced", "single_proxy_agent", "proxy_cluster"))
    return rows


def policy_matches_ci(sn: SNClient, policy: dict, ci_id: str) -> tuple[bool, str]:
    """Evaluate the policy's table + filter against one CI on the instance (table/filter policies only)."""
    if policy.get("monitored_ci_type_script") == "true" or policy.get("monitored_ci_type_group") == "true":
        return False, "policy selects CIs by script/group - not evaluated"
    table = policy.get("table") or ""
    if not table:
        return False, "policy has no table"
    js = ("var g = new GlideRecord(%s); g.addQuery('sys_id', %s); if (%s) g.addEncodedQuery(%s); g.query(); OUT({m: g.hasNext(), t: g.getTableName()});"
          % (json.dumps(table), json.dumps(ci_id), json.dumps(bool(policy.get("filter"))), json.dumps(policy.get("filter") or "")))
    try:
        out = sn.run_script(js, 120, "policy-match")
    except SNError as e:
        return False, f"could not evaluate: {e}"
    m = bool(out and out[0].get("m"))
    return m, "matches" if m else f"CI is not in {table} with filter '{policy.get('filter') or ''}'"


def policy_clients(sn: SNClient, policy_id: str) -> dict | None:
    return sn.first("sn_agent_policy_clients", f"policy={policy_id}", "sys_id,agents_list,sys_updated_on,force_recalc")


def scheduled_checks_request(sn: SNClient, agent_ci_sys_id: str) -> str:
    """Ask the agent for its configured (scheduled) checks - the 'Get Scheduled Checks' action. Returns a request id."""
    js = ("var u = new sn_agent.AgentSystemCommandUtil(); var r = u.getConfiguredChecksForAgent ? u.getConfiguredChecksForAgent(%s) : null; OUT({r: r});"
          % json.dumps(agent_ci_sys_id))
    out = sn.run_script(js, 120, "scheduled-checks")
    return (out[0] or {}).get("r") or ""
