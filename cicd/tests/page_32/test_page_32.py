import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_32_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.regression
def test_page_title(page):
    page.goto(PAGE_32_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.smoke
def test_navigation_to_lessons(page):
    page.goto(PAGE_32_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("page.locator('#nav-lessons')").click()
    expect(page).to_have_url(re.compile(r"lessons"))

@pytest.mark.regression
def test_search_team(page):
    page.goto(PAGE_32_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("page.locator('#q')").fill("Edmonton Oilers")
    page.locator("page.locator('input.btn.btn-primary')").click()

@pytest.mark.regression
def test_pagination(page):
    page.goto(PAGE_32_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()

@pytest.mark.regression
def test_per_page_selector(page):
    page.goto(PAGE_32_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("100")