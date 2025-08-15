import scrapy


class ProductItem(scrapy.Item):
    """Item for storing product information from Myntra"""

    product_id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    discount_price = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    images = scrapy.Field()
    sizes = scrapy.Field()
    colors = scrapy.Field()
    description = scrapy.Field()
    product_url = scrapy.Field()
    scraped_at = scrapy.Field()
    raw_data = scrapy.Field()  # Store raw API response


class UserOrderItem(scrapy.Item):
    """Item for storing user order history from Myntra"""

    order_id = scrapy.Field()
    product_id = scrapy.Field()
    product_name = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    order_date = scrapy.Field()
    delivery_date = scrapy.Field()
    size = scrapy.Field()
    color = scrapy.Field()
    category = scrapy.Field()
    rating_given = scrapy.Field()
    review_text = scrapy.Field()
    scraped_at = scrapy.Field()
    raw_data = scrapy.Field()  # Store raw API response
