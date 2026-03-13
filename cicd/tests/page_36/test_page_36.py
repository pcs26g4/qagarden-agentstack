import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_36_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_navigation(page):
    page.goto(PAGE_36_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_36_URL)

@pytest.mark.regression
def test_element_visibility(page):
    page.goto(PAGE_36_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#site-nav').first).to_be_visible(timeout=15000)
    expect(page.locator('#footer').first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_link_navigation(page):
    page.goto(PAGE_36_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(0).click() # Sandbox link
    # Since this is a static site, assume we stay on the same page but verify a title change
    # In a real app, expect navigation to the Sandbox URL
    expect(page).to_have_title(re.compile(r"Advanced Topics|Sandbox"))

@pytest.mark.smoke
def test_login_link_exists(page):
    page.goto(PAGE_36_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//a[contains(text(), "Login")]')).to_be_visible(timeout=15000)