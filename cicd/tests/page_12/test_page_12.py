import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_12_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_loads_successfully(page):
    """Verify the page loads and the main heading is visible."""
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("page.locator('h1')")).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_search_team_boston(page):
    """Verify that searching for a specific team displays relevant results."""
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("page.locator('#q')").fill("Boston")
    page.locator("page.locator('input.btn.btn-primary')").click()
    expect(page.locator("page.locator('xpath\=\/\/*\[\@id\=\"hockey\"\]\/div\[1\]\/table\[1\]\/tbody\[1\]\/tr\[2\]\/td\[1\]')")).to_have_text("Boston Bruins", timeout=10000)

@pytest.mark.regression
def test_pagination_to_page_2(page):
    """Verify navigating to page 2 displays different team data."""
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("page.locator('xpath\=\/\/*\[contains(\@aria-label, \"Next\")]')").click()
    expect(page.locator("page.locator('xpath\=\/\/*\[\@id\=\"hockey\"\]\/div\[1\]\/table\[1\]\/tbody\[1\]\/tr\[2\]\/td\[1\]')")).to_have_text("Hartford Whalers", timeout=10000)

@pytest.mark.regression
def test_change_per_page_to_50(page):
    """Verify changing the 'per page' selection updates the displayed team count."""
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("page.locator('#per_page')").select_option("50")
    expect(page.locator("page.locator('xpath\=\/\/*\[\@id\=\"hockey\"\]\/div\[1\]\/table\[1\]\/tbody\[1\]\/tr\[2\]\/td\[1\]')")).to_be_visible(timeout=10000)

@pytest.mark.smoke
def test_navigation_links_exist(page):
    """Verify the main navigation links are present."""
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("page.locator('#nav-homepage')")).to_be_visible(timeout=10000)
    expect(page.locator("page.locator('#nav-sandbox')")).to_be_visible(timeout=10000)
    expect(page.locator("page.locator('#nav-lessons')")).to_be_visible(timeout=10000)
    expect(page.locator("page.locator('#nav-faq')")).to_be_visible(timeout=10000)
    expect(page.locator("page.locator('#nav-login')")).to_be_visible(timeout=10000)