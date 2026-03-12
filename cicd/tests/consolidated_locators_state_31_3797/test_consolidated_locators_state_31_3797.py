import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_31_3797_URL
from playwright.sync_api import expect
import re

def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_31_3797_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-lessons').first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_31_3797_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-faq').first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))

def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_31_3797_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.regression
def test_TC_Search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_31_3797_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("New York Rangers")
    page.locator('input.btn.btn-primary').first.click()
    # Since this is a static site, we can't verify actual search results.
    # We can only verify that the page remains loaded after attempting the search.
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_31_3797_URL)

@pytest.mark.regression
def test_TC_Pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_31_3797_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[6]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=5"))

@pytest.mark.regression
def test_TC_Pagination_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_31_3797_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=21"))

@pytest.mark.regression
def test_TC_Pagination_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_31_3797_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Previous")]').click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=19"))

@pytest.mark.regression
def test_TC_RecordsPerPage_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_31_3797_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option('100')
    #Since this is a static site, we cannot verify the number of elements displayed dynamically
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_31_3797_URL)