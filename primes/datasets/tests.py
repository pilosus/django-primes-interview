from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string
from datasets.views import index, submit, process, report
from datasets.models import Processing, Dataset

# Create your tests here.
