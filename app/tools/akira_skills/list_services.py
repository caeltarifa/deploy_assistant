from fastmcp import FastMCP
from playwright.sync_api import sync_playwright

from app.config import PLAYWRIGHT_SLOW_MO_MS
from app.tools.akira_skills.common import ensure_logged_in, new_context, try_save_state


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def list_service_names() -> dict[str, list[str]]:
        """Return the service names currently displayed in the service hub table."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=PLAYWRIGHT_SLOW_MO_MS)
            context = new_context(browser)
            page = context.new_page()

            ensure_logged_in(page, context)
            page.wait_for_load_state("networkidle")
            page.wait_for_selector("tbody tr", timeout=10000)

            rows = page.locator("tbody tr")
            services = []
            for index in range(rows.count()):
                row = rows.nth(index)
                name = row.evaluate(
                    """row => {
                        const span = row.querySelector('span[title]');
                        if (span) {
                            return (span.getAttribute('title') || span.textContent || '').trim();
                        }
                        for (const cell of row.querySelectorAll('td')) {
                            const text = (cell.textContent || '').trim();
                            if (text) return text;
                        }
                        return '';
                    }"""
                )
                if name:
                    services.append(name)

            try_save_state(context)
            browser.close()

        return {"services": services}
