import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_9_E3BD_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.smoke
def test_page_navigation(page):
    page.goto(PAGE_9_E3BD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_9_E3BD_URL)


@pytest.mark.regression
def test_formy_link_navigation(page):
    page.goto(PAGE_9_E3BD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#logo").first.click()
    expect(page).to_have_url(re.compile(r"formy-project"))


@pytest.mark.regression
def test_components_dropdown_visibility(page):
    page.goto(PAGE_9_E3BD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=15000)


@pytest.mark.regression
def test_heading_text(page):
    page.goto(PAGE_9_E3BD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_have_text("Enabled and disabled elements")


@pytest.mark.regression
def test_form_components_visibility(page):
    page.goto(PAGE_9_E3BD_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarNavDropdown").first).to_be_visible(timeout=15000)