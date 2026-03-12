import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import PAGE_2_F871_URL
from playwright.sync_api import expect
import re
import pytest


@pytest.mark.smoke
def test_page_2_link_formy_visible(page):
    page.goto(PAGE_2_F871_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator("#logo").first).to_be_visible(timeout=15000)


@pytest.mark.smoke
def test_page_2_complete_web_form_elements(page):
    page.goto(PAGE_2_F871_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    page.locator("xpath=//a[contains(text(), ")
    expect(page.locator("h1").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[1]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#first-name").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[2]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#last-name").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[3]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#job-title").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[4]/div[1]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#radio-button-1").first).to_be_visible(timeout=15000)
    expect(page.locator("#radio-button-2").first).to_be_visible(timeout=15000)
    expect(page.locator("#radio-button-3").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[5]/div[1]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#checkbox-1").first).to_be_visible(timeout=15000)
    expect(page.locator("#checkbox-2").first).to_be_visible(timeout=15000)
    expect(page.locator("#checkbox-3").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[6]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#select-menu").first).to_be_visible(timeout=15000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[7]/strong[1]").first).to_be_visible(timeout=15000)
    expect(page.locator("#datepicker").first).to_be_visible(timeout=15000)
    expect(page.locator("a.btn.btn-lg.btn-primary").first).to_be_visible(timeout=15000)


@pytest.mark.regression
def test_page_2_complete_web_form_interaction(page):
    page.goto(PAGE_2_F871_URL, timeout=60000)
    page.wait_for_load_state('networkidle')

    page.locator("#first-name").first.fill("John")
    page.locator("#last-name").first.fill("Doe")
    page.locator("#job-title").first.fill("Engineer")
    page.locator("#radio-button-1").first.check()
    page.locator("#checkbox-1").first.check()
    page.locator("#select-menu").first.select_option("1")
    page.locator("#datepicker").first.fill("01/01/2023")

    expect(page.locator("#first-name").first).to_have_value("John", timeout=10000)
    expect(page.locator("#last-name").first).to_have_value("Doe", timeout=10000)
    expect(page.locator("#job-title").first).to_have_value("Engineer", timeout=10000)
    expect(page.locator("#radio-button-1")).is_checked()
    expect(page.locator("#checkbox-1")).is_checked()
    expect(page.locator("#select-menu").first).to_have_value("1", timeout=10000)
    expect(page.locator("#datepicker").first).to_have_value("01/01/2023", timeout=10000)


@pytest.mark.regression
def test_page_2_navigation_links(page):
    page.goto(PAGE_2_F871_URL, timeout=60000)
    page.wait_for_load_state('networkidle')

    page.locator("#navbarDropdownMenuLink").first.click()

    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())
    expect(page.locator("xpath=//a[contains(text(), ")").is_visible())