import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_7_201D_URL
from playwright.sync_api import expect
import re

@pytest.mark.smoke
def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL)
    page.get_by_role('link', name='Lessons').first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))

@pytest.mark.smoke
def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL)
    page.get_by_role('link', name='FAQ').first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))

@pytest.mark.smoke
def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL)
    page.get_by_role('link', name='Login').first.click()
    expect(page).to_have_url(re.compile(r"/login/"))

@pytest.mark.smoke
def test_TC_Navigation_04(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL)
    page.get_by_role('link', name='Sandbox').first.click()
    expect(page).to_have_url(re.compile(r"/pages/"))

@pytest.mark.smoke
def test_TC_Navigation_05(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL)
    page.get_by_role('link', name=re.compile(r"4 video lessons")).click()
    expect(page).to_have_url(re.compile(r"/lessons/"))