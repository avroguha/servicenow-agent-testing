"""ServiceNow REST client: Table API, CI/CD API, attachments, and server-side script execution.

Server-side JavaScript runs through a run-once ``sys_trigger`` (system context, global scope). The script calls
``OUT(obj)`` for every value it wants to return; the values are logged to ``syslog`` under a unique source and read
back here. Basic-auth REST never creates a UI session: anything that is UI-only lives in browser.py.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path

import requests
import urllib3

LOG = logging.getLogger("acctest.snow")


class SNError(RuntimeError):
    pass


class SNClient:
    def __init__(self, instance: str, user: str, password: str, verify_tls: bool = True, timeout: int = 120):
        self.instance = instance.rstrip("/")
        self.s = requests.Session()
        self.s.auth = (user, password)
        self.s.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        self.s.verify = verify_tls
        if not verify_tls:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.timeout = timeout
        self.user = user

    # ---- low level ---------------------------------------------------------------------------------------------
    def _req(self, method: str, path: str, *, params=None, body=None, retries: int = 3, raw: bool = False):
        url = path if path.startswith("http") else self.instance + path
        last = None
        for attempt in range(retries):
            try:
                r = self.s.request(method, url, params=params, data=json.dumps(body) if body is not None else None,
                                   timeout=self.timeout)
            except requests.RequestException as e:
                last = e
                LOG.warning("%s %s failed (%s), retry %d", method, path, e, attempt + 1)
                time.sleep(3 * (attempt + 1))
                continue
            if r.status_code in (429, 502, 503, 504) and attempt < retries - 1:
                LOG.warning("%s %s -> %s, retry %d", method, path, r.status_code, attempt + 1)
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code >= 400:
                raise SNError(f"{method} {path} -> {r.status_code}: {r.text[:600]}")
            if raw:
                return r
            if r.status_code == 204 or not r.content:
                return {}
            return r.json()
        raise SNError(f"{method} {path} failed after {retries} attempts: {last}")

    # ---- Table API ---------------------------------------------------------------------------------------------
    def query(self, table: str, query: str = "", fields: str | None = None, limit: int = 100, display: str = "false",
              offset: int = 0) -> list[dict]:
        params = {"sysparm_query": query, "sysparm_limit": limit, "sysparm_display_value": display,
                  "sysparm_exclude_reference_link": "true", "sysparm_offset": offset}
        if fields:
            params["sysparm_fields"] = fields
        return self._req("GET", f"/api/now/table/{table}", params=params).get("result", [])

    def query_all(self, table: str, query: str = "", fields: str | None = None, page: int = 500, display="false",
                  max_rows: int = 20000) -> list[dict]:
        out: list[dict] = []
        while len(out) < max_rows:
            rows = self.query(table, query, fields, page, display, offset=len(out))
            out.extend(rows)
            if len(rows) < page:
                break
        return out

    def get(self, table: str, sys_id: str, fields: str | None = None, display="false") -> dict:
        params = {"sysparm_display_value": display, "sysparm_exclude_reference_link": "true"}
        if fields:
            params["sysparm_fields"] = fields
        return self._req("GET", f"/api/now/table/{table}/{sys_id}", params=params).get("result", {})

    def first(self, table: str, query: str, fields: str | None = None, display="false") -> dict | None:
        rows = self.query(table, query, fields, 1, display)
        return rows[0] if rows else None

    def insert(self, table: str, data: dict) -> dict:
        return self._req("POST", f"/api/now/table/{table}", body=data).get("result", {})

    def update(self, table: str, sys_id: str, data: dict) -> dict:
        return self._req("PATCH", f"/api/now/table/{table}/{sys_id}", body=data).get("result", {})

    def delete(self, table: str, sys_id: str) -> None:
        self._req("DELETE", f"/api/now/table/{table}/{sys_id}")

    def count(self, table: str, query: str = "") -> int:
        r = self._req("GET", "/api/now/stats/" + table, params={"sysparm_query": query, "sysparm_count": "true"})
        return int(r.get("result", {}).get("stats", {}).get("count", 0))

    def table_exists(self, name: str) -> bool:
        return bool(self.first("sys_db_object", f"name={name}", "name"))

    def property(self, name: str) -> str | None:
        row = self.first("sys_properties", f"name={name}", "value")
        return row["value"] if row else None

    # ---- server-side script ------------------------------------------------------------------------------------
    def run_script(self, js: str, timeout: int = 180, label: str = "run", scope: str | None = None):
        """Run server-side JS as system through a run-once sys_trigger. ``OUT(obj)`` returns values.
        sys_trigger.script holds 8000 characters - keep bodies short."""
        token = uuid.uuid4().hex[:12]
        src = "ACCTEST:" + token
        wrapped = ("var __out=[]; function OUT(o){__out.push(o);}\n"
                   "try {\n" + js + "\n} catch(e) { __out.push({__error: String(e), __stack: (e && e.stack) ? String(e.stack) : ''}); }\n"
                   "gs.log(JSON.stringify(__out), '" + src + "');")
        if len(wrapped) > 7900:
            raise SNError(f"run_script body too large ({len(wrapped)} chars, cap 8000)")
        body = {"name": "acctest " + label + " " + token, "trigger_type": "0", "script": wrapped,
                "next_action": "2000-01-01 00:00:00", "state": "0", "upgrade_safe": "false"}
        if scope:
            body["sys_scope"] = scope
        tr = self.insert("sys_trigger", body)
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(3)
            rows = self.query("syslog", "sys_created_on>=javascript:gs.minutesAgoStart(60)^source=" + src, "message", 1)
            if rows:
                try:
                    out = json.loads(rows[0]["message"])
                except Exception:
                    return rows[0]["message"]
                if out and isinstance(out[-1], dict) and "__error" in out[-1]:
                    raise SNError(f"server script '{label}' failed: {out[-1]['__error']}\n{out[-1].get('__stack', '')}")
                return out
        t = self.query("sys_trigger", "sys_id=" + tr.get("sys_id", ""), "state,last_error,error_count", 1)
        raise SNError(f"run_script '{label}' timed out after {timeout}s; trigger={t}")

    # ---- CI/CD API: store apps and plugins ---------------------------------------------------------------------
    def cicd_install_app(self, scope: str, version: str | None = None) -> str:
        params = {"scope": scope}
        if version:
            params["version"] = version
        r = self._req("POST", "/api/sn_cicd/app_repo/install", params=params, body={})
        return r["result"]["links"]["progress"]["id"]

    def cicd_activate_plugin(self, plugin_id: str) -> str:
        r = self._req("POST", f"/api/sn_cicd/plugin/{plugin_id}/activate", body={})
        return r["result"]["links"]["progress"]["id"]

    def cicd_progress(self, progress_id: str) -> dict:
        return self._req("GET", f"/api/sn_cicd/progress/{progress_id}")["result"]

    def cicd_wait(self, progress_id: str, timeout: int = 3600, interval: int = 20) -> dict:
        deadline = time.time() + timeout
        while time.time() < deadline:
            p = self.cicd_progress(progress_id)
            LOG.info("  progress %s%% %s %s", p.get("percent_complete"), p.get("status_label"), p.get("status_message") or "")
            if p.get("status") in ("2", "3", "4"):  # 2 successful, 3 failed, 4 cancelled
                return p
            time.sleep(interval)
        raise SNError("CI/CD operation did not finish in time")

    # ---- files -------------------------------------------------------------------------------------------------
    def download(self, url: str, dest: Path, chunk: int = 1 << 20) -> Path:
        """Download a URL (instance-relative or absolute). Instance URLs carry basic auth; public ones do not."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        full = url if url.startswith("http") else self.instance + url
        sess = self.s if full.startswith(self.instance) else requests.Session()
        with sess.get(full, stream=True, timeout=self.timeout, allow_redirects=True) as r:
            if r.status_code >= 400:
                raise SNError(f"download {full} -> {r.status_code}")
            with open(dest, "wb") as f:
                for part in r.iter_content(chunk):
                    f.write(part)
        return dest

    def attachment_bytes(self, sys_id: str) -> bytes:
        return self._req("GET", f"/api/now/attachment/{sys_id}/file", raw=True).content

    # ---- convenience -------------------------------------------------------------------------------------------
    def whoami(self) -> dict:
        return self.first("sys_user", f"user_name={self.user}", "user_name,name,sys_id") or {}

    def instance_info(self) -> dict:
        war = self.property("glide.war") or ""
        node = self.first("sys_cluster_state", "", "node_id,status") or {}
        return {"instance": self.instance, "build": war, "node": node.get("node_id", ""), "user": self.user}
