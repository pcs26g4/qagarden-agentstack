import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_11_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_robots_txt_navigation(page):
    """Navigates to the robots.txt page and verifies the URL."""
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_11_URL)

@pytest.mark.regression
def test_page_robots_txt_content(page):
    """Verifies the presence of specific disallow rules in robots.txt."""
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("pre").first).to_be_visible(timeout=10000)
    expect(page.locator("pre").first).to_have_text("User-agent: *\nDisallow: /lessons/\nDisallow: /faq/")

@pytest.mark.regression
def test_page_robots_txt_element_count(page):
    """Checks if the pre element containing the robots.txt content is unique."""
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("pre").first).to_be_visible(timeout=10000)
    assert page.locator("pre").count() == 1

@pytest.mark.regression
def test_page_robots_txt_body_element_visibility(page):
    """Verifies if the body element is visible on the robots.txt page."""
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("body").first).to_be_visible(timeout=10000)