import os
import sys
from pathlib import Path
import json
import logging
import httpx
import re
import time
import random
import shutil
import stat
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv

# Optional: Try-import for LLM providers to avoid crash if missing
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# =========================
# ENV SETUP
# =========================
# Load .env from the project root (qagarden-backend/) where API keys are stored.
# We must search explicitly because this script's CWD may be playwright_gen/ which
# has no .env of its own.
_THIS_DIR = Path(__file__).resolve().parent
for _dotenv_candidate in [
    _THIS_DIR / ".env",                           # playwright_gen/.env
    _THIS_DIR.parent / ".env",                    # qagarden-backend/.env
    _THIS_DIR.parent / "qagarden_agents" / ".env", # AgentStack wrapper .env
    _THIS_DIR.parent.parent / ".env",             # one level above (fallback)
]:
    if _dotenv_candidate.exists():
        load_dotenv(dotenv_path=_dotenv_candidate, override=True) # Override to pick up local changes
        print(f"Loaded .env from: {_dotenv_candidate}")
        break
else:
    load_dotenv()  # Last resort

# Multi-Provider Configuration
XAI_KEY = os.getenv("XAI_API_KEY")
XAI_MODEL = os.getenv("XAI_MODEL", "grok-beta")
XAI_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

GROQ_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

OR_KEY = os.getenv("OPENROUTER_API_KEY")
OR_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-405b-instruct") # Default to strong model
OR_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

HF_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

if not XAI_KEY and not GROQ_KEY and not OR_KEY and not HF_KEY and not GEMINI_KEY:
    raise RuntimeError("No API keys found. Set GEMINI_API_KEY, XAI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, or HUGGINGFACE_API_KEY in .env")

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger(__name__)

# =========================
# CONFIG
# =========================
PROJECT_ROOT = Path(__file__).resolve().parent
PROMPT_FILE = PROJECT_ROOT / "prompt.txt"

CONFIG_DIR = PROJECT_ROOT / "config"
TESTCASES_DIR = PROJECT_ROOT / "testcases"
OUTPUT_TESTS_DIR = PROJECT_ROOT / "tests"

OUTPUT_TESTS_DIR.mkdir(exist_ok=True)

# =========================
# UTILITIES
# =========================
def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def inject_pythonpath(code: str) -> str:
    injection = (
        "import sys\n"
        "import re\n"
        "import pytest\n"
        "from playwright.sync_api import sync_playwright, expect\n"
        "from pathlib import Path\n"
        "ROOT_DIR = Path(__file__).resolve().parent.parent.parent\n"
        "sys.path.insert(0, str(ROOT_DIR))\n\n"
    )
    return injection + code


# =========================
# LLM INTEGRATION (MULTI-PROVIDER)
# =========================
# Groq Key Pool
GROQ_KEYS = [
    key.strip() 
    for key in os.getenv("GROQ_API_KEYS", "").split(",") 
    if key.strip() and "gsk_" in key
]
if not GROQ_KEYS and os.getenv("GROQ_API_KEY"):
    GROQ_KEYS = [os.getenv("GROQ_API_KEY")]

