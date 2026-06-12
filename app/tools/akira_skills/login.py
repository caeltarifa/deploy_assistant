from fastmcp import FastMCP
from playwright.sync_api import sync_playwright

from app.config import (
    PLAYWRIGHT_POSTCLOSE_WAIT_MS,
    PLAYWRIGHT_POSTSUBMIT_WAIT_MS,
    PLAYWRIGHT_POSTTYPE_WAIT_MS,
    PLAYWRIGHT_PRETYPE_WAIT_MS,
    PLAYWRIGHT_SLOW_MO_MS,
    PLAYWRIGHT_STORAGE_STATE_PATH,
)
from app.utils.playwright_helpers import (
    capture_login_request,
    ensure_login_form,
    fill_login_form,
    mask_post_data,
    submit_login_form,
)
from app.config import LOGIN_FIXED_PASSWORD, LOGIN_FIXED_URL, LOGIN_FIXED_USERNAME
from app.tools.akira_skills.common import try_save_state


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def login_fixed_user() -> str:
        """Log into the site with fixed credentials (visible browser)."""
        url = LOGIN_FIXED_URL
        username = LOGIN_FIXED_USERNAME
        password = LOGIN_FIXED_PASSWORD

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=PLAYWRIGHT_SLOW_MO_MS)
            context = browser.new_context()
            page = context.new_page()
            req_capture = capture_login_request(page)

            ensure_login_form(page, url)
            page.wait_for_timeout(PLAYWRIGHT_PRETYPE_WAIT_MS)
            fill_login_form(page, username, password)
            page.wait_for_timeout(PLAYWRIGHT_POSTTYPE_WAIT_MS)

            response_status = None
            submit_login_form(page)
            try:
                response = page.wait_for_response(
                    lambda r: "account/login" in r.url, timeout=8000
                )
                response_status = response.status
            except Exception:
                pass
            try:
                page.wait_for_url(lambda u: "/Login" not in u, timeout=8000)
            except Exception:
                pass
            page.wait_for_timeout(PLAYWRIGHT_POSTSUBMIT_WAIT_MS)
            page.wait_for_load_state("networkidle")

            success = _check_login_success(page)
            if success:
                try_save_state(context)
            current_url = page.url
            page_title = page.title()
            filled_username = ""
            filled_password_len = 0
            try:
                filled_username = page.locator("input[name='Username']").input_value()
                filled_password_len = len(
                    page.locator("input[name='Password']").input_value()
                )
            except Exception:
                pass
            login_post = mask_post_data(req_capture.get("post_data"))
            error_text = ""
            try:
                error_text = page.locator(
                    ".rz-notification, .rz-message, .validation-message, .rz-alert, .rz-text-error"
                ).first.inner_text(timeout=1000)
            except Exception:
                pass
            page.wait_for_timeout(PLAYWRIGHT_POSTCLOSE_WAIT_MS)
            browser.close()

        if success:
            return "Login successful ✅"
        return (
            f"Login failed ❌ (url={current_url}, title={page_title}, "
            f"status={response_status}, error={error_text}, "
            f"filled_user={filled_username}, filled_pass_len={filled_password_len}, "
            f"login_post={login_post})"
        )

    @mcp.tool
    def login(url: str, username: str, password: str) -> str:
        """Log into the site with provided credentials (visible browser)."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=PLAYWRIGHT_SLOW_MO_MS)
            context = browser.new_context()
            page = context.new_page()
            req_capture = capture_login_request(page)

            ensure_login_form(page, url)
            page.wait_for_timeout(PLAYWRIGHT_PRETYPE_WAIT_MS)
            fill_login_form(page, username, password)
            page.wait_for_timeout(PLAYWRIGHT_POSTTYPE_WAIT_MS)

            response_status = None
            submit_login_form(page)
            try:
                response = page.wait_for_response(
                    lambda r: "account/login" in r.url, timeout=8000
                )
                response_status = response.status
            except Exception:
                pass
            try:
                page.wait_for_url(lambda u: "/Login" not in u, timeout=8000)
            except Exception:
                pass
            page.wait_for_timeout(PLAYWRIGHT_POSTSUBMIT_WAIT_MS)
            page.wait_for_load_state("networkidle")

            success = _check_login_success(page)
            if success:
                try_save_state(context)
            current_url = page.url
            page_title = page.title()
            filled_username = ""
            filled_password_len = 0
            try:
                filled_username = page.locator("input[name='Username']").input_value()
                filled_password_len = len(
                    page.locator("input[name='Password']").input_value()
                )
            except Exception:
                pass
            login_post = mask_post_data(req_capture.get("post_data"))
            error_text = ""
            try:
                error_text = page.locator(
                    ".rz-notification, .rz-message, .validation-message, .rz-alert, .rz-text-error"
                ).first.inner_text(timeout=1000)
            except Exception:
                pass
            page.wait_for_timeout(PLAYWRIGHT_POSTCLOSE_WAIT_MS)
            browser.close()

        if success:
            return "Login successful ✅"
        return (
            f"Login failed ❌ (url={current_url}, title={page_title}, "
            f"status={response_status}, error={error_text}, "
            f"filled_user={filled_username}, filled_pass_len={filled_password_len}, "
            f"login_post={login_post})"
        )


def _check_login_success(page) -> bool:
    try:
        page.wait_for_selector("text=Cerrar sesión", timeout=3000)
        return True
    except Exception:
        pass

    try:
        page.wait_for_selector("text=Logout", timeout=1000)
        return True
    except Exception:
        pass

    if "/Login" not in page.url:
        try:
            page.wait_for_selector("input[name='Username']", timeout=1000)
            return False
        except Exception:
            return True

    return False
