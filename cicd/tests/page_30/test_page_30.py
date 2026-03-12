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

@pytest.mark.regression
def test_page_30_verify_heading(page):
    page.goto(PAGE_30_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('h1').first).to_be_visible(timeout=10000)
    expect(page.locator('h1').first).to_have_text(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_page_30_search_team(page):
    page.goto(PAGE_30_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Toronto Maple Leafs")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[6]').first).to_be_visible(timeout=10000)
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[6]/td[1]').first).to_have_text("Toronto Maple Leafs")

@pytest.mark.regression
def test_page_30_navigate_pages(page):
    page.goto(PAGE_30_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"page_num=19"))

@pytest.mark.regression
def test_page_30_change_per_page(page):
    page.goto(PAGE_30_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("100")
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/div[1]/div[1]/h1[1]/small[1]').first).to_have_text("25 items")

@pytest.mark.smoke
def test_page_30_header_links(page):
    page.goto(PAGE_30_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link.hidden-sm.hidden-xs').first.click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url("http://www.scrapethissite.com/")