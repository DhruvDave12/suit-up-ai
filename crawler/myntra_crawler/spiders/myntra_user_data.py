import scrapy
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from myntra_crawler.items import UserOrderItem


class MyntraUserDataSpider(scrapy.Spider):
    """2P Crawler: Scrapes user order history from Myntra (requires login)"""

    name = "myntra_user_data"
    allowed_domains = ["myntra.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "RANDOMIZE_DOWNLOAD_DELAY": 1,
    }

    def __init__(self, email=None, password=None, headless=True, *args, **kwargs):
        super(MyntraUserDataSpider, self).__init__(*args, **kwargs)
        self.email = email
        self.password = password
        self.headless = headless.lower() == "true"
        self.driver = None

        if not self.email or not self.password:
            self.logger.error("Email and password are required for user data spider")
            raise ValueError("Email and password are required")

    def start_requests(self):
        """Initialize Selenium and login"""
        self.setup_driver()

        if self.login():
            # After successful login, start scraping order history
            yield scrapy.Request(
                url="https://www.myntra.com/checkout/orders",
                callback=self.parse_orders_page,
                dont_filter=True,
            )
        else:
            self.logger.error("Failed to login. Stopping spider.")

    def setup_driver(self):
        """Setup Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Add user agent
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

    def login(self):
        """Login to Myntra using Selenium"""
        try:
            self.logger.info("Starting login process...")

            # Navigate to login page
            self.driver.get("https://www.myntra.com/login")
            time.sleep(3)

            # Wait for login form
            wait = WebDriverWait(self.driver, 10)

            # Enter email/phone
            email_input = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[type="text"], input[type="email"]')
                )
            )
            email_input.clear()
            email_input.send_keys(self.email)

            # Click continue
            continue_btn = self.driver.find_element(
                By.CSS_SELECTOR, 'div[data-testid="submit"]'
            )
            continue_btn.click()
            time.sleep(2)

            # Enter password
            password_input = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[type="password"]')
                )
            )
            password_input.clear()
            password_input.send_keys(self.password)

            # Click login
            login_btn = self.driver.find_element(
                By.CSS_SELECTOR, 'div[data-testid="submit"]'
            )
            login_btn.click()

            # Wait for login to complete
            time.sleep(5)

            # Check if login was successful by looking for user profile or orders link
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '[data-testid="user"]')
                    )
                )
                self.logger.info("Login successful")
                return True
            except:
                self.logger.error("Login failed - user element not found")
                return False

        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False

    def parse_orders_page(self, response):
        """Parse orders page using Selenium"""
        try:
            # Navigate to orders page using Selenium
            self.driver.get("https://www.myntra.com/checkout/orders")
            time.sleep(5)

            # Scroll to load more orders
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            scroll_attempts = 0
            max_scrolls = 10

            while scroll_attempts < max_scrolls:
                # Scroll down
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(3)

                # Check if new content loaded
                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1

            # Extract order elements
            order_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                '.orders-orderContainer, .order-item, [data-testid="order"]',
            )

            self.logger.info(f"Found {len(order_elements)} order elements")

            for order_element in order_elements:
                try:
                    order_data = self.extract_order_data(order_element)
                    if order_data:
                        yield order_data
                except Exception as e:
                    self.logger.error(f"Error extracting order data: {str(e)}")
                    continue

            # Look for pagination or "Load More" button
            try:
                load_more_btn = self.driver.find_element(
                    By.CSS_SELECTOR, '[data-testid="load-more"], .load-more'
                )
                if load_more_btn.is_displayed():
                    load_more_btn.click()
                    time.sleep(3)
                    yield scrapy.Request(
                        url=self.driver.current_url,
                        callback=self.parse_orders_page,
                        dont_filter=True,
                    )
            except:
                self.logger.info("No more orders to load")

        except Exception as e:
            self.logger.error(f"Error parsing orders page: {str(e)}")

    def extract_order_data(self, order_element):
        """Extract order data from a single order element"""
        try:
            item = UserOrderItem()

            # Extract order ID
            order_id_elem = order_element.find_element(
                By.CSS_SELECTOR, '.order-id, [data-testid="order-id"]'
            )
            item["order_id"] = order_id_elem.text.strip() if order_id_elem else ""

            # Extract product name
            product_name_elem = order_element.find_element(
                By.CSS_SELECTOR, ".product-name, .item-name"
            )
            item["product_name"] = (
                product_name_elem.text.strip() if product_name_elem else ""
            )

            # Extract brand
            brand_elem = order_element.find_element(
                By.CSS_SELECTOR, ".brand, .item-brand"
            )
            item["brand"] = brand_elem.text.strip() if brand_elem else ""

            # Extract price
            price_elem = order_element.find_element(
                By.CSS_SELECTOR, ".price, .item-price"
            )
            item["price"] = price_elem.text.strip() if price_elem else ""

            # Extract order date
            date_elem = order_element.find_element(
                By.CSS_SELECTOR, ".order-date, .date"
            )
            item["order_date"] = date_elem.text.strip() if date_elem else ""

            # Extract size and color
            size_elem = order_element.find_element(By.CSS_SELECTOR, ".size")
            item["size"] = size_elem.text.strip() if size_elem else ""

            color_elem = order_element.find_element(By.CSS_SELECTOR, ".color")
            item["color"] = color_elem.text.strip() if color_elem else ""

            # Try to extract product ID from link
            product_link = order_element.find_element(
                By.CSS_SELECTOR, 'a[href*="/buy/"]'
            )
            if product_link:
                href = product_link.get_attribute("href")
                item["product_id"] = self.extract_product_id(href)
            else:
                item["product_id"] = ""

            # Extract any ratings or reviews
            try:
                rating_elem = order_element.find_element(
                    By.CSS_SELECTOR, ".rating, .stars"
                )
                item["rating_given"] = rating_elem.text.strip() if rating_elem else ""
            except:
                item["rating_given"] = ""

            try:
                review_elem = order_element.find_element(
                    By.CSS_SELECTOR, ".review-text, .review"
                )
                item["review_text"] = review_elem.text.strip() if review_elem else ""
            except:
                item["review_text"] = ""

            # Store raw HTML for reference
            item["raw_data"] = {
                "html": order_element.get_attribute("outerHTML"),
                "extracted_at": datetime.now().isoformat(),
            }

            return item

        except Exception as e:
            self.logger.error(f"Error extracting order data: {str(e)}")
            return None

    def extract_product_id(self, url):
        """Extract product ID from URL"""
        try:
            parts = url.split("/")
            if "buy" in parts:
                idx = parts.index("buy")
                if idx + 2 < len(parts):
                    return parts[idx + 2]
            return url.split("/")[-1]
        except:
            return ""

    def closed(self, reason):
        """Clean up when spider closes"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed")
