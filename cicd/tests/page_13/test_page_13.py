import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_13_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
@pytest.mark.regression
def test_page_navigation(page):
    page.goto(PAGE_13_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_13_URL)
    expect(page.locator("#nav-sandbox").first).to_be_visible(timeout=10000)
    expect(page.locator("a.nav-link.hidden-sm.hidden-xs").first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_search_hockey_teams(page):
    page.goto(PAGE_13_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    search_term = "Boston Bruins"
    page.locator("#q").first.fill(search_term)
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text(search_term, timeout=10000)

@pytest.mark.regression
def test_pagination_navigation(page):
    page.goto(PAGE_13_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r".*page_num=2"), timeout=10000)

@pytest.mark.regression
def test_change_per_page_setting(page):
    page.goto(PAGE_13_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r".*per_page=50"), timeout=10000)