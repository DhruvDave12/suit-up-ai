import random
from fake_useragent import UserAgent


class RotateUserAgentMiddleware:
    """Middleware to rotate User-Agent headers"""

    def __init__(self):
        self.ua = UserAgent()
        # Fallback user agents if fake_useragent fails
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        ]

    def process_request(self, request, spider):
        try:
            # Try to get a random user agent
            ua = self.ua.random
        except:
            # Fallback to predefined list
            ua = random.choice(self.user_agents)

        request.headers["User-Agent"] = ua
        return None
