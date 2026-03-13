import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_9_918D_URL
from playwright.sync_api import expect
import re

@pytest.mark.smoke
def test_TC_Navigation_01(page):
    """Verify navigation to the Lessons page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_9_918D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.smoke
def test_TC_Navigation_02(page):
    """Verify navigation to the FAQ page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_9_918D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_TC_Navigation_03(page):
    """Verify navigation to the Login page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_9_918D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.smoke
def test_TC_Navigation_04(page):
    """Verify navigation to the home page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_9_918D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link.hidden-sm.hidden-xs').first.click()
    expect(page).to_have_url(re.compile(r"/"))

@pytest.mark.regression
def test_TC_Link_2015_01(page):
    """Verify clicking on 2015 link does not navigate to a new page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_9_918D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#2015').nth(0).click()
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_9_918D_URL)