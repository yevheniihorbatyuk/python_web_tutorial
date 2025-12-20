"""
Example 1: Complete Scrapy to Django ORM Workflow

This example demonstrates a complete end-to-end workflow:
1. Run a Scrapy spider programmatically
2. Save results directly to Django ORM
3. Handle duplicates gracefully
4. Track execution with database models
5. Query and analyze results

Time to complete: 15 minutes
Difficulty: Intermediate
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Setup Django before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils import timezone
from django.db.models import Count, Q
from scrapy.crawler import CrawlerProcess
from code.scrapy_project.quotescrawler.spiders import QuotesSpider, BooksSpider
from code.django_integration.models import Quote, Book, ScrapeJob

logger = logging.getLogger(__name__)


# ============================================================================
# PART 1: Scraping with Database Pipeline
# ============================================================================
class ScrapeAndStoreManager:
    """
    Manages scraping workflow with database persistence.

    Features:
    - Runs Scrapy spider from Python
    - Stores results in Django ORM
    - Tracks duplicate detection
    - Records job execution
    - Provides result analysis
    """

    def __init__(self, spider_name: str, spider_class):
        """
        Initialize manager.

        Args:
            spider_name: Identifier for the spider (quotes, books)
            spider_class: Scrapy spider class to run
        """
        self.spider_name = spider_name
        self.spider_class = spider_class
        self.job = None
        self.results = {
            'created': 0,
            'updated': 0,
            'duplicates': 0,
            'errors': 0,
            'total': 0,
        }

    def create_job_record(self) -> ScrapeJob:
        """Create database record to track this scrape job"""
        self.job = ScrapeJob.objects.create(
            spider_name=self.spider_name,
            status='RUNNING',
            started_at=timezone.now(),
        )
        logger.info(f'Created job record: {self.job.id} for spider: {self.spider_name}')
        return self.job

    def run_spider(self) -> List[Dict[str, Any]]:
        """
        Run Scrapy spider and return results.

        Returns:
            List of scraped items
        """
        if not self.job:
            self.create_job_record()

        items = []

        # Configure Scrapy settings for this run
        settings = {
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'ROBOTSTXT_OBEY': True,
            'CONCURRENT_REQUESTS': 16,
            'DOWNLOAD_DELAY': 1,
            'COOKIES_ENABLED': False,
            'ITEM_PIPELINES': {
                'quotescrawler.pipelines.ValidationPipeline': 100,
                'quotescrawler.pipelines.JsonExportPipeline': 200,
            },
            'LOG_LEVEL': 'INFO',
        }

        try:
            # Create crawler process
            process = CrawlerProcess(settings)

            # Configure spider
            process.crawl(self.spider_class)

            # Run spider
            logger.info(f'Starting spider: {self.spider_name}')
            process.start()

            logger.info(f'Spider completed: {self.spider_name}')
            return items

        except Exception as e:
            logger.error(f'Spider failed: {e}')
            raise

    def store_results(self) -> Dict[str, int]:
        """
        Store scraped items in Django ORM, handling duplicates.

        Returns:
            Dictionary with counts: created, updated, duplicates, errors
        """
        if self.spider_name == 'quotes':
            return self._store_quotes()
        elif self.spider_name == 'books':
            return self._store_books()
        else:
            raise ValueError(f'Unknown spider: {self.spider_name}')

    def _store_quotes(self) -> Dict[str, int]:
        """Store quotes from JSON export"""
        json_file = Path('quotes.json')

        if not json_file.exists():
            logger.warning('No quotes.json found - spider may not have produced output')
            return self.results

        import json

        with open(json_file) as f:
            items = json.load(f)

        for item in items:
            try:
                # Try to get or create the quote
                quote, created = Quote.objects.get_or_create(
                    text=item['text'],
                    author=item['author'],
                    defaults={
                        'tags': item.get('tags', []),
                        'source': item.get('source', 'quotes.toscrape.com'),
                        'scraped_count': 1,
                    }
                )

                if created:
                    self.results['created'] += 1
                    logger.info(f'Created quote by {quote.author}')
                else:
                    # This is a duplicate
                    quote.scraped_count += 1
                    quote.last_scraped = timezone.now()
                    quote.save()
                    self.results['updated'] += 1
                    self.results['duplicates'] += 1
                    logger.debug(f'Updated duplicate quote by {quote.author}')

                self.results['total'] += 1

            except Exception as e:
                self.results['errors'] += 1
                logger.error(f'Error storing quote: {e}')

        logger.info(f'Stored {self.results["total"]} quotes total')
        return self.results

    def _store_books(self) -> Dict[str, int]:
        """Store books from JSON export"""
        json_file = Path('books.json')

        if not json_file.exists():
            logger.warning('No books.json found')
            return self.results

        import json

        with open(json_file) as f:
            items = json.load(f)

        for item in items:
            try:
                book, created = Book.objects.get_or_create(
                    title=item['title'],
                    defaults={
                        'price': item.get('price'),
                        'availability': item.get('availability', 'Unknown'),
                        'rating': item.get('rating', ''),
                        'category': item.get('category', 'Books'),
                        'description': item.get('description', ''),
                        'source': item.get('source', 'books.toscrape.com'),
                        'scraped_count': 1,
                    }
                )

                if created:
                    self.results['created'] += 1
                    logger.info(f'Created book: {book.title}')
                else:
                    book.scraped_count += 1
                    book.last_scraped = timezone.now()
                    book.save()
                    self.results['updated'] += 1
                    self.results['duplicates'] += 1

                self.results['total'] += 1

            except Exception as e:
                self.results['errors'] += 1
                logger.error(f'Error storing book: {e}')

        logger.info(f'Stored {self.results["total"]} books total')
        return self.results

    def finalize_job(self, status: str = 'SUCCESS') -> ScrapeJob:
        """
        Update job record with final results.

        Args:
            status: Final job status (SUCCESS, FAILED)

        Returns:
            Updated ScrapeJob record
        """
        if not self.job:
            return None

        self.job.status = status
        self.job.completed_at = timezone.now()
        self.job.items_count = self.results['total']
        self.job.save()

        logger.info(
            f'Finalized job {self.job.id}: {status} - '
            f'Created: {self.results["created"]}, '
            f'Updated: {self.results["updated"]}, '
            f'Duplicates: {self.results["duplicates"]}, '
            f'Errors: {self.results["errors"]}'
        )

        return self.job

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the job"""
        if not self.job:
            return {}

        duration = None
        if self.job.completed_at:
            duration = (self.job.completed_at - self.job.started_at).total_seconds()

        return {
            'job_id': self.job.id,
            'spider': self.job.spider_name,
            'status': self.job.status,
            'started': self.job.started_at.isoformat(),
            'completed': self.job.completed_at.isoformat() if self.job.completed_at else None,
            'duration_seconds': duration,
            'total_items': self.job.items_count,
            'created': self.results['created'],
            'updated': self.results['updated'],
            'duplicates': self.results['duplicates'],
            'errors': self.results['errors'],
        }


