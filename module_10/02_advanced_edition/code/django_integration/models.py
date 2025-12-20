"""Django models for scraping integration"""

from django.db import models
from django.utils import timezone


class ScrapeJob(models.Model):
    """Track scraping job execution"""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    spider_name = models.CharField(
        max_length=50,
        help_text='Name of the spider (quotes, books, etc)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
    )
    started_at = models.DateTimeField(
        db_index=True,
        help_text='When scraping started'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When scraping completed'
    )
    items_count = models.IntegerField(
        default=0,
        help_text='Number of items scraped'
    )
    error_message = models.TextField(
        blank=True,
        help_text='Error message if failed'
    )
    task_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Celery task ID for tracking'
    )

    class Meta:
        ordering = ['-started_at']
        verbose_name_plural = 'Scrape Jobs'

    def __str__(self):
        return f'{self.spider_name} - {self.status} ({self.started_at.strftime("%Y-%m-%d %H:%M")})'

    def duration(self):
        """Get duration in seconds"""
        if not self.completed_at:
            return None
        return (self.completed_at - self.started_at).total_seconds()

    def is_running(self):
        """Check if currently running"""
        return self.status == 'RUNNING'

    def is_success(self):
        """Check if successful"""
        return self.status == 'SUCCESS'


class Quote(models.Model):
    """Scraped quote from quotes.toscrape.com"""

    text = models.TextField(
        unique=True,
        help_text='Quote text'
    )
    author = models.CharField(
        max_length=200,
        db_index=True,
        help_text='Author name'
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text='List of tags'
    )
    source = models.CharField(
        max_length=100,
        default='quotes.toscrape.com',
        help_text='Source website'
    )
    scraped_count = models.IntegerField(
        default=1,
        help_text='How many times this quote was found'
    )
    last_scraped = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text='When last found'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When first created'
    )

    class Meta:
        ordering = ['-last_scraped']
        indexes = [
            models.Index(fields=['author', 'last_scraped']),
            models.Index(fields=['source', 'created_at']),
        ]

    def __str__(self):
        return f'{self.text[:50]}... - {self.author}'


class Book(models.Model):
    """Scraped book from books.toscrape.com"""

    title = models.CharField(
        max_length=300,
        unique=True,
        help_text='Book title'
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Book price'
    )
    availability = models.CharField(
        max_length=50,
        default='Unknown',
        help_text='In stock / Out of stock'
    )
    rating = models.CharField(
        max_length=20,
        blank=True,
        help_text='Star rating (One, Two, Three, Four, Five)'
    )
    category = models.CharField(
        max_length=100,
        default='Books',
        db_index=True,
        help_text='Book category'
    )
    description = models.TextField(
        blank=True,
        help_text='Book description'
    )
    source = models.CharField(
        max_length=100,
        default='books.toscrape.com',
        help_text='Source website'
    )
    scraped_count = models.IntegerField(
        default=1,
        help_text='How many times this book was found'
    )
    last_scraped = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text='When last found'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When first created'
    )

    class Meta:
        ordering = ['-last_scraped']
        indexes = [
            models.Index(fields=['category', 'last_scraped']),
            models.Index(fields=['source', 'created_at']),
        ]

    def __str__(self):
        return f'{self.title} ({self.category})'


class ScrapingSchedule(models.Model):
    """Configuration for scheduled scraping"""

    FREQUENCY_CHOICES = [
        ('HOURLY', 'Every hour'),
        ('DAILY', 'Every day'),
        ('WEEKLY', 'Every week'),
        ('MONTHLY', 'Every month'),
    ]

    spider_name = models.CharField(
        max_length=50,
        unique=True,
        help_text='Spider to run'
    )
    is_enabled = models.BooleanField(
        default=True,
        help_text='Is this schedule active?'
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='DAILY',
        help_text='How often to run'
    )
    last_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When last executed'
    )
    next_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When scheduled to run next'
    )

    class Meta:
        verbose_name_plural = 'Scraping Schedules'

    def __str__(self):
        return f'{self.spider_name} ({self.frequency})'
