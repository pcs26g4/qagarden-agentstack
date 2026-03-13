import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_17_BC3D_URL
from playwright.sync_api import expect
import re

def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_17_BC3D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("state_17_link_lessons_393_10").first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.regression
def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_17_BC3D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("state_17_link_faq_515_10").first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_17_BC3D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("state_17_link_login_1105_10").first.click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.regression
def test_TC_Navigation_04(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_17_BC3D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("state_17_link_sandbox_267_10").first.click()
    expect(page).to_have_url(re.compile(r"/pages/"))

@pytest.mark.regression
def test_TC_Search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_17_BC3D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("state_17_input_search_for_teams").first.fill("Toronto Maple Leafs")
    page.locator("state_17_input_el").first.click()
    # Add verification here as per requirements.  The test case doesn't specify the element to verify.
    # Example: expect(page.locator("locator_for_search_results").first).to_be_visible()

@pytest.mark.regression
def test_TC_Pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_17_BC3D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("state_17_link_6").first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=6"))

@pytest.mark.regression
def test_TC_Pagination_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_17_BC3D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("state_17_2550100").first.select_option("50")
    # Add verification here as per requirements.  The test case doesn't specify the element to verify.
    # Example: expect(page.locator("locator_for_50_results").first).to_be_visible()