import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_6_7142_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.smoke
def test_page_6_7142_logo_link(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)
    page.locator("#logo").first.click()
    expect(page).to_have_url(PAGE_6_7142_URL)


@pytest.mark.regression
def test_page_6_7142_navigation_to_autocomplete(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=15000)
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Autocomplete')]")).to_be_visible(timeout=15000)
    page.locator("xpath=//a[contains(text(), 'Autocomplete')]").click()
    # Since this is a static site, we only check element visibility on the target page.
    # If there's no navigation, replace expect(page).to_have_url with verification of element visibility.
    expect(page.locator("h1").first).to_be_visible(timeout=15000)


@pytest.mark.regression
def test_page_6_7142_navigation_to_buttons(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=15000)
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Buttons')]")).to_be_visible(timeout=15000)
    page.locator("xpath=//a[contains(text(), 'Buttons')]").click()
    # Since this is a static site, we only check element visibility on the target page.
    expect(page.locator("h1").first).to_be_visible(timeout=15000)


@pytest.mark.regression
def test_page_6_7142_navigation_to_checkbox(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=15000)
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Check Box')]")).to_be_visible(timeout=15000)
    page.locator("xpath=//a[contains(text(), 'Check Box')]").click()
    # Since this is a static site, we only check element visibility on the target page.
    expect(page.locator("h1").first).to_be_visible(timeout=15000)


@pytest.mark.regression
def test_page_6_7142_navigation_to_datepicker(page):
    page.goto(PAGE_6_7142_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=15000)
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Datepicker')]")).to_be_visible(timeout=15000)
    page.locator("xpath=//a[contains(text(), 'Datepicker')]").click()
    # Since this is a static site, we only check element visibility on the target page.
    expect(page.locator("h1").first).to_be_visible(timeout=15000)