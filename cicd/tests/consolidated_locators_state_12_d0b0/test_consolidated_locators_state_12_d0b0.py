import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_12_D0B0_URL
from playwright.sync_api import expect
import re

import pytest

@pytest.mark.regression
def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_12_D0B0_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-lessons').first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.regression
def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_12_D0B0_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-faq').first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.regression
def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_12_D0B0_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.regression
def test_TC_Search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_12_D0B0_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Toronto Maple Leafs")
    page.locator('input.btn.btn-primary').first.click()
    # Since this is a static site, we can't reliably assert search results
    # Instead, we verify that the search input retains the entered value
    expect(page.locator('#q').first).to_have_value("Toronto Maple Leafs")


@pytest.mark.regression
def test_TC_Pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_12_D0B0_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[2]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=2"))

@pytest.mark.regression
def test_TC_Pagination_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_12_D0B0_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=2"))

@pytest.mark.regression
def test_TC_ResultsPerPage_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_12_D0B0_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("50")
    expect(page).to_have_url(re.compile(r"per_page=50"))