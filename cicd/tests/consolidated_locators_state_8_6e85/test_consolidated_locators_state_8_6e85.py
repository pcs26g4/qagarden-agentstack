import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_8_6E85_URL
from playwright.sync_api import expect
import re
import pytest


def test_page_valid_credentials(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.get_by_role('link', name='Lessons').first.click()
    expect(page).to_have_url(re.compile(r"/lessons/"))


def test_page_empty_email(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.get_by_role('link', name='FAQ').first.click()
    expect(page).to_have_url(re.compile(r"/faq/"))


def test_page_invalid_credentials(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.get_by_role('link', name='Login').first.click()
    expect(page).to_have_url(re.compile(r"/login/"))


def test_page_welcome(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.get_by_role('link', name='Sandbox').first.click()
    expect(page).to_have_url(re.compile(r"/pages/"))


def test_page_locked_user(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.get_by_role('link', name='scrape this site').first.click()
    expect(page).to_have_url(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL)


def test_page_problem_user(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#search1").first.fill('Leafs')
    page.locator("#search1").press("Enter")
    expect(page).to_have_url(re.compile(r"Leafs"))


def test_page_performance_glitch_user(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.get_by_role('link', name='5').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=5"))


def test_page_error_user(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_8_6E85_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.get_by_role('link', name='23').first.click()
    expect(page).to_have_url(re.compile(r"/pages/forms/\?page_num=23"))