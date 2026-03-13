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
def test_page_2_navigation(page):
    page.goto(PAGE_2_F871_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(PAGE_2_F871_URL)
    expect(page.locator("#logo").first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_2_complete_web_form_elements(page):
    page.goto(PAGE_2_F871_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("xpath=//a[contains(text(), ")").click()
    expect(page.locator("h1").first).to_be_visible(timeout=10000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[1]/strong[1]").first).to_be_visible(timeout=10000)
    expect(page.locator("#first-name").first).to_be_visible(timeout=10000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[2]/strong[1]").first).to_be_visible(timeout=10000)
    expect(page.locator("#last-name").first).to_be_visible(timeout=10000)
    expect(page.locator("xpath=/html/body/div[1]/form[1]/div[1]/div[3]/strong[1]").first).to_be_visible(timeout=10000)
    expect(page.locator("#job-title").first).to_be_visible(timeout=10000)


@pytest.mark.regression
def test_page_2_fill_and_submit_form(page):
    page.goto(PAGE_2_F871_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator("xpath=//a[contains(text(), ")").click()
    page.locator("#first-name").first.fill("John")
    page.locator("#last-name").first.fill("Doe")
    page.locator("#job-title").first.fill("Engineer")
    page.locator("#radio-button-1").first.check()
    page.locator("#checkbox-1").first.check()
    page.locator("#select-menu").first.select_option("2")
    page.locator("#datepicker").first.fill("01/01/2023")
    page.locator("a.btn.btn-lg.btn-primary").first.click()


@pytest.mark.regression
def test_page_2_check_links(page):
    page.goto(PAGE_2_F871_URL, timeout=60000)
    page.wait_for_load_state('networkidle')

    page.locator("#navbarDropdownMenuLink").first.click()

    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)
    expect(page.locator("xpath=//a[contains(text(), ")")).to_be_visible(timeout=10000)