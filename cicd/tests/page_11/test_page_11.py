import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_11_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_11_navigation(page):
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_11_URL)

@pytest.mark.regression
def test_page_11_advanced_topics_heading_visible(page):
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("page.locator('h3')")).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_11_spoofing_headers_link_present(page):
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//a[contains(text(), "Spoofing Headers")]')).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_11_logins_session_data_link_present(page):
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//a[contains(text(), "Logins & Session Data")]')).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_11_csrf_hidden_values_link_present(page):
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//a[contains(text(), "CSRF & Hidden Values")]')).to_be_visible(timeout=10000)