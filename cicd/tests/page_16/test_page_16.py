import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_16_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_16_title(page):
    page.goto(PAGE_16_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_page_16_search_team(page):
    page.goto(PAGE_16_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#q").first.fill("Edmonton Oilers")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("Edmonton Oilers")

@pytest.mark.regression
def test_page_16_pagination(page):
    page.goto(PAGE_16_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"page_num=6"))

@pytest.mark.smoke
def test_page_16_element_visibility(page):
    page.goto(PAGE_16_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#site-nav').first).to_be_visible()
    expect(page.locator('h1').first).to_be_visible()

@pytest.mark.regression
def test_page_16_change_per_page(page):
    page.goto(PAGE_16_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option('50')