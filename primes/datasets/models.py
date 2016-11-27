from django.db import models
from django.contrib.postgres import fields

from .handlers import handle_uploaded_file


class Dataset(models.Model):
    """
    A model for submissions and their processings.

    `result` field is PostgreSQL only. IT requires Django >= 1.9,
    PostgreSQL >= 9.4, Psycopg2 >= 2.5.4.
    """
    upload = models.FileField(upload_to=handle_uploaded_file)
    result = fields.JSONField(null=True, default=None)
    status = models.NullBooleanField(default=None)
    exception = models.TextField(default='')
    added = models.DateTimeField(auto_now_add=True)
    checked = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{filename}".format(filename=self.upload.name)
