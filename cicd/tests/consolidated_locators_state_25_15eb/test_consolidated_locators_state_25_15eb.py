import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_25_15EB_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.locator('xpath=//a[contains(text(), "Lessons")]').click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.smoke
def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.locator('xpath=//a[contains(text(), "FAQ")]').click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.regression
def test_TC_Search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.locator('#q').first.fill("Edmonton Oilers")
    page.locator('input.btn.btn.primary').first.click()

@pytest.mark.regression
def test_TC_Pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[2]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=1"))

@pytest.mark.regression
def test_TC_Pagination_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[24]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=24"))

@pytest.mark.regression
def test_TC_ResultsPerPage_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_25_15EB_URL, timeout=60000)
    page.locator('#per_page').first.select_option("50")