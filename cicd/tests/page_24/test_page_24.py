import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_24_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_navigation(page):
    page.goto(PAGE_24_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#site-nav").first).to_be_visible(timeout=15000)
    expect(page.locator("h1").first).to_be_visible(timeout=15000)
    page.locator('a.nav-link').nth(0).click()
    page.wait_for_load_state('networkidle')
    expect(page.locator("h1").first).to_be_visible(timeout=15000)
    expect(page).to_have_url("http://www.scrapethissite.com/")

@pytest.mark.regression
def test_search_for_teams(page):
    page.goto(PAGE_24_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('#q').first.fill("New York")
    page.locator('input.btn.btn-primary').first.click()
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("New York Islanders", timeout=10000)
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[1]').first).to_have_text("New York Rangers", timeout=10000)

@pytest.mark.regression
def test_pagination_navigation(page):
    page.goto(PAGE_24_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[14]/a[1]/strong[1]').first).to_have_text("13")
    page.locator('xpath=//*[contains(@aria-label, "Next")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url("http://www.scrapethissite.com/pages/forms/?page_num=14")

@pytest.mark.regression
def test_lessons_link(page):
    page.goto(PAGE_24_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//a[contains(text(), "8 video lessons")]').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url("http://www.scrapethissite.com/lessons/")

@pytest.mark.smoke
def test_faq_link(page):
    page.goto(PAGE_24_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.nav-link').nth(4).click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url("http://www.scrapethissite.com/faq/")