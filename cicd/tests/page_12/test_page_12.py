import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_12_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_12_navigation(page):
    """
    Navigates to the robots.txt page and verifies the URL.
    """
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_12_URL)

@pytest.mark.regression
def test_page_12_useragent_disallow_visibility(page):
    """
    Checks if the robots.txt content is visible.
    """
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("pre").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_12_useragent_disallow_content(page):
    """
    Verifies the content of robots.txt file.
    """
    page.goto(PAGE_12_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expected_text = "User-agent: *\nDisallow: /lessons/\nDisallow: /faq/"
    expect(page.locator("pre").first).to_have_text(expected_text)