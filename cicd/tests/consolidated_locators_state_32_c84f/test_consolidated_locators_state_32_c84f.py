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


def test_tc_navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-lessons').first.click()
    expect(page).to_have_url(re.compile(r"lessons"), timeout=10000)


def test_tc_navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-faq').first.click()
    expect(page).to_have_url(re.compile(r"faq"), timeout=10000)


@pytest.mark.smoke
def test_tc_navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"login"), timeout=10000)


@pytest.mark.regression
def test_tc_search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill('Vancouver Canucks')
    page.locator('input.btn.btn-primary').first.click()
    # Since it's a static website, just check if the search input contains the filled value.
    expect(page.locator('#q').first).to_have_value('Vancouver Canucks', timeout=10000)


@pytest.mark.regression
def test_tc_pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_32_C84F_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[6]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"page_num=5"), timeout=10000)