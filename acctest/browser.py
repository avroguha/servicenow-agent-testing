"""Headless browser (Playwright + Chromium) for the few things REST cannot do or cannot prove.

REST with basic auth never creates a UI session, so UI-only verifications - the agent form rendering, the Agent
Downloads page, the check definition / policy lists as an operator sees them - go through a real logged-in browser.
Screenshots land in the results directory and are linked from result.html.

Usage:
    with Browser(settings, shots_dir) as b:
        if b.login():
            path = b.shot("agent_downloads", "/sn_agent_agent_downloads.do")
"""
from __future__ import annotations

import logging
from pathlib import Path

from .config import Settings
from .util import safe_name

LOG = logging.getLogger("acctest.browser")


class Browser:
    def __init__(self, settings: Settings, shots_dir: Path):
        self.s = settings
        self.shots_dir = shots_dir
        self._pw = None
        self._browser = None
        self.page = None
        self.logged_in = False
        self.error = ""

    # ---- lifecycle -------------------------------------------------------------------------------------------------
    def __enter__(self) -> "Browser":
        if not self.s.browser_enabled:
            self.error = "BROWSER_ENABLED=false"
            return self
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.error = "playwright is not installed (pip install playwright; python -m playwright install chromium)"
            LOG.warning(self.error)
            return self
        try:
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=self.s.browser_headless)
            ctx = self._browser.new_context(viewport={"width": 1400, "height": 900}, ignore_https_errors=not self.s.sn_verify_tls)
            self.page = ctx.new_page()
            self.page.set_default_timeout(60000)
        except Exception as e:  # browser binaries missing etc.
            self.error = f"could not start Chromium: {e}"
            LOG.warning(self.error)
            self.page = None
        return self

    def __exit__(self, *exc) -> None:
        try:
            if self._browser:
                self._browser.close()
            if self._pw:
                self._pw.stop()
        except Exception:
            pass

    @property
    def available(self) -> bool:
        return self.page is not None

    # ---- actions ---------------------------------------------------------------------------------------------------
    def login(self) -> bool:
        if not self.available:
            return False
        if not self.s.sn_ui_login:
            self.error = "SN_UI_LOGIN=false (SSO instance) - UI checks skipped"
            return False
        try:
            self.page.goto(self.s.sn_instance + "/login.do", wait_until="domcontentloaded")
            self.page.fill("#user_name", self.s.sn_user)
            self.page.fill("#user_password", self.s.sn_pass)
            self.page.click("#sysverb_login")
            self.page.wait_for_load_state("networkidle")
            # a successful login leaves /login.do; the Next Experience shell or a classic frame page loads
            ok = "login.do" not in self.page.url and "login_redirect" not in self.page.url
            if not ok:
                # the login form shows an error banner when credentials are wrong
                msg = self.page.locator(".alert, .notification-error, #output_messages").all_inner_texts()
                self.error = "UI login failed: " + " ".join(m.strip() for m in msg if m.strip())[:300]
            self.logged_in = ok
            return ok
        except Exception as e:
            self.error = f"UI login error: {e}"
            LOG.warning(self.error)
            return False

    def goto(self, path: str, wait: str = "networkidle") -> bool:
        if not self.available:
            return False
        try:
            url = path if path.startswith("http") else self.s.sn_instance + path
            self.page.goto(url, wait_until="domcontentloaded")
            try:
                self.page.wait_for_load_state(wait, timeout=30000)
            except Exception:
                pass
            return True
        except Exception as e:
            self.error = f"navigation to {path} failed: {e}"
            return False

    def text(self, selector: str = "body", frame: str | None = "iframe#gsft_main") -> str:
        """Visible text of the page (or of the classic UI frame when present)."""
        if not self.available:
            return ""
        try:
            if frame:
                fl = self.page.frame_locator(frame)
                if fl.locator("body").count():
                    return fl.locator(selector).first.inner_text(timeout=15000)
            return self.page.locator(selector).first.inner_text(timeout=15000)
        except Exception:
            try:
                return self.page.locator(selector).first.inner_text(timeout=15000)
            except Exception:
                return ""

    def html(self, frame: str | None = "iframe#gsft_main") -> str:
        """Full HTML of the page (or of the classic UI frame when present) - for values that live in attributes."""
        if not self.available:
            return ""
        try:
            if frame:
                for f in self.page.frames:
                    if f != self.page.main_frame and "gsft_main" in (f.name or "") + (f.url or ""):
                        return f.content()
            return self.page.content()
        except Exception:
            return ""

    def shot(self, name: str, path: str | None = None) -> str:
        """Navigate (optional) and save a screenshot; returns the file name relative to shots_dir ('' on failure)."""
        if not self.available or not self.s.browser_screenshots:
            return ""
        if path and not self.goto(path):
            return ""
        self.shots_dir.mkdir(parents=True, exist_ok=True)
        fname = safe_name(name) + ".png"
        try:
            self.page.screenshot(path=str(self.shots_dir / fname), full_page=False)
            return fname
        except Exception as e:
            LOG.warning("screenshot %s failed: %s", name, e)
            return ""

    def classic(self, target: str) -> str:
        """URL of a classic page inside the Next Experience frame."""
        return f"/now/nav/ui/classic/params/target/{target}"
