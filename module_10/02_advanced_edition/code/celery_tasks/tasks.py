"""Celery task definitions for async processing"""

import logging
import time
from typing import Dict, Any
from datetime import datetime
from celery import shared_task

logger = logging.getLogger(__name__)


# ============================================================================
# EXAMPLE TASKS
# ============================================================================

@shared_task
def example_task():
    """Simple task that does nothing (for testing)"""
    return 'Task completed'


@shared_task
def example_task_daily():
    """Task that runs daily (for testing)"""
    logger.info('Daily task executed')
    return 'Daily task completed'


# ============================================================================
# LONG-RUNNING TASKS (for demonstration)
# ============================================================================

@shared_task(bind=True)
def long_task(self, duration: int) -> str:
    """
    Task that simulates long-running work.

    Args:
        duration: Number of seconds to sleep

    Returns:
        Completion message
    """
    try:
        logger.info(f'Starting long task for {duration} seconds')

        for i in range(duration):
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': duration,
                    'percent': ((i + 1) / duration) * 100,
                }
            )
            time.sleep(1)

        logger.info(f'Long task completed after {duration} seconds')
        return f'Slept for {duration} seconds'

    except Exception as exc:
        logger.error(f'Long task failed: {exc}')
        raise


# ============================================================================
# DATA PROCESSING TASKS
# ============================================================================

@shared_task(bind=True)
def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process data with error handling and retries.

    Args:
        data: Dictionary of data to process

    Returns:
        Processed data
    """
    try:
        logger.info(f'Processing data with {len(data)} items')

        result = {
            'items_processed': len(data),
            'timestamp': datetime.now().isoformat(),
            'data': data,
        }

        logger.info('Data processing completed')
        return result

    except Exception as exc:
        logger.error(f'Data processing failed: {exc}')
        # Retry with exponential backoff
        countdown = 2 ** self.request.retries
        raise self.retry(exc=exc, countdown=countdown)


# ============================================================================
# RESILIENT TASKS (with retries)
# ============================================================================

@shared_task(bind=True, autoretry_for=(Exception,))
def resilient_task(self, url: str) -> str:
    """
    Task with automatic retries on failure.

    Args:
        url: URL to process

    Returns:
        Processing result
    """
    try:
        logger.info(f'Processing {url}')

        # Simulate work that might fail
        if 'error' in url:
            raise ValueError(f'Invalid URL: {url}')

        result = f'Processed: {url}'
        logger.info(result)
        return result

    except Exception as exc:
        logger.warning(f'Task failed (retry {self.request.retries}): {exc}')
        # Exponential backoff: 1s, 2s, 4s, 8s, 16s...
        countdown = 2 ** self.request.retries
        raise self.retry(exc=exc, countdown=countdown)


# ============================================================================
# EMAIL/NOTIFICATION TASKS
# ============================================================================

@shared_task(bind=True)
def send_notification(self, recipient: str, message: str) -> Dict[str, Any]:
    """
    Send notification (email, SMS, etc).

    Args:
        recipient: Email or phone number
        message: Message content

    Returns:
        Notification status
    """
    try:
        logger.info(f'Sending notification to {recipient}')

        # Simulate sending
        time.sleep(0.1)

        result = {
            'recipient': recipient,
            'status': 'sent',
            'timestamp': datetime.now().isoformat(),
        }

        logger.info(f'Notification sent to {recipient}')
        return result

    except Exception as exc:
        logger.error(f'Failed to send notification: {exc}')
        raise


# ============================================================================
# BATCH PROCESSING TASKS
# ============================================================================

@shared_task(bind=True)
def batch_process(self, items: list) -> Dict[str, Any]:
    """
    Process multiple items as batch.

    Args:
        items: List of items to process

    Returns:
        Processing results
    """
    try:
        logger.info(f'Batch processing {len(items)} items')

        processed = []
        failed = []

        for i, item in enumerate(items):
            try:
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': len(items),
                        'processed': len(processed),
                        'failed': len(failed),
                    }
                )

                # Process item
                processed.append({
                    'item': item,
                    'status': 'success',
                })

            except Exception as item_exc:
                logger.warning(f'Failed to process item {item}: {item_exc}')
                failed.append({
                    'item': item,
                    'error': str(item_exc),
                })

        result = {
            'total': len(items),
            'processed': len(processed),
            'failed': len(failed),
            'timestamp': datetime.now().isoformat(),
        }

        logger.info(f'Batch processing complete: {result}')
        return result

    except Exception as exc:
        logger.error(f'Batch processing failed: {exc}')
        raise


# ============================================================================
# CHAINED TASKS (pipeline pattern)
# ============================================================================

@shared_task
def extract_data(source: str) -> Dict[str, Any]:
    """Extract data from source"""
    logger.info(f'Extracting data from {source}')
    return {
        'source': source,
        'data': ['item1', 'item2', 'item3'],
    }


@shared_task
def transform_data(extracted: Dict[str, Any]) -> Dict[str, Any]:
    """Transform extracted data"""
    logger.info(f'Transforming data from {extracted["source"]}')
    return {
        'source': extracted['source'],
        'data': [x.upper() for x in extracted['data']],
    }


@shared_task
def load_data(transformed: Dict[str, Any]) -> Dict[str, Any]:
    """Load transformed data"""
    logger.info(f'Loading data from {transformed["source"]}')
    return {
        'status': 'loaded',
        'count': len(transformed['data']),
    }


# ============================================================================
# SCHEDULED TASKS (for Celery Beat)
# ============================================================================

@shared_task
def scheduled_cleanup():
    """Run cleanup periodically (hourly)"""
    logger.info('Running scheduled cleanup')
    # Clean old data, clear cache, etc
    return 'Cleanup completed'


@shared_task
def scheduled_report():
    """Generate report periodically (daily)"""
    logger.info('Generating scheduled report')
    return 'Report generated'
