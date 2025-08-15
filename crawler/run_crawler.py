#!/usr/bin/env python3
"""
Simple script to run Myntra crawlers
"""

import os
import sys
import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_products_crawler(category=None, max_pages=5, use_api=False):
    """Run the 3P products crawler"""

    settings = get_project_settings()
    process = CrawlerProcess(settings)

    spider_kwargs = {"max_pages": max_pages}
    if category:
        spider_kwargs["category"] = category

    # Choose between API spider and HTML spider
    spider_name = "myntra_api_products" if use_api else "myntra_products"
    process.crawl(spider_name, **spider_kwargs)
    process.start()


def run_user_data_crawler(email, password, headless=True):
    """Run the 2P user data crawler"""

    if not email or not password:
        print("Error: Email and password are required for user data crawler")
        return

    settings = get_project_settings()
    process = CrawlerProcess(settings)

    process.crawl("myntra_user_data", email=email, password=password, headless=headless)
    process.start()


def main():
    parser = argparse.ArgumentParser(description="Run Myntra Crawlers")
    parser.add_argument(
        "crawler_type", choices=["products", "user_data"], help="Type of crawler to run"
    )

    # Products crawler arguments
    parser.add_argument(
        "--category", help="Specific category to crawl (e.g., men-clothing)"
    )
    parser.add_argument(
        "--max-pages", type=int, default=5, help="Maximum pages to crawl per category"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Use API-based crawler instead of HTML parsing",
    )

    # User data crawler arguments
    parser.add_argument(
        "--email", help="Email for login (required for user_data crawler)"
    )
    parser.add_argument(
        "--password", help="Password for login (required for user_data crawler)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode",
    )

    args = parser.parse_args()

    # Ensure we're in the right directory
    if not os.path.exists("scrapy.cfg"):
        print("Error: Please run this script from the crawler directory")
        sys.exit(1)

    if args.crawler_type == "products":
        crawler_type = "API-based" if args.api else "HTML-based"
        print(f"Starting {crawler_type} products crawler...")
        if args.category:
            print(f"Category: {args.category}")
        print(f"Max pages: {args.max_pages}")

        run_products_crawler(
            category=args.category, max_pages=args.max_pages, use_api=args.api
        )

    elif args.crawler_type == "user_data":
        if not args.email or not args.password:
            print("Error: --email and --password are required for user_data crawler")
            sys.exit(1)

        print(f"Starting user data crawler...")
        print(f"Email: {args.email}")
        print(f"Headless: {args.headless}")

        run_user_data_crawler(
            email=args.email, password=args.password, headless=args.headless
        )


if __name__ == "__main__":
    main()
