"""Django views for triggering and monitoring scraping tasks"""

import logging
from typing import Dict, Any
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from celery.result import AsyncResult

logger = logging.getLogger(__name__)


class StartScrapingView(View):
    """Trigger scraping task from HTTP request"""

    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, spider_name: str = 'quotes') -> JsonResponse:
        """
        Submit scraping task.

        Args:
            spider_name: Name of spider to run (quotes, books)

        Returns:
            JSON with task_id and status
        """
        try:
            # Import here to avoid circular imports
            from code.celery_tasks.tasks import long_task

            # Submit task (would use specific spider task in real scenario)
            task = long_task.delay(10)  # Example: 10 second task

            logger.info(f'Scraping task submitted: {task.id} for spider: {spider_name}')

            return JsonResponse({
                'task_id': task.id,
                'spider_name': spider_name,
                'status': 'submitted',
                'message': f'Scraping {spider_name} has started in background'
            }, status=202)  # 202 Accepted

        except Exception as e:
            logger.error(f'Failed to submit scraping task: {e}')
            return JsonResponse({
                'error': 'Failed to submit task',
                'details': str(e)
            }, status=500)


class ScrapingStatusView(View):
    """Check status of scraping task"""

    @method_decorator(require_http_methods(["GET"]))
    def get(self, request, task_id: str) -> JsonResponse:
        """
        Get task status and progress.

        Args:
            task_id: Celery task ID

        Returns:
            JSON with status and results
        """
        try:
            task = AsyncResult(task_id)

            response = {
                'task_id': task_id,
                'status': task.status,
            }

            if task.status == 'PENDING':
                response.update({
                    'message': 'Task is waiting to execute',
                })

            elif task.status == 'PROGRESS':
                response.update({
                    'progress': task.info.get('current', 0),
                    'total': task.info.get('total', 0),
                    'percent': task.info.get('percent', 0),
                })

            elif task.status == 'SUCCESS':
                response.update({
                    'result': task.result,
                    'message': 'Task completed successfully',
                })

            elif task.status == 'FAILURE':
                response.update({
                    'error': str(task.info),
                    'message': 'Task failed with error',
                })

            elif task.status == 'RETRY':
                response.update({
                    'message': f'Task retrying (attempt {task.request.retries})',
                })

            return JsonResponse(response)

        except Exception as e:
            logger.error(f'Error checking task status: {e}')
            return JsonResponse({
                'error': 'Failed to get task status',
                'details': str(e)
            }, status=500)


class RevokeTaskView(View):
    """Cancel a running task"""

    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, task_id: str) -> JsonResponse:
        """
        Cancel a task.

        Args:
            task_id: Celery task ID to cancel

        Returns:
            JSON with revoke status
        """
        try:
            task = AsyncResult(task_id)
            task.revoke(terminate=True)

            logger.info(f'Task revoked: {task_id}')

            return JsonResponse({
                'task_id': task_id,
                'status': 'revoked',
                'message': 'Task has been canceled'
            })

        except Exception as e:
            logger.error(f'Failed to revoke task: {e}')
            return JsonResponse({
                'error': 'Failed to revoke task',
                'details': str(e)
            }, status=500)


# Function-based views for simpler use cases

def start_quotes_scrape(request):
    """Quick endpoint to start quotes scraping"""
    from code.celery_tasks.tasks import long_task

    task = long_task.delay(10)
    return JsonResponse({
        'task_id': task.id,
        'status': 'submitted'
    }, status=202)


def task_status(request, task_id):
    """Quick endpoint to check task status"""
    task = AsyncResult(task_id)

    response = {
        'task_id': task_id,
        'status': task.status,
    }

    if task.status == 'PROGRESS':
        response['progress'] = task.info
    elif task.status == 'SUCCESS':
        response['result'] = task.result
    elif task.status == 'FAILURE':
        response['error'] = str(task.info)

    return JsonResponse(response)


# URL configuration example (for reference)
"""
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Start scraping
    path('api/scrape/<str:spider_name>/',
         views.StartScrapingView.as_view(),
         name='start_scrape'),

    # Check status
    path('api/task/<str:task_id>/status/',
         views.ScrapingStatusView.as_view(),
         name='task_status'),

    # Revoke task
    path('api/task/<str:task_id>/revoke/',
         views.RevokeTaskView.as_view(),
         name='revoke_task'),

    # Quick endpoints
    path('api/scrape/quotes/',
         views.start_quotes_scrape,
         name='start_quotes'),
    path('api/task/<str:task_id>/',
         views.task_status,
         name='task_status_quick'),
]
"""
