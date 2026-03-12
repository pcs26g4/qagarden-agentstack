import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_1_CDBD_URL
from playwright.sync_api import expect
import re

def test_page_cdbd_navigation(page):
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_1_CDBD_URL)
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)
    expect(page.locator("#navbarNavDropdown").first).to_be_visible(timeout=15000)

@pytest.mark.smoke
def test_page_cdbd_welcome_heading(page):
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=15000)
    expect(page.locator("h1").first).to_have_text("Welcome to Formy")

@pytest.mark.regression
def test_page_cdbd_link_buttons_visible(page):
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("a.btn.btn-lg\:has-text('Buttons')")).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_cdbd_link_checkbox_visible(page):
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("a.btn.btn-lg\:has-text('Checkbox')")).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_cdbd_link_autocomplete_click(page):
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("a.btn.btn-lg\:has-text('Autocomplete')").click()
    page.wait_for_load_state('networkidle')
    expect(page).not_to_have_url(PAGE_1_CDBD_URL)