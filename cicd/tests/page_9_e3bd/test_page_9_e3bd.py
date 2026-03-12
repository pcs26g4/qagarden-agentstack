import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_9_E3BD_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_9_e3bd_navigation(page):
    """
    Navigates to the page and verifies the URL.
    """
    page.goto(PAGE_9_E3BD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_9_E3BD_URL)

@pytest.mark.smoke
def test_page_9_e3bd_logo_link(page):
    """
    Verifies the logo link is visible and clickable.
    """
    page.goto(PAGE_9_E3BD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)

@pytest.mark.smoke
def test_page_9_e3bd_form_components_link(page):
    """
    Verifies the "Form components" link is visible.
    """
    page.goto(PAGE_9_E3BD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_9_e3bd_heading_visibility(page):
    """
    Verifies the heading "Enabled and Disabled elements" is visible.
    """
    page.goto(PAGE_9_E3BD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=15000)