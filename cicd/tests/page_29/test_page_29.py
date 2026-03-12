import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_29_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_navigation(page):
    page.goto(PAGE_29_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#site-nav").first).to_be_visible(timeout=15000)
    expect(page.locator("#nav-homepage").first).to_be_visible(timeout=15000)
    expect(page.locator("#nav-sandbox").first).to_be_visible(timeout=15000)
    expect(page.locator("#nav-lessons").first).to_be_visible(timeout=15000)
    expect(page.locator("#nav-faq").first).to_be_visible(timeout=15000)
    expect(page.locator("#nav-login").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_hockey_teams_header_visibility(page):
    page.goto(PAGE_29_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('h1').first).to_be_visible(timeout=15000)
    expect(page.locator('small').first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_search_team_functionality(page):
    page.goto(PAGE_29_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Vancouver Canucks")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("Vancouver Canucks", timeout=10000)

@pytest.mark.smoke
def test_page_pagination_navigation(page):
    page.goto(PAGE_29_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[18]/a[1]/strong[1]').first).to_be_visible(timeout=15000) # Assert that page 18 is active

@pytest.mark.regression
def test_page_elements_per_page_selection(page):
    page.goto(PAGE_29_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("100")
    page.wait_for_load_state('networkidle')
    # Check number of team name rows.
    team_rows = page.locator("tr.team")
    expect(team_rows).to_have_count(25) # Limit of items is 25 (sanity check)