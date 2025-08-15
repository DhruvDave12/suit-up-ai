#!/usr/bin/env python3
"""
API Discovery Helper for Myntra
Use this to test and analyze API endpoints found via browser network tab
"""

import requests
import json
import time
from urllib.parse import urljoin


class MyntraAPIDiscovery:
    def __init__(self):
        self.session = requests.Session()
        # Common headers that mimic browser requests
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "app": "web",
                "content-type": "application/json",
                "referer": "https://www.myntra.com/men-clothing",
                "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-location-context": "pincode=400018;source=IP",
                "x-meta-app": "channel=web",
                "x-myntra-app": "deviceID=972653e0-8e3e-4062-99dd-0be09569eced;customerID=;reqChannel=web;appFamily=MyntraRetailWeb;",
                "x-myntraweb": "Yes",
                "x-requested-with": "browser",
            }
        )

    def test_api_endpoint(self, url, params=None):
        """Test a discovered API endpoint"""
        try:
            print(f"\n🔍 Testing: {url}")
            if params:
                print(f"📊 Params: {params}")

            response = self.session.get(url, params=params, timeout=10)
            print(f"✅ Status: {response.status_code}")
            print(f"📝 Content-Type: {response.headers.get('content-type', 'Unknown')}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(
                        f"📦 JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'List with ' + str(len(data)) + ' items'}"
                    )

                    # Save response for analysis
                    filename = f"api_response_{int(time.time())}.json"
                    with open(filename, "w") as f:
                        json.dump(data, f, indent=2)
                    print(f"💾 Saved response to: {filename}")

                    return data
                except json.JSONDecodeError:
                    print(f"⚠️  Response is not JSON. Length: {len(response.text)}")
                    print(f"📄 First 200 chars: {response.text[:200]}")
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"📄 Response: {response.text[:200]}")

        except Exception as e:
            print(f"💥 Error: {str(e)}")

        return None

    def analyze_product_data(self, data):
        """Analyze the structure of product data from API response"""
        if not isinstance(data, dict):
            print("⚠️  Data is not a dictionary")
            return

        print("\n📊 DATA ANALYSIS:")
        print("=" * 50)

        # Look for common product data patterns
        product_indicators = ["products", "items", "data", "results", "listings"]

        for key in data.keys():
            value = data[key]
            print(f"\n🔑 Key: '{key}' (Type: {type(value).__name__})")

            if isinstance(value, list) and len(value) > 0:
                print(f"   📋 List with {len(value)} items")
                if isinstance(value[0], dict):
                    print(f"   🏷️  First item keys: {list(value[0].keys())}")
            elif isinstance(value, dict):
                print(f"   📦 Dict with keys: {list(value.keys())}")
            else:
                print(f"   📄 Value: {str(value)[:100]}")


def main():
    """
    Instructions for finding API endpoints:

    1. Open https://www.myntra.com/men-clothing in Chrome
    2. Open DevTools (F12) → Network tab
    3. Filter by "Fetch/XHR"
    4. Refresh the page
    5. Look for API calls that return JSON data
    6. Copy the URL and paste it below

    Common Myntra API patterns to look for:
    - /gateway/v2/search/
    - /api/v1/products/
    - /web/v1/search/
    - Any URL containing 'search', 'product', 'listing'
    """

    discovery = MyntraAPIDiscovery()

    # Real API endpoint found from Network tab
    example_endpoints = [
        "https://www.myntra.com/gateway/v2/search/men-clothing",
    ]

    if not example_endpoints:
        print("🔍 INSTRUCTIONS:")
        print("1. Open Myntra in browser: https://www.myntra.com/men-clothing")
        print("2. Open DevTools (F12) → Network tab → Filter by XHR/Fetch")
        print("3. Refresh page and look for API calls")
        print(
            "4. Copy API URLs and add them to 'example_endpoints' list in this script"
        )
        print("5. Run this script again to test the endpoints")
        return

    # Test with parameters from the curl command
    test_params = {
        "rows": 50,
        "o": 0,  # Start from beginning
        "plaEnabled": "true",
        "xdEnabled": "false",
        "pincode": "400018",
    }

    for endpoint in example_endpoints:
        discovery.test_api_endpoint(endpoint, params=test_params)
        time.sleep(1)  # Be nice to the server


if __name__ == "__main__":
    main()
