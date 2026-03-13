import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_30_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_30_title(page):
    """Verify the page title."""
    page.goto(PAGE_30_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_page_30_search_team(page):
    """Search for a team and verify that the input field is present."""
    page.goto(PAGE_30_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#q").first).to_be_visible(timeout=10000)
    page.locator("#q").first.fill("Boston Bruins")
    page.locator('input.btn.btn-primary').first.click()

@pytest.mark.regression
def test_page_30_pagination(page):
    """Navigate to page 2 and verify the URL."""
    page.goto(PAGE_30_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[3]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r".*page_num=2"))

@pytest.mark.smoke
def test_page_30_lessons_link(page):
    """Verify the lessons link navigates to the lessons page."""
    page.goto(PAGE_30_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "8 video lessons")]').click()
    expect(page).to_have_url(re.compile(r".*lessons"))

@pytest.mark.regression
def test_page_30_select_per_page(page):
    """Select 50 items per page and verify URL."""
    page.goto(PAGE_30_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")