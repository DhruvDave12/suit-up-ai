# Myntra Fashion Crawler

A Scrapy-based crawler system for collecting fashion data from Myntra to build a fashion aggregation platform.

## Features

- **3P Crawler**: Scrapes public product data (products, prices, ratings, images)
- **2P Crawler**: Scrapes user order history and preferences (requires login)
- **JSON Storage**: All data stored in structured JSON files
- **Rate Limiting**: Respectful crawling with built-in delays
- **User Agent Rotation**: Avoids detection with rotating headers

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install ChromeDriver for Selenium (required for user data crawler):
```bash
# On macOS
brew install chromedriver

# On Ubuntu
sudo apt-get install chromium-chromedriver

# Or download manually from https://chromedriver.chromium.org/
```

## Usage

### Products Crawler (3P - Public Data)

Scrape public product listings:

```bash
# Basic usage - crawl all categories
python run_crawler.py products

# Specific category
python run_crawler.py products --category men-clothing

# Limit pages per category
python run_crawler.py products --max-pages 10
```

Available categories:
- `men-clothing`
- `women-clothing`
- `men-footwear`
- `women-footwear`
- `men-accessories`
- `women-accessories`

### User Data Crawler (2P - Personal Data)

Scrape user order history (requires Myntra login):

```bash
python run_crawler.py user_data --email your_email@example.com --password your_password

# Run with visible browser (for debugging)
python run_crawler.py user_data --email your_email@example.com --password your_password --no-headless
```

## Output

All scraped data is saved to the `data/` directory as JSON files:

- `myntra_products_YYYYMMDD_HHMMSS.json` - Product data
- `myntra_user_data_YYYYMMDD_HHMMSS.json` - User order history

## Data Structure

### Product Data
```json
{
  "product_id": "12345",
  "name": "Men's Cotton T-Shirt",
  "brand": "Nike",
  "price": "1999",
  "discount_price": "1499",
  "rating": "4.2",
  "rating_count": "1250",
  "category": "men-clothing",
  "images": ["https://..."],
  "sizes": ["S", "M", "L", "XL"],
  "colors": ["Black", "White"],
  "description": "...",
  "product_url": "https://...",
  "scraped_at": "2024-01-01T12:00:00"
}
```

### User Order Data
```json
{
  "order_id": "ORD123456",
  "product_id": "12345",
  "product_name": "Men's Cotton T-Shirt",
  "brand": "Nike",
  "price": "1499",
  "order_date": "2023-12-15",
  "size": "M",
  "color": "Black",
  "rating_given": "5",
  "review_text": "Great quality!",
  "scraped_at": "2024-01-01T12:00:00"
}
```

## Configuration

Edit `myntra_crawler/settings.py` to customize:

- Download delays
- Concurrent requests
- User agents
- Output formats

## Privacy & Ethics

- **User Data**: Only collect your own order history with explicit consent
- **Rate Limiting**: Built-in delays to avoid overwhelming servers
- **Robots.txt**: Respects website crawling policies
- **Data Storage**: All data stored locally in JSON format

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**:
   - Install ChromeDriver and ensure it's in PATH
   - Or specify path in spider settings

2. **Login fails**:
   - Check credentials
   - Run with `--no-headless` to debug
   - Handle 2FA manually if enabled

3. **No products found**:
   - Myntra may have changed their HTML structure
   - Check and update CSS selectors in spider

4. **Rate limiting**:
   - Increase delays in settings.py
   - Use proxy rotation if needed

## Development

Project structure:
```
crawler/
├── myntra_crawler/
│   ├── spiders/
│   │   ├── myntra_products.py    # 3P crawler
│   │   └── myntra_user_data.py   # 2P crawler
│   ├── items.py                  # Data models
│   ├── pipelines.py             # Data processing
│   ├── settings.py              # Configuration
│   └── middlewares.py           # User agent rotation
├── data/                        # Output JSON files
├── run_crawler.py              # Easy runner script
└── requirements.txt            # Dependencies
```

## Next Steps

1. **Platform Expansion**: Add Nykaa, Ajio crawlers
2. **Data Processing**: Build fashion categorization algorithms
3. **User Profiling**: Implement recommendation system
4. **API Integration**: Connect to fashion aggregation app

## License

This project is for educational and personal use only. Ensure compliance with website terms of service and applicable laws.
