import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_10_BE84_URL
from playwright.sync_api import expect

import re
import pytest

def test_page_navigation_to_formy(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=10000)

@pytest.mark.smoke
def test_page_form_components_section_visibility(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("nav.navbar.navbar-expand-lg.bg-light").first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_link_to_components_visible(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.hover()
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=10000)

@pytest.mark.smoke
def test_page_file_upload_heading_visibility(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_buttons_visibility(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("button.btn.btn-secondary.btn-choose").first).to_be_visible(timeout=10000)
    expect(page.locator("button.btn.btn-warning.btn-reset").first).to_be_visible(timeout=10000)