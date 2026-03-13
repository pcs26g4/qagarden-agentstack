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


@pytest.mark.smoke
def test_page_3_navigation_to_autocomplete(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.locator("xpath=//a[contains(text(), 'Autocomplete')]").click()
    expect(page.locator("h1").first).to_be_visible(timeout=10000)
    expect(page.locator("h1").first).to_have_text("Autocomplete", timeout=10000)


@pytest.mark.regression
def test_page_3_autocomplete_input(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.locator("xpath=//a[contains(text(), 'Autocomplete')]").click()
    page.locator("#autocomplete").first.fill("123 Main St")
    page.locator("#street_number").first.fill("123")
    page.locator("#route").first.fill("Main St")
    page.locator("#locality").first.fill("Anytown")
    page.locator("#administrative_area_level_1").first.fill("CA")
    page.locator("#postal_code").first.fill("90210")
    page.locator("#country").first.fill("USA")


@pytest.mark.regression
def test_page_3_element_visibility(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=10000)
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_3_navigation_buttons(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.locator("xpath=//a[contains(text(), 'Buttons')]").click()
    expect(page.locator("xpath=//a[contains(text(), 'Buttons')]")).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_3_navigation_checkbox(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.locator("xpath=//a[contains(text(), 'Checkbox')]").click()
    expect(page.locator("xpath=//a[contains(text(), 'Checkbox')]")).to_be_visible(timeout=10000)