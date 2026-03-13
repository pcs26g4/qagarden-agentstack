import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_7_181A_URL
from playwright.sync_api import expect
import re
import pytest


def test_drag_and_drop_elements_visible(page):
    page.goto(PAGE_7_181A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=10000)
    expect(page.locator("#box").first).to_be_visible(timeout=10000)
    expect(page.locator("nav.navbar.navbar-expand-lg.bg-light").first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_navigation_to_formy_components(page):
    page.goto(PAGE_7_181A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#logo").first.click()
    expect(page).to_have_url(re.compile(r"formy-project\.herokuapp\.com"))


@pytest.mark.smoke
def test_drag_the_image_text(page):
    page.goto(PAGE_7_181A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_have_text("Drag the image into the box")


@pytest.mark.regression
def test_components_link_present(page):
    page.goto(PAGE_7_181A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#navbarDropdownMenuLink").first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_form_components_dropdown_links(page):
    page.goto(PAGE_7_181A_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("#navbarDropdownMenuLink").first.click()
    expect(page.locator("a.nav-link").first).to_be_visible(timeout=10000)