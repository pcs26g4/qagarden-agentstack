import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_32_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_32_title(page):
    page.goto(PAGE_32_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title("Hockey Teams: Forms, Searching and Pagination | Scrape This Site | A public sandbox for learning web scraping")

@pytest.mark.regression
def test_page_32_search_team(page):
    page.goto(PAGE_32_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#q").first.fill("Boston Bruins")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[21]').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_32_pagination(page):
    page.goto(PAGE_32_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"page_num=21"))

@pytest.mark.regression
def test_page_32_select_per_page(page):
    page.goto(PAGE_32_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[2]/strong[1]').first).to_be_visible(timeout=10000)

@pytest.mark.smoke
def test_page_32_element_visibility(page):
    page.goto(PAGE_32_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#site-nav').first).to_be_visible(timeout=10000)
    expect(page.locator('a.nav-link.hidden-sm.hidden-xs').first).to_be_visible(timeout=10000)
    expect(page.locator('h1').first).to_be_visible(timeout=10000)