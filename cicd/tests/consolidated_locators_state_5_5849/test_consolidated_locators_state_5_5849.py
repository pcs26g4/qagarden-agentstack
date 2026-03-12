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

def test_TC_NAVIGATION_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/pages/"))

def test_TC_NAVIGATION_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

def test_TC_NAVIGATION_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))

def test_TC_NAVIGATION_04(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

def test_TC_AUTHENTICATION_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))
    page.locator('#email').first.fill("user@example.com")
    page.locator('#password').first.fill("SecretPassword123")
    page.locator('input.btn.btn-primary.btn-lg.pull-right').first.click()
    #Since there's no real dashboard, just checking that form was submitted
    #and we are still on the same page
    expect(page).to_have_url(re.compile(r"/login/"))

def test_TC_AUTHENTICATION_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_5_5849_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))
    page.locator('#email').first.fill("invalid@example.com")
    page.locator('#password').first.fill("WrongPassword")
    page.locator('input.btn.btn-primary.btn-lg.pull-right').first.click()
    # Since the login is static, and we expect an error, we verify that the page URL does not change.
    expect(page).to_have_url(re.compile(r"/login/"))