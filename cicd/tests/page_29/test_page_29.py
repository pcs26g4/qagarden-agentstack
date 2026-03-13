import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_29_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.smoke
@pytest.mark.regression
def test_page_29_navigation(page):
    """Verify navigation to the hockey teams page."""
    page.goto(PAGE_29_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_29_URL)
    expect(page.locator("page.locator('h1')")).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_29_search_team(page):
    """Verify searching for a specific hockey team."""
    page.goto(PAGE_29_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    team_name = "Toronto Maple Leafs"
    page.locator("#q").first.fill(team_name)
    page.locator("input.btn.btn-primary").first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[6]/td[1]').first).to_have_text(team_name, timeout=10000)


@pytest.mark.regression
def test_page_29_pagination(page):
    """Verify navigating to a specific page using pagination."""
    page.goto(PAGE_29_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page_number = "19"
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"page_num=19"))


@pytest.mark.regression
def test_page_29_change_per_page(page):
    """Verify changing the number of teams displayed per page."""
    page.goto(PAGE_29_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    expect(page.locator("#per_page").first).to_have_value("50", timeout=10000)