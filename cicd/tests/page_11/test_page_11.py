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

def test_page_robots_txt_content(page):
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("pre").first).to_be_visible(timeout=15000)
    expect(page.locator("pre").first).to_have_text("User-agent: *\nDisallow: /lessons/\nDisallow: /faq/")

@pytest.mark.smoke
def test_page_robots_txt_element_count(page):
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("pre").first).to_be_visible(timeout=15000)
    assert page.locator("pre").count() == 1

@pytest.mark.regression
def test_page_robots_txt_body_exists(page):
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("body").first).to_be_visible(timeout=15000)

@pytest.mark.regression
def test_page_robots_txt_html_exists(page):
    page.goto(PAGE_11_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("html").first).to_be_visible(timeout=15000)