# ============================================================================
# PART 2: Example Usage - Scrape and Store
# ============================================================================
def example_scrape_quotes():
    """
    Complete workflow: Scrape quotes and store in database
    """
    print('\n' + '=' * 70)
    print('EXAMPLE 1: Scrape Quotes and Store in Database')
    print('=' * 70)

    # Create manager
    manager = ScrapeAndStoreManager('quotes', QuotesSpider)

    try:
        # Step 1: Create job record
        print('\n[1/4] Creating job record...')
        job = manager.create_job_record()
        print(f'✓ Job {job.id} created')

        # Step 2: Run spider
        print('\n[2/4] Running Scrapy spider...')
        items = manager.run_spider()
        print(f'✓ Spider completed')

        # Step 3: Store results
        print('\n[3/4] Storing results in database...')
        results = manager.store_results()
        print(f'✓ Stored {results["total"]} quotes')
        print(f'  - Created: {results["created"]}')
        print(f'  - Updated: {results["updated"]}')
        print(f'  - Duplicates: {results["duplicates"]}')
        print(f'  - Errors: {results["errors"]}')

        # Step 4: Finalize and show statistics
        print('\n[4/4] Finalizing job...')
        manager.finalize_job('SUCCESS')
        stats = manager.get_statistics()

        print('\n' + '─' * 70)
        print('JOB STATISTICS:')
        print('─' * 70)
        for key, value in stats.items():
            print(f'{key:20} : {value}')

        return True

    except Exception as e:
        print(f'\n✗ Error: {e}')
        manager.finalize_job('FAILED')
        logger.error(f'Scraping failed: {e}')
        return False


