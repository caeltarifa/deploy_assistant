import os
import re

from app.config import (
    LOGIN_FIXED_PASSWORD,
    LOGIN_FIXED_URL,
    LOGIN_FIXED_USERNAME,
    PLAYWRIGHT_ACTION_WAIT_MS,
    PLAYWRIGHT_POSTSUBMIT_WAIT_MS,
    PLAYWRIGHT_POSTTYPE_WAIT_MS,
    PLAYWRIGHT_PRETYPE_WAIT_MS,
    PLAYWRIGHT_STORAGE_STATE_PATH,
)
from app.utils.playwright_helpers import (
    ensure_login_form,
    fill_login_form,
    submit_login_form,
)


SERVICE_HUB_URL = "http://localhost:9292/service-hub"


def new_context(browser):
    if os.path.exists(PLAYWRIGHT_STORAGE_STATE_PATH):
        try:
            return browser.new_context(storage_state=PLAYWRIGHT_STORAGE_STATE_PATH)
        except Exception:
            pass
    return browser.new_context()


def try_save_state(context) -> None:
    try:
        context.storage_state(path=PLAYWRIGHT_STORAGE_STATE_PATH)
    except Exception:
        pass


def ensure_logged_in(page, context) -> None:
    page.goto(SERVICE_HUB_URL)
    page.wait_for_load_state("networkidle")
    try:
        page.wait_for_selector("text=/M[oó]dulos/", timeout=4000)
        return
    except Exception:
        pass

    ensure_login_form(page, LOGIN_FIXED_URL)
    page.wait_for_timeout(PLAYWRIGHT_PRETYPE_WAIT_MS)
    fill_login_form(page, LOGIN_FIXED_USERNAME, LOGIN_FIXED_PASSWORD)
    page.wait_for_timeout(PLAYWRIGHT_POSTTYPE_WAIT_MS)
    submit_login_form(page)
    page.wait_for_timeout(PLAYWRIGHT_POSTSUBMIT_WAIT_MS)
    page.wait_for_load_state("networkidle")
    try_save_state(context)
    page.goto(SERVICE_HUB_URL)
    page.wait_for_load_state("networkidle")


def fill_labeled_input(page, labels, value: str) -> bool:
    for label_text in labels:
        try:
            label = page.locator(f"label:has-text('{label_text}')").first
            if label.count() == 0:
                continue
            input_box = label.locator(
                "xpath=ancestor::div[contains(@class,'property')][1]//input"
            ).first
            if input_box.count() == 0:
                continue
            input_box.click()
            input_box.fill("")
            input_box.type(value, delay=120)
            page.wait_for_timeout(PLAYWRIGHT_ACTION_WAIT_MS)
            return True
        except Exception:
            continue
    return False


def find_service_row(page, service_name: str):
    pattern = re.compile(re.escape(service_name), re.IGNORECASE)
    row = page.locator("tr").filter(has=page.locator("td", has_text=pattern)).first
    if row.count() > 0:
        return row

    lower = service_name.lower()
    row = page.locator(
        "xpath=//tr[.//span[contains(translate(@title,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜÑ','abcdefghijklmnopqrstuvwxyzáéíóúüñ'),"
        f" '{lower}')]]"
    ).first
    return row
