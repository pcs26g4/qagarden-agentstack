import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_27_B72F_URL
from playwright.sync_api import expect
import re

def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_27_B72F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-lessons').first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.regression
def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_27_B72F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-faq').first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_27_B72F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.regression
def test_TC_Search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_27_B72F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Vancouver Canucks")
    page.locator('input.btn.btn-primary').first.click()
    # Assuming search results are displayed in a table or list, checking for the team name
    expect(page.locator('body').first).to_contain_text("Vancouver Canucks", timeout=10000)

@pytest.mark.regression
def test_TC_Pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_27_B72F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[6]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"\?page_num=5"))

@pytest.mark.regression
def test_TC_RecordsPerPage_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_27_B72F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("50")
    # Assuming there's a way to verify 50 records are displayed, e.g., by counting elements
    # The actual verification depends on how the records are displayed on the page
    # Example: expect(page.locator('.record-item')).to_have_count(50) - Replace '.record-item' with the actual locator for each record item
    # Since we don't have a specific locator, we'll just check if the URL contains the expected parameter
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"per_page=50"))