def call_llm(prompt: str) -> str:
    """Call LLM with Gemini -> Groq -> OpenRouter -> Ollama -> Hugging Face fallback with retries."""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # 1. Try Gemini (Primary per user request)
            if GEMINI_KEY:
                try:
                    return _call_gemini(prompt)
                except Exception as e:
                    logger.warning(f"Gemini failed (Attempt {attempt+1}/{max_retries}): {e}")

            # 2. Try Grok (xAI)
            if XAI_KEY and "your_" not in XAI_KEY:
                try:
                    return _call_xai(prompt)
                except Exception as e:
                    logger.warning(f"Grok (xAI) failed (Attempt {attempt+1}/{max_retries}): {e}")

            # 3. Try Groq (with Rotation)
            if GROQ_KEYS:
                # Rotate keys based on attempt number + random offset to distribute load
                key_index = (attempt + random.randint(0, len(GROQ_KEYS))) % len(GROQ_KEYS)
                current_key = GROQ_KEYS[key_index]
                try:
                    return _call_groq(prompt, current_key)
                except Exception as e:
                    logger.warning(f"Groq failed (Key {key_index+1}/{len(GROQ_KEYS)}): {e}")

            # 4. Try OpenRouter
            if OR_KEY:
                try:
                    return _call_openrouter(prompt)
                except Exception as e:
                    logger.warning(f"OpenRouter failed (Attempt {attempt+1}/{max_retries}): {e}")
            
            # 5. Try Ollama (Local)
            if OLLAMA_URL:
                try:
                    return _call_ollama(prompt)
                except Exception as e:
                    logger.warning(f"Ollama failed (Attempt {attempt+1}/{max_retries}): {e}")

            # 6. Try Hugging Face
            if HF_KEY:
                try:
                    return _call_huggingface(prompt)
                except Exception as e:
                    logger.error(f"Hugging Face failed (Attempt {attempt+1}/{max_retries}): {e}")
            
            # If all failed, wait before retry
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                
        except Exception as catastrophic:
            logger.error(f"Catastrophic error in LLM call: {catastrophic}")
            
    raise RuntimeError("All LLM providers failed after retries")

def _call_gemini(prompt: str) -> str:
    if not genai:
        raise ImportError("google-generativeai package not installed")
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text

def _call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    with httpx.Client(timeout=60) as client:
        response = client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

def _call_xai(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {XAI_KEY}",
        "Content-Type": "application/json"
    }
    # xAI API is OpenAI compatible. 
    # Ensure model name is correct. Standard is "grok-beta" or "grok-2-latest"??
    # 400 usually means invalid JSON or invalid model.
    # Let's try a safer payload and model.
    model = XAI_MODEL if XAI_MODEL else "grok-beta"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert Playwright automation engineer. Output ONLY code."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "stream": False 
    }
    
    with httpx.Client(timeout=60) as client:
        response = client.post(f"{XAI_URL}/chat/completions", headers=headers, json=payload)
        # Log response if it fails for debugging
        if response.status_code == 400:
             logger.error(f"xAI 400 Error Response: {response.text}")
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']


def _call_groq(prompt: str, api_key: str) -> str:
    # Rate limit handling for Groq (very sensitive on free tier)
    import time
    time.sleep(1) # Small delay
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert Playwright automation engineer. Output ONLY code."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    with httpx.Client(timeout=60) as client:
        response = client.post(f"{GROQ_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

def _call_openrouter(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://qa-garden.com",
        "X-Title": "QA Garden Playwright Gen"
    }
    payload = {
        "model": OR_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    with httpx.Client(timeout=60) as client:
        response = client.post(f"{OR_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

def _call_huggingface(prompt: str) -> str:
    api_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_KEY}"}
    
    # Instruction format
    formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    
    payload = {
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": 4096,
            "temperature": 0.1,
            "return_full_text": False
        }
    }
    
    with httpx.Client(timeout=60) as client:
        response = client.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '')
        return ""

def extract_code_only(text: str) -> str:
    if "```python" in text:
        return text.split("```python")[1].split("```")[0].strip()
    if "```" in text:
        return text.split("```")[1].split("```")[0].strip()

    stripped = text.strip()
    if stripped.startswith(("import ", "from ", "def ", "class ")):
        return stripped

    raise RuntimeError("Could not extract Python code from LLM response")

