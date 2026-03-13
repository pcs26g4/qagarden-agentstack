import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_10_BE84_URL
from playwright.sync_api import expect

import pytest

def test_page_navigation(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_10_BE84_URL)
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)
    expect(page.locator("nav.navbar.navbar-expand-lg.bg-light").first).to_be_visible(timeout=15000)
    expect(page.locator("#navbarNavDropdown").first).to_be_visible(timeout=15000)

@pytest.mark.smoke
def test_link_formy_navigation(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#logo").first.click()
    expect(page).to_have_url(PAGE_10_BE84_URL)

@pytest.mark.regression
def test_form_components_dropdown_visibility(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_file_upload_elements_visibility(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("button.btn.btn-secondary.btn-choose").first).to_be_visible(timeout=15000)
    expect(page.locator("button.btn.btn-warning.btn-reset").first).to_be_visible(timeout=15000)
    expect(page.locator("h1").first).to_be_visible(timeout=15000)