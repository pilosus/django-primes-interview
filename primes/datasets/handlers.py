from .models import Processing
from .exceptions import DatasetInputError


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
        # TODO: Celery chain: chain(first(), second(), third())
        #select_json_from_dataset(dataset, processing)
        try:
            # step 1
            select_dataset, select_processing = select_json_from_dataset(dataset, processing)
        except DatasetInputError:
            continue

        # step 2
        test_dataset, test_result = test_function(select_dataset, select_processing)

        # step 3
        result = save_json_to_db(test_dataset, test_result)


# TODO: Celery task; 1nd in chain; routing
def select_json_from_dataset(dataset, processing):
    """
    Pass a JSON from Dataset model for a given dataset to a test function.

    It's the 1st function in the chain.

    :param: processing: Processing instance
    :param dataset: Dataset instance
    :return: Dataset instance; Processing instance
    """
    # mark dataset belonging to the given Processing item
    dataset.processing = processing

    # save dataset
    dataset.save()

    # if dataset got an exception on submission,
    # mark related processing having exceptions,
    # raise an error, so that further execution of the chain stops
    if dataset.exception:
        processing.exceptions = True
        processing.save()
        raise DatasetInputError('Submitted dataset has got an exception')

    return dataset, processing


# TODO: Celery task; 2nd in chain; routing
def test_function(dataset, processing):
    """
    Pass a result of JSON processing to a function that saves result on a model.

    It's the 2nd function in the chain.

    :param dataset: Dataset instance
    :param processing: Processing instance
    :return: Dataset instance; JSON (Python's list of dicts)
    """

    result = []

    # calculate result; handle exceptions
    try:
        result = [{'result': pair['a'] + pair['b']} for pair in dataset.data]
    except Exception as err:
        # exception string = exception type + exception args
        exception_message = "{type}: {message}". \
            format(type=type(err).__name__, message=err)
        # save exception to db
        dataset.exception = exception_message
        processing.exceptions = True

    dataset.save()
    processing.save()

    return dataset, result


# TODO: Celery task; 3rd in chain; routing
def save_json_to_db(dataset, json_data):
    """
    Save input JSON on a model.

    It's a 3rd unction in the chain.

    :param dataset: Dataset instance
    :param json_data: JSON (Python's list of dicts)
    :return: boolean: True if data saved to the data base, False otherwise
    """
    dataset.result = json_data
    dataset.save()

    return not dataset._state.adding
