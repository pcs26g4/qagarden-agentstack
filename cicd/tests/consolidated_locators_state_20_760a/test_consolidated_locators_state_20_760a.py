import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_20_760A_URL
from playwright.sync_api import expect
import re

def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_20_760A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("a\:has-text('Lessons')").click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_20_760A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("a\:has-text('FAQ')").click()
    expect(page).to_have_url(re.compile(r"/faq/"))

def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_20_760A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("a\:has-text('Login')").click()
    expect(page).to_have_url(re.compile(r"/login/"))

def test_TC_Search_01(page,):
    page.goto(CONSOLIDATED_LOCATORS_STATE_20_760A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#team-search").first.fill("Oilers")
    page.locator("li\:has-text('Oilers')").click()
    expect(page.locator("li\:has-text('Oilers')")).to_be_visible()

def test_TC_Pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_20_760A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("a\:has-text('2')").click()
    expect(page).to_have_url(re.compile(r"\?page_num=2"))

def test_TC_ResultsPerPage_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_20_760A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#per-page-select").first.select_option("50")
    expect(page).to_have_url(re.compile(r"per_page=50"))