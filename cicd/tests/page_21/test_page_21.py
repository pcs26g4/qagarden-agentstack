import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_21_URL
from playwright.sync_api import expect
import pytest
import re

@pytest.mark.smoke
def test_page_21_title(page):
    page.goto(PAGE_21_URL)
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))

@pytest.mark.regression
def test_page_21_search_team(page):
    page.goto(PAGE_21_URL)
    page.locator("#q").first.fill("Boston Bruins")
    page.locator("input.btn.btn-primary").first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[1]').first).to_have_text("Boston Bruins")

@pytest.mark.regression
def test_page_21_pagination(page):
    page.goto(PAGE_21_URL)
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r".*page_num=11"))

@pytest.mark.regression
def test_page_21_change_per_page(page):
    page.goto(PAGE_21_URL)
    page.locator("#per_page").first.select_option("50")
    expect(page.locator('xpath=//*[@id="per_page"]/option[2]')).to_be_selected()

@pytest.mark.smoke
def test_page_21_element_visibility(page):
    page.goto(PAGE_21_URL)
    expect(page.locator('#site-nav').first).to_be_visible()
    expect(page.locator('a.nav-link.hidden-sm.hidden-xs').first).to_be_visible()
    expect(page.locator('#hockey').first).to_be_visible()