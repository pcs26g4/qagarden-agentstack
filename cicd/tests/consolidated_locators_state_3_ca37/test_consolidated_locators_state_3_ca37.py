import sys
import re
import pytest
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.urls import CONSOLIDATED_LOCATORS_STATE_3_CA37_URL
from playwright.sync_api import expect
import re

def test_TC_ContentVerification_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#preheader').first).to_have_text("A course to help you", timeout=10000)
    expect(page.locator('#header').first).to_have_text("SCRAPE ANY WEBSITE", timeout=10000)
    expect(page.locator('#postheader').first).to_have_text("Learn how to build your own web scrapers and\nstart collecting the data you need.", timeout=10000)
    expect(page.locator('#subhero').first).to_have_text("Build your first scraper in minutes!", timeout=10000)
    expect(page.locator('#video').first).to_have_text("Learn more about the course:", timeout=10000)
    expect(page.locator('#footer-content').first).to_have_text("\u00a9 Hartley Brody", timeout=10000)

@pytest.mark.smoke
def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL, timeout=60000)
    page.wait_for_load_state('networkidle')
    page.locator('a.gumroad-button').nth(0).click()
    expect(page).to_have_url(re.compile(r"https:\/\/gum\.co\/oLpqb"))