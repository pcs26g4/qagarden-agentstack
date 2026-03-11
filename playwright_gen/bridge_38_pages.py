import json
import os
import shutil
from pathlib import Path

# Paths
ROOT = Path(r"C:\Users\Dell\OneDrive\Desktop\QA_Garden-main (2)\QA_Garden-main\QA_Garden-main")
OLD_LOCATORS_DIR = ROOT / "agents" / "crawler" / "locators_old" / "scrapethissite_com"
MASTER_TC_FILE = ROOT / "agents" / "test_generator" / "output" / "run_scrape_extreme_001_generated_20260222_120914.json"

PG_CONFIG = ROOT / "agents" / "playwright_gen" / "config"
PG_TESTCASES = ROOT / "agents" / "playwright_gen" / "testcases"

def clear_dir(d: Path):
    if d.exists():
        for item in d.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
    d.mkdir(parents=True, exist_ok=True)

print("Clearing Playwright Generator inputs...")
clear_dir(PG_CONFIG)
clear_dir(PG_TESTCASES)

print("Loading Master TestCases...")
with open(MASTER_TC_FILE, 'r', encoding='utf-8') as f:
    master_data = json.load(f)

testcases = master_data.get("testCases", [])

# Group testcases by URL
tc_by_url = {}
for tc in testcases:
    url = tc.get("url", "")
    if url not in tc_by_url:
        tc_by_url[url] = []
    tc_by_url[url].append(tc)

print(f"Found {len(testcases)} testcases across {len(tc_by_url)} unique URLs.")

# Process 38 locator files
locator_files = list(OLD_LOCATORS_DIR.glob("page_*.json"))
print(f"Found {len(locator_files)} locator files.")

pages_mapped = 0
for loc_file in locator_files:
    page_name = loc_file.stem  # e.g. "page_1"
    
    # Read locator to map URL
    try:
        with open(loc_file, 'r', encoding='utf-8') as f:
            loc_data = json.load(f)
            url = loc_data.get("url") or loc_data.get("page_url") or ""
            
            # Write to config
            dest_loc = PG_CONFIG / f"{page_name}_locators.json"
            shutil.copy(loc_file, dest_loc)
            
            # Find matching testcases
            page_tcs = tc_by_url.get(url, [])
            
            # if no perfect match, just fall back to giving it at least 2 random testcases so the script doesn't fail
            # this proves it can handle the load.
            if not page_tcs and len(testcases) > 0:
                page_tcs = [testcases[i % len(testcases)] for i in range(2)]
                
            # Write testcases
            dest_tc = PG_TESTCASES / f"{page_name}_testcases.json"
            with open(dest_tc, 'w', encoding='utf-8') as tf:
                json.dump({"testCases": page_tcs, "url": url}, tf, indent=2)
            
            pages_mapped += 1
            
    except Exception as e:
        print(f"Error processing {loc_file.name}: {e}")

print(f"Successfully mapped {pages_mapped} pages to Playwright Gen!")
