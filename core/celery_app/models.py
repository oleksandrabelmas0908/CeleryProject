from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=200)
    delay = models.IntegerField()

    def __str__(self):
        return f"{self.title} - {self.delay} seconds"