"""result.html - a self-contained report (no external assets, works offline, light and dark)."""
from __future__ import annotations

import html
from pathlib import Path

from .results import CAUSES, ERROR, FAIL, ORDER, PASS, RunResult, SKIP, WARN

LABEL = {PASS: "PASS", FAIL: "FAIL", WARN: "WARN", SKIP: "SKIP", ERROR: "ERROR"}
CAUSE_LABEL = {"agent": "Agent", "content": "Instance content", "target": "Server", "instance": "Instance / MID", "": "Not attributed"}
SECTIONS = ["Pre-flight", "Packages", "Install", "Environment", "Connectivity", "Discovery", "Checks", "Policies", "Resources",
            "Cleanup", "UI", "Uninstall"]

CSS = """
:root{--bg:#f6f7f9;--card:#fff;--fg:#1c2330;--muted:#5d6675;--line:#dfe3ea;--pass:#1d8a4a;--fail:#c62828;--warn:#b26a00;--skip:#6b7280;--error:#8e24aa;--accent:#2457c5;--code:#eef1f6}
@media (prefers-color-scheme:dark){:root{--bg:#0f141b;--card:#171e28;--fg:#e6eaf0;--muted:#9aa5b5;--line:#2a3442;--pass:#3ccf7a;--fail:#ff6b6b;--warn:#ffb340;--skip:#9aa5b5;--error:#d48cff;--accent:#6ea0ff;--code:#0b0f15}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1200px;margin:0 auto;padding:24px 16px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:28px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}h3{font-size:15px;margin:18px 0 8px}
.sub{color:var(--muted);margin-bottom:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin:10px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
.kv div{display:flex;justify-content:space-between;gap:12px;padding:3px 0;border-bottom:1px dotted var(--line)}.kv div span:first-child{color:var(--muted)}
.badge{display:inline-block;min-width:54px;text-align:center;padding:2px 8px;border-radius:12px;font-weight:600;font-size:12px;color:#fff;background:var(--skip)}
.badge.pass{background:var(--pass)}.badge.fail{background:var(--fail)}.badge.warn{background:var(--warn)}.badge.error{background:var(--error)}.badge.skip{background:var(--skip)}
.overall{font-size:28px;padding:8px 18px;border-radius:10px}
table{width:100%;border-collapse:collapse;background:var(--card)}th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.03em}
tr.fail td,tr.error td{background:color-mix(in srgb,var(--fail) 7%,var(--card))}
details{margin-top:4px}summary{cursor:pointer;color:var(--accent)}
pre{background:var(--code);border:1px solid var(--line);border-radius:6px;padding:10px;overflow:auto;max-height:420px;font-size:12px;white-space:pre-wrap;word-break:break-word}
.num{text-align:right;font-variant-numeric:tabular-nums}.muted{color:var(--muted)}.small{font-size:12px}
.pill{display:inline-block;padding:1px 7px;border:1px solid var(--line);border-radius:10px;font-size:12px;margin-right:4px}
img.shot{max-width:100%;border:1px solid var(--line);border-radius:6px;margin-top:6px}
.failbox{border-left:4px solid var(--fail);padding:8px 12px;margin:8px 0;background:color-mix(in srgb,var(--fail) 6%,var(--card))}
.pill.cause-agent{border-color:var(--fail);color:var(--fail)}.pill.cause-content{border-color:var(--warn);color:var(--warn)}
.pill.cause-target{border-color:var(--accent);color:var(--accent)}.pill.cause-instance{border-color:var(--error);color:var(--error)}
"""


def _e(s) -> str:
    return html.escape(str(s if s is not None else ""))


def _badge(status: str) -> str:
    return f'<span class="badge {status}">{LABEL.get(status, status)}</span>'


