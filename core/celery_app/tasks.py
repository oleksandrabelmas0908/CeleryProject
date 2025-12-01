from celery import shared_task

from datetime import timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import json
import logging
import uuid

from .models import Task


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCHEDULED_TASKS_KEY = "scheduled_tasks"


def get_scheduled_tasks():
    """Get all scheduled tasks from Redis cache."""
    tasks = cache.get(SCHEDULED_TASKS_KEY, {})
    return tasks


def add_scheduled_task(task_id, task_data):
    """Add a scheduled task to Redis cache."""
    tasks = get_scheduled_tasks()
    tasks[task_id] = task_data
    cache.set(SCHEDULED_TASKS_KEY, tasks, timeout=None)


def remove_scheduled_task(task_id):
    """Remove a scheduled task from Redis cache."""
    tasks = get_scheduled_tasks()
    if task_id in tasks:
        del tasks[task_id]
        cache.set(SCHEDULED_TASKS_KEY, tasks, timeout=None)


@shared_task()
def execute_task(task_id, title, delay):
    """Task that executes: creates completed Task and removes from Redis."""
    # Create the completed task in database
    task = Task.objects.create(title=title, delay=delay)
    task.save()

    # Remove from scheduled tasks in Redis
    remove_scheduled_task(task_id)

    logger.info(f"Completed task: {title} after {delay} seconds")
    return f"Task {title} completed after {delay} seconds."


def delayed_task(title: str, seconds: int = 0, minutes: int = 0, hours: int = 0):
    """Schedule a task to run at current time + delay."""
    total_delay = seconds + (minutes * 60) + (hours * 3600)
    now = timezone.localtime()
    eta = now + timedelta(seconds=total_delay)
    task_id = str(uuid.uuid4())
    
    # Store in Redis cache
    task_data = {
        "id": task_id,
        "title": title,
        "delay": total_delay,
        "eta": eta.strftime("%Y-%m-%d %H:%M:%S"),
        "scheduled_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    }
    add_scheduled_task(task_id, task_data)
    
    # Schedule the execution
    execute_task.apply_async(args=[task_id, title, total_delay], eta=eta)  # type: ignore
    logger.info(f"Scheduled task: {title} to run at {eta}")
    return task_data