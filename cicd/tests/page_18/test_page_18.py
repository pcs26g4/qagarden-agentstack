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
    expect(page).to_have_url(PAGE_18_URL)
    expect(page.locator("#site-nav").first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_18_search_team(page):
    page.goto(PAGE_18_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    team_name = "Detroit Red Wings"
    page.locator("#q").first.fill(team_name)
    page.locator("input.btn.btn-primary").first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[1]').first).to_have_text(team_name)

@pytest.mark.regression
def test_page_18_pagination_link_click(page):
    page.goto(PAGE_18_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r".*page_num=7"))

@pytest.mark.regression
def test_page_18_per_page_selection(page):
    page.goto(PAGE_18_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    expect(page.locator("#per_page").first).to_have_value("50")

@pytest.mark.regression
def test_page_18_footer_visibility(page):
    page.goto(PAGE_18_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#footer").first).to_be_visible(timeout=10000)