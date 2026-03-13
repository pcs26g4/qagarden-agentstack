import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_13_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.regression
def test_page_13_title(page):
    """Verify the title of the page."""
    page.goto(PAGE_13_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))


@pytest.mark.smoke
def test_page_13_navigation_to_lessons(page):
    """Verify navigation to the lessons page."""
    page.goto(PAGE_13_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"lessons"))


@pytest.mark.regression
def test_page_13_search_team(page):
    """Verify searching for a team and checking the results."""
    page.goto(PAGE_13_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Detroit Red Wings")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_be_visible(timeout=10000)
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("Detroit Red Wings")


@pytest.mark.regression
def test_page_13_pagination(page):
    """Verify pagination functionality."""
    page.goto(PAGE_13_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"page_num=3"))


@pytest.mark.regression
def test_page_13_change_per_page(page):
    """Verify changing the number of teams displayed per page."""
    page.goto(PAGE_13_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("50")
    expect(page.locator('#per_page').first).to_have_value("50")