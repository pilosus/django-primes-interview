import os
import json
import datetime


from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .models import Processing, Dataset
from .handlers import handle_uploaded_file
from .templatetags.datasets_extras import settings_value, replace_flower_port
from .tasks import first_select_json_from_dataset, second_test_function, third_save_json_to_db
from .exceptions import DatasetInputError


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

    def test_dataset_str_representation(self):
        dataset = Dataset.objects.create()
        dataset.name = 'my_file.json'
        dataset.save()

        self.assertEqual(str(dataset), 'my_file.json {0}'.format(dataset.added))

    def test_processing_str_representation(self):
        processing = Processing.objects.create()

        self.assertEqual(str(processing), '{0} {1}'.format(processing.pk,
                         processing.last_modified))

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

    def test_submit_page_handles_exceptions_on_POST_request(self):
        test_files_dir = os.path.join(settings.MEDIA_ROOT, 'tests')
        second_illegal_file = os.path.join(test_files_dir, 'dataset2falsy.json')

        # see https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.post
        with open(second_illegal_file) as fp:
            response = self.client.post(reverse('datasets:submit'), data={'upload': fp})

        dataset = Dataset.objects.first()
        self.assertIn('JSONDecodeError', dataset.exception)


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

    def test_process_page_pagination_without_datasets(self):
        response = self.client.get(reverse("datasets:process"), data={'page': 1})
        self.assertEqual(len(response.context['datasets']), 0)

    def test_process_page_has_page_alias_in_context(self):
        response = self.client.get(reverse("datasets:process"))
        self.assertEqual(response.context['page_alias'], 'process')

    def test_proces_page_pagination_out_of_range(self):
        data = [{"b": 1, "a": 3}]

        # we have 25 items per page
        for i in range(30):
            dataset = Dataset.objects.create()
            dataset.name = "{0}.json".format(i)
            dataset.data = data
            dataset.save()

        # access the page that is out of range
        response = self.client.get(reverse("datasets:process"), data={'page': 1000})

        self.assertEqual(len(response.context['datasets']), 5)


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

    def test_report_page_pagination_out_of_range(self):
        processing = Processing.objects.create()
        data = [{"b": 1, "a": 3}]

        # we have 25 items per page
        for i in range(30):
            dataset = Dataset.objects.create()
            dataset.processing = processing
            dataset.name = "{0}.json".format(i)
            dataset.data = data
            dataset.save()

        # access the page that is out of range
        response = self.client.get(reverse("datasets:report"), data={'page': 1000})
        self.assertEqual(len(response.context['datasets']), 5)


class HandlersTest(TestCase):
    """
    Tests for handlers.
    """
    def test_upload_file_handler(self):
        result = handle_uploaded_file(1, 1)
        self.assertTrue(result.startswith('uploads/'))
        self.assertTrue(result.endswith('.json'))
        self.assertIn(str(timezone.now().year), result)
        self.assertIn(str(timezone.now().month), result)
        self.assertIn(str(timezone.now().day), result)


class TemplateTagsTest(TestCase):
    """
    Tests for custom template filters, tags, etc.
    """

    def test_setting_value_filter(self):
        self.assertEqual(settings.MEDIA_ROOT,
                         settings_value('MEDIA_ROOT'))

    def test_replace_flower_port_tag(self):
        address1 = 'https://127.0.0.1:8000/'
        address2 = 'https://127.0.0.1/'

        self.assertEqual(replace_flower_port(address1),
                         'https://127.0.0.1:{0}/'.format(settings.FLOWER_PORT))
        self.assertEqual(replace_flower_port(address2),
                         'https://127.0.0.1:{0}/'.format(settings.FLOWER_PORT))


class TasksTest(TestCase):
    """
    Tests for Celery tasks.
    """
    def test_first_select_json_from_dataset(self):
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

        dataset.name = 'my_file.json'
        dataset.data = data
        dataset.result = {'result': 0}
        dataset.save()

        dataset_pk, processing_pk = first_select_json_from_dataset((dataset.pk, processing.pk))

        selected_dataset = Dataset.objects.get(pk=dataset_pk)
        selected_processing = Processing.objects.get(pk=processing_pk)

        self.assertEqual(selected_dataset.pk, dataset.pk)
        self.assertEqual(selected_processing.pk, processing.pk)

    def test_first_function_with_exception(self):
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

        dataset.name = 'my_file.json'
        dataset.data = data
        dataset.exception = 'Unknown Exception'
        dataset.save()

        # see: http://stackoverflow.com/a/3166985/4241180
        with self.assertRaises(DatasetInputError) as context:
            dataset_pk, processing_pk = first_select_json_from_dataset((dataset.pk, processing.pk))

        self.assertIn('Submitted dataset has got an exception', str(context.exception))

    def test_second_function_with_legal_input(self):
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

        dataset.name = 'my_file.json'
        dataset.data = data
        dataset.save()

        # what we expect
        expected_result = [{'result': pair['a'] + pair['b']} for pair in data]

        dataset_pk, actual_result = second_test_function((dataset.pk, processing.pk))

        self.assertEqual(expected_result, actual_result)

    def test_second_function_with_illegal_input(self):
        processing = Processing.objects.create()
        dataset = Dataset.objects.create()

        processing.exceptions = False
        processing.save()

        # directory where all dataset files for testing stored
        test_files_dir = os.path.join(settings.MEDIA_ROOT, 'tests')
        fourth_illegal_file = os.path.join(test_files_dir, 'dataset4falsy.json')

        # read first JSON data
        with open(fourth_illegal_file) as data_file:
            data = json.load(data_file)

        dataset.name = 'dataset4falsy.json'
        dataset.data = data
        dataset.save()

        dataset_pk, actual_result = second_test_function((dataset.pk, processing.pk))

        fetched_dataset = Dataset.objects.get(pk=dataset_pk)
        self.assertIsNotNone(fetched_dataset.exception)

    def test_third_function(self):
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

        expected_result = [{'result': pair['a'] + pair['b']} for pair in data]

        dataset.name = 'my_file.json'
        dataset.processing = processing
        dataset.data = data
        dataset.save()

        status = third_save_json_to_db((dataset.pk, expected_result))

        fetched_dataset = Dataset.objects.get(pk=dataset.pk)
        self.assertEqual(expected_result, fetched_dataset.result)
