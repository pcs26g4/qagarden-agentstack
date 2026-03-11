import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_4_2B0A_URL
from playwright.sync_api import expect
import pytest
import re


@pytest.mark.smoke
def test_page_4_2b0a_navigation(page):
    page.goto(PAGE_4_2B0A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=10000)
    expect(page.locator("#navbarNavDropdown").first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_4_2b0a_button_visibility(page):
    page.goto(PAGE_4_2B0A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("button.btn.btn-lg.btn-success").first).to_be_visible(timeout=10000)
    expect(page.locator("button.btn.btn-lg.btn-info").first).to_be_visible(timeout=10000)
    expect(page.locator("button.btn.btn-lg.btn-warning").first).to_be_visible(timeout=10000)
    expect(page.locator("button.btn.btn-lg.btn-danger").first).to_be_visible(timeout=10000)
    expect(page.locator("button.btn.btn-lg.btn-link").first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_4_2b0a_button_group_visibility(page):
    page.goto(PAGE_4_2B0A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#btnGroupDrop1").first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_4_2b0a_dropdown_interaction(page):
    page.goto(PAGE_4_2B0A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#btnGroupDrop1").first.click()
    expect(page.locator("xpath=//a[contains(text(), 'Link 1')]")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), 'Link 2')]")).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_4_2b0a_form_components_link(page):
    page.goto(PAGE_4_2B0A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarNavDropdown").first).to_be_visible(timeout=10000)
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=10000)