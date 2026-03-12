import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_24_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.smoke
def test_page_24_title(page):
    page.goto(PAGE_24_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))


@pytest.mark.regression
def test_page_24_search_team(page):
    page.goto(PAGE_24_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    search_term = "Pittsburgh Penguins"
    page.locator("#q").first.fill(search_term)
    page.locator("input.btn.btn-primary").first.click()
    expect(page.locator("xpath=//*[@id=\"hockey\"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]").first).to_have_text(search_term)


@pytest.mark.regression
def test_page_24_pagination(page):
    page.goto(PAGE_24_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("xpath=//*[@id=\"hockey\"]/div[1]/div[5]/div[1]/ul[1]/li[14]/a[1]").first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[13]/a[1]/strong[1]').first).to_be_visible()


@pytest.mark.regression
def test_page_24_items_per_page(page):
    page.goto(PAGE_24_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    expect(page.locator("#per_page").first).to_have_value("50")

@pytest.mark.smoke
def test_page_24_navigation_links(page):
    page.goto(PAGE_24_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#nav-homepage').first).to_be_visible(timeout=15000)
    expect(page.locator('#nav-sandbox').first).to_be_visible(timeout=15000)
    expect(page.locator('#nav-lessons').first).to_be_visible(timeout=15000)
    expect(page.locator('#nav-faq').first).to_be_visible(timeout=15000)
    expect(page.locator('#nav-login').first).to_be_visible(timeout=15000)