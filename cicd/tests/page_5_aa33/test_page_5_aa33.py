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

@pytest.mark.smoke
def test_page_aa33_navigation_to_home(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#logo").first.click()
    expect(page).to_have_url(PAGE_5_AA33_URL)

@pytest.mark.regression
def test_page_aa33_components_dropdown_visibility(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.hover()
    expect(page.locator("xpath=//a[contains(text(), 'Autocomplete')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Buttons')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Checkbox')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Datepicker')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Drag and Drop')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Dropdown')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Enabled and Disabled elements')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'File Upload')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Key and Mouse Press')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Modal')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Page Scroll')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Radio Button')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Switch Window')]")).to_be_visible(timeout=15000)
    expect(page.locator("xpath=//a[contains(text(), 'Complete Web Form')]")).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_aa33_checkbox_interaction(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.hover()
    page.locator("xpath=//a[contains(text(), 'Checkbox')]").click()
    expect(page.locator("h1").first).to_be_visible(timeout=15000)
    page.locator("#checkbox-1").first.click()
    expect(page.locator("#checkbox-1")).to_be_checked()
    page.locator("#checkbox-2").first.click()
    expect(page.locator("#checkbox-2")).to_be_checked()
    page.locator("#checkbox-3").first.click()
    expect(page.locator("#checkbox-3")).to_be_checked()