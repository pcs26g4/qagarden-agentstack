import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_14_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_title(page):
    """Verify the page title."""
    page.goto(PAGE_14_URL)
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.smoke
def test_navigation_to_lessons(page):
    """Verify navigation to the lessons page."""
    page.goto(PAGE_14_URL)
    page.get_by_role('link', name='Lessons', exact=False).first.click()
    expect(page).to_have_url(re.compile(r"lessons"))

@pytest.mark.regression
def test_search_for_team(page):
    """Verify searching for a team."""
    page.goto(PAGE_14_URL)
    page.locator("#q").first.fill("Detroit Red Wings")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("Detroit Red Wings")

@pytest.mark.regression
def test_pagination_to_page_3(page):
    """Verify navigating to page 3 of the hockey teams."""
    page.goto(PAGE_14_URL)
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[4]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"page_num=3"))

@pytest.mark.regression
def test_change_per_page_to_100(page):
    """Verify changing the number of teams displayed per page to 100."""
    page.goto(PAGE_14_URL)
    page.locator("#per_page").first.select_option("100")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/div[1]/div[1]/h1[1]/small[1]').first).to_have_text(re.compile(r"25 items"))