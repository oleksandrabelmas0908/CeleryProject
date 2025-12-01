from celery import shared_task

import time
import logging

from .models import Task


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@shared_task()
def delayed_task(title, delay):

    time.sleep(delay)

    task = Task.objects.create(title=title, delay=delay)
    task.save()

    logger.info(f"Completed task: {title} after {delay} seconds")

    return f"Task {title} completed after {delay} seconds."