# ============================================================================
# PART 3: Analysis and Reporting
# ============================================================================
class ScrapeAnalyzer:
    """Analyze and report on scraped data"""

    @staticmethod
    def analyze_quotes():
        """Analyze quotes in database"""
        print('\n' + '=' * 70)
        print('QUOTES ANALYSIS')
        print('=' * 70)

        total = Quote.objects.count()
        unique_authors = Quote.objects.values('author').distinct().count()

        # Most duplicated quotes
        duplicates = Quote.objects.filter(
            scraped_count__gt=1
        ).order_by('-scraped_count')[:5]

        # Recently added
        recent = Quote.objects.order_by('-created_at')[:5]

        # By author
        by_author = Quote.objects.values('author').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        print(f'\nTotal quotes: {total}')
        print(f'Unique authors: {unique_authors}')

        print('\n--- Most Duplicated Quotes ---')
        for quote in duplicates:
            print(f'{quote.scraped_count}x: "{quote.text[:50]}..." - {quote.author}')

        print('\n--- Top Authors by Quote Count ---')
        for item in by_author:
            print(f'{item["count"]:3} quotes by {item["author"]}')

        print('\n--- Recently Added ---')
        for quote in recent:
            print(f'- "{quote.text[:40]}..." ({quote.created_at.strftime("%Y-%m-%d %H:%M")})')

    @staticmethod
    def analyze_jobs():
        """Analyze scraping jobs"""
        print('\n' + '=' * 70)
        print('JOB HISTORY ANALYSIS')
        print('=' * 70)

        total = ScrapeJob.objects.count()
        successful = ScrapeJob.objects.filter(status='SUCCESS').count()
        failed = ScrapeJob.objects.filter(status='FAILED').count()

        # Recent jobs
        recent_jobs = ScrapeJob.objects.order_by('-started_at')[:5]

        print(f'\nTotal jobs: {total}')
        print(f'Successful: {successful}')
        print(f'Failed: {failed}')
        print(f'Success rate: {(successful/total*100 if total else 0):.1f}%')

        print('\n--- Recent Jobs ---')
        for job in recent_jobs:
            status_icon = '✓' if job.status == 'SUCCESS' else '✗'
            duration = job.duration()
            duration_str = f'{duration:.1f}s' if duration else 'N/A'
            print(
                f'{status_icon} {job.spider_name:10} {job.status:10} '
                f'{job.items_count:5} items ({duration_str})'
            )

    @staticmethod
    def find_duplicates():
        """Find duplicate quotes seen multiple times"""
        print('\n' + '=' * 70)
        print('DUPLICATE DETECTION')
        print('=' * 70)

        duplicates = Quote.objects.filter(scraped_count__gt=1).count()
        total_duplicate_count = Quote.objects.filter(
            scraped_count__gt=1
        ).aggregate(total=Count('scraped_count'))['total']

        print(f'\nQuotes seen multiple times: {duplicates}')
        print(f'Total duplicate sightings: {total_duplicate_count}')

        print('\n--- Quotes Seen 5+ Times ---')
        frequent = Quote.objects.filter(
            scraped_count__gte=5
        ).order_by('-scraped_count')

        for quote in frequent[:10]:
            print(
                f'{quote.scraped_count:3}x: "{quote.text[:40]}..." '
                f'({quote.last_scraped.strftime("%Y-%m-%d")})'
            )


