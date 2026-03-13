import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_3_CA37_URL
from playwright.sync_api import expect
import re

def test_TC_Navigation_001(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link.hidden-sm.hidden-xs').first.click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"/$"))

def test_TC_Navigation_002(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    expect(page).to_have_url(re.compile(r"\/"))
    page.locator('a.nav-link').nth(0).click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"\/lessons\/"))

def test_TC_Navigation_003(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    expect(page).to_have_url(re.compile(r"\/"))
    page.locator('a.nav-link').nth(0).click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"\/faq\/"))

def test_TC_Navigation_004(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    expect(page).to_have_url(re.compile(r"\/"))
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"\/login\/"))

def test_TC_Navigation_005(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    expect(page).to_have_url(re.compile(r"\/"))
    page.locator('xpath=//a[contains(text(), "Countries of the World: A Simple Example")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"\/pages\/simple\/"))

def test_TC_Navigation_006(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    expect(page).to_have_url(re.compile(r"\/"))
    page.locator('xpath=//a[contains(text(), "Hockey Teams: Forms, Searching and Pagination")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"\/pages\/forms\/"))

def test_TC_Navigation_007(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    expect(page).to_have_url(re.compile(r"\/"))
    page.locator('xpath=//a[contains(text(), "Oscar Winning Films: AJAX and Javascript")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"\/pages\/ajax-javascript\/"))

def test_TC_Navigation_008(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    expect(page).to_have_url(re.compile(r"\/"))
    page.locator('xpath=//a[contains(text(), "Turtles All the Way Down: Frames & iFrames")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"\/pages\/frames\/"))

def test_TC_Navigation_009(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    expect(page).to_have_url(re.compile(r"\/"))
    page.locator('xpath=//*[@id="pages"]/section[1]/div[1]/div[1]/div[1]/div[5]/h3[1]/a[1]').first.click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r"\/pages\/advanced\/"))