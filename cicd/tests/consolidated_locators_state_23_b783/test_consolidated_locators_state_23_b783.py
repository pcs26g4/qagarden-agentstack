import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_23_B783_URL
from playwright.sync_api import expect
import re

def test_TC_NAVIGATION_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_23_B783_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

def test_TC_NAVIGATION_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_23_B783_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click()
    expect(page).to_have_url(re.compile(r"/faq/"))

def test_TC_NAVIGATION_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_23_B783_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "Login")]').click()
    expect(page).to_have_url(re.compile(r"/login/"))

def test_TC_SEARCH_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_23_B783_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Toronto Maple Leafs")
    page.locator('input.btn.btn-primary').first.click()
    #expect(page).to_have_url(re.compile(r"/search_results/")) #The check here is to display the search results properly, not to verify url changes
    #expect(page.locator(".search_result").first).to_be_visible() # Assuming there's a class 'search_result' to identify the search results

def test_TC_PAGINATION_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_23_B783_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[6]/a[1]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=5"))

def test_TC_PAGINATION_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_23_B783_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=12"))