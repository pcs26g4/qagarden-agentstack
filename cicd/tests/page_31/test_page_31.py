import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_31_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.regression
def test_page_check_heading_visibility(page):
    page.goto(PAGE_31_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=10000)


@pytest.mark.smoke
def test_page_check_sandbox_link(page):
    page.goto(PAGE_31_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#nav-sandbox').first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_search_for_teams(page):
    page.goto(PAGE_31_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("Flyers")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[10]/td[1]').first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_check_pagination(page):
    page.goto(PAGE_31_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[21]/a[1]/strong[1]').first).to_be_visible(timeout=10000)