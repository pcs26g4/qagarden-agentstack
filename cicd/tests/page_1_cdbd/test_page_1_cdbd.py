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

def test_page_welcome_heading_visible(page):
    """Verify the welcome heading is visible on the page."""
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=10000)

def test_page_link_formy_visible(page):
    """Verify the 'Formy' link is visible and clickable."""
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=10000)

def test_page_link_autocomplete_visible(page):
    """Verify the 'Autocomplete' link is visible."""
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("a.btn.btn-lg").nth(0)).to_be_visible(timeout=10000)

def test_page_link_buttons_visible(page):
    """Verify the 'Buttons' link is visible."""
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("a.btn.btn-lg").nth(1)).to_be_visible(timeout=10000)

def test_page_link_checkbox_visible(page):
    """Verify the 'Checkbox' link is visible."""
    page.goto(PAGE_1_CDBD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("a.btn.btn-lg").nth(2)).to_be_visible(timeout=10000)