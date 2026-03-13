import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_33_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_33_title_check(page):
    """Verify the page title."""
    page.goto(PAGE_33_URL)
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_page_33_navigation_to_lessons(page):
    """Verify navigation to the lessons page."""
    page.goto(PAGE_33_URL)
    page.locator('#nav-lessons').first.click()
    expect(page).to_have_url(re.compile(r"lessons"))

@pytest.mark.regression
def test_page_33_search_for_team(page):
    """Verify searching for a hockey team."""
    page.goto(PAGE_33_URL)
    page.locator("#q").first.fill("Buffalo Sabres")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("Buffalo Sabres")

@pytest.mark.regression
def test_page_33_change_per_page_count(page):
    """Verify changing the number of teams displayed per page."""
    page.goto(PAGE_33_URL)
    page.locator("#per_page").first.select_option("50")
    expect(page.locator("#per_page").first).to_have_value("50")

@pytest.mark.regression
def test_page_33_pagination(page):
  """Verify navigating to the next page."""
  page.goto(PAGE_33_URL)
  page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
  expect(page).to_have_url(re.compile(r"page_num=23"))