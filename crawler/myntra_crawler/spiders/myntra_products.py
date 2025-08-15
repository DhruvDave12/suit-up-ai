import scrapy
import json
import re
from urllib.parse import urljoin, urlparse, parse_qs
from myntra_crawler.items import ProductItem


class MyntraProductsSpider(scrapy.Spider):
    """3P Crawler: Scrapes public product data from Myntra"""

    name = "myntra_products"
    allowed_domains = ["myntra.com"]

    # Start URLs for different categories
    start_urls = [
        "https://www.myntra.com/men-clothing",
        "https://www.myntra.com/women-clothing",
        "https://www.myntra.com/men-footwear",
        "https://www.myntra.com/women-footwear",
        "https://www.myntra.com/men-accessories",
        "https://www.myntra.com/women-accessories",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": 0.5,
    }

    def __init__(self, category=None, max_pages=5, *args, **kwargs):
        super(MyntraProductsSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.pages_scraped = {}

        # If specific category is provided, override start_urls
        if category:
            self.start_urls = [f"https://www.myntra.com/{category}"]

    def start_requests(self):
        """Generate initial requests"""
        for url in self.start_urls:
            category = url.split("/")[-1]
            self.pages_scraped[category] = 0

            yield scrapy.Request(
                url=url, callback=self.parse_category_page, meta={"category": category}
            )

    def parse_category_page(self, response):
        """Parse category page to extract product URLs"""
        category = response.meta["category"]

        # Extract product URLs using CSS selectors (based on Myntra's structure)
        product_links = response.css('a[href*="/buy/"]::attr(href)').getall()

        # Clean and convert to absolute URLs
        for link in product_links:
            if link:
                product_url = urljoin(response.url, link)
                yield scrapy.Request(
                    url=product_url,
                    callback=self.parse_product,
                    meta={"category": category},
                )

        # Handle pagination
        self.pages_scraped[category] += 1
        if self.pages_scraped[category] < self.max_pages:
            # Look for next page link
            next_page = response.css('a[aria-label="Next"]::attr(href)').get()
            if next_page:
                next_url = urljoin(response.url, next_page)
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_category_page,
                    meta={"category": category},
                )

    def parse_product(self, response):
        """Parse individual product page"""
        category = response.meta["category"]

        try:
            # Try to extract JSON data from script tags
            json_scripts = response.css(
                'script[type="application/ld+json"]::text'
            ).getall()
            product_data = {}

            for script in json_scripts:
                try:
                    data = json.loads(script)
                    if isinstance(data, dict) and data.get("@type") == "Product":
                        product_data = data
                        break
                except json.JSONDecodeError:
                    continue

            # Extract product ID from URL
            product_id = self.extract_product_id(response.url)

            # Create product item
            item = ProductItem()

            # Basic info
            item["product_id"] = product_id
            item["product_url"] = response.url
            item["category"] = category

            # Extract from JSON-LD if available
            if product_data:
                item["name"] = product_data.get("name", "")
                item["brand"] = product_data.get("brand", {}).get("name", "")
                item["description"] = product_data.get("description", "")

                # Price info
                offers = product_data.get("offers", {})
                item["price"] = offers.get("price", "")
                item["discount_price"] = offers.get("price", "")

                # Images
                images = product_data.get("image", [])
                if isinstance(images, list):
                    item["images"] = images
                else:
                    item["images"] = [images] if images else []

                # Rating
                rating_data = product_data.get("aggregateRating", {})
                item["rating"] = rating_data.get("ratingValue", "")
                item["rating_count"] = rating_data.get("reviewCount", "")

            else:
                # Fallback: Extract using CSS selectors
                item["name"] = (
                    response.css("h1.pdp-title::text").get(default="").strip()
                )
                item["brand"] = (
                    response.css("h1.pdp-brand-name::text").get(default="").strip()
                )
                item["description"] = (
                    response.css(".pdp-product-description-content::text")
                    .get(default="")
                    .strip()
                )

                # Price
                price_text = response.css(".pdp-price strong::text").get(default="")
                item["price"] = self.extract_price(price_text)

                discount_price_text = response.css(".pdp-mrp::text").get(default="")
                item["discount_price"] = self.extract_price(discount_price_text)

                # Images
                images = response.css(".image-grid-image::attr(src)").getall()
                item["images"] = [urljoin(response.url, img) for img in images if img]

                # Rating
                rating_text = response.css(".index-overallRating::text").get(default="")
                item["rating"] = self.extract_rating(rating_text)

                rating_count_text = response.css(".index-ratingsCount::text").get(
                    default=""
                )
                item["rating_count"] = self.extract_rating_count(rating_count_text)

            # Extract sizes and colors
            item["sizes"] = response.css(".size-buttons-size-button::text").getall()
            item["colors"] = response.css(".color-buttons-color::attr(title)").getall()

            # Store raw HTML for future reference
            item["raw_data"] = {
                "html_length": len(response.text),
                "url": response.url,
                "status": response.status,
            }

            yield item

        except Exception as e:
            self.logger.error(f"Error parsing product {response.url}: {str(e)}")

    def extract_product_id(self, url):
        """Extract product ID from URL"""
        try:
            # Myntra URLs typically have format: /buy/product-name/12345
            parts = url.split("/")
            if "buy" in parts:
                idx = parts.index("buy")
                if idx + 2 < len(parts):
                    return parts[idx + 2]
            return url.split("/")[-1]
        except:
            return url.split("/")[-1]

    def extract_price(self, price_text):
        """Extract numeric price from text"""
        if not price_text:
            return ""

        # Remove currency symbols and extract numbers
        price_match = re.search(r"[\d,]+", price_text.replace(",", ""))
        return price_match.group() if price_match else ""

    def extract_rating(self, rating_text):
        """Extract rating from text"""
        if not rating_text:
            return ""

        rating_match = re.search(r"(\d+\.?\d*)", rating_text)
        return rating_match.group(1) if rating_match else ""

    def extract_rating_count(self, rating_count_text):
        """Extract rating count from text"""
        if not rating_count_text:
            return ""

        count_match = re.search(r"(\d+)", rating_count_text.replace(",", ""))
        return count_match.group(1) if count_match else ""
