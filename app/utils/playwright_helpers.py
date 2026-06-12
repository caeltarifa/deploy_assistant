from typing import Dict

from app.config import PLAYWRIGHT_ACTION_WAIT_MS


def ensure_login_form(page, url: str) -> str:
    page.goto(url)
    try:
        page.wait_for_selector("input[name='Username']", timeout=5000)
        return url
    except Exception:
        pass

    login_url = url.rstrip("/") + "/Login"
    page.goto(login_url)
    page.wait_for_selector("input[name='Username']", timeout=5000)
    return login_url


def fill_login_form(page, username: str, password: str) -> None:
    user_input = page.locator("input[name='Username']")
    pass_input = page.locator("input[name='Password']")
    user_input.click()
    user_input.fill("")
    user_input.type(username, delay=120)
    page.wait_for_timeout(PLAYWRIGHT_ACTION_WAIT_MS)
    pass_input.click()
    pass_input.fill("")
    pass_input.type(password, delay=120)
    page.wait_for_timeout(PLAYWRIGHT_ACTION_WAIT_MS)


def submit_login_form(page) -> None:
    try:
        page.click("button[type='submit']", timeout=2000)
        return
    except Exception:
        pass

    try:
        page.locator("input[name='Password']").press("Enter", timeout=2000)
        return
    except Exception:
        pass

    try:
        page.locator("form").first.evaluate("form => form.submit()")
    except Exception:
        pass


def capture_login_request(page) -> Dict[str, str]:
    capture: Dict[str, str] = {"url": None, "post_data": None}

    def handler(req):
        url = req.url
        if "account/login" in url.lower():
            capture["url"] = url
            capture["post_data"] = req.post_data

    page.on("request", handler)
    return capture


def mask_post_data(post_data: str) -> str:
    if not post_data:
        return ""
    try:
        parts = []
        for kv in post_data.split("&"):
            if kv.lower().startswith("password="):
                parts.append("password=***")
            else:
                parts.append(kv)
        return "&".join(parts)
    except Exception:
        return "***"


def select_dropdown_option(page, label_text: str, option_text: str) -> None:
    """Select an option from a Radzen dropdown by label and visible option text."""
    label = page.locator(f"label:has-text('{label_text}')").first
    dropdown = label.locator(
        "xpath=ancestor::div[contains(@class,'d-flex')][1]//div[contains(@class,'rz-dropdown')]"
    )
    if dropdown.count() == 0:
        dropdown = label.locator(
            "xpath=ancestor::div[contains(@class,'property')][1]//div[contains(@class,'rz-dropdown')]"
        )
    if dropdown.count() == 0:
        raise RuntimeError(f"Dropdown not found for label: {label_text}")
    dropdown.first.scroll_into_view_if_needed()
    dropdown.first.click(force=True)
    page.wait_for_timeout(PLAYWRIGHT_ACTION_WAIT_MS)
    panel = page.locator(".rz-dropdown-panel:visible")
    option = panel.locator(".rz-dropdown-item", has_text=option_text).first
    option.scroll_into_view_if_needed()
    option.click(force=True)


def select_dropdown_option_in_property(page, label_text: str, option_text: str) -> None:
    """Select option from a dropdown inside a .property block by label text."""
    container = page.locator(".rz-dialog.rz-open .property").filter(
        has=page.locator(f"label:has-text('{label_text}')")
    ).first
    dropdown = container.locator(".rz-dropdown").first
    if dropdown.count() == 0:
        raise RuntimeError(f"Dropdown not found for label: {label_text}")
    dropdown.scroll_into_view_if_needed()
    dropdown.click(force=True)
    page.wait_for_timeout(PLAYWRIGHT_ACTION_WAIT_MS)
    panel = page.locator(".rz-dropdown-panel:visible")
    option = panel.locator(".rz-dropdown-item", has_text=option_text).first
    option.scroll_into_view_if_needed()
    option.click(force=True)


def select_first_dropdown_option(page, label_text: str) -> None:
    """Select the first option from a Radzen dropdown by label."""
    label = page.locator(f"label:has-text('{label_text}')").first
    dropdown = label.locator(
        "xpath=ancestor::div[contains(@class,'d-flex')][1]//div[contains(@class,'rz-dropdown')]"
    )
    if dropdown.count() == 0:
        dropdown = label.locator(
            "xpath=ancestor::div[contains(@class,'property')][1]//div[contains(@class,'rz-dropdown')]"
        )
    if dropdown.count() == 0:
        raise RuntimeError(f"Dropdown not found for label: {label_text}")
    dropdown.first.scroll_into_view_if_needed()
    dropdown.first.click(force=True)
    page.wait_for_timeout(PLAYWRIGHT_ACTION_WAIT_MS)
    panel = page.locator(".rz-dropdown-panel:visible")
    option = panel.locator(".rz-dropdown-item").first
    option.scroll_into_view_if_needed()
    option.click(force=True)
