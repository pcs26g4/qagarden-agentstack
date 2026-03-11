import asyncio
import os
import re
import json
import hashlib
import sys
import logging
import tempfile
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from typing import List, Dict, Set, Optional, Any, AsyncGenerator, Tuple
import heapq
import random
import urllib.robotparser
import httpx
import requests
import xml.etree.ElementTree as ET
import psutil # For memory limit check
from bs4 import BeautifulSoup
import argparse
import shutil

from playwright.async_api import async_playwright, Page, ElementHandle 
from groq import AsyncGroq
from dotenv import load_dotenv, find_dotenv
from browser_manager import BrowserSession

from config import CrawlerConfig
from browse_ai_helper import BrowseAIHelper
from rich_interactions import RichInteractionManager
from visual_analyser import VisualAnalyser


# Force UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("qa_crawler")
logger.setLevel(logging.DEBUG)

# Helper to escape Tailwind CSS selector characters
def _sanitize_css_selector(selector: str) -> str:
    """Escape special characters in Tailwind CSS selectors for Playwright.
    Characters like ':', '!', '[', ']', '&', '=', '/' need to be escaped.
    """
    if not selector:
        return selector
    
    # v18.1: Skip sanitization for non-CSS selectors
    if any(selector.startswith(prefix) for prefix in ["xpath=", "//", "text=", "id=", "css=", "point("]):
        return selector

    # Escape each special character with a backslash
    for ch in [':', '!', '[', ']', '&', '=', '/']:
        selector = selector.replace(ch, f"\\{ch}")
    return selector

