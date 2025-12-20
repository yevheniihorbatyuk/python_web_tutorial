"""Item pipelines for quotescrawler"""

import json
import logging
import scrapy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class ValidationPipeline:
    """Validates item data before processing"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_item(self, item: Dict[str, Any], spider) -> Dict[str, Any]:
        """Validate required fields and data types"""

        # Check required fields
        required_fields = ['text', 'author']
        for field in required_fields:
            if not item.get(field):
                self.logger.warning(f'Missing required field: {field}')
                raise scrapy.exceptions.DropItem(f'Missing {field}')

        # Validate text length
        text = str(item.get('text', '')).strip()
        if len(text) < 5:
            raise scrapy.exceptions.DropItem(f'Text too short: {text[:20]}...')

        # Clean text
        item['text'] = text
        item['author'] = str(item.get('author', '')).strip()

        return item


class DuplicatesPipeline:
    """Filters duplicate items"""

    def __init__(self):
        self.seen = set()
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        """Called when spider is opened"""
        self.logger.info('DuplicatesPipeline opened')

    def close_spider(self, spider):
        """Called when spider is closed"""
        self.logger.info(f'DuplicatesPipeline closed. Seen {len(self.seen)} items')

    def process_item(self, item: Dict[str, Any], spider) -> Dict[str, Any]:
        """Skip if item was seen before"""

        # Create unique identifier
        identifier = (item.get('text'), item.get('author'))

        if identifier in self.seen:
            raise scrapy.exceptions.DropItem(f'Duplicate item found')

        self.seen.add(identifier)
        return item


class JsonExportPipeline:
    """Exports items to JSON file"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.items = []
        self.output_file = None

    def open_spider(self, spider):
        """Create output file when spider opens"""
        # Create data directory if not exists
        data_dir = Path(__file__).parent.parent.parent / 'data'
        data_dir.mkdir(exist_ok=True)

        # File path based on spider name
        filename = f'{spider.name}_output.jsonl'
        self.output_file = data_dir / filename

        self.logger.info(f'Opening {self.output_file}')

    def close_spider(self, spider):
        """Close output file when spider closes"""
        self.logger.info(f'JsonExportPipeline closed. Exported {len(self.items)} items')

    def process_item(self, item: Dict[str, Any], spider) -> Dict[str, Any]:
        """Export item to JSON"""

        # Add scraped_at timestamp if not present
        if 'scraped_at' not in item:
            item['scraped_at'] = datetime.now().isoformat()

        # Write to file (JSONL format: one JSON object per line)
        self.items.append(item)

        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(dict(item), ensure_ascii=False) + '\n')

        return item


# Note: To use this pipeline, you would typically also create a DatabasePipeline
# that saves to Django ORM when integrated. This is shown in the tutorial.
