import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_22_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_22_navigation(page):
    """Verify navigation to page 22."""
    page.goto(PAGE_22_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_22_URL)

@pytest.mark.regression
def test_page_22_header_visibility(page):
    """Verify the hockey teams header is visible."""
    page.goto(PAGE_22_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("page.locator('h1')")).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_22_search_input(page):
    """Verify search input field is present and functional."""
    page.goto(PAGE_22_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#q").first).to_be_visible(timeout=10000)
    page.locator("#q").first.fill("Vancouver")
    page.locator('input.btn.btn-primary').first.click()

@pytest.mark.regression
def test_page_22_pagination_links(page):
    """Verify pagination links are present and clickable."""
    page.goto(PAGE_22_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//*[contains(@aria-label, "Next")]')).to_be_visible(timeout=10000)
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).not_to_have_url(PAGE_22_URL)

@pytest.mark.regression
def test_page_22_per_page_dropdown(page):
    """Verify 'per page' dropdown is functional."""
    page.goto(PAGE_22_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#per_page").first).to_be_visible(timeout=10000)
    page.locator("#per_page").first.select_option("100")
    page.wait_for_load_state('networkidle')