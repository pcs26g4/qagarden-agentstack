import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_22_5227_URL
from playwright.sync_api import expect
import re
import pytest

def test_tc_navigation_01(page):
    """Verify navigation to the Lessons page."""
    page.goto(CONSOLIDATED_LOCATORS_STATE_22_5227_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-lessons').first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.smoke
def test_tc_navigation_02(page):
    """Verify navigation to the FAQ page."""
    page.goto(CONSOLIDATED_LOCATORS_STATE_22_5227_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-faq').first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_tc_navigation_03(page):
    """Verify navigation to the Login page."""
    page.goto(CONSOLIDATED_LOCATORS_STATE_22_5227_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.regression
def test_tc_search_01(page):
    """Verify searching for a team."""
    page.goto(CONSOLIDATED_LOCATORS_STATE_22_5227_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Toronto Maple Leafs")
    page.locator('input.btn.btn-primary').first.click()

@pytest.mark.regression
def test_tc_pagination_01(page):
    """Verify navigating to page 15."""
    page.goto(CONSOLIDATED_LOCATORS_STATE_22_5227_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[16]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=15"))

@pytest.mark.regression
def test_tc_records_per_page_01(page):
    """Verify changing records per page to 100."""
    page.goto(CONSOLIDATED_LOCATORS_STATE_22_5227_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option('100')