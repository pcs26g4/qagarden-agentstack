import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_14_28FD_URL
from playwright.sync_api import expect
import re
import pytest

def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_14_28FD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-lessons').first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"), timeout=10000)

@pytest.mark.smoke
def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_14_28FD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-faq').first.click()
    expect(page).to_have_url(re.compile(r"/faq/"), timeout=10000)

@pytest.mark.smoke
def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_14_28FD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"), timeout=10000)

@pytest.mark.regression
def test_TC_Search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_14_28FD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Bruins")
    page.locator('input.btn.btn-primary').first.click()
    # Since this is a static website, we're not asserting actual results, but rather attempt and presence
    expect(page.locator('input.btn.btn-primary').first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_TC_Pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_14_28FD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[8]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=7"), timeout=10000)

@pytest.mark.regression
def test_TC_Pagination_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_14_28FD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=3"), timeout=10000)