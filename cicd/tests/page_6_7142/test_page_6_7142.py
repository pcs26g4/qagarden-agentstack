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
def test_page_6_7142_logo_link(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_6_7142_components_dropdown_visibility(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.hover()
    expect(page.locator("xpath=//a[contains(text(), 'Autocomplete')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Buttons')]")).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_6_7142_navigate_to_autocomplete(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.hover()
    page.locator("xpath=//a[contains(text(), 'Autocomplete')]").click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"autocomplete"))

@pytest.mark.regression
def test_page_6_7142_heading_visibility(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.hover()
    page.locator("xpath=//a[contains(text(), 'Datepicker')]").click()
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_6_7142_drag_and_drop_link(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.hover()
    page.locator("xpath=//a[contains(text(), 'Drag and Drop')]").click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"draganddrop"))