# =========================
# PAGE DISCOVERY
# =========================
def infer_pages() -> list:
    """
    Three-tier page discovery - works for any website:
    1. Classic: testcases JSON + matching locators JSON (original behavior)
    2. urls.py: pages listed in auto-generated config/urls.py (set by orchestrator)
    3. Locators-only: any page with a locators JSON (fallback)
    """
    pages: list = []

    # Tier 1 - classic match
    for tc_file in TESTCASES_DIR.glob("*_testcases.json"):
        page = tc_file.stem.replace("_testcases", "")
        if (CONFIG_DIR / f"{page}_locators.json").exists() or \
           (CONFIG_DIR / f"{page}_locators.py").exists():
            if page not in pages:
                pages.append(page)

    # Tier 2 - pages declared in urls.py (auto-generated by orchestrator)
    urls_py = CONFIG_DIR / "urls.py"
    if urls_py.exists():
        content = urls_py.read_text(encoding="utf-8")
        for m in re.finditer(r'^(PAGE_[A-Z0-9_]+)_URL\s*=', content, re.MULTILINE):
            page_id = m.group(1).lower()
            if page_id not in pages:
                # Check for hashed/unhashed overlap (e.g. page_1 vs page_1_cdbd)
                # If we have page_1_cdbd, don't add page_1
                is_duplicate = False
                for existing in pages:
                    if existing.startswith(page_id + "_") or page_id.startswith(existing + "_"):
                        is_duplicate = True
                        break
                if not is_duplicate:
                    pages.append(page_id)

    # Tier 3 - locators-only fallback
    for loc_file in CONFIG_DIR.glob("*_locators.json"):
        page = loc_file.stem.replace("_locators", "")
        if page not in pages:
            is_duplicate = False
            for existing in pages:
                if existing.startswith(page + "_") or page.startswith(existing + "_"):
                    is_duplicate = True
                    break
            if not is_duplicate:
                pages.append(page)

    return sorted(pages)

