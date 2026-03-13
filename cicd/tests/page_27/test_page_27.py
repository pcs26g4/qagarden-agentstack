import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_27_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_27_verify_heading(page):
    """Verify the main heading text."""
    page.goto(PAGE_27_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator("page.locator('h1')")).to_be_visible(timeout=10000)
    expect(page.locator("page.locator('h1')")).to_have_text("Hockey Teams: Forms, Searching and Pagination 25 items", timeout=10000)

@pytest.mark.regression
def test_page_27_search_for_team(page):
    """Search for a specific team and verify the search input and submit button are visible."""
    page.goto(PAGE_27_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#q').first).to_be_visible(timeout=10000)
    page.locator('#q').first.fill("Detroit Red Wings")
    expect(page.locator('input.btn.btn-primary').first).to_be_visible(timeout=10000)
    page.locator('input.btn.btn-primary').first.click()

@pytest.mark.regression
def test_page_27_pagination(page):
    """Navigate to a different page using pagination and verify the URL changes."""
    page.goto(PAGE_27_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[3]/a[1]').first.click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r".*page_num=2"))

@pytest.mark.regression
def test_page_27_change_per_page(page):
    """Change the number of teams displayed per page and verify that the URL changes."""
    page.goto(PAGE_27_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("50")
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r".*per_page=50"))

@pytest.mark.smoke
def test_page_27_navigation_links(page):
    """Verify that navigation links are visible and clickable."""
    page.goto(PAGE_27_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('a.nav-link.hidden-sm.hidden-xs').first).to_be_visible(timeout=10000)
    expect(page.locator('a.nav-link').nth(0)).to_be_visible(timeout=10000)
    page.locator('a.nav-link').nth(0).click()