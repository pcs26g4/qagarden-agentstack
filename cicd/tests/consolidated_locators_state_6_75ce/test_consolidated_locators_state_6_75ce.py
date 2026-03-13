import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_6_75CE_URL
from playwright.sync_api import expect
import re

import pytest


def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_6_75CE_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/pages/"))


def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_6_75CE_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))


def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_6_75CE_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))


def test_TC_Navigation_04(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_6_75CE_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))


def test_TC_Authentication_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_6_75CE_URL + "/login/", timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#email').first.fill("testuser@example.com")
    page.locator('#password').first.fill("SecurePassword123!")
    page.locator('input.btn.btn-primary.btn-lg.pull-right').first.click()

@pytest.mark.smoke
def test_TC_Authentication_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_6_75CE_URL + "/login/", timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#email').first.fill("invaliduser@example.com")
    page.locator('#password').first.fill("IncorrectPassword")
    page.locator('input.btn.btn-primary.btn-lg.pull-right').first.click()