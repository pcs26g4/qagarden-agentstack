import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_5_AA33_URL
from playwright.sync_api import expect
import re
import pytest


def test_page_5_aa33_navigation(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_5_AA33_URL)
    expect(page.locator("#logo").first).to_be_visible(timeout=10000)
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=10000)
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")).to_be_visible(timeout=10000)

@pytest.mark.smoke
def test_page_5_aa33_checkboxes_visibility(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("xpath=//a[contains(text(), 'Checkboxes')]").click()
    expect(page.locator("h1").first).to_be_visible(timeout=10000)
    expect(page.locator("#checkbox-1").first).to_be_visible(timeout=10000)
    expect(page.locator("#checkbox-2").first).to_be_visible(timeout=10000)
    expect(page.locator("#checkbox-3").first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_5_aa33_checkboxes_interaction(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("xpath=//a[contains(text(), 'Checkboxes')]").click()
    page.locator("#checkbox-1").first.click()
    expect(page.locator("#checkbox-1")).not_to_be_checked()
    page.locator("#checkbox-2").first.click()
    expect(page.locator("#checkbox-2")).to_be_checked()

@pytest.mark.regression
def test_page_5_aa33_dropdown_link(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Autocomplete')]")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), 'Buttons')]")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), 'Checkbox')]")).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_5_aa33_complete_web_form_link(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Complete Web Form')]")).to_be_visible(timeout=10000)