# ============================================================================
# PART 4: Cleanup and Maintenance
# ============================================================================
class ScrapeMaintenanceManager:
    """Manage scrape data lifecycle"""

    @staticmethod
    def cleanup_old_data(days: int = 30):
        """Delete quotes not seen in specified days"""
        print('\n' + '=' * 70)
        print(f'CLEANUP: Removing quotes not seen in {days} days')
        print('=' * 70)

        cutoff = timezone.now() - timedelta(days=days)
        old_quotes = Quote.objects.filter(last_scraped__lt=cutoff)

        count = old_quotes.count()
        print(f'\nFound {count} quotes not seen since {cutoff.date()}')

        if count > 0:
            old_quotes.delete()
            print(f'✓ Deleted {count} old quotes')

    @staticmethod
    def export_data(format: str = 'json'):
        """Export scraped data"""
        import json
        from decimal import Decimal

        print('\n' + '=' * 70)
        print(f'EXPORT: Exporting data as {format.upper()}')
        print('=' * 70)

        quotes = Quote.objects.all().values()

        # Convert Decimal to float for JSON serialization
        quotes_list = [dict(q) for q in quotes]
        for q in quotes_list:
            q['last_scraped'] = q['last_scraped'].isoformat()
            q['created_at'] = q['created_at'].isoformat()

        filename = f'quotes_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

        with open(filename, 'w') as f:
            json.dump(quotes_list, f, indent=2)

        print(f'✓ Exported {len(quotes_list)} quotes to {filename}')
        return filename

    @staticmethod
    def reset_database():
        """WARNING: Delete all data (for development only)"""
        print('\n' + '=' * 70)
        print('⚠️  RESET DATABASE')
        print('=' * 70)

        count_quotes = Quote.objects.count()
        count_jobs = ScrapeJob.objects.count()

        print(f'\nThis will delete:')
        print(f'  - {count_quotes} quotes')
        print(f'  - {count_jobs} jobs')

        response = input('\nType "yes" to confirm: ')

        if response.lower() == 'yes':
            Quote.objects.all().delete()
            ScrapeJob.objects.all().delete()
            print('\n✓ Database reset')
        else:
            print('\n✗ Cancelled')


# ============================================================================
# MAIN: Run Examples
# ============================================================================
if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print('\n')
    print('╔' + '=' * 68 + '╗')
    print('║' + ' ' * 68 + '║')
    print('║' + '  Example 1: Complete Scrapy to Django ORM Workflow'.center(68) + '║')
    print('║' + ' ' * 68 + '║')
    print('╚' + '=' * 68 + '╝')

    import argparse

    parser = argparse.ArgumentParser(description='Scrape and store workflow examples')
    parser.add_argument(
        'action',
        nargs='?',
        default='scrape',
        choices=['scrape', 'analyze', 'cleanup', 'export', 'reset'],
        help='Action to perform'
    )
    parser.add_argument('--spider', default='quotes', help='Spider to run (quotes, books)')
    parser.add_argument('--days', type=int, default=30, help='Days cutoff for cleanup')

    args = parser.parse_args()

    try:
        if args.action == 'scrape':
            success = example_scrape_quotes()
            sys.exit(0 if success else 1)

        elif args.action == 'analyze':
            ScrapeAnalyzer.analyze_quotes()
            ScrapeAnalyzer.analyze_jobs()
            ScrapeAnalyzer.find_duplicates()

        elif args.action == 'cleanup':
            ScrapeMaintenanceManager.cleanup_old_data(args.days)

        elif args.action == 'export':
            ScrapeMaintenanceManager.export_data()

        elif args.action == 'reset':
            ScrapeMaintenanceManager.reset_database()

    except KeyboardInterrupt:
        print('\n\n✗ Interrupted by user')
        sys.exit(1)

    except Exception as e:
        print(f'\n✗ Error: {e}')
        logger.exception('Unexpected error')
        sys.exit(1)
