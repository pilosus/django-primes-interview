import os
import json
import datetime


from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.template.loader import render_to_string
from datasets.views import index, submit, process, report
from datasets.models import Processing, Dataset


class ProcessingAndDatasetModelsTest(TestCase):
    """
    Tests for App's models.
    """
    def test_create_processing(self):
        processing = Processing.objects.create()
        self.assertIsNone(processing.exceptions)
        self.assertIsNotNone(processing.last_modified)
        self.assertTrue((timezone.now() - processing.last_modified)
                        < datetime.timedelta(minutes=1))

    def test_create_dataset(self):
        dataset = Dataset.objects.create()
        self.assertIsNone(dataset.processing)
        self.assertIs(dataset.name, '')
        self.assertIsNone(dataset.data)
        self.assertIsNone(dataset.result)
        self.assertIs(dataset.exception, '')
        self.assertIsNotNone(dataset.added)
        self.assertTrue((timezone.now() - dataset.added)
                        < datetime.timedelta(minutes=1))


    def test_saving_and_retrieving_data(self):
        # create Dataset and Processing objects
        processing = Processing.objects.create()
        dataset = Dataset.objects.create()

        processing.exceptions = False
        processing.save()

        # directory where all dataset files for testing stored
        test_files_dir = os.path.join(settings.MEDIA_ROOT, 'tests')
        first_legal_file = os.path.join(test_files_dir, 'dataset1.json')

        # read first JSON data
        with open(first_legal_file) as data_file:
            data = json.load(data_file)

        dataset.processing = processing
        dataset.name = 'my_file.json'
        dataset.data = data
        dataset.result = {'result': 0}
        dataset.save()

        saved_processing = Processing.objects.first()
        saved_dataset = Dataset.objects.first()

        self.assertEqual(saved_processing.exceptions, False)
        self.assertEqual(saved_dataset.name, 'my_file.json')
        self.assertEqual(saved_dataset.data, data)
        self.assertEqual(saved_dataset.result, {'result': 0})


class IndexPageTest(TestCase):
    """
    Tests for index view.
    """
    def test_root_url_redirects_to_datasets_index_page(self):
        response = self.client.get('/')
        self.assertRedirects(response, reverse('datasets:index'))

    def test_index_page_returns_correct_html(self):
        response = self.client.get(reverse('datasets:index'))
        self.assertTemplateUsed(response, 'datasets/index.html')

    def test_index_page_has_page_alias_in_context(self):
        response = self.client.get(reverse("datasets:index"))
        self.assertEqual(response.context['page_alias'], 'home')


class SubmitPageTest(TestCase):
    """
    Tests for submit view.
    """
    def test_submit_page_returns_correct_html(self):
        response = self.client.get(reverse('datasets:submit'))
        self.assertTemplateUsed(response, 'datasets/submit.html')

    def test_submit_page_saves_a_POST_request(self):
        test_files_dir = os.path.join(settings.MEDIA_ROOT, 'tests')
        first_legal_file = os.path.join(test_files_dir, 'dataset1.json')

        # see https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.post
        with open(first_legal_file) as fp:
            self.client.post(reverse('datasets:submit'), {'upload': fp})

        self.assertEqual(Dataset.objects.count(), 1, 'File has not been uploaded')

        new_dataset = Dataset.objects.first()
        self.assertEqual(new_dataset.name, 'dataset1.json')

    def test_submit_page_redirects_to_process_page_after_POST_request(self):
        test_files_dir = os.path.join(settings.MEDIA_ROOT, 'tests')
        first_legal_file = os.path.join(test_files_dir, 'dataset1.json')

        # see https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.post
        with open(first_legal_file) as fp:
            response = self.client.post(reverse('datasets:submit'), data={'upload': fp})

        self.assertRedirects(response, reverse('datasets:process'))

    def test_submit_page_has_page_alias_in_context(self):
        response = self.client.get(reverse("datasets:submit"))
        self.assertEqual(response.context['page_alias'], 'submit')


class ProcessPageTest(TestCase):
    """
    Tests for process view.
    """
    def test_process_page_returns_correct_html(self):
        response = self.client.get(reverse('datasets:process'))
        self.assertTemplateUsed(response, 'datasets/process.html')

    def test_process_page_redirects_to_report_page_after_POST_request(self):
        dataset = Dataset.objects.create(name='dataset1.json')

        # directory where all dataset files for testing stored
        test_files_dir = os.path.join(settings.MEDIA_ROOT, 'tests')
        first_legal_file = os.path.join(test_files_dir, 'dataset1.json')

        # read first JSON data
        with open(first_legal_file) as data_file:
            data = json.load(data_file)

        dataset.data = data
        dataset.save()

        with open(first_legal_file) as fp:
            response = self.client.post(reverse('datasets:process'))

        self.assertRedirects(response, reverse('datasets:report'))

    def test_process_page_has_proper_pagination(self):
        data = [{"b": 1, "a": 3}]

        # we have 25 items per page
        for i in range(30):
            dataset = Dataset.objects.create()
            dataset.name = "{0}.json".format(i)
            dataset.data = data
            dataset.save()

        # access first page
        response = self.client.get(reverse("datasets:process"), data={'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['datasets']), 25)

        # access second page
        response = self.client.get(reverse("datasets:process"), data={'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['datasets']), 5)

    def test_process_page_has_page_alias_in_context(self):
        response = self.client.get(reverse("datasets:process"))
        self.assertEqual(response.context['page_alias'], 'process')


class ReportPageTest(TestCase):
    """
    Tests for report view.
    """
    def test_report_page_returns_correct_html(self):
        response = self.client.get(reverse('datasets:report'))
        self.assertTemplateUsed(response, 'datasets/report.html')

    def test_report_page_has_page_alias_in_context(self):
        response = self.client.get(reverse("datasets:report"))
        self.assertEqual(response.context['page_alias'], 'report')

    def test_report_page_has_proper_pagination(self):
        processing = Processing.objects.create()
        data = [{"b": 1, "a": 3}]

        # we have 25 items per page
        for i in range(30):
            dataset = Dataset.objects.create()
            dataset.processing = processing
            dataset.name = "{0}.json".format(i)
            dataset.data = data
            dataset.save()

        # access first page
        response = self.client.get(reverse("datasets:report"), data={'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['datasets']), 25)

        # access second page
        response = self.client.get(reverse("datasets:report"), data={'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['datasets']), 5)
