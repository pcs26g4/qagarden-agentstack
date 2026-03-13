import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_23_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_title(page):
    """Verify the page title."""
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_search_for_teams(page):
    """Search for a team and verify the input field."""
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    team_name = "Pittsburgh Penguins"
    page.locator("#q").first.fill(team_name)
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_contain_text(team_name)

@pytest.mark.regression
def test_pagination(page):
    """Navigate to the next page using pagination."""
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"page_num=13"))

@pytest.mark.regression
def test_check_element_visibility(page):
    """Check if the search input field is visible."""
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#q").first).to_be_visible()

@pytest.mark.smoke
def test_navigation_to_lessons(page):
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-lessons').first.click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"/lessons/"))