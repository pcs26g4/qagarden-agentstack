import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_4_2B0A_URL
from playwright.sync_api import expect
import re
import pytest

def test_page_navigation(page):
    page.goto(PAGE_4_2B0A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)
    expect(page.locator("#navbarNavDropdown").first).to_be_visible(timeout=15000)

@pytest.mark.smoke
def test_primary_button_visibility(page):
    page.goto(PAGE_4_2B0A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("button.btn.btn-lg.btn-success").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_dropdown_menu_interaction(page):
    page.goto(PAGE_4_2B0A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#btnGroupDrop1").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Link 1')]")).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_multiple_buttons_visibility(page):
    page.goto(PAGE_4_2B0A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[3]/div[1]/div[1]/div[1]/button[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[3]/div[1]/div[1]/div[1]/button[2]").first).to_be_visible(timeout=15000)

@pytest.mark.smoke
def test_formy_link_navigation(page):
    page.goto(PAGE_4_2B0A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#logo").first.click()
    expect(page).to_have_url(re.compile(r"formy-project\.com"))