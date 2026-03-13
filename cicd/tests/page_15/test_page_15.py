import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_15_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_15_navigation(page):
    page.goto(PAGE_15_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_15_URL)
    expect(page.locator("h1").first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_15_search_team(page):
    page.goto(PAGE_15_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#q").first.fill("Toronto Maple Leafs")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[1]/th[1]').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_15_pagination(page):
    page.goto(PAGE_15_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r".*page_num=5"))

@pytest.mark.regression
def test_page_15_team_data(page):
    page.goto(PAGE_15_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("Florida Panthers", timeout=10000)
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[2]').first).to_have_text("1993", timeout=10000)
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[3]').first).to_have_text("33", timeout=10000)
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[4]').first).to_have_text("34", timeout=10000)