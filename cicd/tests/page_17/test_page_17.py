import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_17_URL
from playwright.sync_api import expect
import pytest


@pytest.mark.regression
def test_page_17_title(page):
    page.goto(PAGE_17_URL)
    expect(page).to_have_title("Hockey Teams: Forms, Searching and Pagination | Scrape This Site | A public sandbox for learning web scraping")


@pytest.mark.smoke
def test_page_17_navigation_to_page_1(page):
    page.goto(PAGE_17_URL)
    page.locator('xpath=//*[contains(@aria-label, "Previous")]').click()
    expect(page).to_have_url("http://www.scrapethissite.com/pages/forms/?page_num=5")


@pytest.mark.regression
def test_page_17_search_for_team(page):
    page.goto(PAGE_17_URL)
    page.locator('#q').first.fill("Dallas Stars")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_be_visible()


@pytest.mark.regression
def test_page_17_check_pagination_link_visibility(page):
    page.goto(PAGE_17_URL)
    expect(page.locator('xpath=//*[contains(@aria-label, "Next")]')).to_be_visible()
    expect(page.locator('xpath=//*[contains(@aria-label, "Previous")]')).to_be_visible()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[7]/a[1]/strong[1]').first).to_be_visible()


@pytest.mark.regression
def test_page_17_select_per_page_option(page):
    page.goto(PAGE_17_URL)
    page.locator('#per_page').first.select_option("50")
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//*[@id="per_page"]/option[2]').first).to_be_visible()