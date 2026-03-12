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
import pytest


def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a\[href\="\/lessons\/"\]').first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))


def test_TC_Navigation_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a\[href\="\/faq\/"\]').first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))


def test_TC_Navigation_03(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a\[href\="\/login\/"\]').first.click()
    expect(page).to_have_url(re.compile(r"/login/"))


def test_TC_Search_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Toronto Maple Leafs")
    page.locator('input.btn.btn-primary').first.click()


def test_TC_Pagination_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a\[href\="\/pages\/forms\/?page_num\=5"\]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=5"))


def test_TC_Pagination_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_7_201D_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a\[href\="\/pages\/forms\/?page_num\=23"\]').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=23"))