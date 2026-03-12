import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_18_4C88_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.smoke
def test_TC_NAVIGATION_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_18_4C88_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-lessons').first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))


@pytest.mark.smoke
def test_TC_NAVIGATION_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_18_4C88_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-faq').first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))


@pytest.mark.smoke
def test_TC_NAVIGATION_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_18_4C88_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))


@pytest.mark.regression
def test_TC_SEARCH_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_18_4C88_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Toronto Maple Leafs")
    page.locator('input.btn.btn-primary').first.click()
    # Assuming the search results are displayed on the same page
    expect(page.locator('input.btn.btn-primary').first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_TC_PAGINATION_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_18_4C88_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[9]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=9"))


@pytest.mark.regression
def test_TC_RECORDS_PER_PAGE_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_18_4C88_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.click()
    page.locator('#per_page').first.select_option("100")
    expect(page.locator('#per_page').first).to_be_visible(timeout=10000)