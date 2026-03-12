import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_BASE_STATE_EBFA_URL
from playwright.sync_api import expect
import re

def test_TC_Navigation_001(page):
    page.goto(CONSOLIDATED_LOCATORS_BASE_STATE_EBFA_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/pages/"))

def test_TC_Navigation_002(page):
    page.goto(CONSOLIDATED_LOCATORS_BASE_STATE_EBFA_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

def test_TC_Navigation_003(page):
    page.goto(CONSOLIDATED_LOCATORS_BASE_STATE_EBFA_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))

def test_TC_Navigation_004(page):
    page.goto(CONSOLIDATED_LOCATORS_BASE_STATE_EBFA_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

def test_TC_Navigation_005(page):
    page.goto(CONSOLIDATED_LOCATORS_BASE_STATE_EBFA_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Spoofing Headers")]').click()
    expect(page).to_have_url(re.compile(r"/pages/advanced/\?gotcha=headers"))

def test_TC_Navigation_006(page):
    page.goto(CONSOLIDATED_LOCATORS_BASE_STATE_EBFA_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Logins & Session Data")]').click()
    expect(page).to_have_url(re.compile(r"/pages/advanced/\?gotcha=login"))

def test_TC_Navigation_007(page):
    page.goto(CONSOLIDATED_LOCATORS_BASE_STATE_EBFA_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "CSRF & Hidden Values")]').click()
    expect(page).to_have_url(re.compile(r"/pages/advanced/\?gotcha=csrf"))

def test_TC_Authentication_001(page):
    page.goto(CONSOLIDATED_LOCATORS_BASE_STATE_EBFA_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#email').first.fill("test@example.com")
    expect(page.locator('#email').first).to_have_value("test@example.com")

def test_TC_Authentication_002(page):
    page.goto(CONSOLIDATED_LOCATORS_BASE_STATE_EBFA_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#email').first.fill("test!#$%&'*+-/=?^_`{|}~@example.com")
    expect(page.locator('#email').first).to_have_value("test!#$%&'*+-/=?^_`{|}~@example.com")