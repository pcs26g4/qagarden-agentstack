import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_31_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_navigation(page):
    """Verify navigation links are working"""
    page.goto(PAGE_31_URL)
    page.wait_for_load_state('networkidle')
    page.get_by_role("link", name="Lessons").first.click()
    expect(page).to_have_url(re.compile(r"lessons"))
    page.goto(PAGE_31_URL)  # Navigate back

    page.get_by_role("link", name="FAQ").first.click()
    expect(page).to_have_url(re.compile(r"faq"))
    page.goto(PAGE_31_URL)

    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"login"))
    page.goto(PAGE_31_URL)

@pytest.mark.regression
def test_search_hockey_teams(page):
    """Verify searching for a team filters the results."""
    page.goto(PAGE_31_URL)
    page.wait_for_load_state('networkidle')
    team_name = "Toronto Maple Leafs"
    page.locator("#q").first.fill(team_name)
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[11]').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_change_per_page_count(page):
    """Verify changing the number of displayed teams per page updates the table."""
    page.goto(PAGE_31_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[26]').first).to_be_visible(timeout=10000)
    
@pytest.mark.regression
def test_pagination(page):
    """Verify pagination links navigate correctly."""
    page.goto(PAGE_31_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"page_num=20"))