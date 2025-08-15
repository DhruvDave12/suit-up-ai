# Scrapy settings for myntra_crawler project

BOT_NAME = "myntra_crawler"

SPIDER_MODULES = ["myntra_crawler.spiders"]
NEWSPIDER_MODULE = "myntra_crawler.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure pipelines
ITEM_PIPELINES = {
    "myntra_crawler.pipelines.JsonWriterPipeline": 300,
}

# Configure delays and concurrent requests
DOWNLOAD_DELAY = 1  # 1 second delay between requests
RANDOMIZE_DOWNLOAD_DELAY = 0.5  # 0.5 * to 1.5 * DOWNLOAD_DELAY
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# User agent rotation
USER_AGENT = "myntra_crawler (+http://www.yourdomain.com)"
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "myntra_crawler.middlewares.RotateUserAgentMiddleware": 400,
}

# Configure cookies and sessions
COOKIES_ENABLED = True

# Configure logging
LOG_LEVEL = "INFO"

# Output settings
FEEDS = {
    "data/%(name)s_%(time)s.json": {
        "format": "json",
        "encoding": "utf8",
        "store_empty": False,
        "fields": None,
        "indent": 4,
    },
}

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 3
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
