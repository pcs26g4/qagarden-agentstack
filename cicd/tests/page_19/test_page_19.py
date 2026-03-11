import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_19_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_19_title(page):
    page.goto(PAGE_19_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_page_19_search_team(page):
    page.goto(PAGE_19_URL)
    page.wait_for_load_state('networkidle')
    search_term = "Dallas Stars"
    page.locator("#q").first.fill(search_term)
    page.locator("input.btn.btn-primary").first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[5]/td[1]').first).to_have_text(search_term)

@pytest.mark.regression
def test_page_19_navigation_to_page_1(page):
    page.goto(PAGE_19_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[2]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"page_num=1"))

@pytest.mark.regression
def test_page_19_change_per_page_to_50(page):
    page.goto(PAGE_19_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    # Wait for the table to re-render with the new page size.  A more robust solution would be to wait for an element to be created based on the number of rows.
    page.wait_for_load_state('networkidle')
    # Basic check that the table has re-rendered. It does not verify that there are indeed 50 rows.
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]').first).to_be_visible()

@pytest.mark.smoke
def test_page_19_element_visibility(page):
    page.goto(PAGE_19_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#site-nav").first).to_be_visible()
    expect(page.locator("#q").first).to_be_visible()
    expect(page.locator('a.nav-link').nth(0)).to_be_visible()