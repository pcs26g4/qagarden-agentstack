import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_4_E555_URL
from playwright.sync_api import expect
import re

@pytest.mark.smoke
def test_TC_Navigation_001(page):
    """Verify navigation to Sandbox page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_4_E555_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/pages/"))

@pytest.mark.smoke
def test_TC_Navigation_002(page):
    """Verify navigation to Lessons page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_4_E555_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.smoke
def test_TC_Navigation_003(page):
    """Verify navigation to FAQ page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_4_E555_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_TC_Navigation_004(page):
    """Verify navigation to Login page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_4_E555_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.smoke
def test_TC_Navigation_005(page):
    """Verify navigation to Home page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_4_E555_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link.hidden-sm.hidden-xs').first.click()
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_4_E555_URL)

@pytest.mark.regression
def test_TC_Navigation_006(page):
    """Verify navigation to robots.txt"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_4_E555_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a').nth(0).click()
    expect(page).to_have_url(re.compile(r"/robots\.txt/"))