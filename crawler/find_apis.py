#!/usr/bin/env python3
"""
Step-by-step guide to find Myntra API endpoints
Run this script and follow the instructions
"""


def print_instructions():
    print("🔍 MYNTRA API DISCOVERY GUIDE")
    print("=" * 50)
    print()

    print("📋 STEP 1: Open Browser")
    print("• Open Chrome/Firefox")
    print("• Go to: https://www.myntra.com/men-clothing")
    print()

    print("📋 STEP 2: Open Developer Tools")
    print("• Press F12 (or right-click → Inspect)")
    print("• Click on 'Network' tab")
    print("• Click 'XHR' or 'Fetch' filter (to see only API calls)")
    print("• Make sure 'Preserve log' is checked")
    print()

    print("📋 STEP 3: Trigger API Calls")
    print("• Refresh the page (Ctrl+R or Cmd+R)")
    print("• Scroll down to load more products")
    print("• Click on pagination (page 2, 3, etc.)")
    print("• Try changing filters (size, price, brand)")
    print()

    print("📋 STEP 4: Identify API Endpoints")
    print("Look for requests with these patterns:")
    print(
        "✅ URLs containing: 'search', 'product', 'list', 'catalog', 'api', 'gateway'"
    )
    print("✅ Response type: JSON (not HTML)")
    print("✅ Response containing product data")
    print()

    print("📋 STEP 5: Analyze the API Call")
    print("Click on an API request and look at:")
    print("• Request URL")
    print("• Request Headers")
    print("• Query Parameters")
    print("• Response (Preview tab)")
    print()

    print("📋 STEP 6: Copy API Details")
    print("For each useful API call, copy:")
    print("• Full URL")
    print("• Query parameters")
    print("• Important headers")
    print()

    print("🎯 COMMON MYNTRA API PATTERNS TO LOOK FOR:")
    print("• https://www.myntra.com/gateway/...")
    print("• https://www.myntra.com/api/...")
    print("• https://www.myntra.com/web/...")
    print("• Any URL returning JSON with product data")
    print()

    print("🔧 NEXT STEPS:")
    print("1. Find 2-3 API endpoints from Network tab")
    print("2. Test them using: python api_discovery.py")
    print("3. Update myntra_api_products.py with real endpoints")
    print("4. Run the new API-based crawler")
    print()

    print("💡 EXAMPLE OF WHAT YOU'RE LOOKING FOR:")
    print(
        """
    Request URL: https://www.myntra.com/gateway/v2/search/men-clothing?page=1&rows=50
    Method: GET
    Status: 200
    Response: JSON with products array
    """
    )


def create_example_api_test():
    """Create an example to test found APIs"""
    example_code = """
# After finding API endpoints, test them like this:
import requests

def test_myntra_api():
    # Replace with actual URL from Network tab
    api_url = "https://www.myntra.com/gateway/v2/search/men-clothing"

    # Replace with actual parameters from Network tab
    params = {
        'page': 1,
        'rows': 50,
        'category': 'men-clothing'
    }

    # Replace with actual headers from Network tab
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.myntra.com/men-clothing'
    }

    response = requests.get(api_url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {len(data.get('products', []))} products")
        print(f"Response keys: {list(data.keys())}")
    else:
        print(f"❌ Failed: {response.status_code}")

if __name__ == "__main__":
    test_myntra_api()
"""

    with open("test_api_example.py", "w") as f:
        f.write(example_code)

    print(f"📝 Created test_api_example.py - use this as a template after finding APIs")


if __name__ == "__main__":
    print_instructions()
    create_example_api_test()
