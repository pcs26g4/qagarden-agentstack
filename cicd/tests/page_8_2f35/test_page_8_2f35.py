import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_8_2F35_URL
from playwright.sync_api import expect
import re
import pytest


def test_page_dropdown_link_visible(page):
    page.goto(PAGE_8_2F35_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=15000)


def test_page_formy_link_navigation(page):
    page.goto(PAGE_8_2F35_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#logo").first.click()
    expect(page).to_have_url(re.compile(r"formy-project\.herokuapp\.com"))


@pytest.mark.smoke
def test_page_dropdown_button_click(page):
    page.goto(PAGE_8_2F35_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#dropdownMenuButton").first.click()
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=15000)


@pytest.mark.regression
def test_page_dropdown_heading_visible(page):
    page.goto(PAGE_8_2F35_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#dropdownMenuButton").first.click()
    expect(page.locator("h1").first).to_be_visible(timeout=15000)


def test_page_formcomponents_dropdown_visible(page):
    page.goto(PAGE_8_2F35_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarNavDropdown").first).to_be_visible(timeout=15000)