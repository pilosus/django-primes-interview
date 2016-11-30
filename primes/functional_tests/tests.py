import time
import os
import re

from django.test import LiveServerTestCase, TransactionTestCase
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


#class NewVisitorTest(LiveServerTestCase):
class NewVisitorTest(TransactionTestCase):
    """
    User stories as functional tests.
    """
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_list_table(self, row_text):
        """
        A non-testing helper function that checks if given text is in the table.

        :param row_text: str
        :return: assert
        """
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def check_for_text_in_rows_text_dump(self, row_text):
        """
        Check if given text among all found table rows.
        :return:
        """
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        rows_dump = ''.join([row.text for row in rows])
        self.assertIn(row_text, rows_dump)


    def test_can_navigate_submit_process_and_monitor_app(self):
        # `##` comments aren't exactly PEP8 friendly, but why the hell not?
        # `##` denotes milestones, as opposed to `#` for local bits

        ## User goes to the projects's homepage
        # TODO: uncomment when using LiveServerTestCase
        #self.browser.get(self.live_server_url)
        self.browser.get('http://localhost:8000')

        ## User notices he got redirected to the Datasets App's index page
        self.assertIn('Index', self.browser.title)
        self.assertIn('Datasets', self.browser.title)

        ## Following App's index page guidelines, User go to checkout submissions page
        # Selenium's docs: https://selenium-python.readthedocs.io/locating-elements.html
        submit_page_link = self.browser.find_element_by_id('submit_page')
        submit_page_link.click()
        time.sleep(2)

        self.assertIn('Submit', self.browser.title)
        self.assertIn('Datasets', self.browser.title)

        ## User submits a valid JSON file of the required format
        upload_file = self.browser.find_element_by_id('id_upload')

        # directory where all dataset files for testing stored
        test_files_dir = os.path.join(settings.MEDIA_ROOT, 'tests')
        first_legal_file = os.path.join(test_files_dir, 'dataset1.json')
        second_illegal_file = os.path.join(test_files_dir, 'dataset2falsy.json')
        third_legal_file = os.path.join(test_files_dir, 'dataset3.json')
        fourth_illegal_file = os.path.join(test_files_dir, 'fib_formula.png')

        # see also: http://stackoverflow.com/a/10472542/4241180
        upload_file.send_keys(first_legal_file)

        submit_button = self.browser.find_element_by_id('id_submit')
        submit_button.click()
        time.sleep(2)

        ## User got a notification, once file's uploaded
        alert_uploaded = self.browser.find_element_by_class_name('alert-info')
        self.assertIn('Your file has been submitted.', alert_uploaded.text)

        ## User sees the file submitted appears on the processing page
        filename_in_code_tag = self.browser.find_element_by_tag_name('code')
        self.assertIn('dataset1.json', filename_in_code_tag.text)

        ## User submits one more file, this time a file of invalid format
        submit_more_button = self.browser.find_element_by_id('submit_more')
        submit_more_button.click()
        time.sleep(2)

        upload_file = self.browser.find_element_by_id('id_upload')
        upload_file.send_keys(second_illegal_file)
        submit_button = self.browser.find_element_by_id('id_submit')
        submit_button.click()
        time.sleep(2)

        ## User starts out processing of the submitted files
        start_processing = self.browser.find_element_by_id('start_processing')
        start_processing.submit()
        time.sleep(2)

        ## User got notification that file processing has started
        alert_processing_started = self.browser.find_element_by_class_name('alert-info')
        self.assertIn('Please refresh the page in a few moments.',
                      alert_processing_started.text)

        # NB: for LiveServerTestCase only:
        # each tests run destroys the DB, so PK should start from 1.
        processing_started_text = alert_processing_started.text
        processing_pk = re.search(r'\d+', processing_started_text).group(0)
        self.assertIn('Datasets processing #{0} has started.'.format(processing_pk),
                      processing_started_text)

        # TODO: Check if transactions can be saved for LiveServerTestCase too
        # TODO: Otherwise fallback to TransactionTestCase
        # LiveServerTestCase doesn't save data to DB;
        # So if anywhere in the code there's Model query, then it will fail
        # This is what happens when first Celery tasks querying Dataset and Processing models:
        # datasets.models.DoesNotExist: Dataset matching query does not exist.
        # See also:
        # http://stackoverflow.com/a/10369987/4241180
        # See also (autocommit option):
        # http://stackoverflow.com/a/25081791/4241180
        # See also (atomic option)
        # http://stackoverflow.com/a/23914049/4241180
        # See also about autocommit=off

        # Sometimes you need to perform an action related to the current database transaction,
        # but only if the transaction successfully commits. Examples might include a Celery task,
        # an email notification, or a cache invalidation.

        # Django provides the on_commit() function to register callback functions that should be executed
        # after a transaction is successfully committed:
        # https://docs.djangoproject.com/en/1.10/topics/db/transactions/#deactivate-transaction-management
        # https://docs.djangoproject.com/en/1.10/topics/db/transactions/#django.db.transaction.atomic

        ## After a break, User refreshes Report page and sees that he got results
        time.sleep(5)
        #self.browser.refresh()
        report_page_link = self.browser.find_element_by_id('report_page')
        report_page_link.click()
        time.sleep(5)

        ## User sees that valid file processed correctly and has a result column filled
        # one of the results for the `first_legal_file`
        self.check_for_text_in_rows_text_dump("'result': 237620")

        ## User sees that invalid file has exception column filled and no results
        ## User sees that file with exception has red background color
        table_row_red_bg = self.browser.find_element_by_class_name('danger')

        # exception for `second_illegal_file`
        self.check_for_text_in_rows_text_dump("JSONDecodeError")
        self.assertIn('None', table_row_red_bg.text)
        time.sleep(5)

        ## On the right, User sees an abstract of the Last check (exceptions status, timestamp, etc)
        last_check_num = self.browser.find_element_by_id('id_last_check_num')
        self.assertIn(processing_pk, last_check_num.text)

        last_check_status = self.browser.find_element_by_id('id_last_check_status')
        self.assertIn('True', last_check_status.text)

        ## Satisfied, User goes back to sleep
        # Uncomment the self.fail before writing further tests!
        #self.fail('Finish the test!')
