import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_tc_navigation_01(page):
    """Verify navigation to Lessons page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.smoke
def test_tc_navigation_02(page):
    """Verify navigation to FAQ page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_tc_navigation_03(page):
    """Verify navigation to Login page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.regression
def test_tc_navigation_04(page):
    """Verify navigation to Countries of the World page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Countries of the World: A Simple Example")]').click()
    expect(page).to_have_url(re.compile(r"/pages/simple/"))

@pytest.mark.regression
def test_tc_navigation_05(page):
    """Verify navigation to Hockey Teams page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Hockey Teams: Forms, Searching and Pagination")]').click()
    expect(page).to_have_url(re.compile(r"/pages/forms/"))

@pytest.mark.regression
def test_tc_navigation_06(page):
    """Verify navigation to Oscar Winning Films page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Oscar Winning Films: AJAX and Javascript")]').click()
    expect(page).to_have_url(re.compile(r"/pages/ajax-javascript/"))

@pytest.mark.regression
def test_tc_navigation_07(page):
    """Verify navigation to Frames & iFrames page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Turtles All the Way Down: Frames & iFrames")]').click()
    expect(page).to_have_url(re.compile(r"/pages/frames/"))

@pytest.mark.regression
def test_tc_navigation_08(page):
    """Verify navigation to Advanced Topics page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="pages"]/section[1]/div[1]/div[1]/div[1]/div[5]/h3[1]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/advanced/"))

@pytest.mark.smoke
def test_tc_navigation_09(page):
    """Verify navigation to Scrape This Site homepage"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link.hidden-sm.hidden-xs').first.click()
    expect(page).to_have_url(re.compile(r"/"))

@pytest.mark.regression
def test_tc_navigation_10(page):
    """Verify navigation to Sandbox page"""
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#nav-sandbox').first.click()