class QAGardenCrawler:
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self._validate_url(config.url)
        
        # State Graph Infrastructure (Elite Phase B)
        self.state_graph = {
            "nodes": {}, # (url, hash) -> {visited: bool, metadata: {}}
            "edges": []  # List of {from: id, to: id, action: {}}
        }
        self.current_state_id = None

        
        self.max_depth = config.max_depth
        self.max_pages = config.max_pages
        self.max_retries = config.max_retries
        self.failure_policy = config.failure_policy
        self.interaction_history: Set[str] = set()
        self.visited_states: Set[str] = set()
        self.finished_urls: Set[str] = set()
        self.visited_content_hashes: Set[str] = set()
        
        # Control Events
        self.pause_event = asyncio.Event()
        self.pause_event.set() # Start unpaused
        self.abort_event = asyncio.Event()
        
        # NEW: Site-specific locators folder
        domain = self._sanitize_path(urlparse(config.url).netloc.replace('www.', ''))
        # v6.7: Root discovery (no rotation here to prevent data loss on init)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.locators_root = os.path.join(base_dir, "locators_new")
        
        if getattr(config, 'site_specific_locators', True):
            self.locators_dir = os.path.join(self.locators_root, domain)
        else:
            self.locators_dir = self.locators_root
            
        self.debug_dir = os.path.join(self.locators_dir, "debug_screenshots")
            
        # Ensure the domain dir exists
        os.makedirs(self.locators_dir, exist_ok=True)
        
        load_dotenv(find_dotenv())
        self.groq_keys = [
            key.strip() 
            for key in os.getenv("GROQ_API_KEYS", "").split(",") 
            if key.strip() and "gsk_" in key
        ]
        self.groq_key_index = 0
        self.client = AsyncGroq(api_key=self.groq_keys[0]) if (self.groq_keys and config.use_ai) else None
        
        self.all_locators = {} # Consolidated dictionary
        self.seen_xpaths = set()
        self.seen_fingerprints = set()  # NEW: Content-based duplicate detection
        self.screen_id_counter = 0
        self.active_requests = set()
        self.seen_table_hashes = set() # NEW: Table-level deduplication
        
        # Session Handles
        self.session_handle = None
        self.browser_handle = None
        self.context_handle = None
        self.playwright_handle = None
        
        self.robots_parsers = {}
        self.consec_interaction_fails = 0 # NEW: Per-page interaction failure tracking
        
        # Stability & Reliability State
        self.nav_count = 0
        self.consecutive_failures = 0
        self.total_session_restarts = 0
        self.session_authenticated = False # Track if we just logged in
        self.is_cleaning_up = False # Guard for shutdown
        self.start_time = datetime.now()
        self.heartbeat_task = None
        self.browser_handle = None
        self.context_handle = None
        self.browser_rotation_counter = 0
        
        # Rich Interaction Layer - Lazy init in loop to ensure shared context
        self.rich_manager = None 
        self.browse_ai = BrowseAIHelper() if config.browse_ai_enabled else None
        
        # Site Mapping & Priority Queue
        # Site Mapping & Priority Queue (Refactored for Elite Phase B)
        # self.site_graph remains for legacy compatibility if needed, but primary is self.state_graph
        self.site_graph = {} 

        self.discovery_queue = [] # Heapq: (priority, depth, discovery_order, url, parent_url)
        self.discovery_counter = 0 # NEW: For stable FIFO ordering
        self.discovered_urls = set()
        self.robots_parsers: Dict[str, Optional[Any]] = {}
        self.current_semantic_map = {}
        
        # User-Agent Rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]
        import random
        self.current_ua = random.choice(self.user_agents)
        
        self.seen_names = set() # NEW: For collision detection
        self.total_interactions = 0 # NEW v4.1
        self.current_page_fails = 0 # NEW v4.1
        
        self.visual_analyser = VisualAnalyser(api_key=os.getenv("GEMINI_API_KEY")) if config.use_ai else None
        
        logger.info(f"QA Garden Crawler initialized (AI: {'ENABLED' if self.client else 'DISABLED'}, Visual: {'ENABLED' if self.visual_analyser else 'DISABLED'})")


    def _generate_element_fingerprint(self, el: Dict) -> str:
        """v6.2: Stable fingerprint for element deduplication across mutations."""
        tag = el.get('tag', 'unknown')
        xpath = el.get('xpath', 'unknown')
        text = el.get('text', '')[:50]
        # Use XPath as core but add text/tag for collision safety
        return hashlib.md5(f"{tag}|{xpath}|{text}".encode()).hexdigest()

    def _sanitize_path(self, text: str) -> str:
        """v6.5: Robust Windows/Unix path sanitization for domain and file naming."""
        if not text: return "unknown"
        # 1. Replace colons, slashes, and problematic symbols with underscores
        clean = re.sub(r'[:*?"<>|\\/]', '_', text)
        # 2. Replace dots and spaces to be extra safe on Windows for folder names
        clean = re.sub(r'[\s.]+', '_', clean)
        # 3. Strip leading/trailing underscores
        return clean.strip('_')

    def _validate_url(self, url: str):
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Only http and https are allowed.")
        if not parsed.netloc:
            raise ValueError("Invalid URL: Missing domain.")

    def _rotate_locators(self) -> str:
        """
        v6.0: Strict 2-folder Rotation (locators_new -> locators_old).
        Returns the effective root directory.
        """
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        current_root = os.path.join(base_dir, "locators_new")
        previous_root = os.path.join(base_dir, "locators_old")

        try:
            # 1. Clear old backup
            if os.path.exists(previous_root):
                try:
                    shutil.rmtree(previous_root)
                    logger.debug(f"Cleared old backup: {previous_root}")
                except Exception as ex:
                    logger.warning(f"Could not clear {previous_root}: {ex}")
                    # If we can't clear old, we can't rotate current to it cleanly.
                    # Best fallback: Just rename current to a unique timestamped folder to clear the way
                    timestamp_backup = f"{previous_root}_{int(datetime.now().timestamp())}"
                    try:
                        shutil.move(previous_root, timestamp_backup)
                    except: pass 

            # 2. Move current library to backup
            if os.path.exists(current_root):
                try:
                    # Rename instead of move to avoid nesting issues
                    os.rename(current_root, previous_root)
                    logger.info(f"Current locators moved to: {previous_root}")
                except Exception as ex:
                    logger.warning(f"Could not rotate {current_root}: {ex}")
                    # Fallback: just try to clear content of current_root so we are fresh
            
            # 3. Create fresh current root
            os.makedirs(current_root, exist_ok=True)
            return current_root
            
        except Exception as e:
            logger.error(f"Locator rotation failed: {e}")
            os.makedirs(current_root, exist_ok=True)
            return current_root

    async def run(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Main execution loop yielding progress updates using BrowserSession (v6.1 Robustness)"""
        # v6.7: Intentional Rotation at execution start
        self.locators_root = self._rotate_locators()
        if getattr(self.config, 'site_specific_locators', True):
            domain = self._sanitize_path(urlparse(self.config.url).netloc.replace('www.', ''))
            self.locators_dir = os.path.join(self.locators_root, domain)
        else:
            self.locators_dir = self.locators_root
        
        self.debug_dir = os.path.join(self.locators_dir, "debug_screenshots")
        os.makedirs(self.locators_dir, exist_ok=True)
        os.makedirs(self.debug_dir, exist_ok=True)
        # Force Clean domain folder for fresh run
        for f in os.listdir(self.locators_dir):
            if f.endswith(".json") or f.endswith(".png"):
                try: os.remove(os.path.join(self.locators_dir, f))
                except: pass

        try:
            # v6.8: Immediate progress signal
            yield {
                "event": "progress",
                "agent": "crawler",
                "status": "running",
                "progress": 2,
                "message": "Orchestrating browser core...",
                "depth": 0,
                "url": self.config.url
            }

            async with BrowserSession(self.config) as session:
                self.session_handle = session
                self.browser_handle = session.browser
                self.context_handle = session.context
                self.playwright_handle = session.playwright

                try:
                    # v8.0: Initial Navigation Resilience (Retry loop for server stability)
                    page: Optional[Page] = None
                    max_init_retries = 3
                    for init_attempt in range(1, max_init_retries + 1):
                        try:
                            logger.info(f"Initial Startup Attempt {init_attempt}/{max_init_retries}...")
                            page = await session.new_page()
                            
                            page.on("request", lambda request: self.active_requests.add(request.url))
                            page.on("requestfinished", lambda request: self.active_requests.discard(request.url))
                            page.on("requestfailed", lambda request: self.active_requests.discard(request.url))
                            
                            logger.info(f"Navigating to {self.config.url}...")
                            # Use domcontentloaded for broader compatibility (SPAs like Grok)
                            await page.goto(self.config.url, wait_until="domcontentloaded", timeout=self.config.timeout_sec * 1000)
                            await page.wait_for_timeout(2000)
                            break # Success
                        except Exception as e:
                            logger.warning(f"Initial startup attempt {init_attempt} failed: {e}")
                            if init_attempt == max_init_retries:
                                logger.error("All initial startup attempts failed.")
                                raise RuntimeError(f"Failed to reach {self.config.url} after {max_init_retries} attempts: {str(e)}")
                            
                            # Rotate session on failure to get a fresh browser instance
                            logger.info("Rotating session for retry...")
                            await session.rotate()
                            await asyncio.sleep(2)

                    await self._auto_consent(page)
                    
                    # Elite Phase 20: Sitemap Seeding for >95% Coverage
                    if not getattr(self, "sitemap_seeded", False):
                        logger.info("Initializing Omniscient Discovery: Fetching Sitemap...")
                        sitemap_links = await self._fetch_sitemap(self.config.url)
                        self.sitemap_route_count = len(sitemap_links)
                        for link in sitemap_links:
                            if await self._is_url_allowed(link):
                                await self._add_to_queue(link, depth=1, parent_url=self.config.url)
                        if sitemap_links:
                            logger.info(f"Sitemap Seeding Complete: Injected {len(sitemap_links)} routes into frontier.")
                        self.sitemap_seeded = True
                    
                    # Proactive Site Mapping
                    if self.config.enable_site_mapping:
                        async for update in self._proactive_mapping(page):
                            yield update
                    
                    if self.config.auth_creds and not self.session_authenticated:
                        auth_type = await self._detect_auth_type(page)
                        login_selectors = [
                            "a:has-text('Sign In')", "a:has-text('Login')", "button:has-text('Sign In')", 
                            "button:has-text('Log In')", "span:has-text('Sign In')", "a:has-text('Log In')",
                            "a[href*='login']", "a[href*='signin']", "button[id*='login']",
                            "a:has-text('Register')" 
                        ]
                        # v6.9: Handle "Double Bounce" (Home -> Register -> Login)
                        while auth_type not in ["LOGIN", "NONE"]:
                            logger.info(f"Auth state is {auth_type}. Seeking 'Sign In' or 'Login' toggle again... (URL: {page.url})")
                            login_toggle = None
                            for sel in login_selectors:
                                try:
                                    login_toggle = await page.query_selector(sel)
                                    if login_toggle and await login_toggle.is_visible():
                                        break
                                except: pass
                            
                            if login_toggle is not None:
                                logger.info(f"Found login toggle via: {sel}. Clicking...")
                                await login_toggle.click(force=True)
                                await page.wait_for_timeout(3000)
                                auth_type = await self._detect_auth_type(page)
                            else:
                                logger.info("No more login toggles found.")
                                break

                        logger.info(f"Final Auth Decision State: {auth_type} (URL: {page.url})")
                        if auth_type == "LOGIN" or (await self._detect_login(page)):
                            if await self._handle_login(page):
                                self.session_authenticated = True
                                logger.info("Login successful. Continuing with authenticated session.")
                                async for update in self._process_current_page(page, depth=0, path="dashboard"):
                                    yield update
                            else:
                                logger.error("Login process failed.")
                                logger.warning("Auth sequence failed/stalled.")
                                if self.config.failure_policy == "stop":
                                    return

                    # Start Queue-based Crawl - Ensure we process the landing page (Dashboard) first if authenticated
                    if not self.discovery_queue or self.session_authenticated:
                        logger.info(f"Initializing crawl: processing current state ({page.url})...")
                        async for update in self._process_current_page(page, depth=0, path="auth_landing"):
                            yield update
                        self.finished_urls.add(self._normalize_url(page.url))

                    # Now continue with the rest
                    async for update in self._crawl_loop(page):
                        yield update

                    # Finalize
                    output_json = self._save_consolidated_locators()
                    
                    # v5.1: Corrected Coverage Est (Visited / Discovered)
                    visited = len(self.finished_urls)
                    discovered = len(self.discovery_queue) + visited
                    
                    # Elite Phase 20 Coverage Math
                    sitemap_total = getattr(self, "sitemap_route_count", 0)
                    coverage_denominator = sitemap_total if sitemap_total > 0 else discovered
                    coverage_est = (visited / coverage_denominator * 100) if coverage_denominator > 0 else 0
                    
                    logger.info("=====================================================")
                    logger.info(f"*** OMNISCIENT CRAWL COMPLETE (Phase 20 Guarantee) ***")
                    logger.info(f"- Sitemap Routes Known: {sitemap_total}")
                    logger.info(f"- Unique Routes Visited: {visited}")
                    logger.info(f"- Extracted Locators: {len(self.all_locators)}")
                    logger.info(f"- Mathematical Coverage Score: {coverage_est:.2f}%")
                    logger.info("=====================================================")
                    
                    # Use absolute path for dashboard retrieval
                    abs_path = os.path.abspath(output_json)
                    yield {
                        "event": "artifact",
                        "type": "json",
                        "name": "Consolidated Locators",
                        "path": abs_path, 
                        "agent": "crawler"
                    }
                    
                    yield {
                        "event": "coverage_update",
                        "job_id": getattr(self.config, 'job_id', 'unknown'),
                        "discovered": len(self.discovered_urls),
                        "extracted": len(self.all_locators),
                        "coverage_percent": round(coverage_est, 2)
                    }
                    
                    yield {
                        "event": "completed", 
                        "job_id": getattr(self.config, 'job_id', 'unknown'),
                        "page_count": len(self.finished_urls), 
                        "discovered_count": len(self.discovered_urls),
                        "total_locators": len(self.all_locators),
                        "status": "completed",
                        "agent": "crawler",
                        "path": abs_path,
                        "coverage_metric": f"Omniscient Coverage Score: {coverage_est:.2f}% ({visited} visited / {coverage_denominator} domain routes)"
                    }
                finally:
                    pass
            
            logger.info("Crawler run loop finished.")
        except Exception as e:
            logger.critical(f"FATAL STARTUP ERROR: {e}", exc_info=True)
            yield {"event": "log", "message": f"Fatal Startup Error: {e}", "level": "critical"}
            raise e


    def _normalize_url(self, url: str) -> str:
        """Robustly normalize URL to prevent infinite loops and duplicate processing."""
        if not url or not url.strip():
            return ""
        url = url.strip()
        try:
            p = urlparse(url)
            if not p.scheme:
                # Default to https
                url = f"https://{url}"
                p = urlparse(url)

            # 1. Remove fragments (#section)
            p = p._replace(fragment="")

            # 2. Clean query parameters (Remove tracking/session IDs)
            query = parse_qs(p.query, keep_blank_values=True)
            # Standard tracking/noise parameters to strip
            bad_keys = {
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                'fbclid', 'gclid', 'msclkid', '_ga', '_gl', 'session_id', 'sid',
                'jsessionid', 'phpsessid', 'sort', 'order', 'page_size'
            }
            cleaned_query = {k: v for k, v in query.items() if k.lower() not in bad_keys}
            
            # Reconstruct query string (sorted for consistency - Elite Standard)
            sorted_items = sorted(cleaned_query.items())
            query_str = urlencode({k: v[0] if len(v) == 1 else v for k, v in sorted_items}, doseq=True)

            # 3. Normalize netloc and path
            netloc = p.netloc.lower()
            # if netloc.startswith('www.'):
            #     netloc = netloc[4:]
            
            path = p.path.rstrip('/')
            if not path: path = ""

            normalized = urlunparse((
                p.scheme.lower(),
                netloc,
                path,
                p.params,
                query_str,
                ''
            ))
            return normalized
        except Exception as e:
            logger.debug(f"URL normalization error for {url}: {e}")
            return url.rstrip('/')

    async def _add_to_queue(self, url: str, depth: int, parent_url: str = "") -> None:
        raw_url = url
        url = self._normalize_url(url)
        
        # logger.info(f"DIAGNOSTIC: _add_to_queue checking: {url} (parent: {parent_url})")
        
        if url in self.discovered_urls:
            # logger.info(f"DIAGNOSTIC: SKIP (Already Discovered): {url}")
            return
        
        # v1.0: Modular Marketing Filter - prevents "looping back" from authenticated session to public site
        # BUT: Allow depth 0 (sitemaps) regardless of session state
        if self.session_authenticated and depth > 0:
            url_lower = url.lower()
            if any(kw in url_lower for kw in self.config.exclude_marketing_keywords):
                return
            if any(pat in url_lower for pat in self.config.marketing_url_patterns):
                return

        if url in self.finished_urls:
             return
        
        # Check if already in queue (as the 4th element in the tuple)
        if any(url == x[3] for x in self.discovery_queue):
             return
        
        # Max Queue Size Limit (Safety)
        if len(self.discovery_queue) >= self.config.max_queue_size:
            logger.warning(f"Max queue size reached. Skipping discovery for {url}")
            return

        # Check robots.txt and Domain
        is_allowed = await self._is_url_allowed(url)
        if not is_allowed:
            logger.info(f"DIAGNOSTIC: REJECTED by _is_url_allowed: {url}")
            return

        priority = self._calculate_url_priority(url, depth, self.discovery_counter)
        self.discovery_counter += 1
        heapq.heappush(self.discovery_queue, (priority, depth, self.discovery_counter, url, parent_url))
        self.discovered_urls.add(url)
        logger.info(f"DIAGNOSTIC: ADDED TO QUEUE: {url} (Depth: {depth}, Parent: {parent_url})")

    def _calculate_url_priority(self, url: str, depth: int, discovery_order: int) -> int:
        """v6.2 Elite: Pure Natural Traversal (Depth-First + Discovery Order)"""
        # Remove keyword bias to ensure 100% discovery of neutrally-named pages (like podgallery)
        return depth * 10000 + discovery_order

    async def _discover_all_links(self, page: Page) -> List[str]:
        try:
            is_dynamic = getattr(self.config, 'dynamic_crawl', False)
            links = await page.evaluate("""
                (isDynamic) => {
                    const getDomain = (url) => {
                        try {
                            const parsed = new URL(url);
                            return parsed.hostname.toLowerCase().replace('www.', '');
                        } catch(e) { return null; }
                    };
                    
                    const baseDomain = getDomain(window.location.href);
                    if (!baseDomain) return [];

                    const discovered = new Set();

                    function walk(node) {
                        if (!node) return;
                        
                        // 1. Discover <a> links
                        if (node.tagName === 'A' && node.getAttribute('href')) {
                            try {
                                const href = node.getAttribute('href');
                                if (!href.startsWith('javascript:') && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
                                    const absoluteUrl = new URL(href, window.location.href).href;
                                    discovered.add(absoluteUrl);
                                }
                            } catch (e) {}
                        }

                        // 2. Discover canonical link
                        if (node.tagName === 'LINK' && node.rel === 'canonical' && node.getAttribute('href')) {
                            try {
                                const absoluteUrl = new URL(node.getAttribute('href'), window.location.href).href;
                                discovered.add(absoluteUrl);
                            } catch (e) {}
                        }
                        
                        // 3. Discover links in data-attributes (common in SPAs)
                        for (const attr of node.attributes || []) {
                            if (attr.name.includes('href') || attr.name.includes('url') || attr.name === 'to') {
                                try {
                                    const val = attr.value;
                                    if (val && (val.startsWith('/') || val.startsWith('http'))) {
                                        const absoluteUrl = new URL(val, window.location.href).href;
                                        discovered.add(absoluteUrl);
                                    }
                                } catch (e) {}
                            }
                        }

                        // Traverse light DOM
                        let child = node.firstElementChild;
                        while (child) {
                            walk(child);
                            child = child.nextElementSibling;
                        }

                        // Traverse Shadow DOM
                        if (node.shadowRoot) {
                            walk(node.shadowRoot);
                        }
                    }

                    walk(document);

                    return Array.from(discovered).filter(href => {
                        if (isDynamic) return true;
                        const linkDomain = getDomain(href);
                        return linkDomain === baseDomain || (linkDomain && linkDomain.endsWith('.' + baseDomain));
                    });
                }
            """, is_dynamic)
            # Deduplicate while preserving order (Python 3.7+ dicts are ordered)
            links = list(dict.fromkeys(links))
            return links
        except Exception as e:
            logger.error(f"Error in JS link discovery: {e}")
            return []

    async def _is_url_allowed(self, url: str) -> bool:
        """Check if URL is allowed by domain rules and robots.txt (Async v5.0)"""
        if not url.startswith('http'): 
            return False

        # 0. Check User-Defined Exclusions (CLI/Config)
        for pattern in self.config.exclude_paths:
            if pattern in url:
                logger.info(f"Skipping excluded URL pattern '{pattern}': {url}")
                return False
        
        parsed = urlparse(url)
        
        # v5.6: Progressive Resource Filter (Exclude common static assets)
        path_lower = parsed.path.lower()
        static_exts = {
            '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
            '.woff', '.woff2', '.ttf', '.eot', '.mp4', '.webm', '.pdf', '.zip',
            '.map', '.json', '.webmanifest'
        }
        if any(path_lower.endswith(ext) for ext in static_exts):
            logger.debug(f"Rejecting {url}: static asset")
            return False
            
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Domain check: allow subdomains and handle www/non-www
        if getattr(self.config, 'dynamic_crawl', False):
             return True # Bypass domain check for dynamic crawling
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # 1. Domain Match (v6.6: permissive domain matching to handle .ai -> .com redirects)
        # Using root-part comparison (e.g. 'jellypod')
        target_netloc = urlparse(self.config.url).netloc.lower().replace('www.', '')
        target_root = target_netloc.split('.')[0]
        
        link_netloc = netloc.replace('www.', '')
        link_root = link_netloc.split('.')[0]
        
        if link_root and link_root != target_root:
            logger.info(f"DIAGNOSTIC: REJECTED (Domain Mismatch - Allowed Root: {target_root}, Got: {link_root}): {url}")
            return False
        
        logger.info(f"DIAGNOSTIC: ALLOWED (Internal Domain): {url}")
            
        # NEW: Check if robots.txt should be respected
        if not self.config.respect_robots:
            # logger.info(f"DIAGNOSTIC: ALLOWED (Robots.txt Respect Disabled): {url}")
            return True  # Skip robots.txt if disabled in config
        
        # 3. Robots.txt
        if self.config.respect_robots:
            domain = f"{parsed.scheme}://{parsed.netloc}"
            if domain not in self.robots_parsers:
                try:
                    import urllib.robotparser
                    rp = urllib.robotparser.RobotFileParser()
                    rp.set_url(f"{domain}/robots.txt")
                    await asyncio.to_thread(rp.read)
                    self.robots_parsers[domain] = rp
                except Exception as e:
                    self.robots_parsers[domain] = None
            
            parser = self.robots_parsers.get(domain)
            if parser is not None and hasattr(parser, "can_fetch"):
                allowed = parser.can_fetch("*", url)
                return allowed
            
        return True

    async def _proactive_mapping(self, page: Page) -> AsyncGenerator[Dict[str, Any], None]:
        logger.info("Starting proactive site mapping...")
        
        # 1. Sitemap.xml
        if self.config.sitemap_enabled:
            sitemap_urls = await self._fetch_sitemap(self.config.url)
            for u in sitemap_urls:
                await self._add_to_queue(u, depth=0, parent_url="sitemap")
            yield {
                "event": "pages_discovered",
                "count": len(sitemap_urls),
                "source": "sitemap",
                "queue_size": len(self.discovery_queue)
            }

        # 2. Firecrawl or Playwright Map
        discovered = []
        if self.config.firecrawl_api_key:
            try:
                logger.info("Using Firecrawl for site mapping...")
                pass
            except Exception as e:
                logger.warning(f"Firecrawl mapping failed: {e}. Falling back to Playwright.")
        
        # Fallback to Playwright Link Extraction
        if not discovered:
            logger.info("Extracting links via Playwright fallback...")
            discovered = await self._discover_all_links(page)
            
        for u in discovered:
            await self._add_to_queue(u, depth=1, parent_url="initial_map")

        yield {
            "event": "pages_discovered",
            "count": len(discovered),
            "source": "mapping",
            "queue_size": len(self.discovery_queue)
        }

    async def _fetch_sitemap(self, url: str) -> List[str]:
        parsed = urlparse(url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        links = []
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(sitemap_url)
                if resp.status_code == 200:
                    try:
                        root = ET.fromstring(resp.content)
                        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                        # Handle both namespaced and non-namespaced sitemaps
                        for loc in root.findall('.//ns:loc', ns) or root.findall('.//loc'):
                            if loc.text:
                                links.append(loc.text)
                    except ET.ParseError:
                        logger.warning(f"Could not parse sitemap XML for {sitemap_url}")
                else:
                    logger.info(f"Sitemap not found at {sitemap_url} (Status: {resp.status_code})")
        except Exception as e:
            logger.warning(f"Failed to fetch sitemap: {e}")
        return links

    def _check_memory(self):
        """Monitor memory usage and log warnings."""
        mem = psutil.virtual_memory()
        if mem.percent > 95:
            logger.warning(f"Memory usage critical ({mem.percent}%)! Consider closing other applications.")
        elif mem.percent > 80:
            logger.info(f"Memory usage: {mem.percent}%")

    async def _vigorous_scroll(self, page: Page):
        """Elite Phase 20: Triggers all lazy-loaded React/Vue components."""
        logger.info(f"Vigorously scrolling {page.url} to trigger lazy-loads...")
        try:
            prev_height = 0
            for i in range(5): # Max 5 vigorous scrolls to prevent infinite scrolling loops
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_height == prev_height and i > 0:
                    break
                await page.evaluate(f"window.scrollTo(0, {current_height});")
                await page.wait_for_timeout(500) # Wait for network activity to spike
                prev_height = current_height
                
                # Check for stability
                try:
                    await page.wait_for_load_state("networkidle", timeout=2000)
                except: pass
            
            # Scroll back to top
            await page.evaluate("window.scrollTo(0, 0);")
            await page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Vigorous scroll encountered an error: {e}")

    async def _crawl_loop(self, page_dummy: Page) -> AsyncGenerator[Dict[str, Any], None]:
        """v4.9: Fault-tolerant crawl loop with global SDET recovery and session rotation."""
        while self.discovery_queue and len(self.finished_urls) < self.max_pages:
            try:
                if self.abort_event.is_set():
                    logger.info("Abort signal received. Terminating crawl.")
                    yield {"event": "log", "message": "Run aborted by user.", "level": "warning"}
                    break
                
                # Global pause check
                await self.pause_event.wait()

                # Global Duration Check
                elapsed_total = (datetime.now() - self.start_time).total_seconds()
                if elapsed_total > self.config.max_crawl_duration_sec:
                    logger.warning(f"Hard stop: Max crawl duration ({self.config.max_crawl_duration_sec}s) reached.")
                    break

                # emergency over-crawl protection (Phase 0)
                if len(self.finished_urls) >= self.config.max_pages * 1.5:
                    logger.warning(f"Emergency over-crawl protection triggered (Finished: {len(self.finished_urls)}, Max: {self.config.max_pages})")
                    break

                priority, depth, _, normalized_url, parent = heapq.heappop(self.discovery_queue)
                
                if normalized_url in self.finished_urls: continue
                if depth > self.config.max_depth: continue

                # Check Memory & Rotation Logic
                mem = psutil.virtual_memory().percent
                headful_revert = (sys.platform == "win32" and self.config.auto_revert_headful and self.total_interactions >= 30)
                
                if (mem > self.config.context_rotation_mem_threshold or self.nav_count % 15 == 0 or headful_revert):
                    # v5.0: Safe Rotation - only rotate if no active form detected
                    logger.info("Evaluating rotation safety...")
                    is_safe = True
                    try:
                        # Check context handle still alive and has pages
                        if self.context_handle and self.context_handle.pages:
                            active_p = self.context_handle.pages[0]
                            # Check for visible forms on the active page
                            if await active_p.evaluate("document.querySelector('form:not([style*=\"display: none\"])') !== null"):
                                logger.info("Active form detected -> delaying rotation for session stability")
                                is_safe = False
                    except Exception as e:
                        logger.debug(f"Error checking for active form during rotation safety check: {e}")
                        pass # Carry on if check fails, assume safe or handle later

                    if is_safe:
                        logger.info(f"Rotating Environment (Mem: {mem}%, Navs: {self.nav_count}, Revert: {headful_revert})")
                        await self.session_handle.rotate()
                        self.total_session_restarts += 1

                logger.info(f"Navigating to: {normalized_url} (Priority: {priority}, Depth: {depth})")
                
                # Navigation Attempt Block
                success = False
                for attempt in range(1, 5):
                    try:
                        # Calculate progress
                        total_planned = self.config.max_pages or 50
                        current_finished = len(self.finished_urls)
                        percent = min(98, max(5, int((current_finished / total_planned) * 100)))
                        
                        yield {
                            "event": "progress",
                            "progress": percent,
                            "discovered": len(self.discovery_queue),
                            "finished": current_finished,
                            "url": normalized_url,
                            "metrics": {
                                "discovered": len(self.discovery_queue),
                                "finished": current_finished,
                                "elements": len(self.all_locators)
                            }
                        }
                        
                        try:
                            if not self.session_handle:
                                raise RuntimeError("Session handle lost. Attempting recovery...")
                            new_page = await self.session_handle.new_page()
                        except Exception as ne:
                            if "closed" in str(ne).lower() or "connection" in str(ne).lower():
                                logger.warning(f"Browser handler closed during new_page. Forcing emergency rotation: {ne}")
                                await self.session_handle.rotate()
                                new_page = await self.session_handle.new_page()
                            else:
                                raise
                        
                        new_page.on("dialog", lambda dialog: asyncio.create_task(dialog.dismiss()))
                        
                        if attempt > 1:
                            await asyncio.sleep(2 ** attempt)

                        await new_page.goto(normalized_url, wait_until="domcontentloaded", timeout=self.config.timeout_sec * 1000)
                        await self._wait_for_stability(new_page)
                        
                        # Process Page
                        async for update in self._process_current_page(new_page, depth, parent):
                            # Forward page specific updates
                            yield update
                        
                        self.finished_urls.add(normalized_url)
                        self.nav_count += 1
                        self.consecutive_failures = 0
                        success = True
                        await new_page.close()
                        break
                    except Exception as e:
                        logger.warning(f"Attempt {attempt} failed for {normalized_url}: {e}")
                        try: await new_page.close()
                        except Exception as close_err: logger.debug(f"Page close ignored: {close_err}")
                        if attempt == 4: raise

            except Exception as e:
                logger.error(f"Critical loop error on {normalized_url if 'normalized_url' in locals() else 'unknown'}: {str(e)}", exc_info=True)
                self.consecutive_failures += 1
                if self.consecutive_failures > 5:
                    logger.critical("Too many consecutive errors -> aborting.")
                    break
                await asyncio.sleep(2)


    async def _process_current_page(self, page: Page, depth: int, path: str) -> AsyncGenerator[Dict[str, Any], None]:
        logger.debug(f"Entering _process_current_page for {page.url}")
        current_url = self._normalize_url(page.url)
        self.current_page_fails = 0 # Reset fails on new page discovery
        # v5.3: Aggressive Stabilization for SPAs/High-JS sites
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except: pass
        await page.wait_for_timeout(3000)
        
        # v6.0 SDET Enhancement: Probe iFrames for hidden login forms
        if not self.session_authenticated:
            await self._probe_iframes_for_auth(page)

        # v5.6: Persistent Login Retry Loop
        # If we are on the login page, we MUST try to authenticate
        # v6.2 Elite Auth Handling (Universal)
        if await self._detect_auth_page(page) and not self.session_authenticated:
            if await self._handle_auth(page):
                logger.info("Universal Auth Successful!")
                # Refresh URL state
                current_url = self._normalize_url(page.url)
            else:
                logger.error("Universal Auth Failed. Proceeding with caution.")
        
        # 1. IMMEDIATE PRIORITY: Discover and Queue new links
        # This ensures that even if AI analysis hangs/crashes, the crawl frontier expands.
        if depth < self.max_depth:
            new_links = await self._discover_all_links(page)
            for link in new_links:
                await self._add_to_queue(link, depth + 1, current_url)
            
            yield {
                "event": "pages_discovered",
                "count": len(new_links),
                "url": current_url,
                "queue_size": len(self.discovery_queue)
            }

        # 2. Semantic Analysis (AI)
        if self.config.use_ai and depth <= self.config.ai_max_depth:
            self.current_semantic_map = await self._discover_semantic_components(page)
            if self.current_semantic_map:
                logger.info(f"Discovered {len(self.current_semantic_map)} semantic component zones")

        # 2a. Visual Discovery (New Elite Layer)
        if self.visual_analyser and depth <= self.config.ai_max_depth:
            await self._visual_discovery(page)

        
        # 2b. State Awareness (Elite Phase B)
        content_hash = await self._get_page_hash(page)
        state_id = f"{current_url}::{content_hash}"
        self.current_state_id = state_id
        
        if state_id not in self.state_graph["nodes"]:
            self.state_graph["nodes"][state_id] = {
                "url": current_url,
                "hash": content_hash,
                "depth": depth,
                "visited_at": datetime.now().isoformat(),
                "extracted_locators": 0
            }
            logger.info(f"New UI State discovered: {state_id}")
        else:
            logger.info(f"Re-visited existing UI State: {state_id}")

        logger.info(f"Page content hash: {content_hash}")


        # 3. Rich Interactions (AI Specialist)
        # Optimized: Strict checks for AI usage
        if self.config.use_ai and (depth <= self.config.ai_max_depth):
            # v10/10 Logic: Lazy initialize per-page to force shared context
            if not self.rich_manager:
                self.rich_manager = RichInteractionManager(page=page)
            elif hasattr(self.rich_manager, 'page'):
                self.rich_manager.page = page # Update existing
            
            if self.rich_manager and (depth == 0 or len(self.current_semantic_map) > 3):
                logger.info("Triggering Agentic Rich Interaction for deep discovery...")
                pre_agent_url = page.url
                try:
                    # Add timeout to prevent hanging the entire crawl
                    # v5.1: Pass shared page context to preserve sessions
                    rich_summary = await asyncio.wait_for(
                        self.rich_manager.explore_and_interact(current_url, timeout_sec=self.config.ai_timeout_sec), 
                        timeout=self.config.ai_timeout_sec + 5.0
                    )
                    logger.info(f"Rich Interaction Result: {rich_summary}")
                    
                    if page.is_closed():
                        logger.warning("Browser page closed during AI interaction.")
                        return

                    post_agent_url = page.url
                    # Check for AI-driven navigation (crucial for SPAs)
                    if self._normalize_url(post_agent_url) != self._normalize_url(pre_agent_url):
                        logger.info(f"AI Agent navigated to new state: {post_agent_url}. Adding to discovery queue.")
                        await self._add_to_queue(post_agent_url, depth + 1, current_url)
                        
                        # v5.2: State Integrity - Return to original page for extraction if agent wandered off
                        if self._normalize_url(post_agent_url) != self._normalize_url(current_url):
                            logger.warning(f"AI Agent wandered to {post_agent_url}. Returning to {current_url} for extraction integrity.")
                            await page.goto(current_url, wait_until="networkidle")
                            await self._wait_for_stability(page)

                except asyncio.TimeoutError:
                     logger.warning(f"Rich Interaction timed out on {current_url}. Skipping interaction.")
                except Exception as e:
                     logger.warning(f"Rich Interaction failed on {current_url}: {e}")
                     # Ensure we are back on track if it failed mid-navigation
                     if not page.is_closed() and self._normalize_url(page.url) != self._normalize_url(current_url):
                         try:
                            logger.info(f"Restoring page state after AI failure: {current_url}")
                            await page.goto(current_url, wait_until="networkidle")
                         except: pass
        
        if self.browse_ai and depth == 0:
            logger.info("Triggering specialist Browse AI robot for baseline extraction...")
            await self.browse_ai.trigger_robot(current_url)

        if content_hash in self.visited_content_hashes:
            logger.info("Page content already visited. Skipping.")
            return
        self.visited_content_hashes.add(content_hash)

        # 0. WARM UP: Auto-consent and intelligent form filling
        logger.info(f"--- Processing START: {current_url} (Depth: {depth}) ---")
        await self._auto_consent(page)
        await self._auto_interact(page)

        logger.info(f"Emitting progress event for {current_url}...")
        try:
            _finished = len(self.finished_urls)
            _discovered = len(self.discovery_queue)
            # Count actual page_N.json files saved so far for a real locator count
            try:
                _pages_saved = len([f for f in os.listdir(self.locators_dir) if f.startswith("page_") and f.endswith(".json")]) if hasattr(self, 'locators_dir') and os.path.isdir(self.locators_dir) else 0
            except Exception:
                _pages_saved = _finished
            yield {
                "event": "progress",
                "url": current_url,
                "depth": depth,
                "path": path,
                "page_count": _finished + 1,
                "status": "running",
                "metrics": {
                    "finished": _finished + 1,
                    "discovered": _discovered,
                    "elements": len(self.all_locators),
                    "current_url": current_url,
                    "coverage": round(((_finished + 1) / (self.config.max_pages or 50)) * 100, 1)
                }
            }
            logger.info("Progress event successfully yielded and processed by caller.")
        except (ValueError, IOError, BrokenPipeError, Exception) as ey:
            logger.warning(f"Output stream issue during progress yield (likely closed pipe): {ey}")

        # NEW: Discover ALL links from current page FIRST (before interactions)
        # This ensures we find all navigation links immediately
        if depth < self.max_depth:
            logger.info(f"Discovering links from {current_url} at depth {depth}")
            discovered_links = await self._discover_all_links(page)
            logger.info(f"Found {len(discovered_links)} total links on page")
            
            links_added = 0
            links_skipped = 0
            for link_url in discovered_links:
                # _add_to_queue has built-in duplicate checking
                queue_size_before = len(self.discovery_queue)
                await self._add_to_queue(link_url, depth + 1, current_url)
                if len(self.discovery_queue) > queue_size_before:
                    links_added += 1
                    logger.debug(f"Added link: {link_url}")
                else:
                    links_skipped += 1
                    logger.debug(f"Skipped link (duplicate or filtered): {link_url}")
            
            logger.info(f"Link discovery complete: {links_added} added, {links_skipped} skipped, queue size: {len(self.discovery_queue)}")
            
            if links_added > 0:
                logger.info(f"Added {links_added} new links to queue (total queue: {len(self.discovery_queue)})")
                
                yield {
                    "event": "pages_discovered",
                    "count": links_added,
                    "source": "page_links",
                    "queue_size": len(self.discovery_queue),
                    "depth": depth
                }

        safe_path = re.sub(r'\W+', '_', path)
        
        # v5.2: ROBUST PAGE STATE INTEGRITY (FINAL CHECK)
        # Ensure we are on the correct page before extraction, regardless of what happened above.
        if page.is_closed():
             logger.error(f"Page closed before extraction for {current_url}. Skipping.")
             return

        check_url = page.url
        logger.debug(f"Drift Check - Expected: {current_url}, Found: {check_url}")
        if self._normalize_url(check_url) != self._normalize_url(current_url):
             logger.debug("Drift DETECTED!")
             logger.warning(f"Page state drift detected before extraction! Expected {current_url}, found {check_url}. Forcing restoration.")
             try:
                 await page.goto(current_url, wait_until="networkidle")
                 await self._wait_for_stability(page)
                 
                 # v5.3: Session Recovery (Handle AI-induced logout)
                 if "login" in page.url.lower() or await self._detect_login(page):
                     logger.warning("Session lost during AI interaction! Attempting re-authentication...")
                     if await self._handle_login(page):
                         logger.info("Session recovered! Retrying navigation to target.")
                         await page.goto(current_url, wait_until="networkidle")
                         await self._wait_for_stability(page)
                     else:
                         logger.error("Failed to recover session after AI interaction. Extraction may follow on login page.")
                         
             except Exception as e:
                 logger.error(f"Failed to restore page state: {e}")

        # v5.5: Extraction Resilience with Retries
        page_data = None
        max_extract_retries = 3
        for attempt in range(max_extract_retries):
            try:
                page_data = await self._extract_elements(page, safe_path)
                break # Success
            except Exception as e:
                if "context was destroyed" in str(e).lower() or "navigation" in str(e).lower():
                    logger.warning(f"Extraction attempt {attempt + 1} failed for {current_url}: {e}. Retrying navigation...")
                    try:
                        await page.goto(current_url, wait_until="networkidle")
                        await self._wait_for_stability(page)
                    except: pass
                    continue
                else:
                    logger.error(f"Extraction attempt {attempt + 1} failed with unrecoverable error: {e}")
                    break
        
        if not page_data:
            logger.debug(f"page_data is None for {current_url}")
            return # Skip this page if extraction failed after retries
        elif not page_data.get('elements'):
             logger.debug(f"page_data has no elements for {current_url}")
        else:
             logger.debug(f"page_data has {len(page_data['elements'])} elements")

        if page_data and page_data.get('elements'):
            logger.debug(f"About to save {len(page_data['elements'])} elements for {current_url}")
            # Save per-page JSON (v4.2 Lazy Increment)
            self.screen_id_counter += 1
            file_name = f"page_{self.screen_id_counter}.json"
            json_path = os.path.join(self.locators_dir, file_name)
            
            logger.debug(f"Saving to: {os.path.abspath(json_path)}")
            
            # Map elements to global storage AFTER successful extraction but BEFORE save
            for key, el in page_data['elements'].items():
                self.all_locators[f"state_{self.screen_id_counter}_{key}"] = el

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2)
            
            logger.info(f"Saved sequential locator file: {file_name}")
            try:
                yield {"event": "artifact", "type": "json", "path": json_path, "url": current_url}
            except (ValueError, IOError, BrokenPipeError):
                logger.warning("Could not yield artifact event - stream closed.")
            
            logger.info(f"Extracted {len(page_data.get('elements', {}))} elements and {len(page_data.get('tables', []))} tables from {current_url}")
        
        if depth < self.config.max_depth:
            logger.info(f"Starting Interaction Phase for {current_url} (Limit: {self.config.max_interactions_per_page})")
            await self._deep_interact(page, safe_path, depth)
            logger.info(f"Finished Interaction Phase for {current_url}")
            
        self.finished_urls.add(current_url)
        yield {"event": "finish_page", "url": current_url, "screen_id": self.screen_id_counter}
        logger.info(f"--- Processing FINISH: {current_url} (ID: {self.screen_id_counter}) ---")

    async def _visual_discovery(self, page: Page):
        """
        Elite Phase A: Uses Gemini Vision to find elements invisible to DOM scans.
        """
        if not self.visual_analyser:
            return

        logger.info("Triggering Visual Discovery pass...")
        temp_dir = tempfile.gettempdir()
        screenshot_path = os.path.join(temp_dir, f"visual_scan_{int(datetime.now().timestamp())}.png")
        
        try:
            # v6.8: Resilient Check - Ensure page isn't closed before screenshot
            if page.is_closed():
                logger.warning("Visual Discovery skipped: Page already closed.")
                return

            # Memory Guard: Skip expensive vision analysis if RAM is critically low (>95%)
            mem = psutil.virtual_memory().percent
            if mem > 95.0:
                logger.warning(f"Visual Discovery skipped: RAM pressure {mem}% is too high.")
                return

            # Viewport only for speed and reliability
            await page.screenshot(path=screenshot_path, full_page=False) 
            visual_elements = await self.visual_analyser.identify_interactives(screenshot_path, page.url)
            
            new_elements_count = 0
            for v_el in visual_elements:
                v_x, v_y = v_el.get('x', 0), v_el.get('y', 0)
                is_duplicate = False
                
                # Check against ALL existing locators using radius (50px)
                for existing in self.all_locators.values():
                    e_x = existing.get('x', 0)
                    e_y = existing.get('y', 0)
                    if abs(e_x - v_x) < 30 and abs(e_y - v_y) < 30:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    # Create a "Visual Locator"
                    v_name = f"visual_{v_el.get('name', 'element')}"
                    # Use existing semantic naming logic for collisions/uniqueness
                    v_name = self._generate_semantic_name({'name': v_name, 'x': v_x, 'y': v_y})
                    
                    visual_locator = {
                        "name": v_name,
                        "type": v_el.get('type', 'button'),
                        "xpath": f"point({v_x},{v_y})", # Special marker for coordinate-based click
                        "x": v_x,
                        "y": v_y,
                        "source": "vision",
                        "description": v_el.get('description', ''),
                        "confidence": 0.8
                    }
                    self.all_locators[v_name] = visual_locator
                    new_elements_count += 1
            
            if new_elements_count > 0:
                logger.info(f"Visual Discovery augmented extraction with {new_elements_count} visual-only elements.")
            
        except Exception as e:
            logger.error(f"Visual Discovery failed: {e}")
        finally:
            if os.path.exists(screenshot_path):
                try: os.remove(screenshot_path)
                except: pass

    def _deduplicate_elements(self, elements: list) -> list:
        seen = {}

        # Pre-calc interactive XPaths for the text node check
        interactive_xpaths = {e['xpath'] for e in elements if e.get('isInteractive')}
        
        for el in elements:
            name = el.get('element_name')
            xpath = el['xpath']
            
            # 1. Text Node Redundancy Check
            if el['tag'] in ['span', 'div'] and el.get('text'):
                 parent_xpath = xpath.rsplit('/', 1)[0]
                 if parent_xpath in interactive_xpaths:
                     continue # Skip text node that is just label for parent button

            if name in seen:
                existing = seen[name]
                # Prefer interactive, then higher quality
                new_score = el.get('quality_score', 0)
                old_score = existing.get('quality_score', 0)
                new_interactive = el.get('isInteractive', False)
                old_interactive = existing.get('isInteractive', False)
                
                if (new_interactive and not old_interactive) or (new_score > old_score):
                    seen[name] = el
            else:
                seen[name] = el
        
        return list(seen.values())

    async def _extract_elements(self, page: Page, path: str) -> Dict[str, Any]:
        """Extract all interactive elements using Intelligent Extraction (v5.0)."""
        logger.info(f"Extracting elements from {page.url}...")
        self.seen_names = set() # CLEAR PER PAGE TO PREVENT INFINITE GROWTH AND COLLISION DATA LOSS
        
        await self._smart_scroll(page)
        await self._vigorous_scroll(page) # Elite Lazy-Load Trigger
        await self._auto_interact(page)

        script = f"""
        ((includeHiddenStr) => {{
            {self._get_js_helpers()}
            return getAllElements(document, includeHiddenStr === 'true');
        }})('{str(self.config.include_hidden).lower()}')
        """
        
        try:
            raw_elements = await page.evaluate(script)
            logger.info(f"DEBUG: JS Extraction returned {len(raw_elements)} raw elements for {page.url}")
        except Exception as e:
            logger.error(f"CRITICAL: JS Extraction failed: {e}")
            raw_elements = []
        
        processed_elements = []
        skipped_counts = {"filtering": 0, "duplicate": 0, "quality": 0}
        
        for i, el in enumerate(raw_elements):
            # 1. Stricter Python Filtering
            tag = el.get('tag', '').lower()
            role = el.get('role', '').lower()
            
            if not self._is_testable_element(el['tag'], el['attributes'] or {}, el.get('text', '')):
                skipped_counts["filtering"] += 1
                continue
            
            # 2. Quality Score computation (Elite Phase 23)
            quality_score = 50
            if el.get('dataTestId'): quality_score = 95
            elif el.get('id') and not re.search(r'\d{5,}', el['id']): quality_score = 90
            elif el.get('customLabel'): quality_score = 85
            elif role: quality_score = 80
            el['quality_score'] = quality_score

            # Elite Filtering: Radically drop generic structural tags without explicit interaction roles
            # This kills 'div' and 'span' that only act as text wrappers and pollute the LLM
            if tag in ['div', 'span', 'section', 'p', 'article', 'ul', 'li', 'form']:
                is_explicitly_interactive = role in ['button', 'link', 'menuitem', 'checkbox', 'tab', 'switch'] or el.get('onclick') is not None
                if not is_explicitly_interactive and quality_score < 85:
                    skipped_counts["filtering"] += 1
                    continue
            
            # 3. Semantic Naming (using customLabel)
            el['element_name'] = self._generate_semantic_name(el)
            
            # 4. Refine Name
            el['element_name'] = self._refine_element_name(el['element_name'], el)
            
            # 5. Playwright Selector & Strict Validation (Elite Phase 23)
            if not el.get('playwright_selector') and el.get('css'):
                base_selector = el['css']
                # Sanitize Tailwind CSS selectors before using them
                sanitized_selector = _sanitize_css_selector(base_selector)
                try:
                    locator_count = await page.locator(sanitized_selector).count()
                    if locator_count == 1:
                        el['playwright_selector'] = f"page.locator('{base_selector}')"
                        el['is_unique'] = True 
                        el['element_count'] = 1
                    elif locator_count > 1:
                        # Elite Phase 23: Strict Selector Verification Hook
                        # Dynamically reconstruct to strictly unique selector if CSS failed
                        xpath_val = el.get('xpath')
                        if xpath_val:
                            strict_xpath = f"xpath={xpath_val}"
                            if await page.locator(strict_xpath).count() == 1:
                                el['playwright_selector'] = f"page.locator('{strict_xpath}')"
                                el['is_unique'] = True
                                el['element_count'] = 1
                            else:
                                el['playwright_selector'] = f"page.locator('{base_selector}').nth(0)"
                                el['is_unique'] = False
                                el['element_count'] = locator_count
                        else:
                            el['playwright_selector'] = f"page.locator('{base_selector}').nth(0)"
                            el['is_unique'] = False
                            el['element_count'] = locator_count
                        
                        logger.debug(f"Selector {base_selector} reconstructed to {el['playwright_selector']}")
                    else:
                        continue # Failed to locate entirely (dynamic shift), drop it
                except Exception as e:
                    logger.warning(f"Validation failed for {base_selector}: {e}")
                    el['playwright_selector'] = f"page.locator('{base_selector}').nth(0)"
                    el['is_unique'] = False
                    el['element_count'] = 0
            
            # Ensure uniqueness fallbacks for XPath if CSS failed completely
            if not el.get('playwright_selector') and el.get('xpath'):
                 el['playwright_selector'] = f"page.locator('xpath={el['xpath']}')"
                 el['is_unique'] = False

            processed_elements.append(el)
            
        # 6. Deduplication
        final_list = self._deduplicate_elements(processed_elements)
        
        # Convert list to dict keyed by name
        page_elements = {el['element_name']: el for el in final_list}

        logger.debug(f"Extraction finished with {len(page_elements)} elements")
        logger.info(f"Extraction summary: {len(page_elements)} locators saved (from {len(raw_elements)} raw). Skips: {skipped_counts}")
        return {
            "elements": page_elements,
            "url": page.url,
            "screen_id": self.screen_id_counter,
            "timestamp": datetime.now().isoformat(),
            "metadata": {"title": await page.title()}
        }

    async def _deep_interact(self, page: Page, safe_path: str, depth: int) -> None:
        """Unified interaction logic for buttons, links, and dropdowns"""
        current_url = self._normalize_url(page.url)
        
        # 1. State Deduplication
        state_key = f"{current_url}|{await self._get_page_hash(page)}"
        if state_key in self.visited_states:
            return
        self.visited_states.add(state_key)
        
        # 2. Discovery & Sorting
        items = await self._discover_clickables(page)
        items = self._apply_priority_sorting(items)
        
        interaction_timeout = 600 # Increased for v6.0 (allows 100+ interactions)
        start_time = asyncio.get_event_loop().time()
        interaction_count = 0
        
        # 3. Interaction Loop
        for it in items[:self.config.max_interactions_per_page]:
            if asyncio.get_event_loop().time() - start_time > interaction_timeout:
                logger.warning("Overall interaction timeout reached")
                break

            # Elite Phase B: Graph-Aware Skipping
            start_state_id = self.current_state_id
            target_xpath = it['xpath']
            
            # Check if this interaction was already performed from this state
            already_done = any(
                e["from"] == start_state_id and 
                e["action"]["xpath"] == target_xpath 
                for e in self.state_graph["edges"]
            )
            if already_done:
                logger.info(f"Graph-Aware Skipping: Already explored {it['name']} from {start_state_id}")
                continue

            if target_xpath in self.interaction_history:
                continue
            self.interaction_history.add(target_xpath)
            
            locator = page.locator(f"xpath={target_xpath}")

            # v6.2 Elite Interaction Logic: Specialized handling for Selects and Toggles
            tag = it.get('tag', '').lower()
            role = it.get('role', '').lower()
            
            if tag == 'select':
                logger.info(f"Elite Interaction: Exhaustive Select on {it['name']}")
                try:
                    count = await locator.evaluate("el => el.options.length")
                    for idx in range(1, min(count, 4)): # Sample first 3 options
                        await locator.select_option(index=idx)
                        await self._re_extract_after_change(page, current_url)
                        # Note: Selects are complex for graph edges, usually same-state or simple shift.
                except: pass
            elif 'toggle' in it['name'].lower() or role == 'switch' or tag == 'input' and it.get('type') in ['checkbox', 'radio']:
                logger.info(f"Elite Interaction: Toggle states for {it['name']}")
                # Toggle ON (or just Click)
                await self._smart_click(page, target_xpath)
                await self._record_state_transition(page, start_state_id, {"type": "toggle_on", "xpath": target_xpath, "name": it["name"]})
                await self._re_extract_after_change(page, current_url)
                
                # Update start state for second part of toggle
                new_start = self.current_state_id
                # Toggle OFF (Click again)
                await self._smart_click(page, target_xpath)
                await self._record_state_transition(page, new_start, {"type": "toggle_off", "xpath": target_xpath, "name": it["name"]})
                await self._re_extract_after_change(page, current_url)
            else:
                # Standard Click
                success = await self._smart_click(page, target_xpath)
                
                if not success:
                    self.current_page_fails += 1
                    logger.warning(f"Interaction failed ({self.current_page_fails}/{self.config.max_consecutive_interaction_failures})")
                    if self.current_page_fails >= self.config.max_consecutive_interaction_failures:
                        logger.info("Threshold reached -> forcing rotation")
                        break 
                else:
                    self.current_page_fails = 0
                    self.total_interactions += 1
                    interaction_count += 1
                    
                    # Record Edge (Elite Phase B)
                    await self._record_state_transition(page, start_state_id, {"type": "click", "xpath": target_xpath, "name": it["name"]})

                    # Mutation check for standard clicks (revealing modals/menus)
                    await self._re_extract_after_change(page, current_url)

                    # Check for new links after interaction on same page
                    if depth < self.max_depth:
                        new_links = await self._discover_all_links(page)
                        for link in new_links:
                            await self._add_to_queue(link, depth + 1, current_url)
            
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=3000)
            except: pass


    async def _re_extract_after_change(self, page: Page, current_url: str):
        """Mutation detection: Capture new UI components revealed by previous interaction."""
        try:
            # Event-driven wait instead of hard timeout
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=2000)
            except: pass
            
            # Simple check: did the element count change?
            # Elite approach: JS to find all visual nodes
            safe_path = re.sub(r'\W+', '_', urlparse(current_url).path or "index")
            new_data = await self._extract_elements(page, f"{safe_path}_revealed")
            
            new_count = 0
            if new_data and new_data.get('elements'):
                for key, el in new_data['elements'].items():
                    # Only add if we haven't seen this fingerprint before
                    fingerprint = self._generate_element_fingerprint(el)
                    if fingerprint not in self.seen_fingerprints:
                        self.seen_fingerprints.add(fingerprint)
                        self.all_locators[f"revealed_{self.screen_id_counter}_{key}"] = el
                        new_count += 1
            
            if new_count > 0:
                logger.info(f"Mutation Engine: Discovered {new_count} new elements revealed via interaction")
        except Exception as e:
            logger.debug(f"Mutation re-extraction failed: {e}")

    async def _smart_click(self, page: Page, xpath: str, max_retries: int = 2):
        """Elite click with locator API, sync checks, and shadow DOM fallbacks (v4.2)."""
        # Elite Phase A: Coordinate-based click for Vision-discovered elements
        if xpath.startswith("point("):
            try:
                coords = re.findall(r'\d+', xpath)
                x, y = int(coords[0]), int(coords[1])
                logger.info(f"Visual Click: Interacting with coordinates ({x}, {y})")
                await page.mouse.click(x, y)
                return True
            except Exception as ve:
                logger.error(f"Visual Click failed: {ve}")
                return False

        locator_str = f"xpath={xpath}"
        # v6.3: Use .first to prevent strict mode violations for non-unique semantic XPaths
        locator = page.locator(locator_str).first
        
        # Pre-checks (sync in Playwright Python)
        try:
            count = await locator.count() 
            if count == 0:
                logger.error(f"Locator not found before click: {locator_str}")
                return False
            logger.debug(f"Pre-click locator count: {count}")
        except Exception as ce:

            logger.warning(f"Locator count failed: {ce}")

        for attempt in range(max_retries + 1):
            try:
                # 1. Wait for element (v6.3: 5s limit for faster traversal of hidden dropdowns)
                await locator.wait_for(state="visible", timeout=5000)

                # 2. Aggressive JS scroll + center
                await page.evaluate("""
                    (xpath) => {
                        const el = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        if (el) {
                            el.scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});
                        }
                    }
                """, xpath)
                
                # 3. Visibility check (sync!)
                try:
                    box = await locator.bounding_box()
                    v_size = page.viewport_size
                    if box and v_size and (box['y'] < 0 or box['y'] + box['height'] > v_size['height']):
                        if attempt < max_retries:
                            logger.debug(f"Element off-view after scroll (attempt {attempt+1}) -> retrying")
                            continue
                        logger.warning("Element remains off-view")
                except Exception as be:
                    logger.debug(f"Bounding box check failed: {be}")

                # Senior SDET: Capture pre-interaction state for outcome verification
                pre_url = page.url
                pre_content_hash = await self._get_page_hash(page)
                # v10/10 Logic: Network resource count as a signal for interaction processing
                pre_network_count = await page.evaluate("performance.getEntriesByType('resource').length")

                # 4. Native click with force (v6.3: 15s limit for interaction)
                await locator.click(force=True, timeout=15000)

                # 5. SDET Toggle & Select Logic
                is_select = await locator.evaluate("el => el.tagName.toLowerCase() === 'select'")
                if is_select:
                    try:
                        # For select elements, pick the first non-empty option
                        await locator.select_option(index=1)
                        logger.info(f"Selected option for {locator_str}")
                    except: pass
                
                # 6. Advanced stability wait (v4.3: pending resources only, ignore hovers)
                try:
                    await page.wait_for_function("""
                        () => {
                            const pending = performance.getEntriesByType('resource').filter(r => 
                                r.initiatorType !== 'xmlhttprequest' && r.initiatorType !== 'fetch'
                            ).filter(r => !r.responseEnd);
                            return pending.length === 0;
                        }
                    """, timeout=self.config.timeout_sec * 500) # Shorter stability check
                    await page.wait_for_load_state('domcontentloaded', timeout=1000) # Micro-sleep for visual stability
                except:
                    logger.debug("Minor stability timeout - continuing")
                
                # Senior SDET Refinement: 4-Way Outcome Verification (URL/Content/Network/Toast)
                post_url = page.url
                post_content_hash = await self._get_page_hash(page)
                post_network_count = await page.evaluate("performance.getEntriesByType('resource').length")
                
                # Toast/Notification check (v10/10 Polish)
                toast_text = ""
                try:
                    toast = await page.query_selector(".toast, .success-message, .error-message, [role='alert'], .ant-message-notice, [aria-live='polite'], [aria-live='assertive']")
                    if toast and await toast.is_visible():
                        toast_text = (await toast.inner_text()).strip()
                except: pass

                # Determine working status based on multiple signals
                is_nav = self._normalize_url(post_url) != self._normalize_url(pre_url)
                is_dom = post_content_hash != pre_content_hash
                is_net = post_network_count > pre_network_count
                
                if is_nav:
                    status = "working (navigation)"
                    logger.info(f"Outcome Detected: {locator_str} -> WORKING (Navigation to {post_url})")
                elif is_dom or is_net or toast_text:
                    status = "working (State/Network/Toast)"
                    logger.info(f"Outcome Detected: {locator_str} -> WORKING (DOM/Network changed or Toast: '{toast_text}')")
                else:
                    status = "potential_broken"
                    logger.warning(f"Outcome Detected: {locator_str} -> POTENTIAL_BROKEN (No identifiable change)")
                
                logger.info(f"Successful interaction: {locator_str} (Status: {status})")
                return True

            except Exception as e:
                logger.warning(f"Click attempt {attempt+1} failed: {str(e)[:200]}")
                # Diagnostic screenshot on failure
                try:
                    filename = f"interaction_failed_{int(datetime.now().timestamp())}.png"
                    fail_shot = os.path.join(self.debug_dir, filename)
                    await page.screenshot(path=fail_shot)
                    logger.info(f"Diagnostic screenshot saved to {fail_shot}")
                except: pass

                if attempt == max_retries:
                    # 6. Shadow-aware JS fallback (v4.2: Recursive dispatchEvent)
                    try:
                        logger.info(f"Triggering enhanced shadow-piercing JS fallback for {xpath}")
                        await page.evaluate("""
                            (xpath) => {
                                function deepClick(path) {
                                    // 1. Try standard Document Evaluation first
                                    try {
                                        const el = document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                                        if (el) return clickElement(el);
                                    } catch(e) {}

                                    // 2. Recursive Shadow DOM Piercing
                                    const idMatch = path.match(/@id="([^"]+)"/);
                                    const targetId = idMatch ? idMatch[1] : null;

                                    function search(root) {
                                        // Check current root if it's an ID search
                                        if (targetId && root.getElementById) {
                                            const found = root.getElementById(targetId);
                                            if (found) return found;
                                        }

                                        // Native querySelector (shadow-piercing for CSS but we have XPath)
                                        // If we have an ID, we can use CSS fallback inside the shadowRoot
                                        if (targetId) {
                                            try {
                                                const found = root.querySelector(`#${CSS.escape(targetId)}`);
                                                if (found) return found;
                                            } catch(e) {}
                                        }

                                        // Recurse into all children with shadowRoots
                                        const children = root.querySelectorAll('*');
                                        for (const child of children) {
                                            if (child.shadowRoot) {
                                                const found = search(child.shadowRoot);
                                                if (found) return found;
                                            }
                                        }
                                        return null;
                                    }

                                    function clickElement(el) {
                                        if (!el) return false;
                                        el.scrollIntoView({behavior: 'instant', block: 'center'});
                                        el.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                                        el.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
                                        el.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
                                        return true;
                                    }

                                    const target = search(document);
                                    return clickElement(target);
                                }

                                if (!deepClick(xpath)) {
                                    throw new Error("Element not found even in shadow DOM");
                                }
                            }
                        """, xpath)
                        await page.wait_for_load_state('domcontentloaded', timeout=1500)
                        logger.info(f"Shadow-piercing JS click success: {locator_str}")
                        return True
                    except Exception as js_err:
                        logger.error(f"JS fallback failed: {str(js_err)}")
                        raise
        return False

    async def _discover_clickables(self, page: Page) -> List[Dict]:
        script = """
        () => {
            const items = [];
            const all = document.querySelectorAll('button, a, input[type="submit"], input[type="checkbox"], input[type="radio"], select, [role="button"], [role="link"], [role="checkbox"], [role="menuitem"], .btn, .button');
            for (const el of all) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0 && getComputedStyle(el).visibility !== 'hidden') {
                    items.push({
                        tag: el.tagName.toLowerCase(),
                        name: (el.innerText || el.getAttribute('aria-label') || el.id || 'clickable').trim().substring(0, 50),
                        xpath: window.getSmartXPath(el),
                        y: rect.top + window.scrollY,
                        x: rect.left + window.scrollX
                    });
                }
            }
            return items;
        }
        """
        try:
            return await page.evaluate(script)
        except Exception as e:
            logger.debug(f"Handled failure in _discover_clickables: {str(e)}", exc_info=True)
            return []

    def _apply_priority_sorting(self, items: List[Dict]) -> List[Dict]:
        def get_prio(item):
            name = item['name'].lower()
            for i, kw in enumerate(self.config.priority_keywords):
                if kw.lower() in name: return i
            return 999
        return sorted(items, key=lambda x: (get_prio(x), x['y'], x['x']))

    async def _extract_revealed_elements(self, page: Page) -> List[Dict]:
        """Detect newly appeared elements after interaction (e.g. dropdowns)"""
        # Logic similar to _extract_elements but focused on new ones
        return [] # Simplified for now

    async def _detect_auth_page(self, page: Page) -> bool:
        """Elite auth detection: checks URL, inputs, and semantic signals."""
        url = page.url.lower()
        if any(p in url for p in ["/login", "/signin", "/signup", "/register", "/auth"]):
            return True
        
        # Check for password fields (high signal)
        pw_fields = await page.query_selector_all("input[type='password']")
        if pw_fields:
            return True
            
        return False

    async def _handle_auth(self, page: Page) -> bool:
        """v6.2 Universal Auth Handler: Implements retry loop and landing detection."""
        if not await self._detect_auth_page(page):
            return True
            
        creds = self.config.auth_creds
        if not creds or not creds.get('email'):
            logger.warning("Auth detected but no credentials provided. Skipping.")
            return False

        current_url = page.url
        for attempt in range(max(1, self.config.max_retries)):
            logger.info(f"Universal Auth Flow (Attempt {attempt+1}): {current_url}")
            success = await self._handle_login(page)
            if success:
                # v6.2 Landing Detection: Ensure we left the login wall
                try:
                    await page.wait_for_url(lambda u: not any(p in u.lower() for p in ["/login", "/signin"]), timeout=5000)
                    self.session_authenticated = True
                    return True
                except:
                    logger.warning("Login logic succeeded but still on auth URL pattern.")
            
            # Backoff before retry
            await page.screenshot(path=os.path.join(self.debug_dir, f"auth_fail_{attempt}.png"))
            await asyncio.sleep(2 ** attempt)
            if attempt < self.config.max_retries - 1:
                await page.goto(current_url)
        
        return False

    async def _handle_login(self, page: Page) -> bool:
        """Robust, universal login handler with granular error handling (v1.0 Generalization)"""
        creds = self.config.auth_creds
        if not creds or not creds.get('email'):
            logger.warning("No credentials provided for authentication.")
            return False

        email = creds.get('email')
        pwd = creds.get('password', '')

        try:
            logger.info(f"Initializing Unified Login Sequence for: {email[:3]}***@***")
            
            # 1. Ensure we are actually looking at a form (Wait for stability)
            await self._wait_for_stability(page, timeout_ms=3000)

            # 2. Email/Username Input
            logger.info("Attempting to fill email/username...")
            email_selector = "input[type='email'], input[name*='email'], input[name*='user'], #email, #username, #login-email"
            email_locator = page.locator(email_selector).first
            try:
                logger.info(f"Targeting email field: {email_selector}")
                await email_locator.wait_for(state="visible", timeout=10000)
                await email_locator.focus()
                await email_locator.fill("") # Clear
                await email_locator.press_sequentially(email, delay=100)
                logger.info("Email typed with sequential delays.")
                await page.screenshot(path=os.path.join(self.debug_dir, "debug_email_filled.png"))
            except Exception as e:
                logger.warning(f"Email field interaction failed: {e}")
                # Fallback to direct fill if focus/type failed
                try: 
                    await page.fill(email_selector, email)
                except: 
                    pass
                await page.screenshot(path=os.path.join(self.debug_dir, "debug_email_error.png"))
            
            # Handle potential multi-step form (Next button)
            try:
                next_btn = await page.wait_for_selector("button:has-text('Next'), button:has-text('Continue'), button:has-text('Sign in')", timeout=2000)
                if next_btn and await next_btn.is_visible():
                    await next_btn.click()
                    await page.wait_for_load_state('domcontentloaded', timeout=2000)
                    await page.screenshot(path=os.path.join(self.debug_dir, "debug_after_next.png"))
            except: 
                pass

            # 3. Password Input
            logger.info("Attempting to fill password...")
            pass_selector = "input[type='password'], [name*='password'], #password, #login-password"
            pass_locator = page.locator(pass_selector).first
            try:
                await pass_locator.wait_for(state="visible", timeout=5000)
                await pass_locator.focus()
                await pass_locator.fill("") # Clear
                await pass_locator.press_sequentially(pwd, delay=100)
                logger.info("Password typed with sequential delays.")
                await page.screenshot(path=os.path.join(self.debug_dir, "debug_pass_filled.png"))
            except Exception as e:
                logger.warning(f"Password field interaction failed: {e}")
                try: await page.fill(pass_selector, pwd)
                except: pass
                await page.screenshot(path=os.path.join(self.debug_dir, "debug_pass_error.png"))

            # 4. Submit
            logger.info("Submitting login form...")
            submit_selectors = [
                "button[type='submit']", 
                "button.login-button", 
                "button:has-text('Login')", 
                "button:has-text('Log In')",
                "button:has-text('Sign In')", 
                "button:has-text('Log in')",
                "button:has-text('Continue')",
                "[role='button']:has-text('Continue')"
            ]
            
            submit = None
            for selector in submit_selectors:
                try:
                    target = await page.query_selector(selector)
                    if target and await target.is_visible():
                        submit = target
                        logger.info(f"Found submit button: {selector}")
                        break
                except: continue

            if submit:
                await submit.click(force=True)
                logger.info("Submit button clicked (force=True).")
            else:
                await page.keyboard.press("Enter")
                logger.info("No submit button found, pressed Enter.")

            # 5. Wait for Success (Robust SDET Check)
            logger.info(f"Waiting for authentication success. Current URL: {page.url}")
            try:
                # v6.5 logic: URLs, Logout links, or Dashboard containers
                # Expanded for Clerk/SPA redirects
                await page.wait_for_function("""
                    () => {
                        const url = window.location.href;
                        const hasDashboard = url.includes('/dashboard') || url.includes('/projects') || url.includes('/home') || url.includes('/welcome') || url.includes('/app');
                        const hasLogout = document.querySelector('a[href*="/logout"], button:has-text("Logout"), a:has-text("Sign Out"), li:has-text("Logout"), [class*="cl-userButtonTrigger"]');
                        const hasDash = document.querySelector('.dashboard-container, #dashboard, .app-container, .dashboard_layout, .cl-root');
                        const isAuthPage = url.includes('/login') || url.includes('/signup');
                        return (hasDashboard && !isAuthPage) || hasLogout || (hasDash && !isAuthPage);
                    }
                """, timeout=20000)
                
                logger.info(f"Authentication SUCCESS! Landed on: {page.url}")
                self.session_authenticated = True
                await page.wait_for_load_state('networkidle', timeout=4000) # Final settlement wait
                return True
            except Exception as e:
                logger.warning(f"Auth signals timeout ({page.url}). Performing final heuristic check.")
                
                # Check for absence of login form as a success signal
                auth_state = await self._detect_auth_type(page)
                if auth_state == "NONE":
                    logger.info("No login/signup form detected and URL shifted. Assuming SUCCESS.")
                    self.session_authenticated = True
                    return True
                
                logger.error(f"Authentication FAILURE: Still in {auth_state} state.")
                return False

        except Exception as e:
            logger.error(f"Login process failed: {e}")
            await page.screenshot(path=os.path.join(self.debug_dir, "login_error_trace.png"))
            return False

    async def _detect_login(self, page: Page) -> bool:
        """Heuristic check if current page is a login page (v5.5: Shadow DOM aware)"""
        return (await self._detect_auth_type(page)) == "LOGIN"

    async def _probe_iframes_for_auth(self, page: Page) -> bool:
        """v6.0 Shadow Frame Diagnostics: Probes iframes for hidden auth forms (Clerk/Auth0/Stripe)"""
        iframes = await page.query_selector_all("iframe")
        if not iframes:
            return False
            
        logger.info(f"Probing {len(iframes)} iframes for hidden auth forms...")
        creds = self.config.auth_creds
        if not creds or not creds.get('email'):
            return False

        email = creds.get('email')
        pwd = creds.get('password', '')

        for iframe in iframes:
            try:
                frame = await iframe.content_frame()
                if not frame: continue
                
                # Search for password fields in frame
                pass_field = await frame.query_selector("input[type='password'], [name*='password']")
                if pass_field:
                    logger.info("Hidden auth form found in iframe! Attempting nested login...")
                    email_field = await frame.query_selector("input[type='email'], input[name*='email'], input[name*='user']")
                    if email_field:
                        await email_field.fill(email)
                        await pass_field.fill(pwd)
                        
                        # Find login button in frame
                        submit = await frame.query_selector("button[type='submit'], button:has-text('Sign In'), button:has-text('Log In')")
                        if submit:
                            await submit.click()
                            logger.info("Nested login submitted. Waiting for session sync...")
                            await page.wait_for_timeout(5000)
                            self.session_authenticated = True
                            return True
            except Exception as e:
                logger.debug(f"Iframe probe failed for one frame: {e}")
                continue
        return False

    async def _detect_auth_type(self, page: Page) -> str:
        """
        Differentiate between LOGIN, SIGNUP, and NONE based on page signals. (v6.2 Robustness)
        """
        url = page.url.lower()
        content = (await page.content()).lower()
        
        # 1. Signup Signals (Highest priority to avoid mis-authing)
        signup_patterns = ["signup", "register", "join", "create account", "create-account"]
        signup_fields = ["first name", "last name", "phone number", "confirm password"]
        
        has_signup_url = any(p in url for p in signup_patterns)
        has_signup_fields = any(f in content for f in signup_fields)
        
        # 2. Login Signals
        login_patterns = ["login", "signin", "auth", "account"]
        password_field = await page.locator("input[type='password']").count() > 0
        
        if (has_signup_url or has_signup_fields):
            logger.info("Heuristic: Signup page detected.")
            return "SIGNUP"
        
        if password_field or any(p in url for p in login_patterns):
            logger.info("Heuristic: Login page detected.")
            return "LOGIN"
            
        return "NONE"



    async def _get_page_hash(self, page: Page) -> str:
        """Robust content hash for outcome detection (v10/10 SDET)"""
        try:
            # slice(0, 1000) as requested for better accuracy
            return await page.evaluate("document.body.innerHTML.slice(0, 1000)")
        except:
            return ""

    def _generate_semantic_name(self, entry: dict) -> str:
        """Senior SDET Refined Naming Logic: Priority 1 Labels/Roles > Text"""
        # Priority 1: Custom Label (Merged label from label tags)
        if entry.get('customLabel'):
            name = entry['customLabel'].lower().replace(' ', '_').replace("'", "").replace('"', '')
        # Priority 2: aria-label
        elif entry.get('attributes', {}).get('aria-label'):
            name = entry['attributes']['aria-label'].lower().replace(' ', '_')
        # Priority 3: Role (if not default 'element')
        elif entry.get('role') and entry['role'] != 'element':
            name = entry['role'].lower()
        # Priority 4: Text Content (Truncated)
        elif entry.get('text'):
            name = entry['text'][:30].lower().replace(' ', '_').replace("'", "").replace('"', '')
        else:
            name = f"{entry.get('tag', 'element')}_el"

        # Sanitize
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)[:50]
        
        # Priority Collision Resistance: Guarantee uniqueness to prevent data loss in deduplication
        base_name = name
        counter = 1
        while name in self.seen_names:
            if counter == 1 and (entry.get('x', 0) != 0 or entry.get('y', 0) != 0):
                name = f"{base_name}_{int(entry.get('x', 0))}_{int(entry.get('y', 0))}"
            else:
                name = f"{base_name}_{counter}"
            counter += 1

        self.seen_names.add(name)
        return name[:64].strip('_')


    def _refine_element_name(self, name: str, el: Dict) -> str:
        """Quick rule-based refinement - no LLM cost as requested"""
        name = name.lower().replace(" ", "_").replace("-", "_")
        
        # Remove generic prefixes or placeholder names
        name = re.sub(r'^(span|div|element|item|clickable|i|section|main|header|footer)_\d+$', 'unknown', name)
        
        # Get important attributes
        tag = el.get('tag', '')
        if tag:
            tag = tag.lower()
        else:
            tag = ''
        role = (el.get('attributes', {}).get('role') or '').lower()
        
        # Boost priority tags with prefixes
        prefix = ""
        if tag == 'button' or role == 'button': prefix = "btn"
        elif tag == 'a' or role == 'link': prefix = "link"
        elif tag == 'input' or tag == 'textarea': prefix = "input"
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']: prefix = "heading"
        
        # Combine
        if prefix and not name.startswith(prefix):
            if name == 'unknown':
                name = prefix
            else:
                name = f"{prefix}_{name}"
            
        # Add role if present and not already emphasized
        if role and role not in name and role not in ['presentation', 'none']:
            name = f"{role}_{name}"
            
        # Clean up double underscores and length
        name = re.sub(r'_+', '_', name).strip('_')
        return name[:80]

    def _calculate_stability(self, el: Dict) -> int:
        score = 50
        if el['attributes'].get('dataTestId'): score += 40
        elif el['attributes'].get('id') and not re.search(r'\d{5,}', el['attributes']['id']): score += 30
        if el['playwright_selector']: score += 10
        return min(score, 100)
    
    
    def _is_testable_element(self, tag: str, attrs: dict, text: str) -> bool:
        # Drop labels entirely (merged client-side)
        if tag == 'label':
            return False

        # Drop pure structural div/span unless explicit role or onclick
        if tag in ['div', 'span', 'i', 'section']:
            # Check for interactive attributes
            is_interactive = any([
                attrs.get('role') in ['button', 'link', 'checkbox', 'radio', 'tab', 'menuitem'],
                attrs.get('onclick'),
                attrs.get('tabindex') is not None,
                # Short text might be a button label
                (text and len(text.strip()) < 50) 
            ])
            if not is_interactive:
                return False

        # Keep only high-signal elements (v5.4 leniency)
        if tag in ['input', 'button', 'a', 'select', 'textarea']:
            return True

        # Role-based or aria-label keep
        if attrs.get('role') in ['button', 'link', 'checkbox', 'radio', 'tab', 'option', 'menuitem'] or attrs.get('aria-label'):
            return True

        # Lenient text check for dynamic components (Snappod AI)
        if text and 0 < len(text.strip()) < 100:
            return True

        return False # Default reject noise
    
    def _generate_element_fingerprint(self, el: Dict) -> str:
        """Create high-entropy unique fingerprint based on semantic and structural traits."""
        tag = el['tag'].lower()
        attrs = el.get('attributes', {})
        text = (el.get('text') or '').strip()
        
        # Build components for SHA256 hash
        components = [
            tag,
            str(attrs.get('dataTestId') or ''),
            str(attrs.get('id') or ''),
            str(attrs.get('role') or ''),
            str(attrs.get('type') or ''),
            str(attrs.get('name') or ''),
            str(attrs.get('ariaLabel') or ''),
            str(attrs.get('placeholder') or '')
        ]
        
        # Add a snippet of text if it's long enough to be an identifier
        if text and len(text) > 4:
            # Normalize whitespace and limit length for stability
            clean_text = re.sub(r'\s+', ' ', text.lower()).strip()[:80]
            components.append(f"txt:{clean_text}")
        
        # Create hash
        fingerprint_string = "|".join(components)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    async def _validate_playwright_selector(self, page: Page, selector: str, expected_xpath: str) -> Tuple[bool, int]:
        """Validate that a Playwright selector is unique and finds the correct element."""
        try:
            # Simple validation: check if XPath finds exactly one element
            elements = await page.locator(f"xpath={expected_xpath}").all()
            count = len(elements)
            is_unique = count == 1
            return (is_unique, count)
        except Exception as e:
            logger.warning(f"Selector validation failed: {e}")
            return (False, 0)
    
    def _calculate_selector_quality(self, el: Dict, selector: str, is_unique: bool) -> int:
        """Score selector quality from 0-100."""
        if not is_unique:
            return 0  # Invalid selector
        
        score = 0
        attrs = el.get('attributes', {})
        
        # Best: data-testid
        if 'getByTestId' in selector:
            score = 95
        # Excellent: Stable ID
        elif attrs.get('id') and "locator('#" in selector:
            if not re.search(r'\d{5,}', attrs['id']):
                score = 90
            else:
                score = 60  # Dynamic ID
        # Very Good: Role + Name
        elif 'getByRole' in selector:
            score = 85
        # Good: Placeholder or Label
        elif 'getByPlaceholder' in selector or 'getByLabel' in selector:
            score = 80
        # Fair: Text content
        elif 'getByText' in selector:
            text_len = len(el.get('text', ''))
            score = 70 if text_len < 20 else 50
        # Poor: Class selectors
        elif "locator('." in selector:
            score = 40
        # Very Poor: XPath
        elif 'xpath=' in selector:
            score = 60 if '//*[@id=' in selector else 20
        else:
            score = 30
        
        return score

    async def _wait_for_stability(self, page: Page, timeout_ms: Optional[int] = None):
        t = timeout_ms if timeout_ms is not None else (self.config.timeout_sec * 1000)
        try:
            await page.wait_for_load_state("networkidle", timeout=t)
        except:
            pass # Best effort for stability
        await asyncio.sleep(0.5)

    async def _wait_for_network_idle(self):
        start = asyncio.get_event_loop().time()
        while len(self.active_requests) > 0 and (asyncio.get_event_loop().time() - start) < 5:
            await asyncio.sleep(0.2)

    async def _get_page_hash(self, page: Page) -> str:
        """v4.8: Advanced Semantic hashing with selector-based noise filtering."""
        try:
            # Script to get text but strip common dynamic patterns and specific noise selectors
            data = await page.evaluate("""() => {
                const clone = document.body.cloneNode(true);
                // Remove known dynamic items that break state tracking
                const ignoreSelectors = [
                    '.live-clock', '.counter', '[data-last-updated]', 'time', 
                    '.timestamp', '#view-counter', '.weather-widget',
                    '.ad-banner', '[role="timer"]', '.spinner', '.loading',
                    '[aria-live="polite"]'
                ];
                ignoreSelectors.forEach(sel => {
                    try {
                         clone.querySelectorAll(sel).forEach(el => el.remove());
                    } catch(e) {}
                });

                const text = clone.innerText || '';
                // Strip dates, times, and long sequences of numbers
                const cleanText = text.replace(/\\d{1,4}[\\-/:]\\d{1,4}[\\-/:]\\d{1,4}/g, 'DATE')
                                    .replace(/\\d{1,2}:\\d{1,2}(:\\d{1,2})?/g, 'TIME')
                                    .replace(/\\d{6,}/g, 'NUM')
                                    .trim();
                
                // Return raw concatenated string for Python hashing (btoa fails on non-Latin1)
                return cleanText + clone.querySelectorAll('*').length + clone.outerHTML.substring(0, 1000);
            }""")
            return hashlib.sha256(data.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"ERROR in _get_page_hash: {e}")
            return "ERROR_HASH"

    def _get_clean_page_context(self, html: str) -> str:
        """
        'Page Scalpel': Strips HTML of non-visual nodes to get a clean semantic representation.
        Inspired by Crawl4AI's Markdown extraction.
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts, styles, and other metadata
            for tag in soup(['script', 'style', 'meta', 'link', 'noscript', 'svg', 'iframe']):
                tag.decompose()
            
            # Extract basic structure
            lines = []
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'button', 'input', 'label']):
                tag = element.name
                text = element.get_text(strip=True)
                if not text and tag not in ['input']:
                    continue
                
                # Add role or type if available
                attr_info = ""
                if tag == 'input':
                    attr_info = f" [type={element.get('type', 'text')}, name={element.get('name', '')}]"
                elif tag == 'a':
                    attr_info = f" [href={element.get('href', '')}]"
                
                lines.append(f"<{tag}>{text}{attr_info}")
                
            return "\n".join(lines[:150]) # Limit context size
        except Exception as e:
            logger.error(f"Error in _get_clean_page_context: {e}")
            return ""

    async def _discover_semantic_components(self, page: Page) -> Dict[str, str]:
        """
        Uses AI to identify logical UI components on the page.
        """
        if not self.client or not self.config.use_ai:
            return {}

        try:
            source = await page.content()
            clean_context = self._get_clean_page_context(source)
            if not clean_context:
                return {}

            prompt = f"""
            Analyze the following website structure and identify the main logical UI components.
            Group the items into areas like: 'Navigation', 'Search', 'Auth', 'Main Content', 'Footer', etc.
            
            STRUCTURE:
            {clean_context}
            
            Return a JSON object mapping specific keywords or identifiers to their logical group.
            Example: {{"login": "Auth", "cart": "Shopping", "search": "Discovery"}}
            """
            
            # Rotation Logic
            max_retries = 4
            response = None
            
            for attempt in range(max_retries):
                try:
                    response = await self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    break # Success
                except Exception as req_err:
                    # Check for Rate Limit
                    err_str = str(req_err)
                    if "429" in err_str:
                        logger.warning(f"Groq Rate Limit (Key {self.groq_key_index + 1}/{len(self.groq_keys)}). Rotating...")
                        if self.groq_keys:
                            self.groq_key_index = (self.groq_key_index + 1) % len(self.groq_keys)
                            self.client = AsyncGroq(api_key=self.groq_keys[self.groq_key_index])
                            await asyncio.sleep(1)
                            continue
                    
                    if attempt == max_retries - 1:
                        raise req_err # Rethrow if last attempt
                    await asyncio.sleep(1)
            
            if not response:
                return {}
            
            try:
                result = json.loads(response.choices[0].message.content)
                if isinstance(result, dict):
                    return result
                logger.warning(f"Semantic discovery returned non-dict: {type(result)}")
                return {}
            except Exception as ej:
                logger.error(f"Error parsing semantic JSON: {ej}")
                return {}
        except Exception as e:
            logger.warning(f"Semantic component discovery failed: {e}")
            return {}

    # Redundant _normalize_url removed (using the robust one at line 363)

    async def _smart_scroll(self, page: Page):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await page.evaluate("window.scrollTo(0, 0)")

    async def _auto_consent(self, page: Page):
        """v5.2: Enhanced Shadow-piercing Consent Nuke with forced clicks."""
        # 1. JS Nuke: Forcibly hide common modal/overlay patterns
        nuke_script = """
        () => {
            const genericSelectors = [
                '[id*="cookie"]', '[class*="cookie"]', '[id*="consent"]', '[class*="consent"]',
                '[id*="privacy"]', '[class*="privacy"]'
            ];
            genericSelectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    if (el.innerText.toLowerCase().includes('accept') || el.innerText.toLowerCase().includes('agree')) {
                         el.style.display = 'none';
                         el.style.pointerEvents = 'none';
                    }
                });
            });
        }
        """
        try: await page.evaluate(nuke_script)
        except: pass

        # 2. High-confidence phrases (Safe to click links/buttons)
        safe_phrases = ["accept all", "accept cookies", "allow all", "i agree", "got it", "allow selection", "manage cookies"]
        
        for text in safe_phrases:
            try:
                el = await page.query_selector(f"button:has-text('{text}'), a:has-text('{text}'), [role='button']:has-text('{text}')")
                if el and await el.is_visible():
                    await el.click(force=True, timeout=1000)
                    logger.info(f"Auto-consent SAFE click: {text}")
            except Exception: pass

        # 3. Risky single words (Buttons ONLY)
        risky_words = ["accept", "agree", "allow", "ok", "consent"]
        for text in risky_words:
            try:
                el = await page.query_selector(f"button:has-text('{text}'), [role='button']:has-text('{text}')")
                if el and await el.is_visible():
                    content = await el.inner_text()
                    if len(content) < 40: 
                        await el.click(force=True, timeout=1000)
                        logger.info(f"Auto-consent STRICT button click: {text}")
            except Exception: pass

    async def _auto_interact(self, page: Page):
        """Intelligent form-filling and dropdown expansion."""
        
        # 1. Expand Dropdowns/Accordions (NEW)
        try:
            # Click potential toggles
            await page.evaluate("""
                () => {
                    document.querySelectorAll('.dropdown-toggle, [aria-haspopup="true"], [data-toggle="dropdown"]').forEach(el => {
                       if (el.offsetParent !== null) {
                           try { el.click(); } catch(e) {}
                       } 
                    });
                }
            """)
            await asyncio.sleep(0.5) 
        except Exception: pass

        inputs = await page.query_selector_all("input:not([type='hidden']), textarea, select")
        for inp in inputs:
            try:
                tag = await inp.evaluate("el => el.tagName.toLowerCase()")
                type_attr = str(await inp.get_attribute("type") or "").lower()
                name = str(await inp.get_attribute("name") or "").lower()
                id_attr = str(await inp.get_attribute("id") or "").lower()
                placeholder = str(await inp.get_attribute("placeholder") or "").lower()
                label = await inp.evaluate("el => el.labels && el.labels[0] ? el.labels[0].innerText : ''")
                target_str = (name + " " + id_attr + " " + placeholder + " " + label).lower()

                # Basic check for already filled
                if await inp.evaluate("el => el.value"):
                    continue

                # 1. Datepicker Rule
                if any(word in target_str for word in ["date", "datepicker", "birthday"]):
                    await inp.click() # Open picker
                    await asyncio.sleep(1)
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
                    await page.keyboard.type(tomorrow)
                    await page.keyboard.press("Enter")
                    logger.info(f"Filled datefield with {tomorrow}")

                # 2. File Upload Rule
                elif type_attr == "file" or "upload" in target_str:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                        tmp.write(b"Dummy test file content for Formy upload.")
                        dummy_path = tmp.name
                    await inp.set_input_files(dummy_path)
                    logger.info(f"Uploaded dummy file: {dummy_path}")
                    # Note: file remains to ensure upload completes, OS will usually clean temp

                # 3. Autocomplete / Search Rule
                elif "autocomplete" in target_str or "search" in name:
                    await inp.type("Los Angeles")
                    await asyncio.sleep(1)
                    await page.keyboard.press("ArrowDown")
                    await page.keyboard.press("Enter")
                    logger.info("Autocomplete selected")

                # 4. Checkbox Rule
                elif type_attr == "checkbox" or "terms" in target_str:
                    if not await inp.is_checked():
                        await inp.check()
                        logger.info("Checked checkbox")

                # 5. Radio Button Rule
                elif type_attr == "radio":
                    if not await inp.is_checked():
                        await inp.check()
                        logger.info("Selected radio option")
                
                # 6. Generic Catch-all
                elif type_attr in ['text', 'email', 'password', 'tel', 'url', 'number', '']:
                    val = "Test Data"
                    if "email" in target_str: 
                        val = self.config.auth_creds.get('email', "test@example.com") if self.config.auth_creds else "test@example.com"
                    elif "password" in target_str:
                        val = self.config.auth_creds.get('password', "TestPass123") if self.config.auth_creds else "TestPass123"
                    elif "phone" in target_str: val = "555-0199"
                    elif "zip" in target_str: val = "90210"
                    
                    try:
                        await inp.fill(val)
                        logger.info(f"Auto-filled generic {type_attr}: {val}")
                    except: pass

            except Exception as e:
                logger.debug(f"Form-fill skipped for element: {e}")

        # 7. Button/Toggle/Input Clicking (NEW - User Request)
        try:
             # Click buttons that might reveal content, and checkboxes/radios
             await page.evaluate("""
                () => {
                    const clickables = document.querySelectorAll('button:not([type="submit"]), [role="button"], div.btn, span.btn, input[type="checkbox"], input[type="radio"], input[type="file"]');
                    clickables.forEach(el => {
                        // Avoid obvious navigation
                        if (el.closest('a')) return;
                        
                        const text = (el.innerText || el.value || "").toLowerCase();
                        if (text.includes('submit') || text.includes('save') || text.includes('login') || text.includes('sign in')) return;

                        if (el.offsetParent !== null) {
                             try { 
                                 // For checkboxes/radios, only click if not checked
                                 if ((el.type === 'checkbox' || el.type === 'radio') && el.checked) return;
                                 
                                 el.click(); 
                             } catch(e) {}
                        }
                    });
                }
             """)
             await asyncio.sleep(0.5)
        except Exception: pass

    def _get_js_helpers(self) -> str:
        return """
        function getSmartXPath(el) {
            const isDynamic = (id) => {
                if (!id) return false;
                // Helper function to check for common dynamic patterns
                function isLikelyDynamic(id) {
                    return /\\d{5,}/.test(id) || /[a-f0-9-]{32,}/.test(id);
                }
                return isLikelyDynamic(id) ||
                       /^[0-9a-f]{8}-[0-9a-f]{4}/i.test(id) ||
                       /^radix-/.test(id) ||
                       /^headlessui-/.test(id) ||
                       /^cl-/.test(id);
            };

            // 1. Stable semantic attributes first
            const testId = el.getAttribute('data-testid') || el.getAttribute('data-test-id');
            if (testId) return `//*[@data-testid="${testId}"]`;
            
            const ariaLabel = el.getAttribute('aria-label');
            if (ariaLabel) return `//*[contains(@aria-label, "${ariaLabel}")]`;

            if (el.id && !isDynamic(el.id)) return `//*[@id="${el.id}"]`;

            // 2. Specialized handling for buttons/links with unique text
            const tag = el.tagName.toLowerCase();
            if (['button', 'a'].includes(tag)) {
                const text = el.innerText.trim();
                if (text && text.length > 2 && text.length < 50) {
                    // check if text is unique enough (simplified)
                    return `//${tag}[contains(text(), "${text}")]`;
                }
            }
            
            // 3. Form elements by name
            const name = el.getAttribute('name');
            if (name && !isDynamic(name)) return `//${tag}[@name="${name}"]`;

            // 4. Relative Path (Nearest stable ID)
            let current = el;
            let path = '';
            while (current && current.nodeType === 1 && current !== document.body) {
                if (current.id && !isDynamic(current.id)) {
                    return `//*[@id="${current.id}"]` + path;
                }
                let index = 1;
                for (let sib = current.previousSibling; sib; sib = sib.previousSibling) {
                    if (sib.nodeType === 1 && sib.tagName === current.tagName) index++;
                }
                path = '/' + current.tagName.toLowerCase() + '[' + index + ']' + path;
                current = current.parentNode;
            }

            if (el === document.body) return '/html/body';
            return '/html/body' + path;
        }

        function getSmartCSS(el) {
            if (el.id) return '#' + el.id;
            if (el.className && typeof el.className === 'string') {
                const classes = el.className.split(/\\s+/).filter(c => c && !c.match(/\\d/)).join('.');
                if (classes) return el.tagName.toLowerCase() + '.' + classes;
            }
            return el.tagName.toLowerCase();
        }

        function getPlaywrightSelector(el) {
             return ""; // Placeholder
        }

        function getAllElements(root = document, includeHidden = false) {
            const result = [];

            function walk(node, depth = 0) {
                if (depth > 20) return; // Increased depth for modern frameworks
                if (!node) return;

                const nodeType = node.nodeType;
                const tag = (node.tagName || "").toLowerCase();

                // 1. Process as Element
                if (nodeType === 1) {
                    if (['script', 'style', 'noscript', 'meta', 'link', 'head'].includes(tag)) return;

                    // Visibility check
                    if (!includeHidden) {
                        const style = window.getComputedStyle(node);
                        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                        return;
                    }
                }

                // v5.4: Shadow DOM Traversal
                if (node.shadowRoot) {
                    walk(node.shadowRoot, depth + 1);
                }

                    // Special handling for labels
                    if (tag === 'label') {
                        const forId = node.getAttribute('for');
                        if (forId) {
                            const control = document.getElementById(forId) || document.querySelector(`[name="${forId}"]`);
                            if (control) {
                                control.setAttribute('data-custom-label', node.innerText.trim());
                                // We still walk labels because they might contain other things, 
                                // but we skip saving them if they are pure text labels for an ID
                            }
                        }
                    }

                    // Collect meaningful elements
                    const rect = node.getBoundingClientRect();
                    
                    // Elite Phase 20 (DOM Event Fuzzing): Discover hidden handlers in SPAs
                    const computedStyle = window.getComputedStyle(node);
                    const hasPointer = computedStyle.cursor === 'pointer';
                    const hasClickHandler = !!node.onclick || !!node.onmousedown || !!node.getAttribute('onclick') || !!node.getAttribute('ng-click') || !!node.getAttribute('@click') || !!node.getAttribute('v-on:click');
                    const isSemanticInteractive = ['input', 'button', 'a', 'select', 'textarea', 'details', 'summary'].includes(tag);
                    const hasInteractiveRole = ['button', 'link', 'menuitem', 'tab', 'switch', 'checkbox', 'radio'].includes(node.getAttribute('role'));
                    
                    const entry = {
                        tag: tag,
                        text: (node.innerText || '').trim().slice(0, 100),
                        xpath: getSmartXPath(node),
                        css: getSmartCSS(node),
                        role: node.getAttribute('role') || '',
                        id: node.id || '',
                        name: node.getAttribute('name') || '',
                        type: node.getAttribute('type') || '',
                        placeholder: node.getAttribute('placeholder') || '',
                        ariaLabel: node.getAttribute('aria-label') || '',
                        dataTestId: node.getAttribute('data-testid') || '',
                        customLabel: node.getAttribute('data-custom-label') || '',
                        isInteractive: isSemanticInteractive || hasInteractiveRole || hasClickHandler || hasPointer,
                        attributes: {
                             href: node.getAttribute('href'),
                             src: node.getAttribute('src'),
                             class: node.className
                        },
                        x: Math.round(rect.left + window.scrollX),
                        y: Math.round(rect.top + window.scrollY)
                    };

                    // Cleanup empty fields as requested by user
                    ['role', 'name', 'type', 'placeholder', 'ariaLabel', 'dataTestId', 'customLabel'].forEach(key => {
                        if (entry[key] === '') delete entry[key];
                    });

                    // Elite Filtering in JS: Limit the DOM memory footprint by rejecting pure noise early
                    if (entry.isInteractive || entry.role || entry.id || entry.ariaLabel || entry.customLabel || (entry.text && entry.text.length > 0)) {
                        result.push(entry);
                    } else {
                        // pure empty container - skip
                        return; 
                    }
                }

                // 2. Recurse into children (Elements, Document, ShadowRoot)
                if (node.shadowRoot) walk(node.shadowRoot, depth + 1);
                
                const children = node.children || node.childNodes;
                if (children) {
                    Array.from(children).forEach(child => walk(child, depth + 1));
                }
            }

            walk(root);
            return result;
        }
        
        function getRelativeXPath(el) { return ""; } // Placeholder

        window.getAllElements = getAllElements;
        window.getSmartXPath = getSmartXPath;
        window.getSmartCSS = getSmartCSS;
        window.getPlaywrightSelector = getPlaywrightSelector;
        """



    async def _record_state_transition(self, page: Page, from_id: str, action: Dict):
        """Elite Phase B: Captures resulting state and adds edge to graph."""
        new_hash = await self._get_page_hash(page)
        new_url = self._normalize_url(page.url)
        to_id = f"{new_url}::{new_hash}"
        
        # Ensure 'to' node exists
        if to_id not in self.state_graph["nodes"]:
            self.state_graph["nodes"][to_id] = {
                "url": new_url,
                "hash": new_hash,
                "discovered_via": from_id,
                "visited_at": datetime.now().isoformat()
            }

        # Add Edge
        edge = {"from": from_id, "to": to_id, "action": action}
        # Check uniqueness of edge
        is_duplicate = any(e["from"] == edge["from"] and e["to"] == edge["to"] and e["action"]["xpath"] == edge["action"]["xpath"] for e in self.state_graph["edges"])
        if not is_duplicate:
            self.state_graph["edges"].append(edge)
            logger.info(f"Graph Edge recorded: {from_id} --[{action['type']}:{action.get('name', 'unnamed')}]--> {to_id}")
        
        # Update pointer
        self.current_state_id = to_id

    async def _self_heal_to_state(self, page: Page, target_state_id: str) -> bool:
        """Elite Phase B: Session recovery via pathfinding in the state graph."""
        logger.info(f"Self-Healing sequence triggered for state: {target_state_id}")
        
        # 1. Reset to entry point
        await page.goto(self.config.url)
        await self._wait_for_stability(page)
        
        start_hash = await self._get_page_hash(page)
        start_state_id = f"{self._normalize_url(page.url)}::{start_hash}"
        
        # 2. Find path (BFS for shortest path in transitions)
        path = self._find_path(start_state_id, target_state_id)
        if not path:
            logger.error(f"No path found in state graph to {target_state_id}. Self-healing failed.")
            return False
            
        logger.info(f"Path discovered ({len(path)} steps). Executing recovery...")
        
        # 3. Follow the path
        for edge in path:
            action = edge["action"]
            logger.info(f"Recovery Step: {action['type']} on {action['xpath']} ({action.get('name')})")
            
            if action["type"] in ["click", "toggle_on", "toggle_off"]:
                success = await self._smart_click(page, action["xpath"])
                if not success:
                    logger.error("Recovery step failed. Session state corrupted.")
                    return False
            
            await self._wait_for_stability(page)
            
        # 4. Final Verification
        final_hash = await self._get_page_hash(page)
        final_state_id = f"{self._normalize_url(page.url)}::{final_hash}"
        if final_state_id == target_state_id:
            logger.info("Self-healing SUCCESSful. Session restored.")
            self.current_state_id = target_state_id
            return True
        else:
            logger.warning(f"Self-healing landed on {final_state_id} instead of {target_state_id}.")
            return False

    def _find_path(self, start_id: str, target_id: str) -> Optional[List[Dict]]:
        """Dictionary-based BFS for pathfinding in the state graph (Dijkstra-lite)."""
        if start_id == target_id:
            return []
            
        queue = [(start_id, [])]
        visited = {start_id}
        
        while queue:
            node_tuple = queue.pop(0)
            curr_id = node_tuple[0]
            path = node_tuple[1]
            
            # Find all outgoing edges from curr_id
            for edge in self.state_graph["edges"]:
                if edge["from"] == curr_id:
                    next_id = edge["to"]
                    if next_id == target_id:
                        return path + [edge]
                    if next_id not in visited:
                        visited.add(next_id)
                        queue.append((next_id, path + [edge]))
        return None

    def _save_consolidated_locators(self) -> str:
        # Ensure locators_root directory exists
        os.makedirs(self.locators_root, exist_ok=True)
        
        # Save as Python dict (legacy)
        py_path = os.path.join(self.locators_root, 'all_locators.py')
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(f"locators = {json.dumps(self.all_locators, indent=4)}\n")
            f.write(f"state_graph = {json.dumps(self.state_graph, indent=4)}\n")
        
        # Save as pure JSON (for dashboard/next agents)
        json_path = os.path.join(self.locators_root, 'consolidated_locators.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "locators": self.all_locators,
                "state_graph": self.state_graph,
                "metadata": {
                    "total_pages": len(self.finished_urls),
                    "total_locators": len(self.all_locators),
                    "timestamp": datetime.now().isoformat()
                }
            }, f, indent=4)
        return json_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QA Garden Crawler - Elite Reliability Edition (v4)")
    parser.add_argument("--url", type=str, required=True, help="Target URL")
    parser.add_argument("--max-depth", type=int, default=2, help="Max crawl depth")
    parser.add_argument("--max-pages", type=int, default=10, help="Max pages")
    parser.add_argument("--dynamic", action="store_true", help="Enable dynamic discovery")
    parser.add_argument("--camoufox", action="store_true", default=False, help="Use Camoufox stealth")
    parser.add_argument("--headless", action="store_true", help="Force headless mode")
    parser.add_argument("--respect_robots", type=str, default="True", help="Respect robots.txt (True/False)")
    parser.add_argument("--use-ai", action="store_true", help="Enable AI-driven naming and navigation")
    parser.add_argument("--exclude", nargs='*', help="List of URL paths to exclude")
    
    args = parser.parse_args()
    
    # Handle boolean for respect_robots
    respect_robots = args.respect_robots.lower() == "true"
    
    # Auto-load credentials from environment if available
    import os
    env_email = os.environ.get("SNAPPOD_TEST_EMAIL")
    env_pwd = os.environ.get("SNAPPOD_TEST_PASSWORD")
    auth_creds = None
    if env_email and env_pwd:
        auth_creds = {"email": env_email, "password": env_pwd}

    config = CrawlerConfig(
        url=args.url,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
        dynamic_crawl=args.dynamic,
        use_camoufox=args.camoufox,
        headless=args.headless,
        respect_robots=respect_robots,
        exclude_paths=args.exclude if args.exclude else [],
        auth_creds=auth_creds,
        use_ai=args.use_ai
    )
    
    crawler = QAGardenCrawler(config)
    
    async def main():
        async for update in crawler.run():
            if update.get("type") == "log":
                print(f"[{update.get('level', 'INFO')}] {update.get('message')}")
            elif update.get("type") == "page_complete":
                print(f"--- Completed: {update.get('url')} (Total Locators: {update.get('total_locators', 0)}) ---")
            elif update.get("type") == "crawl_complete":
                print(f"Crawl finished. Locators saved to: {update.get('locators_path')}")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCrawl Aborted.")
