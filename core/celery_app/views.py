from django.shortcuts import render, redirect

import logging

from .models import Task
from .tasks import delayed_task, get_scheduled_tasks


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def index(request):
    errors = []

    if request.method == "POST":
        data = request.POST

        title = data.get("title")
        delay = int(data.get("delay", 10))

        logger.info(f"Creating task with title: {title} and delay: {delay}")

        try:
            delayed_task(title, seconds=delay)
            # Redirect to prevent duplicate submission on refresh
            return redirect('create_task')
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            errors.append(str(e))

    # Get pending scheduled tasks from Redis
    scheduled_tasks = list(get_scheduled_tasks().values())
    logger.info(f"Scheduled tasks: {scheduled_tasks}")
    # Get completed tasks from database
    completed_tasks = Task.objects.all().order_by('-id')

    context = {
        "scheduled_tasks": scheduled_tasks,
        "completed_tasks": completed_tasks,
        "errors": errors,
    }

    return render(request, "create-tasks.html", context=context)
