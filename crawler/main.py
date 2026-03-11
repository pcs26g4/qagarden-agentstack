#!/usr/bin/env python3
import asyncio
import os
import argparse

from qa_garden_crawler import QAGardenCrawler
from config import CrawlerConfig
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def main():
    parser = argparse.ArgumentParser(
        description="QA Garden Crawler: AI-Augmented Web Explorer"
    )

    parser.add_argument("urls", nargs="*", help="Target URLs to crawl")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", action="store_false", dest="headless")
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--depth", type=int, default=3)

    # Optimization Arguments
    parser.add_argument("--use-ai", action="store_true")
    parser.add_argument("--ai-depth", type=int, default=1)
    parser.add_argument("--ai-timeout", type=int, default=60)
    parser.add_argument("--strict", action="store_true", default=True)
    parser.add_argument("--no-strict", action="store_false", dest="strict")
    parser.add_argument("--dynamic", action="store_true")
    parser.add_argument("--exclude", nargs="*")
    parser.add_argument("--camoufox", action="store_true")
    parser.add_argument("--max-interactions", type=int, default=8)
    parser.add_argument("--robots", action="store_true")

    args = parser.parse_args()

    # Get URLs from CLI or .env
    target_urls = args.urls or (
        [os.getenv("TARGET_URL")] if os.getenv("TARGET_URL") else []
    )

    if not target_urls:
        print(
            "ERROR: No URLs provided.\n"
            "Usage: python main.py <url1> <url2> ... [--use-ai] [--strict]"
        )
        return

    async def run_crawler_for_url(url):
        print("\n" + "=" * 60)
        print(f"Starting QA Garden Crawler for {url}")
        print(
            f"Mode: {'AI-Enhanced' if args.use_ai else 'Standard Fast'} | "
            f"Strict Filtering: {args.strict} | Camoufox: {args.camoufox}"
        )
        print("=" * 60 + "\n")

        auth_creds = None
        email = os.getenv("LOGIN_EMAIL")
        password = os.getenv("LOGIN_PASSWORD")

        if email and password:
            auth_creds = {"email": email, "password": password}

        config = CrawlerConfig(
            url=url,
            max_pages=args.max_pages,
            max_depth=args.depth,
            headless=args.headless,
            use_ai=args.use_ai,
            ai_max_depth=args.ai_depth,
            strict_element_filtering=args.strict,
            dynamic_crawl=args.dynamic,
            exclude_paths=args.exclude if args.exclude else [],
            use_camoufox=args.camoufox,
            auth_creds=auth_creds,
            ai_timeout_sec=args.ai_timeout,
            max_interactions_per_page=args.max_interactions,
            respect_robots=args.robots,
        )

        crawler = QAGardenCrawler(config)

        async for event in crawler.run():
            e_type = event.get("event")

            if e_type == "progress":
                print(f"[{event.get('depth', 0)}] Processing: {event.get('url')}")
            elif e_type == "pages_discovered":
                print(f"   -> Discovered {event.get('count')} links")
            elif e_type == "log":
                print(f"   -> {event.get('message')}")
            elif e_type == "completed":
                print(f"\nSUCCESS: {event.get('coverage_metric')}")
                if event.get("path"):
                    print(f"Output saved to: {event.get('path')}")

    async def run_all():
        for url in target_urls:
            try:
                await run_crawler_for_url(url)
            except Exception as e:
                print(f"\nError crawling {url}: {e}")
                import traceback

                traceback.print_exc()

    try:
        asyncio.run(run_all())
    except KeyboardInterrupt:
        print("\nCrawl stopped by user.")


if __name__ == "__main__":
    main()