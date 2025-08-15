import json
import os
from datetime import datetime
from itemadapter import ItemAdapter


class JsonWriterPipeline:
    """Pipeline to write items to JSON files"""

    def __init__(self):
        self.files = {}

    def open_spider(self, spider):
        """Initialize file for each spider"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_dir}/{spider.name}_{timestamp}.json"

        self.files[spider.name] = {
            "file": open(filename, "w", encoding="utf-8"),
            "filename": filename,
            "items": [],
        }

        spider.logger.info(f"Opened file: {filename}")

    def close_spider(self, spider):
        """Close file and write all items"""
        if spider.name in self.files:
            file_info = self.files[spider.name]

            # Write all items to file
            json.dump(
                file_info["items"], file_info["file"], ensure_ascii=False, indent=4
            )

            file_info["file"].close()
            spider.logger.info(
                f"Saved {len(file_info['items'])} items to {file_info['filename']}"
            )

    def process_item(self, item, spider):
        """Process each item"""
        adapter = ItemAdapter(item)

        # Add timestamp
        adapter["scraped_at"] = datetime.now().isoformat()

        # Add to items list
        if spider.name in self.files:
            self.files[spider.name]["items"].append(dict(adapter))

        return item


class DuplicatesPipeline:
    """Pipeline to filter out duplicate items"""

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Use product_id for products, order_id for orders
        item_id = adapter.get("product_id") or adapter.get("order_id")

        if item_id in self.ids_seen:
            spider.logger.debug(f"Duplicate item found: {item_id}")
            raise DropItem(f"Duplicate item found: {item}")
        else:
            self.ids_seen.add(item_id)
            return item
