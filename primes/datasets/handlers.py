import re
from django.utils import timezone

from .models import Dataset, Processing


# Model's helper functions #

def handle_uploaded_file(instance, filename):
    """
    Return a path to a file under MEDIA_ROOT directory.

    :param instance: An instance of the model where the FileField is defined
    :param filename: The filename that was originally given to the file.
    :return: A path to where file is to be saved at.
    """
    timestamp = re.sub(r'\.|:| |e|\+', '-', str(timezone.now()))
    return "uploads/{0}.json".format(timestamp)


# Test function chain #

def process_datasets(query_set):
    """
    Process each item of the given QuerySet.
    :param query_set: QuestySet of Dataset objects
    :return: None
    """

    # create Processing object
    processing = Processing.objects.create()

    for dataset in query_set:
        select_json_from_dataset(processing, dataset.id)


# TODO: Celery task; 1nd in chain; routing
def select_json_from_dataset(processing, dataset_id):
    """
    Pass a JSON from Dataset model for a given dataset to a test function.

    It's the 1st function in the chain.

    :param: processing: Processing instance
    :param dataset_id: Dataset model's primary key
    :return: None
    """
    dataset = Dataset.objects.get(pk=dataset_id)

    # mark dataset belonging to the given Processing item
    dataset.processing = processing

    # save dataset
    dataset.save()

    # if dataset hasn't got an exception on submission, process it in test function
    if not dataset.exception:
        test_function(dataset.id, dataset.data)
    else:
        # mark related processing having exceptions
        processing.exceptions = True
        processing.save()


# TODO: Celery task; 2nd in chain; routing
def test_function(dataset_id, json_data):
    """
    Pass a result of JSON processing to a function that saves result on a model.

    It's the 2nd function in the chain.

    :param dataset_id: Dataset model's primary key
    :param json_data: Python list of dicts
    :return: None
    """

    dataset = Dataset.objects.get(pk=dataset_id)
    processing = Processing.objects.get(pk=dataset.processing.id)
    result = []

    # calculate result; handle exceptions
    try:
        result = [{'result': pair['a'] + pair['b']} for pair in json_data]
    except Exception as err:
        # exception string = exception type + exception args
        exception_message = "{type}: {message}". \
            format(type=type(err).__name__, message=err)
        # save exception to db
        dataset.exception = exception_message
        processing.exceptions = True

    dataset.save()
    processing.save()

    # call function to save results
    if result:
        save_json_to_db(dataset.id, result)


# TODO: Celery task; 3rd in chain; routing
def save_json_to_db(dataset_id, json_data):
    """
    Save input JSON on a model.

    It's a 3rd unction in the chain.

    :param dataset_id: Dataset model's primary key
    :param json_data: Python list of dicts
    :return: None
    """
    dataset = Dataset.objects.get(pk=dataset_id)
    dataset.result = json_data
    dataset.save()

