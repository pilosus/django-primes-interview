from django.db import models
from django.contrib.postgres import fields


class Processing(models.Model):
    """
    A model for a processing of the submitted datasets.
    """
    exceptions = models.NullBooleanField(default=None)
    timestamp = models.DateTimeField(auto_now_add=True)


class Dataset(models.Model):
    """
    A model for submissions and their processings.

    `data` and `result` fields is PostgreSQL only.
    They require Django >= 1.9, PostgreSQL >= 9.4, Psycopg2 >= 2.5.4.
    """
    processing = models.ForeignKey(Processing, null=True, default=None)
    name = models.CharField(default='', max_length=255)
    data = fields.JSONField(null=True, default=None)
    result = fields.JSONField(null=True, default=None)
    exception = models.TextField(default='')
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{name} {timestamp}".format(name=self.name, timestamp=self.added)


