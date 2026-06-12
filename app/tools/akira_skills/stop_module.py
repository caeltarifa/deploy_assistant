from fastmcp import FastMCP
from playwright.sync_api import sync_playwright

from app.config import PLAYWRIGHT_POSTSUBMIT_WAIT_MS, PLAYWRIGHT_SLOW_MO_MS
from app.tools.akira_skills.common import (
    ensure_logged_in,
    find_service_row,
    new_context,
    try_save_state,
)


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def stop_service_module(service_name: str) -> str:
        """Stop a service module from the service hub row by name."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=PLAYWRIGHT_SLOW_MO_MS)
            context = new_context(browser)
            page = context.new_page()

            ensure_logged_in(page, context)
            page.wait_for_load_state("networkidle")

            page.wait_for_selector("tbody tr", timeout=10000)
            row = find_service_row(page, service_name)

            if row.count() == 0:
                try_save_state(context)
                browser.close()
                return f"Service module '{service_name}' not found in table."

            # If already stopped, return early
            status_label = row.locator("label").first
            try:
                status_text = status_label.inner_text(timeout=1000).strip().lower()
            except Exception:
                status_text = ""
            if status_text in {"apagado", "detenido", "stopped", "off", "idle"}:
                browser.close()
                return f"Service module '{service_name}' already stopped ✅"
            if row.locator("button:has(i:has-text('play_arrow'))").count() > 0:
                browser.close()
                return f"Service module '{service_name}' already stopped ✅"

            stop_btn = row.locator(
                "button:has(i:has-text('stop')), button:has(i:has-text('stop_circle')), button:has(i:has-text('pause'))"
            ).first
            if stop_btn.count() == 0:
                stop_btn = row.locator("button.rz-danger").first
            if stop_btn.count() == 0:
                raise RuntimeError(f"Stop button not found for '{service_name}'")

            stop_btn.click()
            page.wait_for_selector(".rz-dialog.rz-open.rz-dialog-confirm", timeout=5000)
            page.locator(
                ".rz-dialog.rz-open.rz-dialog-confirm button:has-text('Ok')"
            ).first.click()

            page.wait_for_timeout(PLAYWRIGHT_POSTSUBMIT_WAIT_MS)
            try_save_state(context)
            browser.close()

        return f"Service module '{service_name}' stop requested ✅"
