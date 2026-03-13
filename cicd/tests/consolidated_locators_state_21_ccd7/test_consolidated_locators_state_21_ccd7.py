import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_21_CCD7_URL
from playwright.sync_api import expect
import re
import pytest


def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_21_CCD7_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))


def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_21_CCD7_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))


def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_21_CCD7_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))


def test_TC_Search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_21_CCD7_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Leafs")
    page.locator('input.btn.btn-primary').first.click()


def test_TC_Pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_21_CCD7_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[6]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=6"))


def test_TC_Pagination_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_21_CCD7_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=10"))


def test_TC_RecordsPerPage_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_21_CCD7_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option("100")