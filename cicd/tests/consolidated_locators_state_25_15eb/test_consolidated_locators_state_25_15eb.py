import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_25_15EB_URL
from playwright.sync_api import expect
import re

def test_tc_navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#nav-lessons").first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.smoke
def test_tc_navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#nav-faq").first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_tc_navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.regression
def test_tc_search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Toronto Maple Leafs")
    page.locator('input.btn.btn-primary').first.click()
    # Assuming some result will appear if search is successful, adjust locator accordingly
    # This is a placeholder, replace with a real check for search results
    expect(page.locator("body").first).to_contain_text("Toronto Maple Leafs", timeout=10000)

@pytest.mark.regression
def test_tc_pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[11]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=11"))

@pytest.mark.regression
def test_tc_records_per_page_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("50")
    # Assuming a table with records, adjust selector for rows accordingly
    # This is a placeholder, replace with a real check for number of records
    #expect(page.locator("table tr")).to_have_count(50) #This assumes that the first row is header, and that the number of rows will now be 51
    #If a table contains headers and footers then the number of table rows will be 52
    #Instead, we want to find the number of records specifically.
    #This is a placeholder - adjust with actual locator for record entries
    expect(page.locator("table tbody tr")).to_have_count(50, timeout=10000)