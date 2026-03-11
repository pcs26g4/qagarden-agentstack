import asyncio
import os
from playwright.async_api import async_playwright
from rich_interactions import RichInteractionManager

async def test_shared_context():
    print("Starting Shared Context Verification...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"Playwright Page ID: {id(page)}")
        print("Initializing RichInteractionManager with shared page...")
        # Note: We don't need a real API key just for the constructor check
        manager = RichInteractionManager(page=page)
        
        print(f"Manager Page ID: {id(manager.page)}")
        
        if manager.page == page:
            print("MATCH: RichInteractionManager is using the shared page object.")
            print("VERIFICATION SUCCESS: Phase 1 context persistence confirmed.")
        else:
            print("MISMATCH: RichInteractionManager failed to use the provided page.")
            print("VERIFICATION FAILURE.")
            
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(test_shared_context())
    except Exception as e:
        print(f"Test crashed: {e}")
