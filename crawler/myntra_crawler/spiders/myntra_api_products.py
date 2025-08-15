import scrapy
import json
import time
from urllib.parse import urljoin, urlparse, parse_qs
from myntra_crawler.items import ProductItem


class MyntraAPIProductsSpider(scrapy.Spider):
    """API-based Myntra Products Spider - Uses internal API endpoints instead of HTML parsing"""

    name = "myntra_api_products"
    allowed_domains = ["myntra.com"]

    # Real API endpoints discovered from network tab
    api_endpoints = {
        "search": "https://www.myntra.com/gateway/v2/search",
    }

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "RANDOMIZE_DOWNLOAD_DELAY": 0.5,
        "HTTPERROR_ALLOWED_CODES": [401, 403],  # Allow 401/403 so we can debug them
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "application/json",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "app": "web",
            "content-type": "application/json",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-location-context": "pincode=400018;source=IP",
            "x-meta-app": "channel=web",
            "x-myntraweb": "Yes",
            "x-requested-with": "browser",
        },
    }

    def __init__(self, category=None, max_pages=5, *args, **kwargs):
        super(MyntraAPIProductsSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.category = category or "men-clothing"
        self.pages_scraped = 0

    def start_requests(self):
        """Generate initial requests - first visit main page to get session cookies"""

        # First, we need to discover the API endpoints
        if not self.api_endpoints:
            self.logger.error("❌ No API endpoints configured!")
            self.logger.error(
                "🔍 Please run api_discovery.py first to find the actual API endpoints"
            )
            return

        # First visit the category page to establish session and get cookies
        category_url = f"https://www.myntra.com/{self.category}"

        yield scrapy.Request(
            url=category_url,
            callback=self.parse_category_and_then_api,
            meta={"category": self.category},
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )

    def parse_category_and_then_api(self, response):
        """Parse category page to get session, then call API"""
        category = response.meta["category"]

        self.logger.info(f"✅ Got session cookies from {response.url}")
        self.logger.info(f"🍪 Cookies: {len(response.request.cookies)} found")

        # Now make the API request with the session cookies
        search_url = self.api_endpoints.get("search")
        if search_url:
            # Construct full URL with category
            full_url = f"{search_url}/{category}"
            url_with_params = (
                f"{full_url}?rows=50&o=0&plaEnabled=true&xdEnabled=false&pincode=400018"
            )

            yield scrapy.Request(
                url=url_with_params,
                callback=self.parse_search_api,
                meta={"page": 1, "category": category, "offset": 0},
                headers=self.get_api_headers(),
                dont_filter=True,
            )
        else:
            self.logger.error("❌ Search API endpoint not configured")

    def get_api_headers(self):
        """Get headers that mimic browser API requests"""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Referer": f"https://www.myntra.com/{self.category}",
            "x-myntra-app": "deviceID=972653e0-8e3e-4062-99dd-0be09569eced;customerID=;reqChannel=web;appFamily=MyntraRetailWeb;",
        }

    def parse_search_api(self, response):
        """Parse API response containing product list"""

        # Check response status first
        if response.status != 200:
            self.logger.error(f"❌ API returned status {response.status}")
            self.logger.error(f"📄 Response body: {response.text[:500]}")
            return

        try:
            data = json.loads(response.text)
            page = response.meta["page"]
            category = response.meta["category"]

            self.logger.info(f"✅ API Response Status: {response.status}")
            self.logger.info(f"📦 API Response keys: {list(data.keys())}")

            # Save raw response for debugging
            debug_filename = f"api_debug_response_page_{page}.json"
            with open(debug_filename, "w") as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"💾 Saved debug response to: {debug_filename}")

            # The exact structure depends on Myntra's API response
            # Common patterns to look for:
            products = self.extract_products_from_api_response(data)

            if not products:
                self.logger.warning(
                    f"⚠️  No products found in API response for page {page}"
                )
                self.logger.warning(f"🔍 Available keys: {list(data.keys())}")
                return

            self.logger.info(f"✅ Found {len(products)} products on page {page}")

            # Process each product
            for product_data in products:
                # Extract product details directly from API response
                item = self.create_product_item_from_api(product_data, category)
                if item:
                    yield item

            # Handle pagination using offset
            self.pages_scraped += 1
            if self.pages_scraped < self.max_pages and self.has_more_pages(data):
                current_offset = response.meta.get("offset", 0)
                next_offset = current_offset + 50  # rows per page
                search_url = self.api_endpoints.get("search")
                full_url = f"{search_url}/{category}"

                # Add params to URL for pagination
                url_with_params = f"{full_url}?rows=50&o={next_offset}&plaEnabled=true&xdEnabled=false&pincode=400018"

                yield scrapy.Request(
                    url=url_with_params,
                    callback=self.parse_search_api,
                    meta={
                        "page": page + 1,
                        "category": category,
                        "offset": next_offset,
                    },
                    headers=self.get_api_headers(),
                    dont_filter=True,
                )

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Failed to parse JSON: {e}")
            self.logger.error(f"📄 Raw response: {response.text[:500]}")
        except Exception as e:
            self.logger.error(f"💥 Error parsing API response: {e}")
            self.logger.error(f"📄 Raw response: {response.text[:500]}")

    def extract_products_from_api_response(self, data):
        """Extract products list from API response"""
        # This needs to be customized based on actual API response structure

        # Common patterns in e-commerce APIs:
        possible_keys = [
            "products",
            "items",
            "data",
            "results",
            "listings",
            "productList",
        ]

        for key in possible_keys:
            if key in data and isinstance(data[key], list):
                self.logger.info(f"🎯 Found products in key: '{key}'")
                return data[key]

        # If data itself is a list
        if isinstance(data, list):
            self.logger.info(f"🎯 Data is directly a list with {len(data)} items")
            return data

        # Log available keys for debugging
        if isinstance(data, dict):
            self.logger.warning(
                f"🔍 Available keys in API response: {list(data.keys())}"
            )

        return []

    def has_more_pages(self, data):
        """Check if there are more pages available"""
        # Common pagination indicators:
        pagination_keys = ["hasNext", "hasMore", "totalPages", "nextPage", "pagination"]

        for key in pagination_keys:
            if key in data:
                value = data[key]
                if isinstance(value, bool):
                    return value
                elif isinstance(value, dict) and "hasNext" in value:
                    return value["hasNext"]
                elif isinstance(value, int) and key == "totalPages":
                    return self.pages_scraped < value

        # Fallback: check if we got any products (if yes, might have more)
        products = self.extract_products_from_api_response(data)
        return len(products) > 0

    def create_product_item_from_api(self, product_data, category):
        """Create ProductItem from API response data"""
        try:
            item = ProductItem()

            # Map API fields to our item fields
            # This mapping needs to be updated based on actual API response structure

            # Common field mappings (update based on actual API):
            field_mapping = {
                "product_id": ["id", "productId", "sku", "itemId"],
                "name": ["name", "title", "productName", "displayName"],
                "brand": ["brand", "brandName", "manufacturer"],
                "price": ["price", "currentPrice", "sellingPrice"],
                "discount_price": ["originalPrice", "mrp", "listPrice"],
                "description": ["description", "details", "productDescription"],
                "images": ["images", "imageUrls", "photos", "media"],
                "rating": ["rating", "avgRating", "averageRating"],
                "rating_count": ["ratingCount", "reviewCount", "numReviews"],
                "sizes": ["sizes", "availableSizes", "variants"],
                "colors": ["colors", "availableColors", "colorOptions"],
            }

            # Extract fields using mapping
            for item_field, possible_api_fields in field_mapping.items():
                for api_field in possible_api_fields:
                    if api_field in product_data:
                        item[item_field] = product_data[api_field]
                        break
                else:
                    # Default empty value if not found
                    item[item_field] = ""

            # Set category and URL
            item["category"] = category

            # Construct product URL if we have product ID
            if item.get("product_id"):
                item["product_url"] = (
                    f"https://www.myntra.com/product/{item['product_id']}"
                )

            # Store raw API response for debugging
            item["raw_data"] = {
                "api_response": product_data,
                "source": "api",
                "timestamp": int(time.time()),
            }

            return item

        except Exception as e:
            self.logger.error(f"❌ Error creating item from API data: {e}")
            return None


# Template for updating with real API endpoints
API_ENDPOINT_TEMPLATE = """
# UPDATE THESE WITH REAL API ENDPOINTS FOUND IN NETWORK TAB:

# Example of what to look for in Network tab:
# 1. Search/listing API: Usually contains 'search', 'list', 'catalog'
# 2. Product detail API: Usually contains 'product', 'item', 'detail'
# 3. Look for JSON responses with product data

api_endpoints = {
    "search": "https://www.myntra.com/gateway/v2/search",  # REPLACE WITH REAL URL
    "products": "https://www.myntra.com/api/v1/products",  # REPLACE WITH REAL URL
    # Add more endpoints as discovered
}

# Example parameters seen in Network tab:
search_params = {
    'category': 'men-clothing',
    'page': 1,
    'limit': 50,
    'sort': 'popularity',
    # Add real parameters from Network tab
}
"""
