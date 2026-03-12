import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_33_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.smoke
def test_page_33_title(page):
    page.goto(PAGE_33_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title(re.compile(r"Hockey Teams: Forms, Searching and Pagination"))


@pytest.mark.regression
def test_page_33_search_team(page):
    page.goto(PAGE_33_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#q").first.fill("Buffalo Sabres")
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text("Buffalo Sabres")


@pytest.mark.regression
def test_page_33_check_team_data(page):
    page.goto(PAGE_33_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[2]').first).to_have_text("2010")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[3]').first).to_have_text("43")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[4]').first).to_have_text("29")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[5]').first).to_have_text("10")


@pytest.mark.regression
def test_page_33_select_per_page(page):
    page.goto(PAGE_33_URL)
    page.wait_for_load_state('networkidle')
    page.locator('#per_page').first.select_option('100')
    page.wait_for_load_state('networkidle')  # Ensure the new page loads after selection
    # Add an assertion here if the page reloads with the correct number of items
    # For example:
    # expect(page.locator('tr.team')).to_have_count(25) # Check the number of team rows
    # Note: Adjust the count to the actual number of items displayed after selection


@pytest.mark.regression
def test_page_33_navigation_to_page_3(page):
    page.goto(PAGE_33_URL)
    page.wait_for_load_state('networkidle')
    page.locator('xpath=//*[@id="hockey"]/div[1]/div[5]/div[1]/ul[1]/li[4]/a[1]').first.click()  # Navigate to page 3
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile(r".*page_num=3"))