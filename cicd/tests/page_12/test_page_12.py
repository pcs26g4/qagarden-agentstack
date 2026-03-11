import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_12_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_title(page):
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_search_team(page):
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    search_term = "Boston Bruins"
    page.locator("#q").first.fill(search_term)
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text(search_term, timeout=10000)

@pytest.mark.regression
def test_pagination(page):
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"page_num=2"), timeout=10000)

@pytest.mark.regression
def test_per_page_select(page):
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    page.wait_for_load_state('networkidle')
    expect(page.locator('h1').first).to_have_text(re.compile(r"50 items"), timeout=10000)

@pytest.mark.smoke
def test_element_visibility(page):
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#site-nav').first).to_be_visible(timeout=10000)
    expect(page.locator('#nav-homepage').first).to_be_visible(timeout=10000)
    expect(page.locator('#nav-sandbox').first).to_be_visible(timeout=10000)
    expect(page.locator('#nav-lessons').first).to_be_visible(timeout=10000)
    expect(page.locator('#nav-faq').first).to_be_visible(timeout=10000)
    expect(page.locator('#nav-login').first).to_be_visible(timeout=10000)