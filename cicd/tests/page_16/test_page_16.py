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
    search_term = "Edmonton Oilers"
    page.locator("#q").first.fill(search_term)
    page.locator("input.btn.btn-primary").first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text(search_term)

@pytest.mark.regression
def test_page_16_change_per_page(page):
    page.goto(PAGE_16_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("100")
    expect(page.locator("#per_page").first).to_have_value("100")

@pytest.mark.regression
def test_page_16_navigation_to_page_1(page):
    page.goto(PAGE_16_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[2]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"page_num=1"))