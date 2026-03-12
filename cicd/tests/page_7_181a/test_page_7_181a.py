import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_7_181A_URL
from playwright.sync_api import expect
import re
import pytest


def test_formy_components_page_navigation(page):
    page.goto(PAGE_7_181A_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_7_181A_URL)


def test_formy_components_drag_element_visibility(page):
    page.goto(PAGE_7_181A_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=10000)
    expect(page.locator("#box").first).to_be_visible(timeout=10000)


def test_formy_components_link_navigation(page):
    page.goto(PAGE_7_181A_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#logo").first.click()
    expect(page).to_have_url(re.compile(r"formy-project\.herokuapp\.com"))


def test_formy_components_dropdown_link_visibility(page):
    page.goto(PAGE_7_181A_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=10000)


def test_formy_components_all_elements_visibility(page):
    page.goto(PAGE_7_181A_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator("nav.navbar.navbar-expand-lg.bg-light").first).to_be_visible(timeout=10000)
    expect(page.locator("h1").first).to_be_visible(timeout=10000)
    expect(page.locator("#box").first).to_be_visible(timeout=10000)