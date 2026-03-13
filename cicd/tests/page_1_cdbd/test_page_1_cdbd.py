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

def test_page_welcome_elements_visible(page):
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=10000)
    expect(page.locator("h1").first).to_be_visible(timeout=10000)
    expect(page.locator("a.btn.btn-lg").first).to_be_visible(timeout=10000)

@pytest.mark.smoke
def test_page_navigation_formy_link(page):
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#logo").first.click()
    expect(page).to_have_url(PAGE_1_CDBD_URL)

@pytest.mark.regression
def test_page_form_components_dropdown(page):
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_link_complete_web_form(page):
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("a.btn.btn-lg").nth(12)).to_be_visible(timeout=10000)
    page.locator("a.btn.btn-lg").nth(12).click()

@pytest.mark.regression
def test_page_link_radio_button(page):
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("a.btn.btn-lg").nth(10)).to_be_visible(timeout=10000)
    page.locator("a.btn.btn-lg").nth(10).click()