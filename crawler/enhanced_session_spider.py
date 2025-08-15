import scrapy
import json
import time
import uuid
from urllib.parse import urljoin
from myntra_crawler.items import ProductItem


class EnhancedSessionMyntraSpider(scrapy.Spider):
    """Enhanced Myntra API Spider with robust session management"""

    name = "myntra_enhanced_session"
    allowed_domains = ["myntra.com"]

    # Real API endpoints
    api_endpoints = {
        "search": "https://www.myntra.com/gateway/v2/search",
    }

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "RANDOMIZE_DOWNLOAD_DELAY": 0.5,
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": True,  # Enable cookie debugging
        "HTTPERROR_ALLOWED_CODES": [401, 403, 429],  # Handle auth errors
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [401, 403, 429, 500, 502, 503, 504],
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "application/json",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "app": "web",
            "x-meta-app": "channel=web",
            "x-myntraweb": "Yes",
            "x-requested-with": "browser",
        },
    }

    def __init__(self, category=None, max_pages=5, *args, **kwargs):
        super(EnhancedSessionMyntraSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.category = category or "men-clothing"
        self.pages_scraped = 0
        self.session_established = False

        # Generate unique device ID for session
        self.device_id = str(uuid.uuid4())
        self.logger.info(f"🔑 Generated device ID: {self.device_id}")

    def start_requests(self):
        """Enhanced session initialization"""

        if not self.api_endpoints:
            self.logger.error("❌ No API endpoints configured!")
            return

        # Step 1: Visit main page to establish session
        main_url = "https://www.myntra.com/"
        yield scrapy.Request(
            url=main_url,
            callback=self.establish_base_session,
            meta={"category": self.category, "step": "base_session"},
            headers=self.get_browser_headers(),
            dont_filter=True,
        )

    def establish_base_session(self, response):
        """Establish base session with main site"""
        self.logger.info(f"🔗 Establishing base session from: {response.url}")
        self.log_session_info(response, "Base Session")

        # Step 2: Visit category page for specific session context
        category_url = f"https://www.myntra.com/{self.category}"
        yield scrapy.Request(
            url=category_url,
            callback=self.establish_category_session,
            meta={"category": self.category, "step": "category_session"},
            headers=self.get_browser_headers(),
            dont_filter=True,
        )

    def establish_category_session(self, response):
        """Establish category-specific session"""
        self.logger.info(f"🎯 Establishing category session from: {response.url}")
        self.log_session_info(response, "Category Session")

        # Mark session as established
        self.session_established = True

        # Step 3: Now make the API call
        self.make_api_request(response.meta["category"], 0, 1)

    def make_api_request(self, category, offset, page):
        """Make API request with established session"""
        search_url = self.api_endpoints.get("search")
        if not search_url:
            self.logger.error("❌ Search API endpoint not configured")
            return

        full_url = f"{search_url}/{category}"
        url_with_params = f"{full_url}?rows=50&o={offset}&plaEnabled=true&xdEnabled=false&pincode=400018"

        yield scrapy.Request(
            url=url_with_params,
            callback=self.parse_search_api,
            meta={"page": page, "category": category, "offset": offset},
            headers=self.get_api_headers(),
            dont_filter=True,
            errback=self.handle_api_error,
        )

    def handle_api_error(self, failure):
        """Handle API request failures"""
        request = failure.request
        self.logger.error(f"❌ API request failed: {failure.value}")

        # Check if it's an auth error
        if hasattr(failure.value, "response") and failure.value.response:
            status = failure.value.response.status
            if status in [401, 403]:
                self.logger.warning("🔄 Session expired, re-establishing...")
                # Re-establish session and retry
                return self.start_requests()

        return []

    def parse_search_api(self, response):
        """Parse API response with enhanced error handling"""

        # Enhanced status checking
        if response.status == 401:
            self.logger.warning("🔐 Authentication failed - session may have expired")
            self.log_session_info(response, "Auth Failed")
            return
        elif response.status == 403:
            self.logger.warning("🚫 Access forbidden - may need different headers")
            return
        elif response.status != 200:
            self.logger.error(f"❌ API returned status {response.status}")
            return

        try:
            data = json.loads(response.text)
            page = response.meta["page"]
            category = response.meta["category"]

            self.logger.info(f"✅ API Response Status: {response.status}")
            self.logger.info(f"📦 Response size: {len(response.text)} chars")
            self.logger.info(f"🔑 API Response keys: {list(data.keys())}")

            # Extract products
            products = self.extract_products_from_api_response(data)

            if not products:
                self.logger.warning(f"⚠️  No products found on page {page}")
                return

            self.logger.info(f"✅ Found {len(products)} products on page {page}")

            # Yield products
            for product_data in products:
                item = self.create_product_item_from_api(product_data, category)
                if item:
                    yield item

            # Handle pagination
            self.pages_scraped += 1
            if self.pages_scraped < self.max_pages and self.has_more_pages(data):
                current_offset = response.meta.get("offset", 0)
                next_offset = current_offset + 50

                yield from self.make_api_request(category, next_offset, page + 1)

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Failed to parse JSON: {e}")
        except Exception as e:
            self.logger.error(f"💥 Error parsing API response: {e}")

    def get_browser_headers(self):
        """Get headers for browser requests"""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def get_api_headers(self):
        """Get headers for API requests with session context"""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Referer": f"https://www.myntra.com/{self.category}",
            "x-myntra-app": f"deviceID={self.device_id};customerID=;reqChannel=web;appFamily=MyntraRetailWeb;",
            "x-location-context": "pincode=400018;source=IP",
        }

    def log_session_info(self, response, step_name):
        """Log detailed session information"""
        self.logger.info(f"📊 {step_name} - Status: {response.status}")

        # Log response cookies
        if hasattr(response, "headers") and "Set-Cookie" in response.headers:
            cookies = response.headers.getlist("Set-Cookie")
            self.logger.info(f"🍪 {step_name} - Received {len(cookies)} cookies")
            for cookie in cookies[:3]:  # Log first 3 cookies
                self.logger.debug(f"🍪 Cookie: {cookie.decode()[:100]}...")

        # Log request cookies
        if (
            hasattr(response.request, "headers")
            and "Cookie" in response.request.headers
        ):
            req_cookies = response.request.headers.get("Cookie")
            self.logger.info(
                f"🍪 {step_name} - Sent cookies: {len(req_cookies.decode()) if req_cookies else 0} chars"
            )

    # ... (include other methods from the original spider)

    def extract_products_from_api_response(self, data):
        """Extract products from API response"""
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

        if isinstance(data, list):
            return data

        return []

    def has_more_pages(self, data):
        """Check for more pages"""
        if "hasNextPage" in data:
            return data["hasNextPage"]

        products = self.extract_products_from_api_response(data)
        return len(products) > 0

    def create_product_item_from_api(self, product_data, category):
        """Create product item from API data"""
        try:
            item = ProductItem()

            # Basic mapping
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
            }

            for item_field, possible_api_fields in field_mapping.items():
                for api_field in possible_api_fields:
                    if api_field in product_data:
                        item[item_field] = product_data[api_field]
                        break
                else:
                    item[item_field] = ""

            item["category"] = category
            item["raw_data"] = {
                "api_response": product_data,
                "source": "enhanced_api",
                "timestamp": int(time.time()),
                "session_id": self.device_id,
            }

            return item

        except Exception as e:
            self.logger.error(f"❌ Error creating item: {e}")
            return None
