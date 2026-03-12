import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_35_URL
from playwright.sync_api import expect
import re

@pytest.mark.regression
def test_page_35_title(page):
    page.goto(PAGE_35_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_page_35_search_team(page):
    page.goto(PAGE_35_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#q").first.fill("San Jose Sharks")
    page.locator("input.btn.btn-primary").first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("San Jose Sharks")

@pytest.mark.regression
def test_page_35_change_per_page(page):
    page.goto(PAGE_35_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    expect(page.locator("#per_page").first).to_have_value("50")

@pytest.mark.regression
def test_page_35_pagination_link(page):
    page.goto(PAGE_35_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[3]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r".*page_num=2"))

@pytest.mark.regression
def test_page_35_element_visibility(page):
    page.goto(PAGE_35_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#site-nav").first).to_be_visible()
    expect(page.locator("#footer").first).to_be_visible()