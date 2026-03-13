import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_5_5849_URL
from playwright.sync_api import expect
import re

def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/sandbox/"), timeout=10000)
    
@pytest.mark.regression
def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"), timeout=10000)

@pytest.mark.regression
def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"), timeout=10000)

@pytest.mark.regression
def test_TC_Navigation_04(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"), timeout=10000)

@pytest.mark.regression
def test_TC_Navigation_05(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a').nth(0).click()
    expect(page).to_have_url(re.compile(r"/robots\.txt"), timeout=10000)