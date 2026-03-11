import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_3_9DDB_URL
from playwright.sync_api import expect
import re
import pytest


def test_page_3_9ddb_navigation(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_3_9DDB_URL)
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=15000)
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=15000)


def test_page_3_9ddb_autocomplete_elements_visibility(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.get_by_text("Autocomplete").first.click()
    expect(page.locator("h1").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[1]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#autocomplete").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[2]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#street_number").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[3]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#route").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[4]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#locality").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[5]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#administrative_area_level_1").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[6]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#postal_code").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[7]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#country").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_3_9ddb_autocomplete_interaction(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.get_by_text("Autocomplete").first.click()
    page.locator("#autocomplete").first.fill("1600 Amphitheatre Parkway");
    page.locator("#street_number").first.fill("1600");
    page.locator("#route").first.fill("Amphitheatre Parkway");
    page.locator("#locality").first.fill("Mountain View");
    page.locator("#administrative_area_level_1").first.fill("CA");
    page.locator("#postal_code").first.fill("94043");
    page.locator("#country").first.fill("USA");
    expect(page.locator("#autocomplete").first).to_have_value("1600 Amphitheatre Parkway", timeout=10000);
    expect(page.locator("#street_number").first).to_have_value("1600", timeout=10000);
    expect(page.locator("#route").first).to_have_value("Amphitheatre Parkway", timeout=10000);
    expect(page.locator("#locality").first).to_have_value("Mountain View", timeout=10000);
    expect(page.locator("#administrative_area_level_1").first).to_have_value("CA", timeout=10000);
    expect(page.locator("#postal_code").first).to_have_value("94043", timeout=10000);
    expect(page.locator("#country").first).to_have_value("USA", timeout=10000);

@pytest.mark.smoke
def test_page_3_9ddb_formy_link(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#logo").first.click()
    expect(page).to_have_url(PAGE_3_9DDB_URL)

@pytest.mark.regression
def test_page_3_9ddb_dropdown_menu_navigation(page):
    page.goto(PAGE_3_9DDB_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Buttons')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Checkbox')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Datepicker')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Drag and Drop')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Dropdown')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Enabled and Disabled elements')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'File Upload')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Key and Mouse Press')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Modal')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Page Scroll')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Radio Button')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Switch Window')]")).to_be_visible()
    expect(page.locator("xpath=//a[contains(text(), 'Complete Web Form')]")).to_be_visible()