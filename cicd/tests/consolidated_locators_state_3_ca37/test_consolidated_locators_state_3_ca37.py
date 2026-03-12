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
import pytest

@pytest.mark.smoke
def test_TC_Navigation_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    page.get_by_role('link', name='Get started now', exact=True).first.click()
    expect(page).to_have_url(re.compile(r"^https:\/\/gum\.co\/oLpqb"))

@pytest.mark.regression
def test_TC_ContentVerification_01(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#preheader').first).to_have_text('A course to help you')
    expect(page.locator('#header').first).to_have_text('SCRAPE ANY WEBSITE')
    expect(page.locator('#postheader').first).to_have_text('Learn how to build your own web scrapers and\nstart collecting the data you need.')

@pytest.mark.regression
def test_TC_ContentVerification_02(page):
    page.goto(CONSOLIDATED_LOCATORS_STATE_3_CA37_URL)
    page.wait_for_load_state('networkidle')
    expect(page.locator('#footer-content').first).to_have_text('\u00a9 Hartley Brody')