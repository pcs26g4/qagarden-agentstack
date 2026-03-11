import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_14_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.regression
def test_page_14_title(page):
    """Verify the page title."""
    page.goto(PAGE_14_URL)
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))


@pytest.mark.regression
def test_page_14_search_team(page):
    """Search for a hockey team and verify the results."""
    page.goto(PAGE_14_URL)
    page.locator("#q").first.fill("Kings")
    page.locator("input.btn.btn-primary").first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text(
        "Los Angeles Kings", timeout=10000
    )


@pytest.mark.regression
def test_page_14_pagination(page):
    """Navigate to page 5 and verify the URL."""
    page.goto(PAGE_14_URL)
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[6]/a[1]').first.click()  # Click page 5
    expect(page).to_have_url(re.compile(r".*page_num=5"), timeout=10000)


@pytest.mark.regression
def test_page_14_change_per_page(page):
    """Change the number of items per page and verify the URL updates."""
    page.goto(PAGE_14_URL)
    page.locator("#per_page").first.select_option("50")
    expect(page).to_have_url(re.compile(r".*per_page=50"), timeout=10000)
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[51]/td[1]').first).to_be_visible(
        timeout=15000
    )


@pytest.mark.smoke
def test_page_14_element_visibility(page):
    """Verify key elements on the page are visible."""
    page.goto(PAGE_14_URL)
    expect(page.locator('h1').first).to_be_visible(timeout=15000)
    expect(page.locator('#q').first).to_be_visible(timeout=15000)
    expect(page.locator('input.btn.btn-primary').first).to_be_visible(timeout=15000)
    expect(page.locator('#per_page').first).to_be_visible(timeout=15000)