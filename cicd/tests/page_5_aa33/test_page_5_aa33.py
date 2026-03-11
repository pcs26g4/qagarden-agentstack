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
def test_page_5_aa33_navigation_to_components_checkbox(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.get_by_text("Checkboxes").first.click()
    expect(page.locator("h1").first).to_be_visible(timeout=10000)

@pytest.mark.regression
def test_page_5_aa33_checkbox_interaction(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.get_by_text("Checkboxes").first.click()
    expect(page.locator("#checkbox-1").first).to_be_visible(timeout=10000)
    page.locator("#checkbox-1").first.check()
    expect(page.locator("#checkbox-1")).to_be_checked()
    page.locator("#checkbox-1").first.uncheck()
    expect(page.locator("#checkbox-1")).not_to_be_checked()

@pytest.mark.regression
def test_page_5_aa33_checkbox_2_initial_state(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.get_by_text("Checkboxes").first.click()
    expect(page.locator("#checkbox-2").first).to_be_visible(timeout=10000)
    expect(page.locator("#checkbox-2")).to_be_checked()

@pytest.mark.regression
def test_page_5_aa33_checkbox_3_interaction(page):
    page.goto(PAGE_5_AA33_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    page.get_by_text("Checkboxes").first.click()
    expect(page.locator("#checkbox-3").first).to_be_visible(timeout=10000)
    page.locator("#checkbox-3").first.check()
    expect(page.locator("#checkbox-3")).to_be_checked()
    page.locator("#checkbox-3").first.uncheck()
    expect(page.locator("#checkbox-3")).not_to_be_checked()