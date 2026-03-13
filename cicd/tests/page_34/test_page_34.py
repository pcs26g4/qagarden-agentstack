import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_34_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_34_title(page):
    page.goto(PAGE_34_URL)
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_page_34_search_team(page):
    page.goto(PAGE_34_URL)
    search_term = "Vancouver Canucks"
    page.locator("#q").first.fill(search_term)
    page.locator("input.btn.btn-primary").first.click()
    expect(page.locator("xpath=//*[@id=\"hockey\"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]").first).to_have_text(search_term)

@pytest.mark.regression
def test_page_34_navigation_lessons(page):
    page.goto(PAGE_34_URL)
    page.locator("xpath=//a[contains(text(), \"Lessons\")]").click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.regression
def test_page_34_change_per_page(page):
    page.goto(PAGE_34_URL)
    page.locator("#per_page").first.select_option("50")
    expect(page.locator("#per_page").first).to_have_value("50")

@pytest.mark.regression
def test_page_34_pagination(page):
    page.goto(PAGE_34_URL)
    page.locator("xpath=//*[contains(@aria-label, \"Next\")]").click()
    expect(page).to_have_url(re.compile(r"page_num=24"))