def render(run: RunResult) -> str:
    c = run.counts()
    overall = run.overall()
    parts: list[str] = []
    parts.append(f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                 f"<title>{_e(run.title or 'ACC agent qualification')} {_e(run.version)}</title><style>{CSS}</style></head><body><div class='wrap'>")
    parts.append(f"<h1>{_e(run.title or 'ACC agent qualification')} &mdash; agent {_e(run.version)}</h1>")
    parts.append(f"<div class='sub'>{_e(run.instance)} &middot; MID {_e(run.mid_server)} &middot; {_e(run.started)} &rarr; {_e(run.finished or '…')}</div>")

    # summary
    parts.append("<div class='card'><div style='display:flex;gap:18px;align-items:center;flex-wrap:wrap'>")
    parts.append(f"<span class='badge overall {overall}'>{LABEL[overall]}</span>")
    parts.append("<div class='kv' style='flex:1;min-width:260px'>")
    rt = run.runtimes or {}
    rows = [("Agent version", run.version), ("ACC Framework app", run.app_version), ("Instance build", run.build),
            ("MID endpoint", run.backend_url), ("Targets", ", ".join(t.get("name", "") for t in run.targets) or "none")]
    if rt.get("ruby"):
        rows.insert(1, ("Embedded Ruby", f"{rt['ruby']} ({rt.get('ruby_date', '')})"))
        rows.insert(2, ("Embedded OpenSSL", f"{rt.get('openssl', '?')} ({rt.get('openssl_date', '')})"))
    for k, v in rows:
        parts.append(f"<div><span>{_e(k)}</span><span>{_e(v)}</span></div>")
    parts.append("</div><div class='kv' style='min-width:200px'>")
    for s in (PASS, FAIL, WARN, ERROR, SKIP):
        parts.append(f"<div><span>{_badge(s)}</span><span class='num'>{c[s]}</span></div>")
    parts.append("</div></div></div>")

    # the agent verdict: only what the AGENT owns decides; environment findings are listed apart
    av = run.agent_verdict()
    agent_bad = run.agent_failures()
    env_bad = run.env_failures()
    parts.append("<h2>Agent verdict</h2><div class='card' style='display:flex;gap:18px;align-items:flex-start;flex-wrap:wrap'>")
    parts.append(f"<span class='badge overall {av}'>{'SAFE' if av == PASS else ('NOT SAFE' if av == FAIL else 'NOT TESTED')}</span><div style='flex:1;min-width:260px'>")
    if av == PASS:
        parts.append(f"<b>Agent {_e(run.version)} shows no defect of its own on the targets tested.</b> Every test that failed is owned by the "
                     "environment (server prerequisites, instance content or MID) and is listed under <i>Environment findings</i> below; "
                     "it will fail the same way with any agent version.")
    elif av == FAIL:
        parts.append(f"<b>{len(agent_bad)} failure(s) are the agent's own, or could not be attributed</b> - read them before deploying:<ul>"
                     + "".join(f"<li>{_e(r.section)} &rsaquo; {_e(r.name)}" + (f" <span class='pill'>{_e(r.target)}</span>" if r.target else "")
                               + f" <span class='pill cause-{_e(r.cause or 'none')}'>{_e(CAUSE_LABEL.get(r.cause, r.cause) if r.cause else 'not attributed')}</span>"
                               + f"<div class='small'>{_e(r.message[:300])}</div></li>" for r in agent_bad) + "</ul>")
    else:
        parts.append("Nothing was executed.")
    parts.append("</div></div>")
    if env_bad:
        parts.append("<h3>Environment findings <span class='small muted'>(not the agent's fault - fix the environment or raise with ServiceNow)</span></h3><table><tr><th>Cause</th><th>Test</th><th>Target</th><th>What</th></tr>")
        for r in env_bad:
            parts.append(f"<tr><td><span class='pill cause-{_e(r.cause)}'>{_e(CAUSE_LABEL.get(r.cause, r.cause))}</span></td><td>{_e(r.name)}</td><td>{_e(r.target)}</td><td class='small'>{_e(r.message[:400])}</td></tr>")
        parts.append("</table>")

    # verdict / failures first
    bad = [r for r in run.results if r.status in (FAIL, ERROR)]
    if bad:
        parts.append("<h2>What failed</h2>")
        causes = run.causes()
        parts.append("<div class='card'><b>Whose fault is it?</b> "
                     + " &middot; ".join(f"<span class='pill cause-{_e(c or 'none')}'>{_e(CAUSE_LABEL.get(c, c))}: {n}</span>" for c, n in
                                         sorted(causes.items(), key=lambda kv: -kv[1]))
                     + "<div class='small muted' style='margin-top:6px'>"
                     + " ".join(f"<b>{_e(CAUSE_LABEL[c])}</b> = {_e(CAUSES[c])}." for c in CAUSES if c in causes)
                     + (" <b>Not attributed</b> = the evidence does not say; read it." if "" in causes else "")
                     + "</div></div>")
        for r in bad:
            parts.append(f"<div class='failbox'><b>{_e(r.section)} &rsaquo; {_e(r.name)}</b>"
                         + (f" <span class='pill'>{_e(r.target)}</span>" if r.target else "")
                         + (f" <span class='pill cause-{_e(r.cause)}'>cause: {_e(CAUSE_LABEL.get(r.cause, r.cause))}</span>" if r.cause else "")
                         + f"<div>{_e(r.message)}</div>"
                         + (f"<details><summary>evidence</summary><pre>{_e(r.details)}</pre></details>" if r.details else "")
                         + "</div>")
    else:
        parts.append("<div class='card'>No failures. Every executed test passed"
                     + (f"; {c[WARN]} warning(s) need a look." if c[WARN] else ".") + "</div>")

    # per target matrix
    if run.targets:
        parts.append("<h2>Targets</h2><table><tr><th>Target</th><th>OS</th><th>Package</th><th>Reach</th>"
                     + "".join(f"<th>{_e(s)}</th>" for s in SECTIONS if any(r.section == s and r.target for r in run.results))
                     + "<th>Result</th></tr>")
        for t in run.targets:
            name = t.get("name", "")
            rows = [r for r in run.results if r.target == name]
            cells = []
            for s in SECTIONS:
                if not any(r.section == s and r.target for r in run.results):
                    continue
                sec = [r for r in rows if r.section == s]
                if not sec:
                    cells.append("<td class='muted'>&ndash;</td>")
                    continue
                worst = min(sec, key=lambda r: ORDER[r.status]).status
                cnt = sum(1 for r in sec if r.status == PASS)
                cells.append(f"<td>{_badge(worst)} <span class='small muted'>{cnt}/{len(sec)}</span></td>")
            worst_all = min(rows, key=lambda r: ORDER[r.status]).status if rows else SKIP
            parts.append(f"<tr><td><b>{_e(name)}</b></td><td>{_e(t.get('distro') or t.get('os'))}</td><td>{_e(t.get('os'))}</td>"
                         f"<td class='small'>{_e(t.get('transport'))} {_e(t.get('host') or t.get('vmid', ''))}</td>{''.join(cells)}<td>{_badge(worst_all)}</td></tr>")
        parts.append("</table>")

    # packages
    if run.packages:
        parts.append("<h2>Agent packages (dist/)</h2><table><tr><th>OS key</th><th>File</th><th class='num'>Size</th><th>SHA-256</th><th>State</th></tr>")
        for p in run.packages:
            size = p.get("size") or 0
            state = "downloaded" if p.get("downloaded") else ("available" if p.get("available") else "not on server")
            parts.append(f"<tr><td>{_e(p.get('os_key'))}</td><td class='small'>{_e(p.get('file'))}</td><td class='num'>{size / (1 << 20):.1f} MB</td>"
                         f"<td class='small' style='font-family:monospace'>{_e((p.get('sha256') or '')[:16])}{'…' if p.get('sha256') else ''}</td><td>{_e(state)}</td></tr>")
        parts.append("</table>")

    # components for the security audit
    if run.components:
        targets = sorted({c.get("target", "") for c in run.components})
        parts.append("<h2>Components inside the agent <span class='small muted'>(for the security audit; also components.csv)</span></h2>"
                     "<div class='card small'>The agent carries its own interpreter, crypto library and gems, independent of what the OS has. "
                     "Rows marked <i>package</i> were read from the downloaded package without installing; rows with a target name were read on that host after "
                     "installation. Plugin assets come from the instance (content apps), not from the agent package.</div>")
        parts.append("<table><tr><th>Component</th><th>Version</th><th>Kind</th><th>Source</th><th>Seen on</th></tr>")
        key_order = {"agent": 0, "agent package": 0, "compiler/runtime": 1, "interpreter": 2, "crypto library": 3, "tool (from the instance)": 4,
                     "shared library": 5, "plugin content (from the instance)": 6, "Ruby gem": 7}
        for c in sorted(run.components, key=lambda c: (key_order.get(c.get("kind", ""), 9), c.get("component", ""), c.get("target", ""))):
            parts.append(f"<tr><td>{_e(c.get('component'))}</td><td class='small' style='font-family:monospace'>{_e(c.get('version'))}</td><td class='small'>{_e(c.get('kind'))}</td>"
                         f"<td class='small'>{_e(c.get('source'))}</td><td class='small'>{_e(c.get('target') or 'package')}</td></tr>")
        parts.append("</table>")

    # performance: what the agent cost the host while it worked
    if run.perf:
        parts.append("<h2>Performance <span class='small muted'>(agent resource usage and host impact; raw samples in perf-&lt;target&gt;.csv)</span></h2>"
                     "<div class='card small'>Sampled on the host every few seconds while the agent worked. <b>Agent CPU</b> is the whole agent process tree "
                     "(acc plus the checks and osquery it spawns) in % of one core; <b>share of host</b> is that same CPU as a fraction of all cores. "
                     "<b>Host CPU busy</b> is the whole machine, everything included. The <i>idle</i> row is the agent connected with nothing to do; "
                     "the difference between the working phases and idle is the agent's impact on the host.</div>")
        for p in run.perf:
            parts.append(f"<h3>{_e(p.get('target'))} <span class='small muted'>{_e(p.get('distro') or '')} &middot; {p.get('ncpu')} cores &middot; "
                         f"{p.get('samples')} samples every {p.get('step_s', '?')}s</span></h3>")
            parts.append("<table><tr><th>Phase</th><th class='num'>Seconds</th><th class='num'>Agent CPU avg / peak<br><span class='muted small'>% of one core</span></th>"
                         "<th class='num'>Share of host</th><th class='num'>Agent RSS avg / peak MB</th><th class='num'>Procs / threads / fds</th>"
                         "<th class='num'>Disk read / written MB</th><th class='num'>Host CPU busy avg / peak</th><th class='num'>Load1 max</th><th class='num'>Host memory used &Delta; MB</th></tr>")
            rows = list(p.get("phases", [])) + [dict(p.get("impact", {}).get("load", {}), phase="all working phases"), dict(p.get("overall", {}), phase="whole window")]
            for ph in rows:
                if not ph.get("samples"):
                    parts.append(f"<tr><td>{_e(ph.get('phase'))}</td><td class='num'>{ph.get('duration_s', 0)}</td><td colspan='8' class='muted small'>no samples</td></tr>")
                    continue
                parts.append(f"<tr><td><b>{_e(ph.get('phase'))}</b></td><td class='num'>{ph['duration_s']}</td>"
                             f"<td class='num'>{ph['agent_cpu_avg']:g} / {ph['agent_cpu_peak']:g}</td><td class='num'>{ph['agent_share_avg']:g}%</td>"
                             f"<td class='num'>{ph['agent_rss_avg_mb']} / {ph['agent_rss_peak_mb']}</td>"
                             f"<td class='num'>{ph['agent_procs_max']} / {ph['agent_threads_max']} / {ph['agent_fds_max']}</td>"
                             f"<td class='num'>{ph['agent_read_mb']:g} / {ph['agent_write_mb']:g}</td>"
                             f"<td class='num'>{ph['host_busy_avg']:g}% / {ph['host_busy_peak']:g}%</td><td class='num'>{ph['load1_max']:g}</td>"
                             f"<td class='num'>{ph['host_mem_delta_mb']:+d}</td></tr>")
            parts.append("</table>")
            imp = p.get("impact", {})
            if imp.get("host_busy_delta") is not None:
                parts.append(f"<div class='small' style='margin:-6px 0 14px'>Host impact: CPU busy <b>{imp['host_busy_delta']:+g} points</b> working vs idle; "
                             f"the agent tree itself averaged <b>{imp.get('agent_share_load_avg'):g}%</b> of the host's CPU capacity while working"
                             + ("" if p.get("io_readable") else "; disk counters were not readable on this host (sampler not root)") + ".</div>")

    # all results by section
    parts.append("<h2>All tests</h2>")
    for s in SECTIONS:
        rows = [r for r in run.results if r.section == s]
        if not rows:
            continue
        parts.append(f"<h3>{_e(s)} <span class='small muted'>({len(rows)})</span></h3><table><tr><th style='width:70px'>Status</th><th>Test</th><th>Target</th><th>Result</th><th class='num'>s</th></tr>")
        for r in sorted(rows, key=lambda r: (ORDER[r.status], r.target, r.name)):
            det = ""
            if r.details:
                det += f"<details><summary>evidence</summary><pre>{_e(r.details)}</pre></details>"
            if r.evidence:
                ev = "\n".join(f"{k}: {v}" for k, v in r.evidence.items())
                det += f"<details><summary>data</summary><pre>{_e(ev)}</pre></details>"
            if r.screenshot:
                det += f"<details><summary>screenshot</summary><img class='shot' src='{_e(r.screenshot)}' alt='screenshot'></details>"
            cause = f" <span class='pill cause-{_e(r.cause)}'>cause: {_e(CAUSE_LABEL.get(r.cause, r.cause))}</span>" if r.cause else ""
            parts.append(f"<tr class='{r.status}'><td>{_badge(r.status)}{cause}</td><td><b>{_e(r.name)}</b><div class='small muted'>{_e(r.id)}</div></td>"
                         f"<td>{_e(r.target)}</td><td>{_e(r.message)}{det}</td><td class='num'>{r.duration_s:.0f}</td></tr>")
        parts.append("</table>")

    if run.notes:
        parts.append("<h2>Notes</h2><div class='card'><ul>" + "".join(f"<li>{_e(n)}</li>" for n in run.notes) + "</ul></div>")

    parts.append("<h2>Settings used</h2><div class='card kv small'>")
    for k, v in sorted(run.settings.items()):
        parts.append(f"<div><span>{_e(k)}</span><span>{_e(v)}</span></div>")
    parts.append("</div><div class='muted small' style='margin-top:24px'>Generated by acctest. Secrets are redacted; host names and addresses are those of the environment the run was made in.</div></div></body></html>")
    return "".join(parts)


def write_report(run: RunResult, out_dir: Path, basename: str = "result") -> Path:
    """result.html for a full run; a subset run (--targets) is written as result-partial-<timestamp>.html so it never
    replaces the full picture of the version."""
    out_dir.mkdir(parents=True, exist_ok=True)
    run.save(out_dir / f"{basename}.json")
    p = out_dir / f"{basename}.html"
    p.write_text(render(run), encoding="utf-8")
    if run.components:
        import csv
        with (out_dir / ("components.csv" if basename == "result" else f"{basename}-components.csv")).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["component", "version", "kind", "source", "target"], extrasaction="ignore")
            w.writeheader()
            for c in run.components:
                w.writerow({**c, "target": c.get("target") or "package"})
    for p_ in run.perf:
        series = p_.get("series") or []
        if not series:
            continue
        import csv
        fn = (f"perf-{p_.get('target')}.csv" if basename == "result" else f"{basename}-perf-{p_.get('target')}.csv")
        with (out_dir / fn).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(series[0].keys()), extrasaction="ignore")
            w.writeheader()
            for row in series:
                w.writerow(row)
    return p
