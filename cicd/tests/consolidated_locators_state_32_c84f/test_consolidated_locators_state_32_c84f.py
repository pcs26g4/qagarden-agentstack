import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_32_C84F_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.regression
def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.regression
def test_TC_Navigation_04(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/pages/"))

@pytest.mark.regression
def test_TC_Search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill('Ottawa Senators')
    page.locator('input.btn.btn-primary').first.click()

@pytest.mark.regression
def test_TC_Pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[3]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"\?page_num=2"))

@pytest.mark.regression
def test_TC_Pagination_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"\?page_num=21"))

@pytest.mark.regression
def test_TC_Pagination_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Previous")]').click()
    expect(page).to_have_url(re.compile(r"\?page_num=19"))

@pytest.mark.regression
def test_TC_RecordsPerPage_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option('50')