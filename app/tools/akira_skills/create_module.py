from fastmcp import FastMCP
from playwright.sync_api import sync_playwright

from app.config import (
    PLAYWRIGHT_ACTION_WAIT_MS,
    PLAYWRIGHT_POSTCLOSE_WAIT_MS,
    PLAYWRIGHT_POSTSUBMIT_WAIT_MS,
    PLAYWRIGHT_POSTTYPE_WAIT_MS,
    PLAYWRIGHT_PRETYPE_WAIT_MS,
    PLAYWRIGHT_SLOW_MO_MS,
)
from app.tools.akira_skills.common import (
    SERVICE_HUB_URL,
    ensure_logged_in,
    fill_labeled_input,
    new_context,
    try_save_state,
)
from app.utils.playwright_helpers import (
    select_dropdown_option,
    select_dropdown_option_in_property,
    select_first_dropdown_option,
)


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def create_service_module(service_name: str, video_url: str) -> str:
        """Create a service module via the UI, advancing with Next on each step."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=PLAYWRIGHT_SLOW_MO_MS)
            context = new_context(browser)
            page = context.new_page()

            # Ensure logged in (uses saved storage state when available)
            ensure_logged_in(page, context)

            # Click add button under "Modulos" header
            try:
                page.wait_for_selector("text=/M[oó]dulos/", timeout=10000)
            except Exception:
                current_url = page.url
                page_title = page.title()
                raise RuntimeError(
                    f"Module header not found (url={current_url}, title={page_title})"
                )

            add_button = page.locator("text=/M[oó]dulos/").locator(
                "xpath=ancestor::div[contains(@class,'d-flex')][1]//button"
            ).filter(has=page.locator(".add-button")).first
            if add_button.count() == 0:
                add_button = page.locator("text=/M[oó]dulos/").locator(
                    "xpath=ancestor::div[contains(@class,'d-flex')][1]//button[contains(@class,'add-button')]"
                ).first
            if add_button.count() == 0:
                add_button = page.locator("button:has-text('+')").first
            add_button.click()

            # Wait for dialog
            page.wait_for_selector(".rz-dialog.rz-open", timeout=10000)

            # Fill service name
            if not fill_labeled_input(
                page,
                ["Nombre del servicio", "Nombre del módulo", "Nombre del modulo", "Nombre"],
                service_name,
            ):
                # Fallback: first textbox in dialog
                page.locator(".rz-dialog.rz-open input.rz-textbox").first.fill(service_name)

            # Ensure Active is checked
            try:
                active_box = page.locator("label:has-text('Activo')").first.evaluate_handle(
                    "label => label.closest('.property').querySelector('.rz-chkbox')"
                )
                el = active_box.as_element()
                if el:
                    cls = el.get_attribute("class") or ""
                    if "rz-state-active" not in cls:
                        el.click()
            except Exception:
                pass

            # Go to Step 2 (Modulo)
            page.click("a.rz-steps-next")
            page.wait_for_timeout(PLAYWRIGHT_ACTION_WAIT_MS)
            page.wait_for_selector("label:has-text('Module type')", timeout=10000)

            # Step 2 selections
            select_dropdown_option(page, "Module type", "VT")
            select_first_dropdown_option(page, "Model")
            page.wait_for_selector("label:has-text('Accelerator')", timeout=10000)
            select_dropdown_option_in_property(page, "Accelerator", "NVIDIA_TensorRT")

            # Step 3 (Captura)
            page.click("a.rz-steps-next")
            page.wait_for_timeout(PLAYWRIGHT_ACTION_WAIT_MS)
            page.wait_for_selector("label:has-text('Tipo de captura')", timeout=10000)

            select_dropdown_option_in_property(page, "Tipo de captura", "GStreamer")
            select_dropdown_option_in_property(page, "Origen de video", "Url")

            # Fill URL
            try:
                url_input = page.locator("label:has-text('Url')").locator(
                    "xpath=ancestor::div[contains(@class,'property')][1]//input"
                ).first
                url_input.click()
                url_input.fill("")
                url_input.type(video_url, delay=120)
            except Exception:
                page.locator(".rz-dialog.rz-open input.rz-textbox").last.fill(video_url)

            # Ensure Inference GPU is checked
            try:
                inf_box = page.locator(".rz-dialog.rz-open .property").filter(
                    has=page.locator("label:has-text('Inferencia GPU')")
                ).locator(".rz-chkbox").first
                cls = inf_box.get_attribute("class") or ""
                if "rz-state-active" not in cls:
                    inf_box.click()
            except Exception:
                pass

            # Advance remaining steps (Zonas -> Preview)
            for _ in range(2):
                page.click("a.rz-steps-next")
                page.wait_for_timeout(PLAYWRIGHT_ACTION_WAIT_MS)

            # Final step: click Next one more time if present (acts as Save)
            try:
                page.click("a.rz-steps-next", timeout=3000)
            except Exception:
                pass
            # Fallback: explicit save/confirm buttons
            for label in ["Guardar", "Aceptar", "Save", "Confirmar"]:
                try:
                    page.locator(
                        f".rz-dialog.rz-open button:has-text('{label}')"
                    ).first.click(timeout=1500)
                    break
                except Exception:
                    continue

            page.wait_for_timeout(PLAYWRIGHT_POSTCLOSE_WAIT_MS)
            try_save_state(context)
            browser.close()

        return f"Service module '{service_name}' submitted ✅"
