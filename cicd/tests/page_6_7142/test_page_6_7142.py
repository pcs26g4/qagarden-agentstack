import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_6_7142_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_6_7142_navigation(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_6_7142_URL)

@pytest.mark.regression
def test_page_6_7142_formy_link(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)
    page.locator("#logo").first.click()
    expect(page).to_have_url(re.compile(r"formy-project\.herokuapp\.com"))

@pytest.mark.regression
def test_page_6_7142_components_dropdown_visibility(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=15000)
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Autocomplete')]")).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_6_7142_buttons_link(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Buttons')]")).to_be_visible(timeout=15000)
    page.locator("xpath=//a[contains(text(), 'Buttons')]").click()
    expect(page).to_have_url(re.compile(r"buttons"))

@pytest.mark.regression
def test_page_6_7142_heading_visibility(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.locator("xpath=//a[contains(text(), 'Datepicker')]").click()
    expect(page.locator("h1").first).to_be_visible(timeout=15000)