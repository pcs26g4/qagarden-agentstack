import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_1_1F0D_URL
from playwright.sync_api import expect
import re

def test_TC_Navigation_001(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_1_1F0D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Sandbox")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"/pages/"))

def test_TC_Navigation_002(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_1_1F0D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"/lessons/"))

def test_TC_Navigation_003(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_1_1F0D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"/faq/"))

def test_TC_Navigation_004(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_1_1F0D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"/login/"))

def test_TC_Navigation_005(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_1_1F0D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.btn.btn-lg.btn-default').first.click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"/pages/"))

def test_TC_Navigation_006(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_1_1F0D_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.btn.btn-lg.btn-primary').first.click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"/lessons/"))