import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_11_47E8_URL
from playwright.sync_api import expect
import re

URL = CONSOLIDATED_LOCATORS_STATE_11_47E8_URL

@pytest.mark.smoke
@pytest.mark.regression
def test_TC_Navigation_001(page):
    page.goto(URL)
    page.get_by_role("link", name="Lessons").first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.smoke
@pytest.mark.regression
def test_TC_Navigation_002(page):
    page.goto(URL)
    page.get_by_role("link", name="FAQ").first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
@pytest.mark.regression
def test_TC_Navigation_003(page):
    page.goto(URL)
    page.get_by_role("link", name="Login").first.click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.smoke
@pytest.mark.regression
def test_TC_Navigation_004(page):
    page.goto(URL)
    page.get_by_role("link", name="Sandbox").first.click()
    expect(page).to_have_url(re.compile(r"/pages/"))

@pytest.mark.regression
def test_TC_AdvancedPages_001(page):
    page.goto(URL)
    page.get_by_role("link", name="Spoofing Headers").first.click()
    expect(page).to_have_url(re.compile(r"/pages/advanced/\?gotcha=headers"))

@pytest.mark.regression
def test_TC_AdvancedPages_002(page):
    page.goto(URL)
    page.get_by_role("link", name="Logins & Session Data").first.click()
    expect(page).to_have_url(re.compile(r"/pages/advanced/\?gotcha=login"))

@pytest.mark.regression
def test_TC_AdvancedPages_003(page):
    page.goto(URL)
    page.get_by_role("link", name="CSRF & Hidden Values").first.click()
    expect(page).to_have_url(re.compile(r"/pages/advanced/\?gotcha=csrf"))