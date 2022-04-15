import uuid

from django.db import models


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    visible = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ("start_date", "name")

    def __str__(self):
        return self.name
