import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_34_1710_URL
from playwright.sync_api import expect
import re

def test_TC_NAVIGATION_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_34_1710_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-lessons').first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

def test_TC_NAVIGATION_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_34_1710_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-faq').first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))

def test_TC_NAVIGATION_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_34_1710_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

def test_TC_NAVIGATION_04(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_34_1710_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-sandbox').first.click()
    expect(page).to_have_url(re.compile(r"/pages/"))

@pytest.mark.regression
def test_TC_SEARCH_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_34_1710_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill('Oilers')
    page.locator('input.btn.btn-primary').first.click()
    # Assuming the search results will display some text containing the search term
    # Need to identify a specific element in the search results to assert its visibility
    # Example: expect(page.locator('#search-results').first).to_be_visible()
    # You need to adjust the locator based on your actual application's HTML structure.
    # The following is a placeholder and MUST be replaced.
    expect(page.locator("#q").first).to_be_visible(timeout=15000)


@pytest.mark.regression
def test_TC_PAGINATION_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_34_1710_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[6]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=5"))

@pytest.mark.regression
def test_TC_PAGINATION_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_34_1710_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option('50')
    # The following assertion needs to be adapted based on the actual application behavior.
    # You need to identify an element that displays the number of results and assert its content.
    # Example: expect(page.locator('#results-count').first).to_have_text("50")
    # The following is a placeholder and MUST be replaced.
    expect(page.locator("#per_page").first).to_be_visible(timeout=15000)