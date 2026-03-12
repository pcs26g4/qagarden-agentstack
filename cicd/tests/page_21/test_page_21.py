import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_21_URL
from playwright.sync_api import expect
import pytest

@pytest.mark.regression
def test_page_21_title(page):
    page.goto(PAGE_21_URL)
    expect(page).to_have_title("Hockey Teams: Forms, Searching and Pagination | Scrape This Site | A public sandbox for learning web scraping")

@pytest.mark.regression
def test_page_21_search_team(page):
    page.goto(PAGE_21_URL)
    page.locator("#q").first.fill("Dallas")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[6]/td[1]').first).to_contain_text("Dallas Stars")

@pytest.mark.regression
def test_page_21_navigate_to_page_3(page):
    page.goto(PAGE_21_URL)
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[4]/a[1]').first.click()
    expect(page).to_have_url("http://www.scrapethissite.com/pages/forms/?page_num=3")

@pytest.mark.regression
def test_page_21_change_per_page_to_50(page):
    page.goto(PAGE_21_URL)
    page.locator("#per_page").first.select_option("50")
    expect(page.locator("#per_page").first).to_have_value("50")

@pytest.mark.regression
def test_page_21_elements_visible(page):
    page.goto(PAGE_21_URL)
    expect(page.locator('h1').first).to_be_visible()
    expect(page.locator('#q').first).to_be_visible()
    expect(page.locator('input.btn.btn-primary').first).to_be_visible()