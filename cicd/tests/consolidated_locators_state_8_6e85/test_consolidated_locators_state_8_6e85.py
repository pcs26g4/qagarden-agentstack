import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_8_6E85_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_TC_Navigation_01(page):
    """Verify navigation to the Lessons page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.smoke
def test_TC_Navigation_02(page):
    """Verify navigation to the FAQ page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_TC_Navigation_03(page):
    """Verify navigation to the Login page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.smoke
def test_TC_Navigation_04(page):
    """Verify navigation to the Sandbox page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/pages/"))

@pytest.mark.smoke
def test_TC_Navigation_05(page):
    """Verify navigation to lessons page using 3 video lessons link"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "3 video lessons")]').click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.regression
def test_TC_Content_01(page):
    """Verify footer text"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#footer').first).to_have_text(re.compile(r"Lessons and Videos © Hartley Brody 2023"))