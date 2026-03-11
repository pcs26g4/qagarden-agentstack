import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_20_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_20_navigation(page):
    page.goto(PAGE_20_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_20_URL)

@pytest.mark.regression
def test_page_20_search_team(page):
    page.goto(PAGE_20_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#q").first.fill("Toronto Maple Leafs")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("Toronto Maple Leafs", timeout=10000)

@pytest.mark.regression
def test_page_20_pagination(page):
    page.goto(PAGE_20_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_20_change_per_page(page):
    page.goto(PAGE_20_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option('100')
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[26]/td[1]').first).to_be_visible(timeout=10000)

@pytest.mark.smoke
def test_page_20_header_visibility(page):
    page.goto(PAGE_20_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('h1').first).to_be_visible(timeout=10000)
    expect(page.locator('#site-nav').first).to_be_visible(timeout=10000)