# =========================
# GENERATE config/urls.py
# =========================
def generate_urls_config():
    urls_path = CONFIG_DIR / "urls.py"
    target_url = None

    # --- STEP 1: Read ALL existing URL variables from the current urls.py ---
    # The orchestrator writes a complete urls.py with PAGE_1_URL ... PAGE_N_URL.
    # We must NOT overwrite those - only extend/merge.
    existing_vars: dict = {}
    if urls_path.exists():
        content = urls_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                var, _, val = line.partition("=")
                var = var.strip()
                val = val.strip().strip('"').strip("'")
                if var:
                    existing_vars[var] = val
                if var == "BASE_URL":
                    target_url = val

    # --- STEP 2: Fallback target URL ---
    if not target_url:
        crawler_env_path = PROJECT_ROOT.parent / "crawler" / ".env"
        if crawler_env_path.exists():
            try:
                with open(crawler_env_path, 'r') as f:
                    for line in f:
                        if line.startswith("TARGET_URL="):
                            target_url = line.split("=")[1].strip().strip('"').strip("'")
                            break
            except: pass

    if not target_url:
        target_url = "https://example.com"

    if not target_url.endswith("/"):
        target_url += "/"

    existing_vars["BASE_URL"] = target_url

    # --- STEP 3: Add missing PAGE_*_URL entries from locator files ---
    all_pages = infer_pages()
    for page in all_pages:
        var_name = page.upper().replace(" ", "_").replace("-", "_") + "_URL"
        if var_name in existing_vars:
            continue  # Already exists -- do not overwrite

        page_url = None

        # Try testcases file first
        tc_path = TESTCASES_DIR / f"{page}_testcases.json"
        if tc_path.exists():
            try:
                with open(tc_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    page_url = data.get("url") or data.get("pageUrl")
                    if not page_url:
                        page_data = data.get(page)
                        if isinstance(page_data, dict):
                            page_url = page_data.get("url")
            except: pass

        # Try locators file for URL
        if not page_url:
            loc_path = CONFIG_DIR / f"{page}_locators.json"
            if loc_path.exists():
                try:
                    with open(loc_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        page_url = data.get("url") or data.get("page_url")
                except: pass

        if not page_url:
            page_url = target_url  # Fallback to base

        existing_vars[var_name] = page_url

    # --- STEP 4: Add legacy fallbacks if missing ---
    for fallback_var in ["LOGIN_URL", "SIGNUP_URL", "WELCOME_URL"]:
        if fallback_var not in existing_vars:
            existing_vars[fallback_var] = target_url

    # --- STEP 5: Write merged urls.py ---
    lines = ["# Page URLs for Playwright tests"]
    # BASE_URL first
    lines.append(f'BASE_URL = "{existing_vars.pop("BASE_URL", target_url)}"')
    lines.append("")
    # All PAGE_* vars sorted
    for var in sorted(k for k in existing_vars if k.startswith("PAGE_")):
        lines.append(f'{var} = "{existing_vars[var]}"')
    # Remaining vars (LOGIN_URL etc.)
    for var, val in existing_vars.items():
        if not var.startswith("PAGE_"):
            lines.append(f'{var} = "{val}"')

    write_file(urls_path, "\n".join(lines).strip())
    page_url_count = sum(1 for k in existing_vars if k.startswith("PAGE_"))
    logger.info(f"config/urls.py generated/updated with {page_url_count} page URLs")


# =========================
# GENERATE conftest.py
# =========================
def generate_conftest():
    content = """
import sys
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright, expect
import logging
import datetime
import time
import threading

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        # v25.0: Added args to allow launch on restricted environments like EC2/Ubuntu
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        yield browser
        browser.close()

@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()

@pytest.fixture
def authenticated_page(context):
    \"\"\"Generic authenticated page fixture. Fallback to simple page if no LOGIN_URL.\"\"\"
    page = context.new_page()
    try:
        from config.urls import LOGIN_URL
        page.goto(LOGIN_URL, timeout=60000)
    except (ImportError, AttributeError):
        # Fallback for sites without explicit login
        pass
    
    page.wait_for_load_state("networkidle")
    yield page
    page.close()

# --- TRIAGE REPORTING HOOK ---
import os
import requests
import base64

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    '''
    Hook to capture test failures and send them to the Triage Engine.
    Includes screenshot and source code context.
    '''
    # Execute all other hooks to obtain the report object
    outcome = yield
    report = outcome.get_result()
    
    # We only care about failures during call (execution) or setup
    if report.when == "call" and report.failed:
        try:
            # 1. Capture Screenshot
            screenshot_b64 = None
            if "page" in item.funcargs:
                page = item.funcargs["page"]
                screenshot_bytes = page.screenshot(type="jpeg", quality=50)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            elif "authenticated_page" in item.funcargs:
                page = item.funcargs["authenticated_page"]
                screenshot_bytes = page.screenshot(type="jpeg", quality=50)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            # 2. Get Source Code
            source_code = ""
            try:
                # Read the test file
                with open(item.fspath, "r", encoding="utf-8") as f:
                    source_code = f.read()
            except Exception as e:
                source_code = f"Could not read source: {e}"

            # 3. Check for Run ID
            run_id = os.environ.get("TRIAGE_RUN_ID", "default_manual_run")

            # 4. Payload for Triage Engine
            payload = {
                "run_id": run_id,
                "test_name": item.nodeid,
                "file_path": str(item.fspath),
                "error_message": str(report.longrepr),
                "stack_trace": str(report.longrepr),  # Pytest longrepr contains trace
                "source_code": source_code,
                "screenshot": screenshot_b64,
                "llm_model": "gemini-pro", # Default model for Triage analysis
                "bert_url": "", # BERT disabled (using pattern matching fallback) to avoid 404s
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # 5. Send to Triage Engine (Fire and Forget to avoid blocking)
            def send_report():
                try:
                    requests.post("http://localhost:8004/api/triage", json=payload, timeout=2)
                except Exception as e:
                    print(f"Failed to report to Triage: {e}")

            threading.Thread(target=send_report).start()
            
        except Exception as e:
            print(f"Error in Triage Hook: {e}")
"""
    write_file(OUTPUT_TESTS_DIR / "conftest.py", content.strip())
    print("conftest.py generated")

# =========================
# GENERATE CI/CD METADATA
# =========================
def generate_requirements():
    content = """
pytest==8.0.0
pytest-playwright==0.4.4
pytest-xdist==3.5.0
requests==2.31.0
python-dotenv==1.0.1
"""
    req_path = PROJECT_ROOT / "requirements.txt"
    write_file(req_path, content.strip())
    print("requirements.txt generated for CI/CD")

def generate_github_actions():
    content = """
name: QA Garden Automated Pipeline
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Ensure browsers are installed
      run: python -m playwright install --with-deps chromium
    - name: Run Playwright tests
      run: pytest tests/ -v -n auto
      env:
        # Pass secrets dynamically through Action Environment Variables
        LOGIN_PASSWORD: ${{ secrets.LOGIN_PASSWORD }}
    - uses: actions/upload-artifact@v4
      if: always()
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 7
"""
    yml_path = PROJECT_ROOT / ".github" / "workflows" / "playwright.yml"
    write_file(yml_path, content.strip())
    print(".github/workflows/playwright.yml generated for GitHub Actions")

# =========================
# GENERATE TESTS PER PAGE
# =========================

def generate_page_tests(page: str, base_prompt: str):
    locator_file = CONFIG_DIR / f"{page}_locators.json"
    testcase_file = TESTCASES_DIR / f"{page}_testcases.json"

    if not locator_file.exists():
        print(f"Skipping {page} (no locators file found at {locator_file})")
        return

    locator_json = locator_file.read_text(encoding="utf-8")

    # Filter locators to avoid token bloat
    try:
        if len(locator_json) > 50000:
            print(f"Warning: {page} locators file is large ({len(locator_json)} chars). Proceeding with truncation risk.")
    except Exception as e:
        print(f"Error processing JSON for {page}: {e}")

    # Build testcases section - use file if available, otherwise ask LLM to infer from locators
    if testcase_file.exists():
        testcase_json = testcase_file.read_text(encoding="utf-8")
        testcase_section = f"TEST CASES JSON:\n{testcase_json}"
    else:
        # Locators-only mode: let the LLM figure out the test cases
        testcase_section = (
            "TEST CASES JSON: (Not provided - infer meaningful test cases from the locators above)\n"
            "Generate 3-5 practical test cases covering: navigation, form submission (if applicable),\n"
            "element visibility, and interactive element functionality."
        )

    url_var = page.upper().replace(" ", "_").replace("-", "_") + "_URL"

    page_prompt = f"""
{base_prompt}

PAGE: {page}
URL_VARIABLE: {url_var}

LOCATORS JSON:
{locator_json}

{testcase_section}

Generate a complete pytest Playwright test file.
Output ONLY valid Python code.
"""

    print(f"Generating tests for {page}...")
    try:
        raw_output = call_llm(page_prompt)
        test_code = extract_code_only(raw_output)
        test_code = inject_pythonpath(test_code)
        
        # Post-processing to fix common LLM mistakes (camelCase -> snake_case)
        test_code = test_code.replace(".getByRole(", ".get_by_role(")
        test_code = test_code.replace(".getByText(", ".get_by_text(")
        test_code = test_code.replace(".getByLabel(", ".get_by_label(")
        test_code = test_code.replace(".getByPlaceholder(", ".get_by_placeholder(")
        test_code = test_code.replace(".getByTestId(", ".get_by_test_id(")
        test_code = test_code.replace(".getByTitle(", ".get_by_title(")
        test_code = test_code.replace(".getByAltText(", ".get_by_alt_text(")
        
        # New: Sanitize Tailwind CSS selectors (Escape colons, brackets, etc.)
        def sanitize_selectors(code):
            patterns = [
                r"locator\(['\"](.+?)['\"]\)",
                r"expect\(page\)\.to_have_selector\(['\"](.+?)['\"]\)",
                r"expect\(page\)\.to_be_visible\(['\"](.+?)['\"]\)",
                r"page\.click\(['\"](.+?)['\"]\)",
                r"page\.fill\(['\"](.+?)['\"]\)"
            ]
            
            for p in patterns:
                def escape_match(m):
                    s = m.group(1)
                    # v18.1: Skip non-CSS selectors
                    if any(s.startswith(prefix) for prefix in ["xpath=", "//", "text=", "id=", "css=", "point("]):
                        return m.group(0)
                    # Escape special Tailwind/CSS characters
                    for ch in [':', '!', '[', ']', '&', '=', '/', '@']:
                        s = s.replace(ch, f"\\{ch}")
                    return m.group(0).replace(m.group(1), s)
                
                code = re.sub(p, escape_match, code)
            return code
        
        test_code = sanitize_selectors(test_code)
        
        # Ensure locators are not ambiguous by appending .first if no nth/first/last already present
        def ensure_single_element(code):
            # Include assertions as well to prevent strict mode violations
            methods = ["click", "fill", "hover", "select_option", "check", "uncheck", "to_be_visible", "to_be_hidden", "to_have_text", "to_contain_text", "to_have_value", "to_be_enabled"]
            for method in methods:
                # 1. Standard locator usage: page.locator(...).click(
                pattern = rf"(page\.(get_by_[a-z_]+|locator)\([^)]+\))\.{method}\("
                def add_first(m):
                    expr = m.group(1)
                    if not any(x in expr for x in [".nth(", ".first", ".last"]):
                        return f"{expr}.first.{method}("
                    return m.group(0)
                code = re.sub(pattern, add_first, code)
                
                # 2. Expect case: expect(page.locator(...)).to_be_visible()
                expect_pattern = rf"expect\(\s*(page\.(get_by_[a-z_]+|locator)\([^)]+\))\s*\)\.{method}\("
                def add_first_expect(m):
                    expr = m.group(1)
                    if not any(x in expr for x in [".nth(", ".first", ".last"]):
                        return f"expect({expr}.first).{method}("
                    return m.group(0)
                code = re.sub(expect_pattern, add_first_expect, code)

            # 3. Special case for to_have_count(1) or similar if the LLM generated to_be_visible for a list
            # We already handle it by adding .first to visible checks.
            return code
        
        test_code = ensure_single_element(test_code)

        test_dir = OUTPUT_TESTS_DIR / page
        out_path = test_dir / f"test_{page}.py"
        write_file(out_path, test_code)

        print(f"Generated {out_path}")
    except Exception as e:
        print(f"Failed to generate tests for {page}: {e}")


# =========================
# MAIN
# =========================
def main():
    print("Starting LLM-based test generation (Multi-Provider: OpenRouter -> Hugging Face)")

    # CLEAR output directory to remove stale tests from previous runs
    if OUTPUT_TESTS_DIR.exists():
        try:
            # Robust cleanup for Windows/Linux
            for item in OUTPUT_TESTS_DIR.iterdir():
                try:
                    if item.is_file() or item.is_symlink():
                        item.chmod(stat.S_IWRITE)
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                except Exception as e:
                    logger.warning(f"Could not delete {item}: {e}")
            logger.info(f"Cleared previous tests at {OUTPUT_TESTS_DIR}")
        except Exception as e:
            logger.warning(f"Could not clear tests directory: {e}")
    
    OUTPUT_TESTS_DIR.mkdir(parents=True, exist_ok=True)

    if not PROMPT_FILE.exists():
        logger.warning(f"prompt.txt not found at {PROMPT_FILE}, creating default.")
        write_file(PROMPT_FILE, "You are an expert Playwright automation engineer. Generate robust test cases.")

    base_prompt = read_file(PROMPT_FILE)

    pages = infer_pages()
    if not pages:
        print("No valid pages detected. Check:")
        print(f"  - {TESTCASES_DIR} for *_testcases.json files")
        print(f"  - {CONFIG_DIR} for *_locators.json or *_locators.py files")
        print(f"  - {CONFIG_DIR / 'urls.py'} for PAGE_*_URL entries")
        print("Exiting gracefully - no tests generated.")
        return
    
    print(f"Discovered {len(pages)} pages: {pages}")

    generate_urls_config()
    generate_conftest()
    generate_requirements()
    generate_github_actions()

    # Run test generation in parallel
    print(f"Generating tests for {len(pages)} pages in parallel...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(generate_page_tests, page, base_prompt): page for page in pages}
        
        for future in concurrent.futures.as_completed(futures):
            page = futures[future]
            try:
                future.result()
            except Exception as exc:
                print(f"Page {page} generated an exception: {exc}")

    print("Test generation completed successfully")

if __name__ == "__main__":
    main()