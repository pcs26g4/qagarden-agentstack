import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_23_URL
from playwright.sync_api import expect
import re
import pytest

@pytest.mark.smoke
def test_page_23_title(page):
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_title("Hockey Teams: Forms, Searching and Pagination | Scrape This Site | A public sandbox for learning web scraping")

@pytest.mark.regression
def test_page_23_search_team(page):
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    search_term = "Vancouver Canucks"
    page.locator("#q").first.fill(search_term)
    page.locator('input.btn.btn-primary').first.click()
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[2]/td[1]').first).to_have_text(search_term)

@pytest.mark.regression
def test_page_23_check_team_data(page):
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[1]').first).to_have_text("Washington Capitals")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[2]').first).to_have_text("1999")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[3]').first).to_have_text("44")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[4]').first).to_have_text("24")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[5]').first).to_have_text("2")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[6]').first).to_have_text("0.537")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[7]').first).to_have_text("227")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[8]').first).to_have_text("194")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/table[1]/tbody[1]/tr[3]/td[9]').first).to_have_text("33")

@pytest.mark.regression
def test_page_23_check_pagination_element_visibility(page):
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('xpath=//*[contains(@aria-label, "Previous")]')).to_be_visible()
    expect(page.locator('xpath=//*[contains(@aria-label, "Next")]')).to_be_visible()

@pytest.mark.regression
def test_page_23_select_50_per_page(page):
    page.goto(PAGE_23_URL)
    page.wait_for_load_state('networkidle')
    page.locator("#per_page").first.select_option("50")
    expect(page.locator('xpath=//*[@id="hockey"]/div[1]/div[1]/div[1]/h1[1]/small[1]').first).to_have_text("25 items") #Expect the count to stay the same due to total teams being only 25.