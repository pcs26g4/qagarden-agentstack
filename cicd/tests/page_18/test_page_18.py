import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_18_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_18_navigation(page):
    page.goto(PAGE_18_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#site-nav").first).to_be_visible(timeout=10000)
    expect(page.locator("h1").first).to_have_text(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_page_18_search_team(page):
    page.goto(PAGE_18_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#q").first.fill("Colorado Avalanche")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("Colorado Avalanche")

@pytest.mark.regression
def test_page_18_pagination(page):
    page.goto(PAGE_18_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"page_num=8"))

@pytest.mark.regression
def test_page_18_items_per_page(page):
    page.goto(PAGE_18_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    page.wait_for_load_state('networkidle')
    #Basic check that the page has changed
    expect(page.locator("h1 small").first).to_have_text(re.compile(r"50 items"))

@pytest.mark.smoke
def test_page_18_elements_visible(page):
    page.goto(PAGE_18_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#site-nav").first).to_be_visible(timeout=10000)
    expect(page.locator("#q").first).to_be_visible(timeout=10000)
    expect(page.locator('input.btn.btn-primary').first).to_be_visible(timeout=10000)
    expect(page.locator("#footer").first).to_be_visible(timeout=10000)