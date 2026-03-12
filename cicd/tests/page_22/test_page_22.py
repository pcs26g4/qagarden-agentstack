import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_22_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.smoke
def test_page_22_title(page):
    page.goto(PAGE_22_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))


@pytest.mark.regression
def test_page_22_search_team(page):
    page.goto(PAGE_22_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#q").first.fill("Boston Bruins")
    page.locator("input.btn.btn-primary").first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[1]').first).to_have_text("Boston Bruins", timeout=10000)


@pytest.mark.regression
def test_page_22_pagination(page):
    page.goto(PAGE_22_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"page_num=11"))


@pytest.mark.regression
def test_page_22_elements_visibility(page):
    page.goto(PAGE_22_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('h1').first).to_be_visible()
    expect(page.locator('#q').first).to_be_visible()
    expect(page.locator('input.btn.btn-primary').first).to_be_visible()
    expect(page.locator('#per_page').first).to_be_visible()


@pytest.mark.smoke
def test_page_22_navigation_links(page):
    page.goto(PAGE_22_URL)
    page.wait_for_load_state('networkidle')
    page.get_by_role("link", name="Lessons").first.click()
    expect(page).to_have_url(re.compile(r"lessons"))