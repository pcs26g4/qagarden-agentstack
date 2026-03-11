import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_10_BE84_URL
from playwright.sync_api import expect
import re
import pytest


def test_page_file_upload_heading_visibility(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=15000)


def test_page_file_upload_choose_button_visibility(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("button.btn.btn-secondary.btn-choose").first).to_be_visible(timeout=15000)


def test_page_file_upload_reset_button_visibility(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("button.btn.btn-warning.btn-reset").first).to_be_visible(timeout=15000)


@pytest.mark.smoke
def test_page_formy_link_navigation(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#logo").first.click()
    expect(page).to_have_url(re.compile(r"formy-project\.herokuapp\.com"))


@pytest.mark.regression
def test_page_form_components_link_visibility(page):
    page.goto(PAGE_10_BE84_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarNavDropdown").first).to_be_visible(timeout=15000)