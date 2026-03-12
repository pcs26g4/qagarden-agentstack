import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_19_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_title(page):
    page.goto(PAGE_19_URL)
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_hockey_teams_header_visible(page):
    page.goto(PAGE_19_URL)
    expect(page.locator('h1').first).to_be_visible()

@pytest.mark.regression
def test_search_for_teams(page):
    page.goto(PAGE_19_URL)
    page.locator('#q').first.fill("Colorado")
    page.locator('input.btn.btn-primary').first.click()

@pytest.mark.regression
def test_pagination_navigation(page):
    page.goto(PAGE_19_URL)
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"page_num=8"))

@pytest.mark.regression
def test_change_items_per_page(page):
    page.goto(PAGE_19_URL)
    page.locator('#per_page').first.select_option('100')
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_19_URL) # URL does not change.