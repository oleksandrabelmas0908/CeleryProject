from django.shortcuts import render

import logging

from .models import Task
from .tasks import delayed_task


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def index(request):

    if request.method == "POST":
        data =  request.POST

        title = data.get("title")
        delay = int(data.get("delay", 10))

        logger.info(f"Creating task with title: {title} and delay: {delay}")

        errors = []

        try:
            delayed_task.delay(title, delay)
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            errors.append(str(e))
            return render(request, "create-tasks.html", context={"errors": errors})
        
        messages = Task.objects.all()
        
        context = {
            "messages": messages,
            "errors": errors,
        }

    return render(request, "create-tasks.html", context=context)
