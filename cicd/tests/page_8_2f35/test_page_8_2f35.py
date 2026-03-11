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

def test_page_formy_link(page):
    page.goto(PAGE_8_2F35_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)
    page.locator("#logo").first.click()
    expect(page).to_have_url("https://formy-project.herokuapp.com/", timeout=15000)

@pytest.mark.smoke
def test_page_components_dropdown_visibility(page):
    page.goto(PAGE_8_2F35_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_components_dropdown_interaction(page):
    page.goto(PAGE_8_2F35_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_dropdown_button_visibility(page):
    page.goto(PAGE_8_2F35_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#dropdownMenuButton").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_heading_visibility(page):
    page.goto(PAGE_8_2F35_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=15000)