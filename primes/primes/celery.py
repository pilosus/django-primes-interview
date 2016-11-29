# Following Celery's Django Guide
# http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

import os
from celery import Celery


# set the default Django settings module for the `celery` program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "primes.settings")

# create a Celery app instance
app = Celery('primes')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# Celery will be looking for `tasks.py` file in apps' directories.
app.autodiscover_tasks()


# Dump its own request information
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
