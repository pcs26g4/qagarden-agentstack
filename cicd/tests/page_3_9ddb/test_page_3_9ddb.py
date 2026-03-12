import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_3_9DDB_URL
from playwright.sync_api import expect
import re
import pytest


def test_page_3_9ddb_navigation(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=15000)
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=15000)


@pytest.mark.smoke
def test_page_3_9ddb_autocomplete_link(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.locator("xpath=//a[contains(text(), 'Autocomplete')]").click()
    expect(page.locator("h1").first).to_be_visible(timeout=15000)


@pytest.mark.regression
def test_page_3_9ddb_fill_autocomplete_form(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.locator("xpath=//a[contains(text(), 'Autocomplete')]").click()
    page.locator("#autocomplete").first.fill("1600 Amphitheatre Parkway")
    page.locator("#street_number").first.fill("1600")
    page.locator("#route").first.fill("Amphitheatre Parkway")
    page.locator("#locality").first.fill("Mountain View")
    page.locator("#administrative_area_level_1").first.fill("CA")
    page.locator("#postal_code").first.fill("94043")
    page.locator("#country").first.fill("USA")
    expect(page.locator("#autocomplete").first).to_have_value("1600 Amphitheatre Parkway")


@pytest.mark.regression
def test_page_3_9ddb_buttons_link(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.locator("xpath=//a[contains(text(), 'Buttons')]").click()
    expect(page).to_have_url(PAGE_3_9DDB_URL)  # Verify page stays on same URL.