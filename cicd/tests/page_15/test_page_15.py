import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_15_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_15_navigation(page):
    """Verify navigation to the hockey teams page."""
    page.goto(PAGE_15_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_15_URL)
    expect(page.locator('h1').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_15_search_team(page):
    """Verify searching for a specific team."""
    page.goto(PAGE_15_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    team_name = "Toronto Maple Leafs"
    page.locator('#q').first.fill(team_name)
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('table.table').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_15_pagination(page):
    """Verify navigating to a specific page using pagination links."""
    page.goto(PAGE_15_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).not_to_have_url(PAGE_15_URL)

@pytest.mark.regression
def test_page_15_elements_visibility(page):
    """Verify the visibility of key elements on the page."""
    page.goto(PAGE_15_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#site-nav').first).to_be_visible(timeout=10000)
    expect(page.locator('h1').first).to_be_visible(timeout=10000)
    expect(page.locator('table.table').first).to_be_visible(timeout=10000)
    expect(page.locator('#footer').first).to_be_visible(timeout=10000)
    expect(page.locator('#q').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_15_select_50_teams_per_page(page):
    """Verify selecting 50 teams per page."""
    page.goto(PAGE_15_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("50")
    page.wait_for_load_state('networkidle')
    expect(page.locator('table.table').first).to_be_visible(timeout=10000)