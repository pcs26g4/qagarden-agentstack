import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_25_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_25_header_visibility(page):
    page.goto(PAGE_25_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('h1').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_25_search_team(page):
    page.goto(PAGE_25_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Boston Bruins")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[21]').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_25_navigation_to_page_2(page):
    page.goto(PAGE_25_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[3]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r".*page_num=2"))

@pytest.mark.regression
def test_page_25_select_50_per_page(page):
    page.goto(PAGE_25_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("50")
    expect(page).to_have_url(re.compile(r".*per_page=50"))

@pytest.mark.smoke
def test_page_25_main_navigation_links(page):
    page.goto(PAGE_25_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#site-nav').first).to_be_visible(timeout=10000)
    page.locator('a.nav-link.hidden-sm.hidden-xs').first.click()
    page.go_back()
    page.locator('a.nav-link').nth(0).click()
    page.go_back()
    page.locator('a.nav-link').nth(1).click()
    page.go_back()
    page.locator('xpath=//a[contains(text(), "Login")]').click()