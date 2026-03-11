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
def test_page_23_navigation(page):
    """
    Verify navigation to the hockey teams page.
    """
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_23_URL)
    expect(page.locator("page.locator('h1')")).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_23_search_team(page):
    """
    Verify searching for a team.
    """
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    search_term = "Boston Bruins"
    page.locator("#q").first.fill(search_term)
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[11]').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_23_pagination(page):
    """
    Verify pagination functionality by clicking next page.
    """
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"page_num=13"))

@pytest.mark.regression
def test_page_23_per_page_dropdown(page):
    """
    Verify changing the number of items per page.
    """
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    expect(page.locator("#per_page").first).to_have_value("50")