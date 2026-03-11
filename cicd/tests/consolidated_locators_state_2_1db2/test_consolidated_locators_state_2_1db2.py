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

def test_TC_Navigation_001(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.smoke
def test_TC_Navigation_002(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Countries of the World: A Simple Example")]').click()
    expect(page).to_have_url(re.compile(r"/pages/simple/"))

@pytest.mark.smoke
def test_TC_Navigation_003(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Hockey Teams: Forms, Searching and Pagination")]').click()
    expect(page).to_have_url(re.compile(r"/pages/forms/"))

@pytest.mark.smoke
def test_TC_Navigation_004(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Oscar Winning Films: AJAX and Javascript")]').click()
    expect(page).to_have_url(re.compile(r"/pages/ajax-javascript/"))

@pytest.mark.smoke
def test_TC_Navigation_005(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Turtles All the Way Down: Frames & iFrames")]').click()
    expect(page).to_have_url(re.compile(r"/pages/frames/"))

@pytest.mark.regression
def test_TC_Navigation_006(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="pages"]/section[1]/div[1]/div[1]/div[1]/div[5]/h3[1]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/advanced/"))

@pytest.mark.regression
def test_TC_Navigation_007(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link.hidden-sm.hidden-xs').first.click()
    expect(page).to_have_url(re.compile(r"/$"))

@pytest.mark.regression
def test_TC_Navigation_008(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/pages/"))

@pytest.mark.regression
def test_TC_Navigation_009(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.regression
def test_TC_Navigation_010(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_2_1DB2_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))